from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
import csv

from satcom_platform.config.models import ProjectConfig


def parse_utc(value: str) -> datetime:
    result = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if result.tzinfo is None or result.utcoffset() != timedelta(0):
        raise ValueError("UTC timestamp with Z or +00:00 offset required")
    return result.astimezone(timezone.utc)


@dataclass(frozen=True)
class RunPlan:
    config: ProjectConfig
    time_grid: tuple[datetime, ...]
    enabled_satellite_ids: tuple[str, ...]


def build_run_plan(config: ProjectConfig) -> RunPlan:
    from satcom_platform.config.validate import validate_project

    validate_project(config).raise_for_errors()
    scenario = config.data["scenario"]
    start, stop = parse_utc(scenario["start_utc"]), parse_utc(scenario["stop_utc"])
    step = float(scenario["sample_step_s"])
    count = int((stop - start).total_seconds() // step) + 1
    if count > 1_000_000:
        raise ValueError("Time grid exceeds 1,000,000 points")
    satellite_path = config.resolve(config.data["inputs"]["satellite_config_file"])
    with satellite_path.open("r", encoding="utf-8-sig", newline="") as stream:
        enabled = tuple(row["satellite_id"] for row in csv.DictReader(stream) if row["enabled"] == "true")
    return RunPlan(config, tuple(start + timedelta(seconds=i * step) for i in range(count)), enabled)
