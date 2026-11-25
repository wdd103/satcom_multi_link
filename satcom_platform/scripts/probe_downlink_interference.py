"""End-to-end STK smoke test using a disposable copy of the example project."""
from __future__ import annotations

import csv
import math
import shutil
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from satcom_platform import load_project, save_project
from satcom_platform.simulation.stk_run import run


def rows(path):
    with path.open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


def main():
    base = Path(__file__).parents[1]
    with tempfile.TemporaryDirectory(prefix="interference-smoke-", dir=base / "tests") as directory:
        project = Path(directory) / "project"
        shutil.copytree(base / "examples/minimal_project", project, ignore=shutil.ignore_patterns("runs"))
        config = load_project(project)
        config.data["scenario"]["sample_step_s"] = 120
        config.data["propagation"].update(downlink_interference_model="COCHANNEL_AGGREGATE", doppler_compensation="IDEAL")
        satellite_file = project / "config/satellite_config.csv"
        satellites = rows(satellite_file)
        for row in satellites:
            row["enabled"] = str(row["satellite_id"] in {"SAT41917", "SAT41918", "SAT41923"}).lower()
        with satellite_file.open("w", encoding="utf-8", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=list(satellites[0]))
            writer.writeheader()
            writer.writerows(satellites)
        save_project(config)
        run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ-") + uuid4().hex[:8]
        output = project / "runs" / run_id
        result = run(project, output)
        assert result["state"] == "COMPLETE", result
        assert not result.get("stk_progress_error"), result.get("stk_progress_error")
        budget = rows(output / "link_budget.csv")
        details = rows(output / "interference_contributions.csv")
        assert details, "Expected overlap between SAT41918 and SAT41923"
        assert len(budget) == 72, len(budget)
        visible = {}
        for filename, id_field in (("link_geometry.csv", "aircraft_id"), ("gateway_geometry.csv", "gateway_id")):
            for row in rows(output / filename):
                visible[(row[id_field], row["satellite_id"], row["time_utc"])] = row["access"] == "true"
        devices = {row["device_id"]: row for row in rows(project / "config/transmitter_receiver.csv")}
        contributions = {}
        for row in details:
            assert row["satellite_id"] != row["interferer_satellite_id"]
            victim = devices[row["receiver_id"]]["platform_id"]
            assert visible[(victim, row["interferer_satellite_id"], row["time_utc"])], row
            key = row["link_id"], row["satellite_id"], row["time_utc"]
            contributions.setdefault(key, []).append(float(row["received_power_w"]))
        positive = 0
        for row in budget:
            if row["access"] != "true":
                continue
            assert abs(float(row["residual_frequency_offset_hz"])) < 1e-6
            if row["sinr_db"] == "":
                continue
            expected = math.fsum(contributions.get((row["link_id"], row["satellite_id"], row["time_utc"]), []))
            assert math.isclose(float(row["interference_power_w"]), expected, rel_tol=1e-10, abs_tol=1e-30)
            assert float(row["sinr_db"]) <= float(row["cn_db"]) + 1e-8
            positive += expected > 0
        assert positive > 0
        assert (output / "scenario_bundle.zip").is_file()
        print(f"INTERFERENCE_VERIFIED: {len(budget)} budgets; {len(details)} contributions; {positive} interfered samples; visibility, self-exclusion, power sum, ideal Doppler and archive verified", flush=True)


if __name__ == "__main__":
    main()
