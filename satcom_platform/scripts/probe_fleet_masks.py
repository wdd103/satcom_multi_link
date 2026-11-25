"""Validate two aircraft and native body-mask sensors in an isolated STK instance."""
import csv
import shutil
import tempfile
from pathlib import Path
from datetime import datetime, timezone
from uuid import uuid4

from satcom_platform import load_project, save_project
from satcom_platform.config.fleet import clone_fleet
from satcom_platform.simulation.stk_run import run
from satcom_platform.web import _snapshot, _write_table, TABLE_FILES


def read(path):
    with path.open(encoding="utf-8-sig",newline="") as stream:
        return list(csv.DictReader(stream))


def main():
    base = Path(__file__).parents[1]
    with tempfile.TemporaryDirectory(prefix="fleet-smoke-",dir=base/"tests") as directory:
        project=Path(directory)/"project"
        shutil.copytree(base/"examples/minimal_project",project,ignore=shutil.ignore_patterns("runs"))
        config=load_project(project)
        snapshot=_snapshot(config)
        data,tables=clone_fleet(config.data,snapshot["tables"],"AC1",["AC2"],lat_step=.01)
        data["scenario"]["sample_step_s"]=120
        for row in tables["satellites"]["rows"]:
            row["enabled"]=str(row["satellite_id"] in {"SAT41918","SAT41923"}).lower()
        for table,key in TABLE_FILES.items():
            _write_table(project/data["inputs"][key],tables[table]["columns"],tables[table]["rows"])
        config.data.clear();config.data.update(data);save_project(config)
        run_id=datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ-")+uuid4().hex[:8]
        output=project/"runs"/run_id
        result=run(project,output,isolated_stk=True)
        assert result["state"]=="COMPLETE"
        budget=read(output/"link_budget.csv")
        masks=read(output/"aircraft_sensor_visibility.csv")
        assert set(result["manifest"]["aircraft_ids"])=={"AC1","AC2"}
        assert len(budget)==72,len(budget)
        assert len(masks)==24,len(masks)
        assert {r["aircraft_id"] for r in masks}=={"AC1","AC2"}
        lookup={(r["aircraft_id"],r["sensor_id"],r["satellite_id"],r["time_utc"]):r for r in masks}
        for row in budget:
            if row["aircraft_id"]:
                mask=lookup[(row["aircraft_id"],row["mask_sensor_id"],row["satellite_id"],row["time_utc"])]
                if mask["sensor_access"]=="false":
                    assert row["access"]=="false"
                if row["geometric_access"]=="true":
                    assert row["range_m"]!=""
        devices={r["device_id"]:r for r in read(project/data["inputs"]["transmitter_receiver_file"])}
        for row in read(output/"interference_contributions.csv"):
            rx=devices[row["receiver_id"]]
            if rx["platform_type"]=="AIRCRAFT":
                assert lookup[(rx["platform_id"],"RoofAntennaMask",row["interferer_satellite_id"],row["time_utc"])]["effective_access"]=="true"
        print("FLEET_MASK_VERIFIED",len(budget),"budget rows;",len(masks),"sensor rows; blocked geometric samples:",sum(r["geometric_access"]=="true" and r["sensor_access"]=="false" for r in masks),flush=True)


if __name__=="__main__":
    main()
