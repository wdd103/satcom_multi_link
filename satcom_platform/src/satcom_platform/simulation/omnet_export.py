"""Versioned, directed, half-open link intervals for OMNeT++ consumers."""

from __future__ import annotations

import csv
from datetime import datetime
from pathlib import Path

from satcom_platform.simulation.run_plan import parse_utc

SPEED_OF_LIGHT_MPS = 299792458.0
COLUMNS = ["run_id", "link_instance_id", "link_id", "direction", "source_id", "target_id",
           "start_utc", "end_utc", "start_s", "end_s", "available", "range_m",
           "propagation_delay_s", "ebno_db", "cn_db", "ber", "modulation", "capacity_bps",
           "sinr_db", "ebni_db", "ber_with_interference"]


def export_timeline(path: Path, run_id: str, start: datetime, stop: datetime, step_s: float,
                    geometry_rows: list[dict], budget_rows: list[dict],
                    links: list[dict], devices: dict[str, dict]) -> int:
    geometry = {(r["aircraft_id"], r["satellite_id"], r["time_utc"]): r for r in geometry_rows}
    lookup = {r["link_id"]: r for r in links}
    rows = []
    for budget in budget_rows:
        instant = parse_utc(budget["time_utc"])
        if instant >= stop:
            continue
        link = lookup[budget["link_id"]]
        tx, rx = devices[link["tx_id"]], devices[link["rx_id"]]
        sid = budget["satellite_id"]
        source = sid if tx["platform_type"] == "SATELLITE" else tx["platform_id"]
        target = sid if rx["platform_type"] == "SATELLITE" else rx["platform_id"]
        if tx["platform_type"] == "AIRCRAFT" or rx["platform_type"] == "AIRCRAFT":
            geom = geometry.get((budget["aircraft_id"], sid, budget["time_utc"]))
        else:
            geom = None
        distance = budget.get("range_m") or (geom or {}).get("range_m") or ""
        available = (budget["access"] == "true" and budget.get("meets_min_cn") != "false"
                     and budget.get("meets_min_sinr") != "false" and distance != "")
        end = min(instant.timestamp() + step_s, stop.timestamp())
        end_time = datetime.fromtimestamp(end, tz=instant.tzinfo)
        rows.append({"run_id": run_id, "link_instance_id": f"{link['link_id']}:{sid}",
                     "link_id": link["link_id"], "direction": link["direction"],
                     "source_id": source, "target_id": target,
                     "start_utc": budget["time_utc"], "end_utc": end_time.isoformat(timespec="milliseconds").replace("+00:00", "Z"),
                     "start_s": (instant - start).total_seconds(), "end_s": (end_time - start).total_seconds(),
                     "available": str(available).lower(), "range_m": distance if available else "",
                     "propagation_delay_s": float(distance) / SPEED_OF_LIGHT_MPS if available else "",
                     "ebno_db": budget["ebno_db"] if available else "", "cn_db": budget["cn_db"] if available else "",
                     "ber": budget["ber"] if available else "", "modulation": "STK_DEFAULT_BPSK",
                     "sinr_db": budget.get("sinr_db", "") if available else "",
                     "ebni_db": budget.get("ebni_db", "") if available else "",
                     "ber_with_interference": budget.get("ber_with_interference", "") if available else "",
                     "capacity_bps": tx["data_rate_bps"] if available else 0})
    rows.sort(key=lambda r: (float(r["start_s"]), r["link_instance_id"], r["source_id"]))
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=COLUMNS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    return len(rows)
