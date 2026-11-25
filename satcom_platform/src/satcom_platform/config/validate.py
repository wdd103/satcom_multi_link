from __future__ import annotations

import csv
import hashlib
import math
import os
import re
from collections import defaultdict
from datetime import timedelta
from pathlib import Path
from typing import Any

import yaml

from satcom_platform.adapters.tle import TLEError, parse_tle
from satcom_platform.simulation.run_plan import parse_utc
from satcom_platform.simulation.rf_environment import MODELS, PARAMETERS
from satcom_platform.simulation.antenna_pattern import Apenst818

from .models import Issue, ProjectConfig, ValidationReport

ID = re.compile(r"^[A-Za-z][A-Za-z0-9_]*$")
TABLES = {
    "aircraft_track_file": ("aircraft_track", ("schema_version", "aircraft_id", "time_utc", "lat_deg", "lon_deg", "alt_m")),
    "satellite_config_file": ("satellite_config", ("schema_version", "satellite_id", "norad_id", "display_name", "enabled")),
    "transmitter_receiver_file": ("transmitter_receiver", ("schema_version", "device_id", "platform_type", "platform_id", "role", "frequency_hz", "power_dbw", "bandwidth_hz", "data_rate_bps", "noise_figure_db", "system_noise_temp_k", "feeder_loss_db", "polarization", "antenna_id")),
    "antenna_file": ("antenna", ("schema_version", "antenna_id", "platform_type", "platform_id", "model", "peak_gain_dbi", "center_frequency_hz", "beamwidth_deg", "pointing_mode", "mount_yaw_deg", "mount_pitch_deg", "mount_roll_deg", "pattern_file")),
}


def validate_project(config: ProjectConfig, level: str = "offline") -> ValidationReport:
    if level not in {"offline", "preflight"}:
        raise ValueError("level must be offline or preflight")
    issues: list[Issue] = []

    def add(code: str, message: str, location: str, *, warning: bool = False, input_error: bool = False) -> None:
        csv_location = location.startswith(("aircraft_track.csv", "satellite_config.csv", "transmitter_receiver.csv", "antenna.csv"))
        issues.append(Issue("WARNING" if warning else "ERROR", code, message, location,
                            "INPUT" if input_error or csv_location else "CONFIG"))

    def number(value: Any, location: str, *, positive: bool = False, minimum: float | None = None,
               maximum: float | None = None, required: bool = True) -> float | None:
        if value is None or value == "":
            if required:
                add("REQUIRED", "Value is required", location)
            return None
        try:
            parsed = float(value)
        except (TypeError, ValueError):
            add("NUMBER", f"Invalid number: {value}", location)
            return None
        if not math.isfinite(parsed) or (positive and parsed <= 0) or (minimum is not None and parsed < minimum) or (maximum is not None and parsed > maximum):
            add("RANGE", f"Value outside allowed range: {value}", location)
        return parsed

    def enum(value: Any, values: set[str], location: str) -> None:
        if value not in values:
            add("ENUM", f"Expected one of {', '.join(sorted(values))}", location)

    def ident(value: Any, location: str) -> None:
        if not isinstance(value, str) or not ID.fullmatch(value):
            add("ID", "Expected [A-Za-z][A-Za-z0-9_]*", location)

    data = config.data
    version = str(data.get("schema_version", ""))
    if version != "1.0":
        add("SCHEMA_VERSION", f"Unsupported schema version: {version or '<missing>'}", "scenario.yaml:schema_version")
    ident(data.get("project_id"), "scenario.yaml:project_id")
    for key in ("scenario", "inputs", "propagation", "attitude", "links", "output"):
        if key not in data:
            add("REQUIRED", "Section is required", f"scenario.yaml:{key}")
        elif not isinstance(data[key], list if key == "links" else dict):
            add("TYPE", "Section has wrong type", f"scenario.yaml:{key}")
    for key in data.keys() - {"schema_version", "project_id", "scenario", "inputs", "propagation", "attitude", "gateways", "links", "output", "aircraft", "sensors"}:
        add("UNKNOWN_FIELD", "Unknown top-level field retained", f"scenario.yaml:{key}", warning=True)

    scenario = data.get("scenario") if isinstance(data.get("scenario"), dict) else {}
    inputs = data.get("inputs") if isinstance(data.get("inputs"), dict) else {}
    propagation = data.get("propagation") if isinstance(data.get("propagation"), dict) else {}
    attitude = data.get("attitude") if isinstance(data.get("attitude"), dict) else {}
    output = data.get("output") if isinstance(data.get("output"), dict) else {}
    links = data.get("links") if isinstance(data.get("links"), list) else []
    gateways = {}
    gateway_list = data.get("gateways", [])
    if not isinstance(gateway_list, list):
        add("TYPE", "gateways must be a list", "scenario.yaml:gateways")
        gateway_list = []
    for index, gateway in enumerate(gateway_list):
        loc = f"scenario.yaml:gateways[{index}]"
        if not isinstance(gateway, dict):
            add("GATEWAY", "Gateway must be a mapping", loc)
            continue
        gid = gateway.get("gateway_id")
        ident(gid, f"{loc}.gateway_id")
        if isinstance(gid, str) and gid in gateways:
            add("DUPLICATE", f"Duplicate gateway {gid}", loc)
        if isinstance(gid, str):
            gateways[gid] = gateway
        number(gateway.get("lat_deg"), f"{loc}.lat_deg", minimum=-90, maximum=90)
        number(gateway.get("lon_deg"), f"{loc}.lon_deg", minimum=-180, maximum=180)
        number(gateway.get("alt_m"), f"{loc}.alt_m")

    times = []
    for key in ("start_utc", "stop_utc"):
        try:
            times.append(parse_utc(str(scenario[key])))
        except (KeyError, ValueError, TypeError):
            add("UTC_TIME", "Valid ISO 8601 UTC timestamp required", f"scenario.yaml:scenario.{key}")
    if len(times) == 2 and times[0] >= times[1]:
        add("TIME_ORDER", "start_utc must be before stop_utc", "scenario.yaml:scenario")
    number(scenario.get("sample_step_s"), "scenario.yaml:scenario.sample_step_s", positive=True)
    number(scenario.get("min_elevation_deg", 0), "scenario.yaml:scenario.min_elevation_deg", minimum=0, maximum=90)
    enum(scenario.get("time_scale"), {"UTC"}, "scenario.yaml:scenario.time_scale")
    enum(scenario.get("earth_model"), {"WGS84"}, "scenario.yaml:scenario.earth_model")
    enum(scenario.get("output_coordinate_frame"), {"WGS84_GEODETIC"}, "scenario.yaml:scenario.output_coordinate_frame")
    enum(inputs.get("aircraft_source"), {"CSV", "GENERATED"}, "scenario.yaml:inputs.aircraft_source")
    enum(propagation.get("satellite_propagator"), {"SGP4"}, "scenario.yaml:propagation.satellite_propagator")
    for key, (model, *_) in MODELS.items():
        enum(propagation.get(key, "NONE"), {"NONE", model}, f"scenario.yaml:propagation.{key}")
    interference_enabled = propagation.get("downlink_interference_model", "NONE") == "COCHANNEL_AGGREGATE"
    enum(propagation.get("downlink_interference_model", "NONE"), {"NONE", "COCHANNEL_AGGREGATE"}, "scenario.yaml:propagation.downlink_interference_model")
    enum(propagation.get("doppler_compensation", "FIXED"), {"FIXED", "IDEAL"}, "scenario.yaml:propagation.doppler_compensation")
    if interference_enabled and propagation.get("doppler_compensation") != "IDEAL":
        add("INTERFERENCE_DOPPLER", "Co-channel aggregation requires IDEAL Doppler compensation", "scenario.yaml:propagation.doppler_compensation")
    enum(propagation.get("polarization_loss_model"), {"EXPLICIT"}, "scenario.yaml:propagation.polarization_loss_model")
    for key, (default, minimum, maximum) in PARAMETERS.items():
        number(propagation.get(key, default), f"scenario.yaml:propagation.{key}", minimum=minimum, maximum=maximum)
    try:
        if float(propagation.get("cloud_thickness_m", 500)) > float(propagation.get("cloud_ceiling_m", 3000)):
            add("CLOUD_LAYER", "Cloud thickness cannot exceed cloud ceiling", "scenario.yaml:propagation.cloud_thickness_m")
    except (TypeError, ValueError):
        pass
    number(propagation.get("tle_max_age_days_warning", 14), "scenario.yaml:propagation.tle_max_age_days_warning", minimum=0)
    number(propagation.get("default_other_loss_db", 0), "scenario.yaml:propagation.default_other_loss_db", minimum=0)
    enum(attitude.get("aircraft_mode"), {"UNAVAILABLE", "FROM_CSV", "ASSUMED_LEVEL_TRACK"}, "scenario.yaml:attitude.aircraft_mode")
    enum(attitude.get("satellite_mode"), {"UNAVAILABLE"}, "scenario.yaml:attitude.satellite_mode")
    if not isinstance(output.get("root_dir"), str) or not output["root_dir"].strip():
        add("REQUIRED", "Output directory required", "scenario.yaml:output.root_dir")
    else:
        out_dir = config.resolve(output["root_dir"])
        existing = next((p for p in (out_dir, *out_dir.parents) if p.exists()), None)
        if existing is None or not os.access(existing, os.W_OK):
            add("OUTPUT_DIRECTORY", "Output directory parent is not writable", "scenario.yaml:output.root_dir")
        if out_dir.is_absolute() and not out_dir.is_relative_to(config.root):
            add("NONPORTABLE_PATH", "External absolute output path", "scenario.yaml:output.root_dir", warning=True)

    tables: dict[str, list[dict[str, str]]] = {}
    for key, (name, required_columns) in TABLES.items():
        value = inputs.get(key)
        location = f"scenario.yaml:inputs.{key}"
        if not isinstance(value, str) or not value.strip():
            add("REQUIRED", "Input path required", location)
            tables[name] = []
            continue
        path = config.resolve(value)
        if path.is_absolute() and not path.is_relative_to(config.root):
            add("NONPORTABLE_PATH", "External absolute input path", location, warning=True)
        try:
            with path.open("r", encoding="utf-8-sig", newline="") as stream:
                reader = csv.DictReader(stream)
                headers = reader.fieldnames or []
                missing = set(required_columns) - set(headers)
                for column in sorted(missing):
                    add("CSV_COLUMN", f"Missing column {column}", str(path), input_error=True)
                for column in sorted(set(headers) - set(required_columns)):
                    if name == "aircraft_track" and column in {"heading_deg", "pitch_deg", "roll_deg"}:
                        continue
                    if name == "antenna" and column in {"aperture_efficiency", "pattern_coefficient_a", "pattern_coefficient_b"}:
                        continue
                    add("UNKNOWN_FIELD", f"Unknown CSV column retained: {column}", str(path), warning=True)
                rows = []
                for line_no, row in enumerate(reader, 2):
                    row["__line__"] = str(line_no)
                    rows.append(row)
                    if None in row:
                        add("CSV_WIDTH", "Too many fields", f"{path}:{line_no}", input_error=True)
                    if row.get("schema_version") != "1.0":
                        add("SCHEMA_VERSION", "Row requires schema_version 1.0", f"{path}:{line_no}", input_error=True)
                tables[name] = rows
                if not rows:
                    add("CSV_EMPTY", "No data rows", str(path), input_error=True)
        except (OSError, UnicodeError, csv.Error) as exc:
            add("INPUT_UNREADABLE", str(exc), str(path), input_error=True)
            tables[name] = []

    tle_value = inputs.get("tle_file")
    tles = []
    if not isinstance(tle_value, str) or not tle_value.strip():
        add("REQUIRED", "TLE path required", "scenario.yaml:inputs.tle_file")
    else:
        tle_path = config.resolve(tle_value)
        if tle_path.suffix.lower() not in {".tle", ".tce"}:
            add("TLE_EXTENSION", "Expected .tle or .tce", str(tle_path))
        if tle_path.is_absolute() and not tle_path.is_relative_to(config.root):
            add("NONPORTABLE_PATH", "External absolute input path", str(tle_path), warning=True)
        try:
            tles = parse_tle(tle_path)
        except (OSError, UnicodeError, TLEError) as exc:
            add("TLE_INVALID", str(exc), str(tle_path), input_error=True)

    tracks = tables.get("aircraft_track", [])
    aircraft: set[str] = set()
    track_times: dict[str, list] = defaultdict(list)
    keys = set()
    for row in tracks:
        loc = f"aircraft_track.csv:{row['__line__']}"
        aid = row.get("aircraft_id", "")
        ident(aid, f"{loc}:aircraft_id")
        aircraft.add(aid)
        try:
            instant = parse_utc(row.get("time_utc", ""))
            track_times[aid].append(instant)
            key = (aid, instant)
            if key in keys:
                add("DUPLICATE", "Duplicate aircraft/time key", loc, input_error=True)
            keys.add(key)
        except (TypeError, ValueError):
            add("UTC_TIME", "Invalid UTC time", f"{loc}:time_utc", input_error=True)
        number(row.get("lat_deg"), f"{loc}:lat_deg", minimum=-90, maximum=90)
        number(row.get("lon_deg"), f"{loc}:lon_deg", minimum=-180, maximum=180)
        number(row.get("alt_m"), f"{loc}:alt_m")
        attitude_values = [row.get(x, "") for x in ("heading_deg", "pitch_deg", "roll_deg")]
        if any(attitude_values) and not all(attitude_values):
            add("ATTITUDE_PARTIAL", "All three attitude fields must be present together", loc, input_error=True)
        for field, value in zip(("heading_deg", "pitch_deg", "roll_deg"), attitude_values):
            if value:
                number(value, f"{loc}:{field}")
    for aid, values in track_times.items():
        if values != sorted(values) or len(values) != len(set(values)):
            add("TRACK_ORDER", "Times must be strictly increasing per aircraft", f"aircraft_track.csv:{aid}", input_error=True)
        if len(times) == 2 and values and (values[0] > times[0] or values[-1] < times[1]):
            add("TRACK_COVERAGE", "Track does not cover entire scenario", f"aircraft_track.csv:{aid}", input_error=True)
    if attitude.get("aircraft_mode") == "FROM_CSV" and any(
        not all(row.get(x) for x in ("heading_deg", "pitch_deg", "roll_deg")) for row in tracks
    ):
        add("ATTITUDE_MISSING", "FROM_CSV requires all three attitude fields on every track row", "aircraft_track.csv", input_error=True)
    if inputs.get("aircraft_source") == "GENERATED":
        generated_file = config.root / "input" / "aircraft_generation.yaml"
        if not generated_file.is_file():
            add("GENERATION_METADATA", "Generated track requires input/aircraft_generation.yaml", str(generated_file), input_error=True)
        else:
            try:
                metadata = yaml.safe_load(generated_file.read_text(encoding="utf-8-sig"))
                track_path = config.resolve(inputs["aircraft_track_file"])
                actual_hash = hashlib.sha256(track_path.read_bytes()).hexdigest()
                if not isinstance(metadata, dict) or metadata.get("track_sha256") != actual_hash:
                    add("GENERATION_HASH", "Generated track hash does not match metadata", str(generated_file), input_error=True)
            except (OSError, UnicodeError, yaml.YAMLError, KeyError) as exc:
                add("GENERATION_METADATA", str(exc), str(generated_file), input_error=True)

    plane_settings, sensor_settings = {}, {}
    for section in ("aircraft", "sensors"):
        entries = data.get(section, [])
        if not isinstance(entries, list):
            add("TYPE", f"{section} must be a list", f"scenario.yaml:{section}")
            continue
        for index, entry in enumerate(entries):
            loc = f"scenario.yaml:{section}[{index}]"
            if not isinstance(entry, dict):
                add("TYPE", "Expected a mapping", loc)
                continue
            aid = entry.get("aircraft_id")
            ident(aid, f"{loc}.aircraft_id")
            if aid not in aircraft:
                add("AIRCRAFT_REFERENCE", f"Aircraft {aid} has no input track", loc)
            for key in ("model_file", "native_template", "graphics_template", "mask_file"):
                value = entry.get(key)
                if value:
                    if not isinstance(value, str) or not config.resolve(value).is_file():
                        add("ASSET_MISSING", f"Missing {key}: {value}", loc)
                    elif not config.resolve(value).resolve().is_relative_to(config.root.resolve()):
                        add("NONPORTABLE_PATH", f"External asset: {value}", loc, warning=True)
            if section == "aircraft":
                if aid in plane_settings:
                    add("DUPLICATE", f"Duplicate aircraft configuration {aid}", loc)
                plane_settings[aid] = entry
                number(entry.get("model_scale", 1), f"{loc}.model_scale", positive=True)
                for axis in "xyz":
                    number(entry.get(f"model_offset_{axis}_m", 0), f"{loc}.model_offset_{axis}_m")
                    number(entry.get(f"model_rotation_{axis}_deg", 0), f"{loc}.model_rotation_{axis}_deg")
            else:
                sid = entry.get("sensor_id")
                ident(sid, f"{loc}.sensor_id")
                pair = (aid, sid)
                if pair in sensor_settings:
                    add("DUPLICATE", f"Duplicate sensor {aid}/{sid}", loc)
                sensor_settings[pair] = entry
                for key in ("enabled", "use_mask"):
                    if not isinstance(entry.get(key, True if key == "enabled" else False), bool):
                        add("BOOL", f"{key} requires true or false", loc)
                if entry.get("use_mask") and not entry.get("mask_file"):
                    add("MASK_REQUIRED", "Enabled body masking requires a .bmsk file", loc)
                if entry.get("mask_file") and Path(str(entry["mask_file"])).suffix.lower() != ".bmsk":
                    add("MASK_FORMAT", "Body mask must be a .bmsk file", loc)
                number(entry.get("half_angle_deg", 90), f"{loc}.half_angle_deg", positive=True, maximum=180)
                for key in ("x_m", "y_m", "z_m", "qx", "qy", "qz", "qw"):
                    number(entry.get(key, 1 if key == "qw" else 0), f"{loc}.{key}")
                try:
                    norm = sum(float(entry.get(key, 1 if key == "qw" else 0))**2 for key in ("qx","qy","qz","qw"))
                    if abs(norm-1) > .001:
                        add("SENSOR_QUATERNION", "Sensor quaternion must have unit norm", loc)
                except (ValueError, TypeError, OverflowError):
                    pass
    for aid, entry in plane_settings.items():
        selected = entry.get("visibility_sensor_id")
        if selected and not sensor_settings.get((aid, selected), {}).get("enabled", False):
            add("SENSOR_REFERENCE", f"Selected sensor is missing or disabled: {aid}/{selected}", "scenario.yaml:aircraft")

    satellites: dict[str, dict[str, str]] = {}
    enabled_norad: set[int] = set()
    tle_ids = {record.norad_id for record in tles}
    for norad in sorted(tle_ids):
        if sum(record.norad_id == norad for record in tles) > 1:
            add("TLE_MULTIPLE_EPOCHS", f"NORAD {norad} has multiple TLE epochs; M2 selection policy is pending", str(config.resolve(tle_value)), warning=True)
    try:
        max_age = float(propagation.get("tle_max_age_days_warning", 14))
        if not math.isfinite(max_age) or max_age < 0:
            max_age = 14
    except (TypeError, ValueError):
        max_age = 14
    for row in tables.get("satellite_config", []):
        loc = f"satellite_config.csv:{row['__line__']}"
        sid = row.get("satellite_id", "")
        ident(sid, f"{loc}:satellite_id")
        if sid in satellites:
            add("DUPLICATE", f"Duplicate satellite ID {sid}", loc, input_error=True)
        satellites[sid] = row
        if row.get("enabled") not in {"true", "false"}:
            add("BOOL", "enabled must be true or false", f"{loc}:enabled", input_error=True)
        try:
            norad = int(row.get("norad_id", ""))
            if norad not in tle_ids:
                add("TLE_REFERENCE", f"NORAD {norad} absent from TLE", loc, input_error=True)
            if row.get("enabled") == "true":
                if norad in enabled_norad:
                    add("DUPLICATE", f"Enabled NORAD {norad} repeated", loc, input_error=True)
                enabled_norad.add(norad)
            if len(times) == 2 and row.get("enabled") == "true":
                matching = [r for r in tles if r.norad_id == norad]
                if matching and min(abs((times[0] - r.epoch_utc).total_seconds()) for r in matching) > max_age * 86400:
                    add("TLE_AGE", f"TLE epoch is more than {max_age:g} days from scenario start", loc, warning=True)
        except (TypeError, ValueError):
            add("NORAD_ID", "Invalid NORAD ID", f"{loc}:norad_id", input_error=True)
    if not any(r.get("enabled") == "true" for r in satellites.values()):
        add("NO_SATELLITE", "At least one enabled satellite required", "satellite_config.csv")

    antennas: dict[str, dict[str, str]] = {}
    devices: dict[str, dict[str, str]] = {}
    for name, destination, id_field in (("antenna", antennas, "antenna_id"), ("transmitter_receiver", devices, "device_id")):
        for row in tables.get(name, []):
            loc = f"{name}.csv:{row['__line__']}"
            eid = row.get(id_field, "")
            ident(eid, f"{loc}:{id_field}")
            if eid in destination:
                add("DUPLICATE", f"Duplicate {id_field} {eid}", loc, input_error=True)
            destination[eid] = row
            enum(row.get("platform_type"), {"AIRCRAFT", "SATELLITE", "GATEWAY"}, f"{loc}:platform_type")
            pid = row.get("platform_id", "")
            ident(pid, f"{loc}:platform_id")
            owners = {"AIRCRAFT": aircraft, "SATELLITE": satellites, "GATEWAY": gateways}
            if pid not in owners.get(row.get("platform_type"), set()):
                add("PLATFORM_REFERENCE", f"Unknown platform {pid}", f"{loc}:platform_id", input_error=True)
            if name == "antenna":
                enum(row.get("model"), {"SIMPLE", "APENST818V01"}, f"{loc}:model")
                if row.get("model") == "APENST818V01":
                    try:
                        pattern = Apenst818.from_row(row)
                        if pattern.metadata()["wide_beam_adaptation"]:
                            add("PATTERN_WIDE_BEAM", "APENST818 phi0 outside reference range 0.1–10 degrees; explicit wide-beam adaptation", loc, warning=True)
                    except (ValueError, TypeError, KeyError, OverflowError) as exc:
                        add("ANTENNA_PATTERN", str(exc), loc)
                enum(row.get("pointing_mode"), {"ISOTROPIC", "BORESIGHT_FIXED", "TARGET_TRACKING"}, f"{loc}:pointing_mode")
                number(row.get("peak_gain_dbi"), f"{loc}:peak_gain_dbi")
                number(row.get("center_frequency_hz"), f"{loc}:center_frequency_hz", positive=True)
                if row.get("pointing_mode") != "ISOTROPIC":
                    number(row.get("beamwidth_deg"), f"{loc}:beamwidth_deg", positive=True, maximum=360)
                for field in ("mount_yaw_deg", "mount_pitch_deg", "mount_roll_deg"):
                    number(row.get(field), f"{loc}:{field}")
                if row.get("pattern_file"):
                    add("PATTERN_UNSUPPORTED", "External pattern adapter is not implemented", f"{loc}:pattern_file")
                if row.get("pointing_mode") == "BORESIGHT_FIXED" and row.get("platform_type") == "AIRCRAFT" and attitude.get("aircraft_mode") == "UNAVAILABLE":
                    add("ATTITUDE_UNAVAILABLE", "Fixed aircraft boresight requires attitude", loc)
                if row.get("pointing_mode") == "BORESIGHT_FIXED" and row.get("platform_type") == "SATELLITE":
                    add("ATTITUDE_UNAVAILABLE", "Fixed satellite boresight requires attitude", loc)
                if row.get("pointing_mode") == "TARGET_TRACKING":
                    add("IDEAL_TRACKING", "TARGET_TRACKING assumes ideal pointing", loc, warning=True)
            else:
                enum(row.get("role"), {"TX", "RX"}, f"{loc}:role")
                enum(row.get("polarization"), {"LINEAR_H", "LINEAR_V", "RHCP", "LHCP"}, f"{loc}:polarization")
                number(row.get("frequency_hz"), f"{loc}:frequency_hz", positive=True)
                try:
                    ghz = float(row.get("frequency_hz", "")) / 1e9
                    for key, low, high in (("atmosphere_model", 1, 1000), ("rain_model", 1, 55),
                                           ("cloud_fog_model", 1, 1000), ("tropo_scintillation_model", 4, 20)):
                        if propagation.get(key, "NONE") != "NONE" and not low <= ghz <= high:
                            add("RF_MODEL_FREQUENCY", f"{key} requires {low}–{high} GHz", f"{loc}:frequency_hz")
                except (TypeError, ValueError):
                    pass
                number(row.get("bandwidth_hz"), f"{loc}:bandwidth_hz", positive=True)
                number(row.get("feeder_loss_db"), f"{loc}:feeder_loss_db", minimum=0)
                if row.get("role") == "TX":
                    number(row.get("power_dbw"), f"{loc}:power_dbw")
                    number(row.get("data_rate_bps"), f"{loc}:data_rate_bps", positive=True)
                    for field in ("noise_figure_db", "system_noise_temp_k"):
                        if row.get(field):
                            add("NOT_APPLICABLE", f"TX {field} must be empty", f"{loc}:{field}")
                elif row.get("role") == "RX":
                    if row.get("power_dbw") or row.get("data_rate_bps"):
                        add("NOT_APPLICABLE", "RX power and data rate must be empty", loc)
                    has_nf, has_temp = bool(row.get("noise_figure_db")), bool(row.get("system_noise_temp_k"))
                    if has_nf == has_temp:
                        add("NOISE_METRIC", "RX requires exactly one noise metric", loc)
                    if has_nf:
                        number(row["noise_figure_db"], f"{loc}:noise_figure_db", minimum=0)
                    if has_temp:
                        number(row["system_noise_temp_k"], f"{loc}:system_noise_temp_k", positive=True)

    for row in devices.values():
        aid = row.get("antenna_id", "")
        antenna = antennas.get(aid)
        loc = f"transmitter_receiver.csv:{row['__line__']}"
        if antenna is None:
            add("ANTENNA_REFERENCE", f"Unknown antenna {aid}", f"{loc}:antenna_id", input_error=True)
        else:
            if (row.get("platform_type"), row.get("platform_id")) != (antenna.get("platform_type"), antenna.get("platform_id")):
                add("ANTENNA_OWNER", f"Antenna {aid} belongs to another platform", loc, input_error=True)
            try:
                if abs(float(row["frequency_hz"]) / float(antenna["center_frequency_hz"]) - 1) > .001:
                    add("ANTENNA_FREQUENCY", f"Antenna {aid} center frequency differs by over 0.1%", loc)
            except (ValueError, ZeroDivisionError, TypeError, KeyError):
                pass

    seen_links = set()
    if not links:
        add("LINKS_EMPTY", "At least one link required", "scenario.yaml:links")
    for index, link in enumerate(links):
        loc = f"scenario.yaml:links[{index}]"
        if not isinstance(link, dict):
            add("LINK", "Link must be a mapping", loc)
            continue
        lid = link.get("link_id")
        ident(lid, f"{loc}.link_id")
        if isinstance(lid, str):
            if lid in seen_links:
                add("DUPLICATE", f"Duplicate link ID {lid}", loc)
            seen_links.add(lid)
        direction = link.get("direction")
        enum(direction, {"UPLINK", "DOWNLINK", "FEEDER_DOWNLINK", "FEEDER_UPLINK"}, f"{loc}.direction")
        tx_id, rx_id = link.get("tx_id"), link.get("rx_id")
        tx = devices.get(tx_id) if isinstance(tx_id, str) else None
        rx = devices.get(rx_id) if isinstance(rx_id, str) else None
        if tx is None or rx is None:
            add("DEVICE_REFERENCE", "Link references missing TX or RX", loc, input_error=True)
            continue
        mask_sensor = link.get("mask_sensor_id")
        if mask_sensor:
            owner = next((device["platform_id"] for device in (tx,rx) if device.get("platform_type") == "AIRCRAFT"), None)
            if not sensor_settings.get((owner, mask_sensor), {}).get("enabled", False):
                add("SENSOR_REFERENCE", f"Link sensor is missing or disabled: {owner}/{mask_sensor}", loc)
        expected = {"UPLINK": ("AIRCRAFT", "SATELLITE"), "DOWNLINK": ("SATELLITE", "AIRCRAFT"),
                    "FEEDER_DOWNLINK": ("SATELLITE", "GATEWAY"), "FEEDER_UPLINK": ("GATEWAY", "SATELLITE")}.get(direction)
        if tx.get("role") != "TX" or rx.get("role") != "RX" or (tx.get("platform_type"), rx.get("platform_type")) != expected:
            add("LINK_PAIR", "Invalid TX/RX roles or direction", loc)
        if rx.get("platform_type") == "SATELLITE" and satellites.get(rx.get("platform_id"), {}).get("enabled") != "true":
            add("LINK_INACTIVE_SATELLITE", "Link RX satellite is disabled and will be omitted from the scene", loc, warning=True)
        if tx.get("platform_type") == "SATELLITE" and satellites.get(tx.get("platform_id"), {}).get("enabled") != "true":
            add("LINK_INACTIVE_SATELLITE", "Link TX satellite is disabled and will be omitted from the scene", loc, warning=True)
        try:
            if abs(float(tx["frequency_hz"]) / float(rx["frequency_hz"]) - 1) > .001:
                add("LINK_FREQUENCY", "TX/RX frequencies differ by over 0.1%", loc)
            if float(tx["bandwidth_hz"]) != float(rx["bandwidth_hz"]):
                add("BANDWIDTH_MISMATCH", "TX/RX bandwidth differs", loc, warning=True)
        except (ValueError, ZeroDivisionError, TypeError, KeyError):
            pass
        if tx.get("polarization") != rx.get("polarization"):
            add("POLARIZATION_MISMATCH", "TX/RX polarizations differ", loc, warning=True)
        if interference_enabled and direction in {"DOWNLINK", "FEEDER_DOWNLINK"}:
            for device in (tx, rx):
                antenna = antennas.get(device.get("antenna_id"), {})
                if antenna.get("model") != "APENST818V01" or antenna.get("pointing_mode") != "TARGET_TRACKING":
                    add("INTERFERENCE_ANTENNA", "Downlink interference requires APENST818V01 and TARGET_TRACKING on both ends", loc)
            # A TX template is one physical continuously active beam per satellite.
            for other in links[:index]:
                if isinstance(other, dict) and other.get("tx_id") == tx_id:
                    add("INTERFERENCE_TX_TARGET", "Each downlink TX must have exactly one beam target; use separate TX IDs for separate beams", loc)
            try:
                if float(tx.get("bandwidth_hz") or 0) != 2 * float(tx.get("data_rate_bps") or 0):
                    add("INTERFERENCE_SPECTRUM", "Default BPSK spectrum requires TX bandwidth = 2 × data rate", loc)
            except (ValueError, TypeError):
                pass
        number(link.get("min_sinr_db"), f"{loc}.min_sinr_db", required=False)
        number(link.get("other_loss_db", 0), f"{loc}.other_loss_db", minimum=0)
        number(link.get("min_cn_db"), f"{loc}.min_cn_db", required=False)

    if level == "preflight":
        issues.append(Issue("WARNING", "STK_SIMPLE_BUDGET_ASSUMPTIONS", "STK uses on-axis Simple TX/RX equivalents; APENST818 off-axis interference and SINR are computed by the platform; mount angles are not simulated", "STK", "STK"))
    return ValidationReport(tuple(issues))
