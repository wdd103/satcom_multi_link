"""Build an STK 12 geometry scene and export only values returned by STK."""

from __future__ import annotations

import csv
import hashlib
import json
import math
import os
import re
import shutil
import sys
import traceback
import zipfile
from datetime import datetime, timezone
from pathlib import Path

from satcom_platform.adapters.tle import parse_tle
from satcom_platform.config.load_save import load_project
from satcom_platform.simulation.comm_model import simple_link_values
from satcom_platform.simulation.rf_environment import configure_environment, configure_receiver_rain
from satcom_platform.simulation.progress import RunProgress
from satcom_platform.simulation.omnet_export import export_timeline
from satcom_platform.simulation.antenna_pattern import Apenst818
from satcom_platform.simulation.interference import RESULT_COLUMNS, DETAIL_COLUMNS
from satcom_platform.simulation.stk_interference import analyze as analyze_interference
from satcom_platform.simulation.fleet_stk import stage_assets, create_aircraft, create_sensors, sample_sensors, selected_sensor
from satcom_platform.simulation.run_plan import build_run_plan, parse_utc


def utc_text(value: datetime) -> str:
    return value.strftime("%d %b %Y %H:%M:%S.%f")[:-3]


def iso_text(value: datetime) -> str:
    return value.isoformat(timespec="milliseconds").replace("+00:00", "Z")


def write_json(path: Path, data: dict) -> None:
    temp = path.with_suffix(".tmp")
    temp.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    temp.replace(path)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


def write_csv(path: Path, columns: list[str], rows: list[dict]) -> None:
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=columns, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def make_ephemeris(rows: list[dict[str, str]], path: Path) -> None:
    """Use geodetic WGS84 height in meters and first-order Lagrange interpolation."""
    epoch = parse_utc(rows[0]["time_utc"])
    lines = ["stk.v.12.0", "BEGIN Ephemeris", f"NumberOfEphemerisPoints {len(rows)}",
             f"ScenarioEpoch {utc_text(epoch)}", "CentralBody Earth", "CoordinateSystem Fixed",
             "DistanceUnit Meters", "InterpolationMethod Lagrange", "InterpolationSamplesM1 1",
             "EphemerisLLATimePos"]
    for row in rows:
        seconds = (parse_utc(row["time_utc"]) - epoch).total_seconds()
        lines.append(f"{seconds:.6f} {float(row['lat_deg']):.10f} {float(row['lon_deg']):.10f} {float(row['alt_m']):.3f}")
    lines.append("END Ephemeris")
    path.write_text("\n".join(lines) + "\n", encoding="ascii")


def values(result, name: str) -> list:
    return list(result.DataSets.GetDataSetByName(name).GetValues())


def run(project: Path, output: Path, satellite_limit: int = 0, *, isolated_stk: bool = False) -> dict:
    output = output.resolve()
    config = load_project(project)
    plan = build_run_plan(config)
    output.mkdir(parents=True, exist_ok=True)
    status_path = output / "status.json"
    status = {"state": "RUNNING", "phase": "PREPARING", "run_id": output.name, "error": None, "files": [], "pid": os.getpid(),
              "stk_connected": False, "scenario_created": False, "scene_saved": False,
              "started_utc": iso_text(datetime.now(timezone.utc))}
    progress = RunProgress(status, lambda: write_json(status_path, status))
    progress.stage("PREPARING")

    tracks = read_csv(config.resolve(config.data["inputs"]["aircraft_track_file"]))
    aircraft_ids = sorted({row["aircraft_id"] for row in tracks})
    satellites = [row for row in read_csv(config.resolve(config.data["inputs"]["satellite_config_file"]))
                  if row["enabled"] == "true"]
    if satellite_limit:
        satellites = satellites[:satellite_limit]
    if not satellites:
        raise ValueError("No enabled satellites selected")
    tle_path = config.resolve(config.data["inputs"]["tle_file"])
    tle_by_id = {}
    for record in parse_tle(tle_path):
        # Prefer the record closest to scenario start when a file has repeated NORAD IDs.
        key = record.norad_id
        if key not in tle_by_id or abs((record.epoch_utc - plan.time_grid[0]).total_seconds()) < abs((tle_by_id[key].epoch_utc - plan.time_grid[0]).total_seconds()):
            tle_by_id[key] = record
    for aid in aircraft_ids:
        make_ephemeris([row for row in tracks if row["aircraft_id"] == aid], output / f"{aid}.e")

    progress.stage("CONNECTING")
    import pythoncom
    import win32com.client
    pythoncom.CoInitialize()
    try:
        app = (win32com.client.DispatchEx if isolated_stk else win32com.client.Dispatch)("STK12.Application")
        app.Visible = not isolated_stk
        root = app.Personality2
        status["stk_connected"] = True
        write_json(status_path, status)
        root.UnitPreferences.Item("DateFormat").SetCurrentUnit("UTCG")
        root.UnitPreferences.Item("Distance").SetCurrentUnit("m")
        try:
            existing = str(root.CurrentScenario.InstanceName)
        except Exception:
            existing = ""
        if existing:
            if not re.fullmatch(re.escape(config.data["project_id"]) + r"_\d{8}T\d{6}Z_[0-9a-f]{8}", existing):
                raise RuntimeError(f"STK already has an unrelated open scenario: {existing}")
            root.CloseScenario()
        root.NewScenario(f"{config.data['project_id']}_{output.name.replace('-', '_')}")
        scene = root.CurrentScenario
        scene.SetTimePeriod(utc_text(plan.time_grid[0]), utc_text(plan.time_grid[-1]))
        progress.attach_stk(root)
        status["scenario_created"] = True
        write_json(status_path, status)
        root.Rewind()
        progress.stage("RF_ENVIRONMENT")
        rf_environment = configure_environment(root, config.data["propagation"])
        write_json(output / "rf_environment.json", rf_environment)
        gateways = config.data.get("gateways", [])
        progress.stage("BUILDING", len(aircraft_ids) + len(satellites) + len(gateways))
        stage_assets(config, output)
        built_objects = 0
        for aid in aircraft_ids:
            progress.update(built_objects, f"航空器 {aid}")
            create_aircraft(root, config, output, aid)
            built_objects += 1
            progress.update(built_objects, f"航空器 {aid}")
        for sat in satellites:
            sid, norad = sat["satellite_id"], int(sat["norad_id"])
            progress.update(built_objects, f"卫星 {sid}")
            root.ExecuteCommand(f"New / Satellite {sid}")
            root.ExecuteCommand(f'ImportTLEFile * "{tle_path}" SSCNumber {norad} Satellite */Satellite/{sid} AutoPropagate On TimeStep {float(config.data["scenario"]["sample_step_s"]):g}')
            built_objects += 1
            progress.update(built_objects, f"卫星 {sid}")
        for gateway in gateways:
            gid = gateway["gateway_id"]
            root.ExecuteCommand(f"New / Facility {gid}")
            root.ExecuteCommand(f"SetPosition */Facility/{gid} Geodetic {float(gateway['lat_deg']):.10f} {float(gateway['lon_deg']):.10f} {float(gateway['alt_m']):.3f}")
            built_objects += 1
            progress.update(built_objects, f"网关 {gid}")
        sensors = create_sensors(root, config, output)

        progress.stage("COMPUTING", len(aircraft_ids) * len(satellites) * len(plan.time_grid))
        root.UnitPreferences.Item("DateFormat").SetCurrentUnit("EpSec")
        start = 0.0
        step = float(config.data["scenario"]["sample_step_s"])
        stop = (plan.time_grid[-1] - plan.time_grid[0]).total_seconds()
        aircraft_rows = []
        geometry_rows = []
        min_elevation = float(config.data["scenario"].get("min_elevation_deg", 0))
        for aid in aircraft_ids:
            aircraft = root.GetObjectFromPath(f"*/Aircraft/{aid}")
            lla = aircraft.DataProviders.Item("LLA State").Group.Item("Fixed")
            result = lla.ExecElements(start, stop, step, ["Time", "Lat", "Lon", "Alt"])
            lat, lon, alt = (values(result, name) for name in ("Lat", "Lon", "Alt"))
            if len(lat) != len(plan.time_grid):
                raise RuntimeError(f"STK returned {len(lat)} aircraft points; expected {len(plan.time_grid)}")
            for index, instant in enumerate(plan.time_grid):
                aircraft_rows.append({"aircraft_id": aid, "time_utc": iso_text(instant),
                                      "lat_deg": lat[index], "lon_deg": lon[index], "alt_m": alt[index]})
            source = [row for row in tracks if row["aircraft_id"] == aid]
            for index, row in ((0, source[0]), (-1, source[-1])):
                if abs(float(lat[index]) - float(row["lat_deg"])) > 1e-5 or abs(float(lon[index]) - float(row["lon_deg"])) > 1e-5 or abs(float(alt[index]) - float(row["alt_m"])) > 1:
                    raise RuntimeError(f"STK aircraft endpoint mismatch for {aid}")
            for sat in satellites:
                sid = sat["satellite_id"]
                progress.update(len(geometry_rows), f"{aid} → {sid}", force=True)
                satellite = root.GetObjectFromPath(f"*/Satellite/{sid}")
                access = aircraft.GetAccessToObject(satellite)
                access.ComputeAccess()
                intervals = [access.ComputedAccessIntervalTimes.GetInterval(i) for i in range(access.ComputedAccessIntervalTimes.Count)]
                aer = access.DataProviders.Item("AER Data").Group.Item("Default")
                for index, instant in enumerate(plan.time_grid):
                    second = index * step
                    visible_interval = any(float(a) - 1e-6 <= second <= float(b) + 1e-6 for a, b in intervals)
                    elevation = range_m = azimuth = ""
                    if visible_interval:
                        point = aer.ExecSingle(second)
                        elevation = float(values(point, "Elevation")[0])
                        azimuth = float(values(point, "Azimuth")[0])
                        range_m = float(values(point, "Range")[0])
                    geometry_rows.append({"aircraft_id": aid, "satellite_id": sid,
                                          "time_utc": iso_text(instant),
                                          "access": str(bool(visible_interval and elevation >= min_elevation)).lower(),
                                          "azimuth_deg": azimuth, "elevation_deg": elevation,
                                          "range_m": range_m})
                    progress.update(len(geometry_rows), f"{aid} → {sid} · 采样 {index + 1}/{len(plan.time_grid)}")
        root.UnitPreferences.Item("Bandwidth").SetCurrentUnit("Hz")
        root.UnitPreferences.Item("Power").SetCurrentUnit("dBW")
        root.UnitPreferences.Item("Frequency").SetCurrentUnit("Hz")
        devices = {row["device_id"]: row for row in read_csv(config.resolve(config.data["inputs"]["transmitter_receiver_file"]))}
        antennas = {row["antenna_id"]: row for row in read_csv(config.resolve(config.data["inputs"]["antenna_file"]))}
        pattern_metadata = {}
        extra_files = []
        for antenna_id, antenna in antennas.items():
            if antenna["model"] == "APENST818V01":
                pattern = Apenst818.from_row(antenna)
                filename = f"antenna_{antenna_id}.ant"
                pattern.export(output / filename)
                extra_files.append(filename)
                pattern_metadata[antenna_id] = pattern.metadata()
        reference = config.root / "config" / "APENST818V01.pdf"
        if reference.is_file():
            shutil.copy2(reference, output / reference.name)
            extra_files.append(reference.name)
        write_json(output / "antenna_patterns.json", pattern_metadata)
        extra_files.append("antenna_patterns.json")
        geometry_visible = {(row["aircraft_id"], row["satellite_id"], row["time_utc"]): row["access"] == "true"
                            for row in geometry_rows}
        aircraft_ranges = {(row["aircraft_id"], row["satellite_id"], row["time_utc"]): row["range_m"] for row in geometry_rows}
        feeder_geometry = {}
        feeder_rows = []
        progress.stage("GATEWAY_GEOMETRY", len(gateways) * len(satellites) * len(plan.time_grid))
        for gateway in gateways:
            gid = gateway["gateway_id"]
            facility = root.GetObjectFromPath(f"*/Facility/{gid}")
            for sat in satellites:
                sid = sat["satellite_id"]
                progress.update(len(feeder_rows), f"{gid} → {sid}", force=True)
                access = facility.GetAccessToObject(root.GetObjectFromPath(f"*/Satellite/{sid}"))
                access.ComputeAccess()
                intervals = [access.ComputedAccessIntervalTimes.GetInterval(i) for i in range(access.ComputedAccessIntervalTimes.Count)]
                aer = access.DataProviders.Item("AER Data").Group.Item("Default")
                for index, instant in enumerate(plan.time_grid):
                    second = index * step
                    visible = any(float(a) - 1e-6 <= second <= float(b) + 1e-6 for a, b in intervals)
                    elevation = distance = ""
                    if visible:
                        point = aer.ExecSingle(second)
                        elevation = float(values(point, "Elevation")[0])
                        distance = float(values(point, "Range")[0])
                    ok = bool(visible and elevation >= min_elevation)
                    key = (gid, sid, iso_text(instant))
                    feeder_geometry[key] = (ok, distance)
                    feeder_rows.append({"gateway_id": gid, "satellite_id": sid, "time_utc": key[2],
                                        "access": str(ok).lower(), "elevation_deg": elevation, "range_m": distance})
                    progress.update(len(feeder_rows), f"{gid} → {sid} · 采样 {index + 1}/{len(plan.time_grid)}")
        sensor_visibility, sensor_rows = sample_sensors(root, sensors, [s["satellite_id"] for s in satellites],
            [iso_text(instant) for instant in plan.time_grid], step, geometry_visible, progress)
        budget_rows = []
        created = set()
        object_paths = {}
        receiver_tracking_readback = {}
        progress.stage("COMMUNICATIONS", len(config.data["links"]) * len(satellites) * len(plan.time_grid))
        for link in config.data["links"]:
            tx_template, rx_template = devices[link["tx_id"]], devices[link["rx_id"]]
            if tx_template["polarization"] != rx_template["polarization"]:
                raise ValueError(f"{link['link_id']}: polarization mismatch is not supported by the simple budget model")
            mapped = simple_link_values(tx_template, rx_template,
                                        antennas[tx_template["antenna_id"]], antennas[rx_template["antenna_id"]],
                                        float(link.get("other_loss_db", 0)))
            for sat in satellites:
                sid = sat["satellite_id"]
                progress.update(len(budget_rows), f"链路 {link['link_id']} · {sid}", force=True)
                aircraft_template = next((item for item in (tx_template, rx_template) if item["platform_type"] == "AIRCRAFT"), None)
                aid = aircraft_template["platform_id"] if aircraft_template else ""
                gateway_template = next((item for item in (tx_template, rx_template) if item["platform_type"] == "GATEWAY"), None)
                gid = gateway_template["platform_id"] if gateway_template else ""
                mask_sensor = selected_sensor(config.data, link, aid)
                paths = []
                for template in (tx_template, rx_template):
                    owner = {"AIRCRAFT": f"*/Aircraft/{aid}", "SATELLITE": f"*/Satellite/{sid}",
                             "GATEWAY": f"*/Facility/{gid}"}[template["platform_type"]]
                    klass = "Transmitter" if template["role"] == "TX" else "Receiver"
                    name = f"{link['link_id']}_{template['device_id']}"
                    path = f"{owner}/{klass}/{name}"
                    paths.append(path)
                    if path not in created:
                        root.ExecuteCommand(f"New / {owner}/{klass} {name}")
                        created.add(path)
                        if klass == "Transmitter":
                            root.ExecuteCommand(f"Transmitter {path} SetValue Model.Frequency {mapped['frequency_hz']:.9f} Hz")
                            root.ExecuteCommand(f"Transmitter {path} SetValue Model.EIRP {mapped['eirp_dbw']:.9f} dBW")
                            root.ExecuteCommand(f"Transmitter {path} SetValue Model.DataRate {mapped['data_rate_bps']:.9f} b*sec^-1")
                        else:
                            root.ExecuteCommand(f"Receiver {path} SetValue Model.FrequencyAutoTracking false")
                            root.ExecuteCommand(f"Receiver {path} SetValue Model.Frequency {mapped['frequency_hz']:.9f} Hz")
                            if config.data["propagation"].get("doppler_compensation", "FIXED") == "IDEAL":
                                root.ExecuteCommand(f"Receiver {path} SetValue Model.FrequencyAutoTracking true")
                                tracking = root.ExecuteCommand(f"Receiver_RM {path} GetValue Model.FrequencyAutoTracking")
                                text = "\n".join(str(tracking.Item(i)) for i in range(tracking.Count))
                                if "true" not in text.lower():
                                    raise RuntimeError(f"Receiver ideal frequency tracking readback failed: {path}: {text}")
                                receiver_tracking_readback[path] = text
                            root.ExecuteCommand(f"Receiver {path} SetValue Model.AutoScaleBandwidth false")
                            root.ExecuteCommand(f"Receiver {path} SetValue Model.Bandwidth {mapped['bandwidth_hz']:.9f} Hz")
                            root.ExecuteCommand(f"Receiver {path} SetValue Model.GOverT {mapped['g_over_t_dbk']:.9f} dB/K")
                            configure_receiver_rain(root, path, config.data["propagation"])
                object_paths[(link["link_id"], sid)] = paths
                tx_object = root.GetObjectFromPath(paths[0])
                rx_object = root.GetObjectFromPath(paths[1])
                access = tx_object.GetAccessToObject(rx_object)
                access.ComputeAccess()
                intervals = [access.ComputedAccessIntervalTimes.GetInterval(i) for i in range(access.ComputedAccessIntervalTimes.Count)]
                provider = access.DataProviders.Item("Link Information")
                for index, instant in enumerate(plan.time_grid):
                    time_utc = iso_text(instant)
                    second = index * step
                    geom_ok = feeder_geometry[(gid, sid, time_utc)][0] if gid else geometry_visible[(aid, sid, time_utc)]
                    distance = feeder_geometry[(gid, sid, time_utc)][1] if gid else aircraft_ranges[(aid,sid,time_utc)]
                    mask_ok = sensor_visibility[(aid,mask_sensor,sid,time_utc)] if mask_sensor else True
                    available = geom_ok and mask_ok and any(
                        float(a) - 1e-6 <= second <= float(b) + 1e-6 for a, b in intervals)
                    cn = ebno = ber = ""
                    rip = frequency_offset = ""
                    losses = {name: "" for name in ("rain_loss_db", "gas_loss_db", "cloud_fog_loss_db", "tropo_scintillation_loss_db")}
                    if available:
                        point = provider.ExecSingle(second)
                        reported_bandwidth = float(values(point, "Bandwidth")[0])
                        if abs(reported_bandwidth / mapped["bandwidth_hz"] - 1) > .001:
                            raise RuntimeError(f"{link['link_id']}/{sid}: STK bandwidth {reported_bandwidth:g} Hz differs from configured {mapped['bandwidth_hz']:g} Hz")
                        cn = float(values(point, "C/N")[0])
                        ebno = float(values(point, "Eb/No")[0])
                        ber = float(values(point, "BER")[0])
                        rip = float(values(point, "Rcvd. Iso. Power")[0])
                        frequency_offset = float(values(point, "Freq. Doppler Shift")[0])
                        for column, element in (("rain_loss_db", "Rain Loss"), ("gas_loss_db", "Atmos Loss"),
                                                ("cloud_fog_loss_db", "CloudsFog Loss"),
                                                ("tropo_scintillation_loss_db", "TropoScintill Loss")):
                            losses[column] = float(values(point, element)[0])
                        expected_cn = ebno + 10 * math.log10(mapped["data_rate_bps"] / mapped["bandwidth_hz"])
                        if abs(cn - expected_cn) > .1:
                            raise RuntimeError(f"{link['link_id']}/{sid}: STK C/N and Eb/No do not reconcile")
                        if abs(float(values(point, "EIRP")[0]) - mapped["eirp_dbw"]) > .01:
                            raise RuntimeError(f"{link['link_id']}/{sid}: STK EIRP readback mismatch")
                    budget_rows.append({"link_id": link["link_id"], "direction": link["direction"],
                                        "aircraft_id": aid, "gateway_id": gid, "satellite_id": sid, "time_utc": time_utc,
                                        "access": str(bool(available)).lower(), "frequency_hz": mapped["frequency_hz"],
                                        "geometric_access": str(bool(geom_ok)).lower(), "mask_sensor_id": mask_sensor,
                                        "sensor_access": str(bool(mask_ok)).lower() if mask_sensor else "",
                                        "bandwidth_hz": mapped["bandwidth_hz"], "eirp_dbw": mapped["eirp_dbw"],
                                        "g_over_t_dbk": mapped["g_over_t_dbk"], "receiver_noise_temp_k": mapped["receiver_noise_temp_k"],
                                        "cn_db": cn, "ebno_db": ebno, "ber": ber, "range_m": distance,
                                        "received_iso_power_dbw": rip, "stk_frequency_doppler_shift_hz": frequency_offset,
                                        "residual_frequency_offset_hz": (0.0 if config.data["propagation"].get("doppler_compensation", "FIXED") == "IDEAL" else frequency_offset) if available else "",
                                        **{column: "" for column in RESULT_COLUMNS},
                                        **losses,
                                        "meets_min_cn": str(cn >= float(link["min_cn_db"])).lower() if cn != "" and link.get("min_cn_db") not in {None, ""} else ""})
                    progress.update(len(budget_rows), f"链路 {link['link_id']} · {sid} · 采样 {index + 1}/{len(plan.time_grid)}")
        interference_rows = []
        interference_enabled = config.data["propagation"].get("downlink_interference_model", "NONE") == "COCHANNEL_AGGREGATE"
        if interference_enabled:
            receiver_masks = {}
            for link in config.data["links"]:
                rx = devices[link["rx_id"]]
                if rx["platform_type"] != "AIRCRAFT":
                    continue
                sensor_id = selected_sensor(config.data, link, rx["platform_id"])
                if sensor_id:
                    for sat in satellites:
                        for instant in plan.time_grid:
                            stamp = iso_text(instant)
                            receiver_masks[(rx["device_id"],sat["satellite_id"],stamp)] = sensor_visibility[(rx["platform_id"],sensor_id,sat["satellite_id"],stamp)]
            interference_rows = analyze_interference(root, config.data["links"], devices, antennas, satellites,
                [iso_text(instant) for instant in plan.time_grid], step, geometry_visible, feeder_geometry,
                object_paths, budget_rows, progress, receiver_masks=receiver_masks)
        progress.stage("EXPORTING", 3, "导出 CSV 与网络时间线")
        write_csv(output / "aircraft_state.csv", ["aircraft_id", "time_utc", "lat_deg", "lon_deg", "alt_m"], aircraft_rows)
        write_csv(output / "link_geometry.csv", ["aircraft_id", "satellite_id", "time_utc", "access", "azimuth_deg", "elevation_deg", "range_m"], geometry_rows)
        write_csv(output / "gateway_geometry.csv", ["gateway_id", "satellite_id", "time_utc", "access", "elevation_deg", "range_m"], feeder_rows)
        write_csv(output / "aircraft_sensor_visibility.csv", ["aircraft_id","sensor_id","satellite_id","time_utc","geometric_access","sensor_access","effective_access","use_body_mask"], sensor_rows)
        extra_files.append("aircraft_sensor_visibility.csv")
        write_csv(output / "link_budget.csv", ["link_id", "direction", "aircraft_id", "gateway_id", "satellite_id", "time_utc", "access", "geometric_access", "mask_sensor_id", "sensor_access", "range_m", "frequency_hz", "bandwidth_hz", "eirp_dbw", "g_over_t_dbk", "receiver_noise_temp_k", "cn_db", "ebno_db", "ber", "meets_min_cn", "rain_loss_db", "gas_loss_db", "cloud_fog_loss_db", "tropo_scintillation_loss_db", "received_iso_power_dbw", "stk_frequency_doppler_shift_hz", "residual_frequency_offset_hz", *RESULT_COLUMNS], budget_rows)
        write_csv(output / "interference_contributions.csv", DETAIL_COLUMNS, interference_rows)
        extra_files.append("interference_contributions.csv")
        timeline_rows = export_timeline(output / "omnet_link_timeline.csv", output.name, plan.time_grid[0], plan.time_grid[-1], step,
                                        geometry_rows, budget_rows, config.data["links"], devices)
        progress.update(1, "保存 STK 场景", force=True)
        root.UnitPreferences.Item("DateFormat").SetCurrentUnit("UTCG")
        scene_path = output / "scenario.sc"
        root.SaveScenarioAs(str(scene_path))
        if not scene_path.is_file():
            raise RuntimeError("STK did not create scenario.sc")
        status["scene_saved"] = True
        write_json(status_path, status)
        manifest = {"status": "GEOMETRY_AND_BUDGET_COMPLETE", "stk_version": str(root.ExecuteCommand("GetSTKVersion /").Item(0)),
                    "project_id": config.data["project_id"], "scenario_start_utc": iso_text(plan.time_grid[0]),
                    "scenario_stop_utc": iso_text(plan.time_grid[-1]), "sample_step_s": step,
                    "aircraft_ids": aircraft_ids, "satellites": [{"satellite_id": row["satellite_id"],
                    "norad_id": row["norad_id"], "tle_epoch_utc": iso_text(tle_by_id[int(row["norad_id"])].epoch_utc)} for row in satellites],
                    "samples": len(plan.time_grid), "aircraft_rows": len(aircraft_rows),
                    "geometry_rows": len(geometry_rows), "gateway_geometry_rows": len(feeder_rows),
                    "budget_rows": len(budget_rows), "omnet_timeline_rows": timeline_rows,
                    "omnet_timeline_schema_version": "1.0", "omnet_timeline_interval": "[start_s,end_s)",
                    "gateways": gateways,
                    "rf_environment": rf_environment,
                    "aircraft_configuration": config.data.get("aircraft", []),
                    "sensor_configuration": config.data.get("sensors", []),
                    "body_masking": {"implementation":"Native STK Sensor Access including FOV and .bmsk, intersected with geometric visibility and minimum elevation; applies to service and interference paths", "samples":len(sensor_rows)},
                    "antenna_patterns": pattern_metadata,
                    "doppler_compensation": config.data["propagation"].get("doppler_compensation", "FIXED"),
                    "receiver_frequency_tracking_readback": receiver_tracking_readback,
                    "residual_frequency_offset_definition": "Zero by IDEAL compensation assumption; raw STK Freq. Doppler Shift retained separately",
                    "interference": {"enabled": interference_enabled, "model": "COCHANNEL_AGGREGATE" if interference_enabled else "NONE",
                        "implementation": "STK on-axis cross-path budgets plus platform APENST818 off-axis aggregation; not native STK CommSystem SINR",
                        "activity": "All configured satellite downlink TX beams continuously active; exclude serving satellite",
                        "visibility": "STK geometric access and scenario minimum elevation at victim receiver",
                        "pointing": "Victim RX points at candidate satellite; interfering TX points at its own link endpoint",
                        "spectrum": "Same nominal center frequency (within 1 Hz); no adjacent-channel interference",
                        "ber_model": "Coherent uncoded BPSK AWGN with aggregate interference treated as noise; retain STK BER if I=0",
                        "contribution_rows": len(interference_rows)},
                    "budget_access_rows": sum(row["access"] == "true" for row in budget_rows), "min_elevation_deg": min_elevation,
                    "interpolation": "STK Lagrange order 1; WGS84 geodetic altitude in meters",
                    "communications": "STK Simple TX/RX on-axis equivalents; directional interference uses exported APENST818V01 formula; feeder and other losses folded into EIRP/G/T; receiver noise figure assumes 290 K reference; BPSK default; no mount-angle simulation",
                    "input_sha256": {key: hashlib.sha256(config.resolve(config.data["inputs"][key]).read_bytes()).hexdigest()
                                     for key in ("aircraft_track_file", "tle_file", "satellite_config_file",
                                                 "transmitter_receiver_file", "antenna_file")}}
        write_json(output / "manifest.json", manifest)
        progress.update(2, "打包场景及结果", force=True)
        with zipfile.ZipFile(output / "scenario_bundle.zip", "w", compression=zipfile.ZIP_DEFLATED) as archive:
            for path in output.rglob("*"):
                if path.is_file() and path.name not in {"status.json", "worker.log", "scenario_bundle.zip"}:
                    archive.write(path, path.relative_to(output))
            archive.write(config.scenario_file, "source/config/scenario.yaml")
            for key in ("aircraft_track_file", "tle_file", "satellite_config_file",
                        "transmitter_receiver_file", "antenna_file"):
                source = config.resolve(config.data["inputs"][key])
                archive.write(source, f"source/{source.name}")
        status.update(state="COMPLETE", phase="COMPLETE", files=["scenario_bundle.zip", "scenario.sc", "aircraft_state.csv", "link_geometry.csv", "gateway_geometry.csv", "link_budget.csv", "omnet_link_timeline.csv", "manifest.json", "rf_environment.json"] + extra_files + [f"{aid}.e" for aid in aircraft_ids],
                      manifest=manifest, finished_utc=iso_text(datetime.now(timezone.utc)))
        progress.complete()
        return status
    except Exception as exc:
        progress.fail(f"{type(exc).__name__}: {exc}")
        raise
    finally:
        if isolated_stk and "app" in locals():
            app.Quit()
        pythoncom.CoUninitialize()


def main() -> None:
    project, output = Path(sys.argv[1]), Path(sys.argv[2])
    limit = int(sys.argv[3]) if len(sys.argv) > 3 else 0
    try:
        run(project, output, limit)
    except Exception as exc:
        output.mkdir(parents=True, exist_ok=True)
        status_path = output / "status.json"
        try:
            status = json.loads(status_path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            status = {}
        status.update(state="FAILED", error=f"{type(exc).__name__}: {exc}",
                      trace=traceback.format_exc(), finished_utc=iso_text(datetime.now(timezone.utc)))
        write_json(status_path, status)
        print(status["trace"], file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
