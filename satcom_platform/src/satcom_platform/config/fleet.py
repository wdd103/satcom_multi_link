"""Portable STK aircraft/sensor templates and draft-only fleet cloning."""
from __future__ import annotations

import copy
import csv
import hashlib
import re
import shutil
import stat
from pathlib import Path


def copy_asset(source: Path, target: Path) -> None:
    if target.is_file() and target.read_bytes() == source.read_bytes():
        target.chmod(stat.S_IREAD | stat.S_IWRITE)
        return
    if target.exists():
        target.chmod(stat.S_IREAD | stat.S_IWRITE)
    shutil.copy2(source, target)
    target.chmod(stat.S_IREAD | stat.S_IWRITE)


def block(text: str, name: str) -> tuple[int, int, str]:
    match = re.search(rf"(?m)^\s*BEGIN {re.escape(name)}\s*$", text)
    if not match:
        raise ValueError(f"STK block not found: {name}")
    depth = 0
    for line in re.finditer(r"(?m)^[ \t]*(BEGIN|Class|END)\b[^\r\n]*", text[match.start():]):
        depth += 1 if line.group(1) in {"BEGIN", "Class"} else -1
        if depth == 0:
            end = match.start() + line.end()
            return match.start(), end, text[match.start():end]
    raise ValueError(f"Unclosed STK block: {name}")


def field(text: str, name: str, default="") -> str:
    match = re.search(rf"(?m)^\s*{re.escape(name)}[ \t]+([^\r\n]+)", text)
    return match.group(1).strip().strip('"') if match else default


def replace_field(text: str, name: str, value) -> str:
    pattern = rf"(?m)^([ \t]*{re.escape(name)})[ \t]+[^\r\n]+"
    if not re.search(pattern, text):
        raise ValueError(f"Missing editable STK field: {name}")
    return re.sub(pattern, lambda match: f"{match.group(1)}\t\t {value}", text, count=1)


def aircraft_names(scene: Path) -> list[str]:
    text = scene.read_text(encoding="utf-8-sig")
    match = re.search(r"(?ms)^\s*Class Aircraft\s*\n(.*?)^\s*END Class", text)
    if not match:
        raise ValueError("场景中未找到飞机对象")
    return [line.strip().split()[0] for line in match.group(1).splitlines() if line.strip()]


def import_scene(scene: Path, project: Path) -> tuple[list[dict], list[dict]]:
    """Copy template inputs; never load, save or modify the user's STK scene."""
    scene = scene.resolve()
    if scene.suffix.lower() != ".sc" or not scene.is_file():
        raise ValueError("请选择已有 STK .sc 场景文件")
    aircraft, sensors = [], []
    for aid in aircraft_names(scene):
        if not re.fullmatch(r"[A-Za-z][A-Za-z0-9_]*", aid):
            raise ValueError(f"飞机 ID 不兼容: {aid}")
        native, graphics = scene.parent / f"{aid}.ac", scene.parent / f"{aid}.ac3"
        text, visual = native.read_text(encoding="utf-8-sig"), graphics.read_text(encoding="utf-8-sig")
        related = sorted(p for p in scene.parent.iterdir() if p.suffix.lower() in {".sn", ".sn3", ".bmsk"})
        key = hashlib.sha256(native.read_bytes()+graphics.read_bytes()+str(scene).encode()+b"".join(p.read_bytes() for p in related)).hexdigest()[:12]
        asset = project / "assets/aircraft" / f"{aid}_{key}"
        asset.mkdir(parents=True, exist_ok=True)
        for source in (native, graphics):
            copy_asset(source, asset / source.name)
        model_name = field(visual, "Modelfile")
        candidates = [scene.parent / model_name, Path(model_name),
                      Path("C:/Program Files/AGI/STK 12/STKData/VO/Models") / model_name]
        model = next((p for p in candidates if p.is_file()), None)
        if model is None:
            raise ValueError(f"找不到飞机模型: {model_name}")
        copy_asset(model, asset / model.name)
        relative = lambda path: path.relative_to(project).as_posix()
        entry = {"aircraft_id": aid, "model_file": relative(asset/model.name),
                 "model_scale": float(field(visual, "ModelScale", "1")),
                 "native_template": relative(asset/native.name), "graphics_template": relative(asset/graphics.name),
                 "visibility_sensor_id": "", "attitude_mode": "TEMPLATE", "source_scene": str(scene)}
        for axis, value in zip("xyz", field(visual, "ModelPosOffset", "0 0 0").split()):
            entry[f"model_offset_{axis}_m"] = float(value) if field(visual,"UseModelPosOffset") == "Yes" else 0
        for axis, value in zip("xyz", field(visual, "ModelRotation", "0 0 0").split()):
            entry[f"model_rotation_{axis}_deg"] = float(value) if field(visual,"UseModelRotation") == "Yes" else 0
        children = block(text, "SubObjects")[2]
        match = re.search(r"(?ms)^\s*Class Sensor\s*\n(.*?)^\s*END Class", children)
        for name in ([line.strip().split()[0] for line in match.group(1).splitlines() if line.strip()] if match else []):
            sensor_file = scene.parent / f"{name}.sn"
            sensor_text = sensor_file.read_text(encoding="utf-8-sig")
            location = block(sensor_text, "Location")[2]
            pointing = block(sensor_text, "Pointing")[2]
            if "BEGIN Fixed" not in location or "BEGIN Fixed" not in pointing or "BEGIN SimpleCone" not in sensor_text:
                raise ValueError(f"传感器 {name} 当前仅支持固定位置/固定四元数指向/圆锥视场")
            copy_asset(sensor_file, asset / sensor_file.name)
            sensor_graphics = sensor_file.with_suffix(".sn3")
            if sensor_graphics.is_file():
                copy_asset(sensor_graphics, asset / sensor_graphics.name)
            mask_name = field(sensor_text, "AzElMask").removeprefix("AzElMaskFile:").strip().strip('"')
            mask_path = Path(mask_name)
            if not mask_path.is_absolute():
                mask_path = scene.parent / mask_path
            if mask_name and mask_path.is_file():
                copy_asset(mask_path, asset / mask_path.name)
            elif "SensorAzElMask IncludeIntervals" in sensor_text:
                raise ValueError(f"传感器 {name} 缺少遮挡文件: {mask_path}")
            sensor = {"aircraft_id": aid, "sensor_id": name, "enabled": True,
                      "native_template": relative(asset/sensor_file.name),
                      "graphics_template": relative(asset/sensor_graphics.name) if sensor_graphics.is_file() else "",
                      "half_angle_deg": float(field(sensor_text, "ConeAngle", "90")),
                      "use_mask": "SensorAzElMask IncludeIntervals" in sensor_text,
                      "mask_file": relative(asset/mask_path.name) if mask_name and mask_path.is_file() else ""}
            for axis in "xyz":
                sensor[f"{axis}_m"] = float(field(location, axis.upper(), "0"))
            for axis, native_key in (("qx","Qx"),("qy","Qy"),("qz","Qz"),("qw","Qs")):
                sensor[axis] = float(field(pointing, native_key, "1" if axis == "qw" else "0"))
            sensors.append(sensor)
            if not entry["visibility_sensor_id"]:
                entry["visibility_sensor_id"] = name
        aircraft.append(entry)
    return aircraft, sensors


def clone_fleet(data: dict, tables: dict, source_id: str, names: list[str], *, lat_step=0, lon_step=0, alt_step=0):
    data, tables = copy.deepcopy(data), copy.deepcopy(tables)
    known = {row["aircraft_id"] for row in tables["track"]["rows"]}
    if source_id not in known or not names or len(names) > 100:
        raise ValueError("选择已有飞机；一次复制 1–100 架")
    if len(set(names)) != len(names) or any(name in known or not re.fullmatch(r"[A-Za-z][A-Za-z0-9_]*", name) for name in names):
        raise ValueError("新飞机 ID 重复或格式不合法")
    planes = data.setdefault("aircraft", [])
    source = next((p for p in planes if p["aircraft_id"] == source_id), {"aircraft_id": source_id})
    sensors = data.setdefault("sensors", [])
    source_sensors = [s for s in sensors if s["aircraft_id"] == source_id]
    track = [row for row in tables["track"]["rows"] if row["aircraft_id"] == source_id]
    source_devices = {row["device_id"]: row for row in tables["devices"]["rows"]}
    source_antennas = {row["antenna_id"]: row for row in tables["antennas"]["rows"]}
    links = [link for link in data["links"] if any(source_devices[link[key]]["platform_type"] == "AIRCRAFT" and source_devices[link[key]]["platform_id"] == source_id for key in ("tx_id","rx_id"))]
    if not links:
        raise ValueError("源飞机没有可复制的收发机链路")
    used_devices, used_antennas = set(source_devices), set(source_antennas)
    used_links = {link["link_id"] for link in data["links"]}
    for index, name in enumerate(names, 1):
        planes.append({**copy.deepcopy(source), "aircraft_id": name})
        sensors.extend({**copy.deepcopy(sensor), "aircraft_id": name} for sensor in source_sensors)
        for row in track:
            item = {**row, "aircraft_id": name, "lat_deg": str(float(row["lat_deg"])+index*float(lat_step)),
                    "lon_deg": str(float(row["lon_deg"])+index*float(lon_step)), "alt_m": str(float(row["alt_m"])+index*float(alt_step))}
            if not -90 <= float(item["lat_deg"]) <= 90 or not -180 <= float(item["lon_deg"]) <= 180:
                raise ValueError("批量航迹偏移超出经纬度范围")
            tables["track"]["rows"].append(item)
        device_map, antenna_map = {}, {}
        for link in links:
            item = copy.deepcopy(link)
            item["link_id"] = f"{name}_{link['link_id']}"
            if item["link_id"] in used_links:
                raise ValueError("复制后链路 ID 冲突")
            used_links.add(item["link_id"])
            for key in ("tx_id","rx_id"):
                old_id = link[key]
                if old_id not in device_map:
                    device = copy.deepcopy(source_devices[old_id])
                    new_id = f"{name}_{old_id}"
                    if new_id in used_devices:
                        raise ValueError("复制后设备 ID 冲突")
                    used_devices.add(new_id)
                    device_map[old_id] = new_id
                    old_ant = device["antenna_id"]
                    if old_ant not in antenna_map:
                        new_ant = f"{name}_{old_ant}"
                        if new_ant in used_antennas:
                            raise ValueError("复制后天线 ID 冲突")
                        used_antennas.add(new_ant)
                        antenna_map[old_ant] = new_ant
                        ant = {**source_antennas[old_ant], "antenna_id": new_ant}
                        if ant["platform_type"] == "AIRCRAFT":
                            ant["platform_id"] = name
                        tables["antennas"]["rows"].append(ant)
                    device.update(device_id=new_id, antenna_id=antenna_map[old_ant])
                    if device["platform_type"] == "AIRCRAFT":
                        device["platform_id"] = name
                    tables["devices"]["rows"].append(device)
                item[key] = device_map[old_id]
            data["links"].append(item)
    data["inputs"]["aircraft_source"] = "CSV"
    return data, tables
