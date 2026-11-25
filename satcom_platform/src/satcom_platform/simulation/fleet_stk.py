"""Instantiate portable native aircraft templates and native body-mask sensors."""
from __future__ import annotations

import hashlib
import shutil
import os
from pathlib import Path

from satcom_platform.config.fleet import block, field, replace_field


def stage_assets(config, output: Path) -> None:
    if (config.root / "assets").is_dir():
        shutil.copytree(config.root / "assets", output / "assets", dirs_exist_ok=True)


def local_asset(config, output: Path, value: str) -> Path:
    source = config.resolve(value).resolve()
    if source.is_relative_to(config.root.resolve()):
        target = output / source.relative_to(config.root.resolve())
    else:
        target = output / "assets/external" / (hashlib.sha256(str(source).encode()).hexdigest()[:10] + "_" + source.name)
    target.parent.mkdir(parents=True, exist_ok=True)
    if not target.exists():
        shutil.copy2(source, target)
    return target


def create_aircraft(root, config, output: Path, aid: str) -> dict:
    settings = next((p for p in config.data.get("aircraft", []) if p["aircraft_id"] == aid), {})
    if settings.get("native_template"):
        text = config.resolve(settings["native_template"]).read_text(encoding="utf-8-sig")
        old_name = field(text, "Name")
        begin, end, _ = block(text, "SubObjects")
        text = text[:begin] + "\n    BEGIN SubObjects\n    END SubObjects" + text[end:]
        text = replace_field(text, "Name", aid).replace(f"Aircraft/{old_name}", f"Aircraft/{aid}")
        begin, end, external = block(text, "StkExternal")
        text = text[:begin] + replace_field(external, "Filename", f"{aid}.e") + text[end:]
        native = output / f"{aid}.ac"
        native.write_text(text, encoding="utf-8")
        if settings.get("graphics_template"):
            visual = config.resolve(settings["graphics_template"]).read_text(encoding="utf-8-sig")
            if settings.get("model_file"):
                model = local_asset(config, output, settings["model_file"])
                visual = replace_field(visual, "Modelfile", model.relative_to(output).as_posix())
                visual = replace_field(visual, "UseCatalogModelFile", "No")
            visual = replace_field(visual, "ModelScale", settings.get("model_scale", 1))
            offset = [float(settings.get(f"model_offset_{axis}_m", 0)) for axis in "xyz"]
            visual = replace_field(visual, "UseModelPosOffset", "Yes" if any(offset) else "No")
            visual = replace_field(visual, "ModelPosOffset", " ".join(map(str,offset)))
            native.with_suffix(".ac3").write_text(visual, encoding="utf-8")
        root.ExecuteCommand(f'Load / */Aircraft "{native}"')
    else:
        root.ExecuteCommand(f"New / Aircraft {aid}")
    root.ExecuteCommand(f'SetState */Aircraft/{aid} FromFile "{output / (aid + ".e")}"')
    if settings.get("model_file"):
        model = local_asset(config, output, settings["model_file"])
        root.ExecuteCommand(f'VO */Aircraft/{aid} Model File "{model}"')
        root.ExecuteCommand(f"VO */Aircraft/{aid} ScaleModel {float(settings.get('model_scale',1)):g}")
    return settings


def create_sensors(root, config, output: Path) -> list[dict]:
    result = []
    for settings in config.data.get("sensors", []):
        if not settings.get("enabled", True):
            continue
        aid, sid = settings["aircraft_id"], settings["sensor_id"]
        path = f"*/Aircraft/{aid}/Sensor/{sid}"
        if settings.get("native_template"):
            native = output / "sensor_templates" / aid / f"{sid}.sn"
            native.parent.mkdir(parents=True, exist_ok=True)
            text = config.resolve(settings["native_template"]).read_text(encoding="utf-8-sig")
            text = replace_field(text, "Name", sid)
            begin,end,_ = block(text,"SubObjects")
            text = text[:begin]+"\n    BEGIN SubObjects\n    END SubObjects"+text[end:]
            if settings.get("mask_file"):
                mask = local_asset(config, output, settings["mask_file"])
                mask_relative = os.path.relpath(mask,native.parent).replace("\\","/")
                text = replace_field(text,"AzElMask", f"AzElMaskFile: {mask_relative}")
            native.write_text(text, encoding="utf-8")
            if settings.get("graphics_template"):
                shutil.copy2(config.resolve(settings["graphics_template"]), native.with_suffix(".sn3"))
            root.ExecuteCommand(f'Load / */Aircraft/{aid}/Sensor "{native}"')
        else:
            root.ExecuteCommand(f"New / */Aircraft/{aid}/Sensor {sid}")
        root.GetObjectFromPath(path).Pattern.ConeAngle = float(settings.get("half_angle_deg",90))
        location = " ".join(f"{float(settings.get(f'{axis}_m',0)):.12g}" for axis in "xyz")
        root.ExecuteCommand(f"Location {path} Fixed Cartesian {location}")
        quaternion = " ".join(f"{float(settings.get(key,1 if key=='qw' else 0)):.16g}" for key in ("qx","qy","qz","qw"))
        root.ExecuteCommand(f"Point {path} Fixed Quaternion {quaternion}")
        if settings.get("use_mask"):
            mask = local_asset(config, output, settings["mask_file"])
            root.ExecuteCommand(f'SetAzElMask {path} MaskFile "{mask}"')
            root.ExecuteCommand(f"SetConstraint {path} SensorAzElMask On")
        else:
            root.ExecuteCommand(f"SetAzElMask {path} None")
            root.ExecuteCommand(f"SetConstraint {path} SensorAzElMask Off")
        result.append({**settings, "stk_path": path})
    return result


def sample_sensors(root, sensors, satellite_ids, times, step, geometry_visible, progress):
    visibility, rows = {}, []
    progress.stage("BODY_MASK", len(sensors)*len(satellite_ids)*len(times))
    for sensor in sensors:
        obj = root.GetObjectFromPath(sensor["stk_path"])
        aid, sensor_id = sensor["aircraft_id"], sensor["sensor_id"]
        for sid in satellite_ids:
            progress.update(len(rows), f"遮挡可见性 {aid}/{sensor_id} → {sid}")
            access = obj.GetAccessToObject(root.GetObjectFromPath(f"*/Satellite/{sid}"))
            access.ComputeAccess()
            intervals = [access.ComputedAccessIntervalTimes.GetInterval(i) for i in range(access.ComputedAccessIntervalTimes.Count)]
            for index, instant in enumerate(times):
                second = index*step
                clear = any(float(a)-1e-6 <= second <= float(b)+1e-6 for a,b in intervals)
                geometry = geometry_visible[(aid,sid,instant)]
                visibility[(aid,sensor_id,sid,instant)] = clear
                rows.append({"aircraft_id":aid,"sensor_id":sensor_id,"satellite_id":sid,"time_utc":instant,
                             "geometric_access":str(geometry).lower(),"sensor_access":str(clear).lower(),
                             "effective_access":str(geometry and clear).lower(),"use_body_mask":str(sensor.get("use_mask",False)).lower()})
                progress.update(len(rows), f"{aid}/{sensor_id} → {sid} · 采样 {index+1}/{len(times)}")
    return visibility, rows


def selected_sensor(data: dict, link: dict, aircraft_id: str) -> str:
    if not aircraft_id:
        return ""
    return link.get("mask_sensor_id") or next((p.get("visibility_sensor_id", "") for p in data.get("aircraft", []) if p["aircraft_id"] == aircraft_id), "")
