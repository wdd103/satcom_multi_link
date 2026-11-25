"""Local-only browser console backed by the shared configuration validator."""

from __future__ import annotations

import argparse
import csv
import os
import shutil
import json
import re
import subprocess
import sys
import tempfile
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from flask import Flask, jsonify, request, send_from_directory

from .adapters.tle import TLEError, parse_tle
from .config.load_save import load_project, save_project
from .config.models import ProjectConfig
from .config.validate import ID, validate_project
from .config.fleet import import_scene, clone_fleet
from .simulation.trajectory_generator import generate_track
from .simulation.run_plan import build_run_plan


ASSETS = Path(__file__).parent / "web_assets"
EXAMPLE = Path(__file__).parents[2] / "examples" / "minimal_project"
TABLE_FILES = {"track": "aircraft_track_file", "satellites": "satellite_config_file",
               "devices": "transmitter_receiver_file", "antennas": "antenna_file"}
SATELLITE_COLUMNS = ["schema_version", "satellite_id", "norad_id", "display_name", "enabled"]


def _satellite_table(records, previous: dict[str, Any]) -> dict[str, Any]:
    """Derive unique scene satellites from TLE without changing orbital lines."""
    old_by_norad = {str(row.get("norad_id")): row for row in previous.get("rows", [])}
    rows, seen, used_ids = [], set(), set()
    for record in records:
        norad = str(record.norad_id)
        if norad in seen:
            continue
        seen.add(norad)
        old = old_by_norad.get(norad, {})
        satellite_id = old.get("satellite_id") or f"SAT{norad}"
        if satellite_id in used_ids:
            satellite_id = f"SAT{norad}"
        used_ids.add(satellite_id)
        rows.append({"schema_version": "1.0", "satellite_id": satellite_id,
                     "norad_id": norad, "display_name": old.get("display_name") or record.name,
                     "enabled": old.get("enabled") if old.get("enabled") in {"true", "false"} else "true"})
    return {"columns": SATELLITE_COLUMNS, "rows": rows}


def _tle_preview(path: Path, previous: dict[str, Any]) -> dict[str, Any]:
    records = parse_tle(path)
    return {"tle_records": [{"norad_id": r.norad_id, "name": r.name,
                              "epoch_utc": r.epoch_utc.isoformat().replace("+00:00", "Z"),
                              "line1_number": r.line1_number, "line2_number": r.line2_number}
                             for r in records],
            "satellites": _satellite_table(records, previous)}


def _read_table(path: Path) -> dict[str, Any]:
    try:
        with path.open("r", encoding="utf-8-sig", newline="") as stream:
            reader = csv.DictReader(stream)
            return {"columns": reader.fieldnames or [], "rows": list(reader)}
    except OSError:
        return {"columns": [], "rows": []}


def _normalize_satellites(table: dict[str, Any]) -> dict[str, Any]:
    """Accept common spreadsheet renderings while keeping the CSV as source."""
    result = {"columns": table["columns"], "rows": [dict(row) for row in table["rows"]]}
    for row in result["rows"]:
        version = str(row.get("schema_version", "")).strip()
        if version in {"1", "1.0"}:
            row["schema_version"] = "1.0"
        enabled = str(row.get("enabled", "")).strip().lower()
        if enabled in {"true", "1"}:
            row["enabled"] = "true"
        elif enabled in {"false", "0"}:
            row["enabled"] = "false"
    return result


def _write_table(path: Path, columns: list[str], rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, name = tempfile.mkstemp(prefix=f".{path.stem}-", suffix=".csv", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=columns, extrasaction="ignore", lineterminator="\n")
            writer.writeheader()
            for row in rows:
                writer.writerow({column: row.get(column, "") for column in columns})
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(name, path)
    finally:
        if os.path.exists(name):
            os.unlink(name)


def _snapshot(config: ProjectConfig) -> dict[str, Any]:
    data = config.data
    inputs = data.get("inputs", {})
    satellite_value = inputs.get("satellite_config_file")
    satellite_csv = (config.resolve(satellite_value) if isinstance(satellite_value, str) and satellite_value else None)
    satellite_source = "CSV" if satellite_csv is not None and satellite_csv.is_file() else "TLE_CANDIDATE"
    tables = {}
    for display, key in TABLE_FILES.items():
        value = inputs.get(key)
        tables[display] = _read_table(config.resolve(value)) if isinstance(value, str) and value else {"columns": [], "rows": []}
    if satellite_source == "CSV":
        normalized = _normalize_satellites(tables["satellites"])
        needs_satellite_save = normalized != tables["satellites"]
        tables["satellites"] = normalized
    else:
        needs_satellite_save = False
    tle_records = []
    tle_path = inputs.get("tle_file")
    if isinstance(tle_path, str) and tle_path:
        try:
            parsed = _tle_preview(config.resolve(tle_path), tables["satellites"])
            tle_records = parsed["tle_records"]
            if satellite_source == "TLE_CANDIDATE":
                needs_satellite_save = True
                tables["satellites"] = parsed["satellites"]
        except (OSError, UnicodeError, TLEError):
            pass
    report = (_validate_draft(config, {"scenario": data, "tables": tables})
              if needs_satellite_save else validate_project(config))
    return {"root": str(config.root), "scenario_file": str(config.scenario_file),
            "scenario": data, "tables": tables, "tle_records": tle_records,
            "needs_satellite_save": needs_satellite_save, "satellite_source": satellite_source,
            "environment": _environment(),
            "mask_files": [p.relative_to(config.root).as_posix() for base in (config.root/"assets", config.root/"config") if base.is_dir() for p in sorted(base.rglob("*.bmsk"))],
            "validation": report.as_dict(),
            "capabilities": {"configuration": "AVAILABLE", "offline_validation": "AVAILABLE",
                             "stk_geometry": "AVAILABLE_WITH_STK12", "communications": "SIMPLE_BUDGET_WITH_STK12", "gui": "LOCAL_WEB"}}


def _environment() -> dict[str, Any]:
    result = {"stk_installed_file_version": None, "stk12_com_registered": False}
    try:
        import winreg

        with winreg.OpenKey(winreg.HKEY_CLASSES_ROOT, r"STK12.Application\CLSID") as key:
            clsid, _ = winreg.QueryValueEx(key, None)
        result["stk12_com_registered"] = True
        with winreg.OpenKey(winreg.HKEY_CLASSES_ROOT, rf"CLSID\{clsid}\LocalServer32") as key:
            command, _ = winreg.QueryValueEx(key, None)
        end = command.lower().find(".exe") + 4
        executable = command[:end].strip('"') if end >= 4 else ""
        if os.path.isfile(executable):
            import win32api

            info = win32api.GetFileVersionInfo(executable, "\\")
            ms, ls = info["FileVersionMS"], info["FileVersionLS"]
            result["stk_installed_file_version"] = ".".join(map(str, (ms >> 16, ms & 65535, ls >> 16, ls & 65535)))
    except (OSError, ImportError):
        pass
    return result


def create_app(project: str | Path | None = None) -> Flask:
    app = Flask(__name__, static_folder=None)
    app.config["PROJECT"] = Path(project or EXAMPLE).resolve()

    def current() -> ProjectConfig:
        return load_project(app.config["PROJECT"])

    @app.get("/")
    def index():
        return send_from_directory(ASSETS, "index.html")

    @app.get("/assets/<path:name>")
    def asset(name: str):
        return send_from_directory(ASSETS, name)

    @app.get("/api/project")
    def project_snapshot():
        try:
            return jsonify(_snapshot(current()))
        except (FileNotFoundError, ValueError) as exc:
            return jsonify({"error": str(exc)}), 400

    @app.post("/api/open")
    def open_project():
        path = request.get_json(silent=True, force=True).get("path", "")
        try:
            config = load_project(path)
            app.config["PROJECT"] = config.root
            return jsonify(_snapshot(config))
        except (FileNotFoundError, ValueError, OSError) as exc:
            return jsonify({"error": str(exc)}), 400

    @app.post("/api/new")
    def new_project():
        path = Path(request.get_json(silent=True, force=True).get("path", "")).resolve()
        if path.exists():
            return jsonify({"error": "目标目录已存在，请选择新目录。"}), 400
        try:
            shutil.copytree(EXAMPLE, path)
            app.config["PROJECT"] = path
            return jsonify(_snapshot(current()))
        except (OSError, ValueError) as exc:
            return jsonify({"error": str(exc)}), 400

    @app.post("/api/save-as")
    def save_as():
        path = Path(request.get_json(silent=True, force=True).get("path", "")).resolve()
        if path.exists():
            return jsonify({"error": "目标目录已存在，请选择新目录。"}), 400
        try:
            source = current()
            shutil.copytree(source.root, path, ignore=shutil.ignore_patterns("runs", "generated", "__pycache__", ".git"))
            app.config["PROJECT"] = path
            return jsonify(_snapshot(current()))
        except (OSError, ValueError) as exc:
            return jsonify({"error": str(exc)}), 400

    @app.post("/api/validate-draft")
    def validate_draft():
        try:
            report = _validate_draft(current(), request.get_json(force=True))
            return jsonify(report.as_dict())
        except (ValueError, OSError, TypeError) as exc:
            return jsonify({"error": str(exc)}), 400

    @app.post("/api/save")
    def save():
        try:
            config = current()
            payload = request.get_json(force=True)
            report = _validate_draft(config, payload)
            if not report.ok:
                return jsonify({"error": "校验未通过，未写入文件。", "validation": report.as_dict()}), 422
            data, tables = payload["scenario"], payload.get("tables", {})
            inputs = data["inputs"]
            for display, table in tables.items():
                if display not in TABLE_FILES:
                    continue
                relative = Path(inputs[TABLE_FILES[display]])
                if relative.is_absolute() or ".." in relative.parts:
                    raise ValueError("Web 编辑仅支持项目内的相对 CSV 路径")
                _write_table(config.root / relative, table["columns"], table["rows"])
            save_project(ProjectConfig(config.root, config.scenario_file, data))
            return jsonify(_snapshot(current()))
        except (ValueError, OSError, TypeError, KeyError) as exc:
            return jsonify({"error": str(exc)}), 400

    @app.post("/api/upload/<kind>")
    def upload(kind: str):
        if kind not in {"tle", "track", "mask"}:
            return jsonify({"error": "Unsupported upload kind"}), 400
        file = request.files.get("file")
        if file is None or not file.filename:
            return jsonify({"error": "请选择文件。"}), 400
        if kind == "tle" and Path(file.filename).suffix.lower() not in {".tle", ".tce"}:
            return jsonify({"error": "TLE 文件应为 .tle 或 .tce。"}), 400
        config = current()
        if kind == "mask":
            if Path(file.filename).suffix.lower() != ".bmsk":
                return jsonify({"error": "请选择 .bmsk 遮挡文件"}), 400
            content = file.read(20*1024*1024+1)
            if len(content) > 20*1024*1024 or b"BEGIN Exclusion" not in content:
                return jsonify({"error": "遮挡文件格式无效或超过 20 MB"}), 400
            name = re.sub(r"[^A-Za-z0-9_.-]", "_", Path(file.filename).stem)
            digest = __import__("hashlib").sha256(content).hexdigest()[:12]
            relative = Path("assets/masks") / f"{name}_{digest}.bmsk"
            target = config.root / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(content)
            return jsonify({"path": relative.as_posix()})
        target = config.root / "input" / ("satellites.tle" if kind == "tle" else "aircraft_track.csv")
        target.parent.mkdir(parents=True, exist_ok=True)
        fd, name = tempfile.mkstemp(prefix=".upload-", dir=target.parent)
        try:
            with os.fdopen(fd, "wb") as stream:
                shutil.copyfileobj(file.stream, stream)
                stream.flush()
                os.fsync(stream.fileno())
            if kind == "tle":
                _tle_preview(Path(name), {"rows": []})
            os.replace(name, target)
        except (OSError, UnicodeError, TLEError, ValueError, TypeError) as exc:
            return jsonify({"error": str(exc)}), 400
        finally:
            if os.path.exists(name):
                os.unlink(name)
        config.data["inputs"]["tle_file" if kind == "tle" else "aircraft_track_file"] = f"input/{target.name}"
        snapshot = _snapshot(config)
        return jsonify(snapshot)

    @app.post("/api/parse-tle")
    def preview_tle():
        try:
            config = current()
            payload = request.get_json(force=True)
            value = payload.get("path")
            if not isinstance(value, str) or not value.strip():
                raise ValueError("请输入 TLE 文件路径")
            path = config.resolve(value)
            if path.suffix.lower() not in {".tle", ".tce"}:
                raise ValueError("TLE 文件应为 .tle 或 .tce")
            satellite_csv = config.resolve(config.data["inputs"]["satellite_config_file"])
            source = "CSV" if satellite_csv.is_file() else "TLE_CANDIDATE"
            previous = _normalize_satellites(_read_table(satellite_csv)) if source == "CSV" else {"rows": []}
            preview = _tle_preview(path, previous)
            if source == "CSV":
                preview["satellites"] = previous
            preview["satellite_source"] = source
            return jsonify(preview)
        except (OSError, UnicodeError, TLEError, ValueError, TypeError) as exc:
            return jsonify({"error": str(exc)}), 400

    @app.post("/api/fleet/import-scene")
    def import_fleet_scene():
        try:
            config = current()
            aircraft, sensors = import_scene(Path(request.get_json(force=True)["path"]), config.root)
            return jsonify({"aircraft": aircraft, "sensors": sensors,
                            "mask_files": [p.relative_to(config.root).as_posix() for p in (config.root/"assets").rglob("*.bmsk")]})
        except (OSError, ValueError, TypeError, KeyError) as exc:
            return jsonify({"error": str(exc)}), 400

    @app.post("/api/fleet/clone")
    def clone_aircraft():
        try:
            payload = request.get_json(force=True)
            data, tables = clone_fleet(payload["scenario"], payload["tables"], payload["source_id"], payload["names"],
                lat_step=payload.get("lat_step",0), lon_step=payload.get("lon_step",0), alt_step=payload.get("alt_step",0))
            report = _validate_draft(current(), {"scenario": data, "tables": tables})
            if not report.ok:
                return jsonify({"error": "复制结果校验未通过", "validation": report.as_dict()}), 422
            return jsonify({"scenario": data, "tables": tables, "validation": report.as_dict()})
        except (OSError, ValueError, TypeError, KeyError) as exc:
            return jsonify({"error": str(exc)}), 400

    @app.post("/api/save-satellites")
    def save_satellites():
        try:
            config = current()
            table = request.get_json(force=True).get("satellites")
            if not isinstance(table, dict) or not isinstance(table.get("rows"), list):
                raise ValueError("卫星清单格式无效")
            table = _normalize_satellites(table)
            rows, satellite_ids, norad_ids = table["rows"], set(), set()
            for row in rows:
                if not isinstance(row, dict):
                    raise ValueError("卫星清单存在无效行")
                sid, norad = row.get("satellite_id"), str(row.get("norad_id"))
                if row.get("schema_version") != "1.0" or not isinstance(sid, str) or not ID.fullmatch(sid):
                    raise ValueError(f"卫星 {norad} 的版本或 ID 无效")
                if sid in satellite_ids or norad in norad_ids:
                    raise ValueError("卫星 ID 或 NORAD 编号重复")
                if row.get("enabled") not in {"true", "false"} or not str(row.get("display_name", "")).strip():
                    raise ValueError(f"卫星 {sid} 的启用状态或名称无效")
                satellite_ids.add(sid)
                norad_ids.add(norad)
            if not any(row["enabled"] == "true" for row in rows):
                raise ValueError("至少启用一颗卫星")
            relative = Path(config.data["inputs"]["satellite_config_file"])
            if relative.is_absolute() or ".." in relative.parts:
                raise ValueError("网页只支持写入项目内的卫星清单")
            _write_table(config.root / relative, SATELLITE_COLUMNS, rows)
            return jsonify(_snapshot(current()))
        except (OSError, UnicodeError, TLEError, ValueError, TypeError, KeyError) as exc:
            return jsonify({"error": str(exc)}), 400

    @app.post("/api/generate-track")
    def generate():
        try:
            config = current()
            values = request.get_json(force=True)
            generate_track(config.root, aircraft_id=values["aircraft_id"],
                           start_utc=values["start_utc"], stop_utc=values["stop_utc"],
                           step_s=float(values["step_s"]),
                           start_lat_deg=float(values["start_lat_deg"]),
                           start_lon_deg=float(values["start_lon_deg"]),
                           stop_lat_deg=float(values["stop_lat_deg"]),
                           stop_lon_deg=float(values["stop_lon_deg"]),
                           altitude_m=float(values["altitude_m"]))
            config.data["inputs"]["aircraft_source"] = "GENERATED"
            return jsonify(_snapshot(config))
        except (ValueError, KeyError, OSError) as exc:
            return jsonify({"error": str(exc)}), 400

    def run_root(config: ProjectConfig) -> Path:
        root = config.resolve(config.data["output"]["root_dir"]).resolve()
        if not root.is_relative_to(config.root):
            raise ValueError("网页运行仅支持项目目录内的输出路径")
        return root

    def read_run_status(folder: Path) -> dict[str, Any]:
        state = json.loads((folder / "status.json").read_text(encoding="utf-8"))
        if state.get("state") == "RUNNING":
            started = state.get("started_utc")
            try:
                age = (datetime.now(timezone.utc) - datetime.fromisoformat(started.replace("Z", "+00:00"))).total_seconds()
            except (AttributeError, ValueError):
                age = datetime.now(timezone.utc).timestamp() - folder.stat().st_mtime
            if age >= (7200 if state.get("pid") else 2700):
                state = {**state, "state": "INTERRUPTED", "error": "运行进程未报告完成；请检查 worker.log 或重新运行"}
        return state

    @app.post("/api/run")
    def start_run():
        try:
            config = current()
            report = validate_project(config)
            if not report.ok:
                return jsonify({"error": "请先修复已保存项目的离线校验错误", "validation": report.as_dict()}), 422
            plan = build_run_plan(config)
            payload = request.get_json(silent=True) or {}
            limit = int(payload.get("satellite_limit", 0))
            if limit < 0 or limit > len(plan.enabled_satellite_ids):
                raise ValueError("卫星数量超出已启用范围")
            root = run_root(config)
            root.mkdir(parents=True, exist_ok=True)
            for folder in root.iterdir():
                if not folder.is_dir() or not (folder / "status.json").is_file():
                    continue
                state = read_run_status(folder)
                if state.get("state") == "RUNNING":
                    return jsonify({"error": f"已有运行正在执行：{folder.name}"}), 409
            run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + "-" + uuid.uuid4().hex[:8]
            folder = root / run_id
            folder.mkdir()
            (folder / "status.json").write_text(json.dumps({"state": "RUNNING", "phase": "STARTING", "files": []}), encoding="utf-8")
            log = (folder / "worker.log").open("w", encoding="utf-8")
            try:
                worker_env = os.environ.copy()
                worker_env["PYTHONPATH"] = str(Path(__file__).parents[1]) + os.pathsep + worker_env.get("PYTHONPATH", "")
                subprocess.Popen([sys.executable, "-m", "satcom_platform.simulation.stk_run",
                                  str(config.root), str(folder), str(limit)], cwd=config.root,
                                 env=worker_env, stdout=log, stderr=subprocess.STDOUT,
                                 creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
            finally:
                log.close()
            return jsonify({"run_id": run_id, "state": "RUNNING"}), 202
        except (OSError, ValueError, TypeError, KeyError) as exc:
            return jsonify({"error": str(exc)}), 400

    def located_run(run_id: str) -> Path:
        if not re.fullmatch(r"\d{8}T\d{6}Z-[0-9a-f]{8}", run_id):
            raise ValueError("无效运行编号")
        folder = run_root(current()) / run_id
        if not folder.is_dir():
            raise FileNotFoundError("运行不存在")
        return folder

    @app.get("/api/runs")
    def list_runs():
        try:
            root = run_root(current())
            runs = []
            if root.is_dir():
                for folder in sorted(root.iterdir(), reverse=True):
                    if re.fullmatch(r"\d{8}T\d{6}Z-[0-9a-f]{8}", folder.name) and (folder / "status.json").is_file():
                        status = read_run_status(folder)
                        runs.append({"run_id": folder.name, **status})
            return jsonify({"runs": runs[:20]})
        except (OSError, ValueError, KeyError) as exc:
            return jsonify({"error": str(exc)}), 400

    @app.get("/api/runs/<run_id>")
    def run_status(run_id: str):
        try:
            return jsonify(read_run_status(located_run(run_id)))
        except (OSError, ValueError, KeyError) as exc:
            return jsonify({"error": str(exc)}), 404

    @app.get("/api/runs/<run_id>/files/<name>")
    def run_file(run_id: str, name: str):
        try:
            folder = located_run(run_id)
            status = json.loads((folder / "status.json").read_text(encoding="utf-8"))
            if status.get("state") != "COMPLETE" or name not in status.get("files", []):
                raise FileNotFoundError("文件尚未生成")
            return send_from_directory(folder, name, as_attachment=True)
        except (OSError, ValueError, KeyError) as exc:
            return jsonify({"error": str(exc)}), 404

    return app


def _validate_draft(config: ProjectConfig, payload: dict[str, Any]):
    data = payload.get("scenario")
    tables = payload.get("tables", {})
    if not isinstance(data, dict) or not isinstance(tables, dict):
        raise ValueError("Expected scenario and tables objects")
    with tempfile.TemporaryDirectory(prefix=".validation-", dir=config.root) as directory:
        stage = Path(directory)
        (stage / "config").mkdir()
        if (config.root / "assets").is_dir():
            shutil.copytree(config.root / "assets", stage / "assets")
        inputs = data.get("inputs", {})
        if not isinstance(inputs, dict):
            raise ValueError("inputs must be a mapping")
        for key in ("aircraft_track_file", "tle_file", "transmitter_receiver_file", "antenna_file", "satellite_config_file"):
            value = inputs.get(key)
            if not isinstance(value, str) or not value:
                continue
            relative = Path(value)
            if relative.is_absolute() or ".." in relative.parts:
                continue
            original = config.root / relative
            target = stage / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            if original.is_file():
                shutil.copy2(original, target)
        metadata = config.root / "input" / "aircraft_generation.yaml"
        if metadata.is_file():
            (stage / "input").mkdir(exist_ok=True)
            shutil.copy2(metadata, stage / "input" / metadata.name)
        for display, table in tables.items():
            if display not in TABLE_FILES or not isinstance(table, dict):
                continue
            value = inputs.get(TABLE_FILES[display])
            if not isinstance(value, str):
                continue
            relative = Path(value)
            if relative.is_absolute() or ".." in relative.parts:
                continue
            columns, rows = table.get("columns"), table.get("rows")
            if not isinstance(columns, list) or not isinstance(rows, list):
                raise ValueError(f"Invalid table {display}")
            _write_table(stage / relative, columns, rows)
        candidate = ProjectConfig(stage, stage / "config" / "scenario.yaml", data)
        return validate_project(candidate)


def main() -> None:
    parser = argparse.ArgumentParser(description="Local Satcom Platform web console")
    parser.add_argument("--project", default=str(EXAMPLE), help="Project directory or scenario.yaml")
    parser.add_argument("--port", type=int, default=8765)
    args = parser.parse_args()
    app = create_app(args.project)
    app.run(host="127.0.0.1", port=args.port, debug=False)


if __name__ == "__main__":
    main()
