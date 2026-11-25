from __future__ import annotations

import os
import tempfile
from copy import deepcopy
from pathlib import Path

import yaml

from .models import ProjectConfig


def load_project(project_dir_or_scenario_yaml: str | Path) -> ProjectConfig:
    source = Path(project_dir_or_scenario_yaml).resolve()
    scenario_file = source / "config" / "scenario.yaml" if source.is_dir() else source
    if not scenario_file.is_file():
        raise FileNotFoundError(f"Scenario configuration not found: {scenario_file}")
    root = scenario_file.parent.parent if scenario_file.parent.name == "config" else scenario_file.parent
    try:
        with scenario_file.open("r", encoding="utf-8-sig") as stream:
            data = yaml.safe_load(stream)
    except yaml.YAMLError as exc:
        raise ValueError(f"Invalid scenario YAML {scenario_file}: {exc}") from exc
    if not isinstance(data, dict):
        raise ValueError(f"Scenario must contain a YAML mapping: {scenario_file}")
    return ProjectConfig(root=root, scenario_file=scenario_file, data=data)


def save_project(config: ProjectConfig) -> None:
    """Atomically write the validated scenario YAML; referenced CSVs stay intact."""
    from .validate import validate_project

    normalized = deepcopy(config.data)
    if isinstance(normalized.get("scenario"), dict):
        normalized["scenario"].setdefault("min_elevation_deg", 0)
    if isinstance(normalized.get("propagation"), dict):
        normalized["propagation"].setdefault("tle_max_age_days_warning", 14)
        normalized["propagation"].setdefault("default_other_loss_db", 0)
    validate_project(ProjectConfig(config.root, config.scenario_file, normalized)).raise_for_errors()
    target = config.scenario_file
    target.parent.mkdir(parents=True, exist_ok=True)
    fd, name = tempfile.mkstemp(prefix=".scenario-", suffix=".yaml", dir=target.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as stream:
            yaml.safe_dump(normalized, stream, allow_unicode=True, sort_keys=False)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(name, target)
    finally:
        if os.path.exists(name):
            os.unlink(name)
