from __future__ import annotations

import csv
import io
import json
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from satcom_platform import build_run_plan, load_project, save_project, validate_project
from satcom_platform.adapters.tle import TLEError, parse_tle
from satcom_platform.simulation.trajectory_generator import generate_track
from satcom_platform.simulation.stk_run import make_ephemeris
from satcom_platform.simulation.comm_model import simple_link_values
from satcom_platform.simulation.rf_environment import MODELS
from satcom_platform.web import create_app


EXAMPLE = Path(__file__).parents[1] / "examples" / "minimal_project"


def tle_line(text: str) -> str:
    body = text.ljust(68)[:68]
    checksum = sum(int(x) if x.isdigit() else (1 if x == "-" else 0) for x in body) % 10
    return body + str(checksum)


class CoreTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory(dir=Path(__file__).parent)
        self.addCleanup(self.temp.cleanup)
        self.project = Path(self.temp.name) / "project"
        shutil.copytree(EXAMPLE, self.project, ignore=shutil.ignore_patterns("runs"))
        self.tle = self.project / "input" / "satellites.tle"
        self.tle.write_text("TEST SAT\n" + tle_line("1 25544U 98067A   26316.08333333  .00000000  00000-0  00000-0 0  000") + "\n" +
                            tle_line("2 25544  51.6000 100.0000 0001000 100.0000 200.0000 15.00000000 0000") + "\n", encoding="ascii")
        (self.project / "config" / "satellite_config.csv").write_text(
            "schema_version,satellite_id,norad_id,display_name,enabled\n1.0,SAT1,25544,TEST SAT,true\n",
            encoding="utf-8")
        for name in ("transmitter_receiver.csv", "antenna.csv"):
            path = self.project / "config" / name
            path.write_text(path.read_text(encoding="utf-8").replace("SAT41917", "SAT1"), encoding="utf-8")

    def test_valid_project_and_grid(self) -> None:
        config = load_project(self.project)
        report = validate_project(config)
        self.assertTrue(report.ok, report.as_dict())
        plan = build_run_plan(config)
        self.assertEqual(len(plan.time_grid), 61)
        self.assertEqual(plan.time_grid[0].isoformat(), "2026-11-12T02:00:00+00:00")

    def test_interference_settings_save_and_tracking_guard(self) -> None:
        client = create_app(self.project).test_client()
        snapshot = client.get("/api/project").get_json()
        draft = snapshot["scenario"]
        draft["propagation"].update(downlink_interference_model="COCHANNEL_AGGREGATE", doppler_compensation="FIXED")
        payload = {"scenario": draft, "tables": snapshot["tables"]}
        rejected = client.post("/api/save", json=payload)
        self.assertEqual(rejected.status_code, 422)
        self.assertIn("INTERFERENCE_DOPPLER", {issue["code"] for issue in rejected.get_json()["validation"]["issues"]})
        draft["propagation"]["doppler_compensation"] = "IDEAL"
        draft["links"][1]["min_sinr_db"] = 2.5
        saved = client.post("/api/save", json=payload)
        self.assertEqual(saved.status_code, 200, saved.get_json())
        self.assertEqual(load_project(self.project).data["links"][1]["min_sinr_db"], 2.5)
        self.assertEqual(saved.get_json()["scenario"]["propagation"]["downlink_interference_model"], "COCHANNEL_AGGREGATE")

    def test_interference_requires_directional_pattern_and_unique_beams(self) -> None:
        config = load_project(self.project)
        config.data["links"].append({**config.data["links"][1], "link_id": "DUPLICATE_BEAM"})
        self.assertIn("INTERFERENCE_TX_TARGET", {issue.code for issue in validate_project(config).issues})
        config.data["links"].pop()
        antenna_file = self.project / "config/antenna.csv"
        antenna_file.write_text(antenna_file.read_text(encoding="utf-8").replace("APENST818V01", "SIMPLE"), encoding="utf-8")
        self.assertIn("INTERFERENCE_ANTENNA", {issue.code for issue in validate_project(config).issues})
        config.data["propagation"]["downlink_interference_model"] = "NONE"
        self.assertTrue(validate_project(config).ok)

    def test_rf_models_web_save_reload_and_disable(self) -> None:
        client = create_app(self.project).test_client()
        snapshot = client.get("/api/project").get_json()
        propagation = snapshot["scenario"]["propagation"]
        for key, spec in MODELS.items():
            propagation[key] = spec[0]
        propagation.update(rain_outage_percent=0.05, scintillation_outage_percent=0.2,
                           cloud_ceiling_m=6000, cloud_thickness_m=1000,
                           cloud_temperature_k=260, cloud_liquid_water_density_g_m3=0.8)
        payload = {"scenario": snapshot["scenario"], "tables": snapshot["tables"]}
        response = client.post("/api/save", json=payload)
        self.assertEqual(response.status_code, 200, response.get_json())
        self.assertEqual(load_project(self.project).data["propagation"], propagation)
        self.assertEqual(client.get("/api/project").get_json()["scenario"]["propagation"], propagation)
        for key in MODELS:
            propagation[key] = "NONE"
        response = client.post("/api/save", json=payload)
        self.assertEqual(response.status_code, 200, response.get_json())
        self.assertTrue(all(load_project(self.project).data["propagation"][key] == "NONE" for key in MODELS))

    def test_rf_invalid_parameters_do_not_save(self) -> None:
        client = create_app(self.project).test_client()
        snapshot = client.get("/api/project").get_json()
        scenario_file = self.project / "config/scenario.yaml"
        before = scenario_file.read_bytes()
        for key, value in (("rain_outage_percent", 0), ("scintillation_outage_percent", 101),
                           ("cloud_thickness_m", 4000), ("cloud_liquid_water_density_g_m3", -1),
                           ("atmosphere_model", "TYPO")):
            with self.subTest(key=key):
                draft = __import__("copy").deepcopy(snapshot["scenario"])
                draft["propagation"][key] = value
                response = client.post("/api/save", json={"scenario": draft, "tables": snapshot["tables"]})
                self.assertEqual(response.status_code, 422, response.get_json())
                self.assertEqual(scenario_file.read_bytes(), before)

    def test_rf_old_config_and_frequency_limits(self) -> None:
        config = load_project(self.project)
        for key in ("cloud_fog_model", "tropo_scintillation_model"):
            config.data["propagation"].pop(key, None)
        self.assertTrue(validate_project(config).ok)
        config.data["propagation"]["tropo_scintillation_model"] = "ITU_R_P618"
        device_file = self.project / "config/transmitter_receiver.csv"
        device_file.write_text(device_file.read_text(encoding="utf-8").replace("14000000000", "2000000000"), encoding="utf-8")
        self.assertIn("RF_MODEL_FREQUENCY", {issue.code for issue in validate_project(config).issues})

    def test_stk_ephemeris_and_web_run_status(self) -> None:
        track = self.project / "input" / "aircraft_track.csv"
        with track.open(encoding="utf-8", newline="") as stream:
            rows = list(csv.DictReader(stream))
        ephemeris = self.project / "AC1.e"
        make_ephemeris(rows, ephemeris)
        content = ephemeris.read_text(encoding="ascii")
        self.assertIn("EphemerisLLATimePos", content)
        self.assertIn("DistanceUnit Meters", content)
        self.assertIn("600.000000 32.2304000000 122.4737000000 10000.000", content)
        client = create_app(self.project).test_client()
        with patch("satcom_platform.web.subprocess.Popen"):
            started = client.post("/api/run", json={"satellite_limit": 1})
        self.assertEqual(started.status_code, 202, started.get_json())
        run_id = started.get_json()["run_id"]
        self.assertEqual(client.get(f"/api/runs/{run_id}").get_json()["state"], "RUNNING")
        self.assertEqual(client.get(f"/api/runs/{run_id}/files/manifest.json").status_code, 404)

    def test_simple_link_maps_gain_noise_and_losses(self) -> None:
        devices = {r["device_id"]: r for r in csv.DictReader((self.project / "config/transmitter_receiver.csv").open(encoding="utf-8"))}
        antennas = {r["antenna_id"]: r for r in csv.DictReader((self.project / "config/antenna.csv").open(encoding="utf-8"))}
        tx, rx = devices["ATX1"], devices["SRX1"]
        mapped = simple_link_values(tx, rx, antennas[tx["antenna_id"]], antennas[rx["antenna_id"]], 2.0)
        self.assertAlmostEqual(mapped["eirp_dbw"], 22.0)
        self.assertAlmostEqual(mapped["receiver_noise_temp_k"], 290 * 10 ** .3)
        self.assertAlmostEqual(mapped["g_over_t_dbk"], 20 - 1 - 10 * __import__("math").log10(mapped["receiver_noise_temp_k"]))
        tilted = dict(antennas[tx["antenna_id"]], mount_yaw_deg="5")
        with self.assertRaisesRegex(ValueError, "mount angles"):
            simple_link_values(tx, rx, tilted, antennas[rx["antenna_id"]], 2.0)

    def test_missing_reference_reports_input_error(self) -> None:
        path = self.project / "config" / "transmitter_receiver.csv"
        path.write_text(path.read_text(encoding="utf-8").replace("AANT_TX", "MISSING"), encoding="utf-8")
        report = validate_project(load_project(self.project))
        self.assertFalse(report.ok)
        self.assertEqual(report.exit_code, 3)
        self.assertIn("ANTENNA_REFERENCE", {i.code for i in report.issues})

    def test_save_round_trip_and_preflight_exit(self) -> None:
        config = load_project(self.project)
        save_project(config)
        self.assertEqual(load_project(config.scenario_file).data, config.data)
        report = validate_project(config, level="preflight")
        self.assertEqual(report.exit_code, 0)
        self.assertIn("STK_SIMPLE_BUDGET_ASSUMPTIONS", {i.code for i in report.issues})

    def test_tle_checksum_failure(self) -> None:
        content = self.tle.read_text(encoding="ascii")
        self.tle.write_text(content[:-2] + ("0" if content[-2] != "0" else "1") + "\n", encoding="ascii")
        with self.assertRaises(TLEError):
            parse_tle(self.tle)

    def test_generated_track_and_hash(self) -> None:
        track, metadata = generate_track(self.project, aircraft_id="AC1",
            start_utc="2026-11-12T02:00:00Z", stop_utc="2026-11-12T02:10:00Z",
            step_s=17, start_lat_deg=31.23, start_lon_deg=121.47,
            stop_lat_deg=32.23, stop_lon_deg=122.47, altitude_m=10000)
        with track.open(newline="", encoding="utf-8") as stream:
            rows = list(csv.DictReader(stream))
        self.assertEqual(rows[-1]["time_utc"], "2026-11-12T02:10:00.000Z")
        self.assertTrue(metadata.is_file())
        config = load_project(self.project)
        config.data["inputs"]["aircraft_source"] = "GENERATED"
        self.assertTrue(validate_project(config).ok)

    def test_web_validates_before_saving_and_round_trips(self) -> None:
        client = create_app(self.project).test_client()
        snapshot = client.get("/api/project").get_json()
        self.assertEqual(snapshot["scenario"]["project_id"], "DemoSatcom")
        for route in ("/", "/assets/app.js"):
            response = client.get(route)
            self.assertEqual(response.status_code, 200)
            response.close()
        scenario_file = self.project / "config" / "scenario.yaml"
        before = scenario_file.read_bytes()
        draft = snapshot["scenario"]
        draft["scenario"]["sample_step_s"] = -1
        response = client.post("/api/save", json={"scenario": draft, "tables": snapshot["tables"]})
        self.assertEqual(response.status_code, 422)
        self.assertEqual(scenario_file.read_bytes(), before)
        draft["scenario"]["sample_step_s"] = 15
        response = client.post("/api/save", json={"scenario": draft, "tables": snapshot["tables"]})
        self.assertEqual(response.status_code, 200, response.get_json())
        self.assertEqual(load_project(self.project).data["scenario"]["sample_step_s"], 15)

    def test_web_saves_device_antenna_and_link_edits(self) -> None:
        client = create_app(self.project).test_client()
        snapshot = client.get("/api/project").get_json()
        draft, tables = snapshot["scenario"], snapshot["tables"]
        tables["devices"]["rows"][0]["power_dbw"] = "12.5"
        tables["antennas"]["rows"][0]["peak_gain_dbi"] = "16.5"
        draft["links"][0]["min_cn_db"] = "4.5"
        response = client.post("/api/save", json={"scenario": draft, "tables": tables})
        self.assertEqual(response.status_code, 200, response.get_json())
        with (self.project / "config" / "transmitter_receiver.csv").open(newline="", encoding="utf-8") as stream:
            self.assertEqual(list(csv.DictReader(stream))[0]["power_dbw"], "12.5")
        with (self.project / "config" / "antenna.csv").open(newline="", encoding="utf-8") as stream:
            self.assertEqual(list(csv.DictReader(stream))[0]["peak_gain_dbi"], "16.5")
        self.assertEqual(load_project(self.project).data["links"][0]["min_cn_db"], "4.5")

    def test_spreadsheet_satellite_values_display_and_save_canonically(self) -> None:
        satellite_csv = self.project / "config" / "satellite_config.csv"
        satellite_csv.write_text(
            "schema_version,satellite_id,norad_id,display_name,enabled\n1,SAT1,25544,TEST SAT,TRUE\n",
            encoding="utf-8")
        client = create_app(self.project).test_client()
        snapshot = client.get("/api/project").get_json()
        self.assertEqual(snapshot["tables"]["satellites"]["rows"][0]["enabled"], "true")
        self.assertEqual(snapshot["tables"]["satellites"]["rows"][0]["schema_version"], "1.0")
        self.assertTrue(snapshot["validation"]["ok"])
        saved = client.post("/api/save", json={"scenario": snapshot["scenario"], "tables": snapshot["tables"]})
        self.assertEqual(saved.status_code, 200, saved.get_json())
        self.assertIn("1.0,SAT1,25544,TEST SAT,true", satellite_csv.read_text(encoding="utf-8"))

    def test_tle_import_populates_scene_and_selection_does_not_rewrite_tle(self) -> None:
        client = create_app(self.project).test_client()
        old = client.get("/api/project").get_json()
        satellite_csv = self.project / "config" / "satellite_config.csv"
        csv_before = satellite_csv.read_bytes()
        second = "SECOND SAT\n" + tle_line("1 12345U 98067A   26316.08333333  .00000000  00000-0  00000-0 0  000") + "\n" + \
                 tle_line("2 12345  51.6000 100.0000 0001000 100.0000 200.0000 15.00000000 0000") + "\n"
        upload = client.post("/api/upload/tle", data={"file": (io.BytesIO(self.tle.read_bytes() + second.encode("ascii")), "satellites.tle"),
                                                   "satellites": json.dumps(old["tables"]["satellites"])},
                             content_type="multipart/form-data")
        self.assertEqual(upload.status_code, 200, upload.get_json())
        snapshot = upload.get_json()
        rows = snapshot["tables"]["satellites"]["rows"]
        self.assertEqual(snapshot["satellite_source"], "CSV")
        self.assertEqual({r["norad_id"] for r in rows}, {"25544"})
        self.assertEqual(rows[0]["satellite_id"], "SAT1")
        self.assertEqual(satellite_csv.read_bytes(), csv_before)
        self.assertEqual({str(r["norad_id"]) for r in snapshot["tle_records"]}, {"25544", "12345"})
        tle_bytes = self.tle.read_bytes()
        rows[0]["display_name"] = "CSV CHOICE"
        saved = client.post("/api/save-satellites", json={"satellites": snapshot["tables"]["satellites"]})
        self.assertEqual(saved.status_code, 200, saved.get_json())
        self.assertEqual(self.tle.read_bytes(), tle_bytes)
        plan = build_run_plan(load_project(self.project))
        self.assertEqual(plan.enabled_satellite_ids, ("SAT1",))
        self.assertEqual(saved.get_json()["tables"]["satellites"]["rows"][0]["display_name"], "CSV CHOICE")

    def test_tle_path_preview_does_not_write_files(self) -> None:
        client = create_app(self.project).test_client()
        before = self.tle.read_bytes()
        preview = client.post("/api/parse-tle", json={"path": "input/satellites.tle"})
        self.assertEqual(preview.status_code, 200, preview.get_json())
        self.assertEqual(preview.get_json()["satellites"]["rows"][0]["norad_id"], "25544")
        self.assertEqual(preview.get_json()["satellite_source"], "CSV")
        self.assertEqual(self.tle.read_bytes(), before)

    def test_missing_csv_uses_all_tle_satellites_enabled(self) -> None:
        (self.project / "config" / "satellite_config.csv").unlink()
        second = "SECOND SAT\n" + tle_line("1 12345U 98067A   26316.08333333  .00000000  00000-0  00000-0 0  000") + "\n" + \
                 tle_line("2 12345  51.6000 100.0000 0001000 100.0000 200.0000 15.00000000 0000") + "\n"
        self.tle.write_bytes(self.tle.read_bytes() + second.encode("ascii"))
        snapshot = create_app(self.project).test_client().get("/api/project").get_json()
        self.assertEqual({row["norad_id"] for row in snapshot["tables"]["satellites"]["rows"]}, {"25544", "12345"})
        self.assertTrue(all(row["enabled"] == "true" for row in snapshot["tables"]["satellites"]["rows"]))

    def test_existing_tle_populates_list_when_project_opens(self) -> None:
        self.tle.write_text("NEW SAT\n" + tle_line("1 12345U 98067A   26316.08333333  .00000000  00000-0  00000-0 0  000") + "\n" +
                            tle_line("2 12345  51.6000 100.0000 0001000 100.0000 200.0000 15.00000000 0000") + "\n", encoding="ascii")
        satellite_csv = self.project / "config" / "satellite_config.csv"
        satellite_csv.unlink()
        snapshot = create_app(self.project).test_client().get("/api/project").get_json()
        self.assertTrue(snapshot["needs_satellite_save"])
        self.assertEqual(snapshot["satellite_source"], "TLE_CANDIDATE")
        self.assertEqual(snapshot["tables"]["satellites"]["rows"][0]["norad_id"], "12345")
        self.assertEqual(snapshot["tables"]["satellites"]["rows"][0]["enabled"], "true")
        self.assertFalse(satellite_csv.exists())
        tle_before = self.tle.read_bytes()
        saved = create_app(self.project).test_client().post(
            "/api/save-satellites", json={"satellites": snapshot["tables"]["satellites"]})
        self.assertEqual(saved.status_code, 200, saved.get_json())
        self.assertEqual(self.tle.read_bytes(), tle_before)
        with satellite_csv.open(newline="", encoding="utf-8") as stream:
            self.assertEqual(list(csv.DictReader(stream))[0]["norad_id"], "12345")
        self.assertEqual(saved.get_json()["satellite_source"], "CSV")
        self.tle.write_text("TEST SAT\n" + tle_line("1 25544U 98067A   26316.08333333  .00000000  00000-0  00000-0 0  000") + "\n" +
                            tle_line("2 25544  51.6000 100.0000 0001000 100.0000 200.0000 15.00000000 0000") + "\n", encoding="ascii")
        reloaded = create_app(self.project).test_client().get("/api/project").get_json()
        self.assertEqual(reloaded["tables"]["satellites"]["rows"][0]["norad_id"], "12345")
        self.assertFalse(reloaded["needs_satellite_save"])


if __name__ == "__main__":
    unittest.main()
