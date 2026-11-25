"""Preflight a STK timeline for the fixed three-node OMNeT++ model."""

import argparse
import csv
import math
from collections import defaultdict
from pathlib import Path


def check(path: Path, satellite: str, aircraft: str, gateway: str) -> tuple[str, int, float]:
    expected = {
        "UPLINK": (aircraft, satellite),
        "FEEDER_DOWNLINK": (satellite, gateway),
        "FEEDER_UPLINK": (gateway, satellite),
        "DOWNLINK": (satellite, aircraft),
    }
    grouped = defaultdict(list)
    run_ids = set()
    with path.open(newline="", encoding="utf-8-sig") as stream:
        reader = csv.DictReader(stream)
        required = {"run_id", "link_instance_id", "direction", "source_id", "target_id", "start_s", "end_s", "available", "range_m", "propagation_delay_s", "capacity_bps"}
        if not required.issubset(reader.fieldnames or []):
            raise ValueError(f"missing columns: {sorted(required - set(reader.fieldnames or []))}")
        for row in reader:
            if not row["link_instance_id"].endswith(":" + satellite):
                continue
            direction = row["direction"]
            if direction not in expected or (row["source_id"], row["target_id"]) != expected[direction]:
                raise ValueError(f"unexpected directed link: {row['link_instance_id']}")
            start, end = float(row["start_s"]), float(row["end_s"])
            if not all(map(math.isfinite, (start, end))) or end <= start:
                raise ValueError(f"invalid interval: {row['link_instance_id']} at {start}")
            if row["available"] not in {"true", "false"}:
                raise ValueError("available must be true or false")
            if row["available"] == "true":
                distance = float(row["range_m"])
                delay = float(row["propagation_delay_s"])
                rate = float(row["capacity_bps"])
                if distance <= 0 or rate <= 0 or not math.isclose(delay, distance / 299792458, rel_tol=1e-9):
                    raise ValueError("inconsistent distance, delay, or rate")
            elif float(row["capacity_bps"]) != 0:
                raise ValueError("unavailable link must have zero capacity")
            grouped[direction].append((start, end))
            run_ids.add(row["run_id"])
    if set(grouped) != set(expected) or len(run_ids) != 1:
        raise ValueError("four directions and one run ID are required")
    baseline = None
    for direction, intervals in grouped.items():
        intervals.sort()
        if intervals[0][0] != 0:
            raise ValueError(f"{direction} does not start at zero")
        for before, after in zip(intervals, intervals[1:]):
            if not math.isclose(before[1], after[0], abs_tol=1e-9):
                raise ValueError(f"gap or overlap in {direction}")
        if baseline is None:
            baseline = intervals
        elif intervals != baseline:
            raise ValueError("directions have different time grids")
    return run_ids.pop(), len(baseline), baseline[-1][1]


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("timeline", type=Path)
    parser.add_argument("--satellite", default="SAT41918")
    parser.add_argument("--aircraft", default="AC1")
    parser.add_argument("--gateway", default="GW1")
    args = parser.parse_args()
    run_id, intervals, end = check(args.timeline, args.satellite, args.aircraft, args.gateway)
    print(f"VALID run_id={run_id} satellite={args.satellite} intervals={intervals} end_s={end:g}")
