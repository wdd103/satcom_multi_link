from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class ProjectConfig:
    root: Path
    scenario_file: Path
    data: dict[str, Any]

    def resolve(self, value: str) -> Path:
        path = Path(value)
        return path if path.is_absolute() else self.root / path


@dataclass(frozen=True)
class Issue:
    severity: str
    code: str
    message: str
    location: str
    category: str = "CONFIG"

    def as_dict(self) -> dict[str, str]:
        return vars(self).copy()


@dataclass(frozen=True)
class ValidationReport:
    issues: tuple[Issue, ...]

    @property
    def ok(self) -> bool:
        return not any(issue.severity == "ERROR" for issue in self.issues)

    @property
    def exit_code(self) -> int:
        if self.ok:
            return 0
        errors = [i for i in self.issues if i.severity == "ERROR"]
        if any(i.category == "INPUT" for i in errors):
            return 3
        if any(i.category == "CONFIG" for i in errors):
            return 2
        return 4

    def as_dict(self) -> dict[str, Any]:
        return {"ok": self.ok, "exit_code": self.exit_code,
                "issues": [issue.as_dict() for issue in self.issues]}

    def raise_for_errors(self) -> None:
        if not self.ok:
            raise ValueError("; ".join(f"{i.location}: {i.message}" for i in self.issues if i.severity == "ERROR"))
