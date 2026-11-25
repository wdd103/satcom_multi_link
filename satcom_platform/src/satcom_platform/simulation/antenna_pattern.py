"""APENST818V01 co-polar pattern, with explicit wide-beam adaptation."""
from __future__ import annotations

import math
from dataclasses import asdict, dataclass
from pathlib import Path


@dataclass(frozen=True)
class Apenst818:
    peak_gain_dbi: float
    phi0_deg: float
    coefficient_a: float
    coefficient_b: float
    efficiency: float

    @property
    def curvature(self) -> float:
        return 0.0025 * 10 ** (self.peak_gain_dbi / 10) / (self.efficiency * math.pi ** 2)

    @classmethod
    def from_row(cls, row: dict) -> "Apenst818":
        peak = float(row["peak_gain_dbi"])
        phi0 = float(row["beamwidth_deg"])
        efficiency = float(row.get("aperture_efficiency") or 0.7)
        b = float(row.get("pattern_coefficient_b") or 25)
        if not all(math.isfinite(x) for x in (peak, phi0, efficiency, b)):
            raise ValueError("Pattern parameters must be finite")
        if not 0 < phi0 <= 180 or not 0 < efficiency <= 1 or not 10 <= b <= 50:
            raise ValueError("Pattern requires phi0 in (0,180], efficiency in (0,1], B in [10,50]")
        main_edge = peak - 0.0025 * 10 ** (peak / 10) / (efficiency * math.pi ** 2) * phi0 ** 2
        a = float(row.get("pattern_coefficient_a") or (main_edge + b * math.log10(phi0)))
        if not math.isfinite(a) or not 18 <= a <= 52:
            raise ValueError("APENST818 coefficient A must be in [18,52]; adjust phi0, B or gain")
        if main_edge < max(a - b * math.log10(phi0), -10) - 1e-8:
            raise ValueError("APENST818 main-lobe edge is below the sidelobe envelope")
        return cls(peak, phi0, a, b, efficiency)

    def gain(self, off_axis_deg: float) -> float:
        if not math.isfinite(off_axis_deg) or not 0 <= off_axis_deg <= 180:
            raise ValueError("Off-axis angle must be in [0,180] degrees")
        if off_axis_deg < self.phi0_deg:
            return self.peak_gain_dbi - self.curvature * off_axis_deg ** 2
        return max(self.coefficient_a - self.coefficient_b * math.log10(off_axis_deg), -10)

    def metadata(self) -> dict:
        return {**asdict(self), "model": "APENST818V01", "source": "APENST818V01.pdf",
                "phi0_mapping": "beamwidth_deg is used as transition angle phi0, not HPBW",
                "wide_beam_adaptation": not 0.1 <= self.phi0_deg <= 10,
                "cross_polar": "same pattern as co-polar; no extra cross-polar discrimination"}

    def export(self, path: Path) -> None:
        angles = sorted({i / 10 for i in range(1801)} | {self.phi0_deg})
        lines = ["stk.v.12.0", "SymmetricPattern", "AngleUnits Degrees",
                 f"NumberOfPoints {len(angles)}", "PatternData"]
        lines.extend(f"{angle:.8f} {self.gain(angle):.10f}" for angle in angles)
        path.write_text("\n".join(lines) + "\n", encoding="ascii")


def gain_delta(row: dict, angle_deg: float) -> float:
    if row["pointing_mode"] == "ISOTROPIC":
        return 0.0
    if row["model"] != "APENST818V01":
        raise ValueError("Directional interference calculation requires APENST818V01 antennas")
    pattern = Apenst818.from_row(row)
    return pattern.gain(angle_deg) - pattern.peak_gain_dbi


def separation_deg(origin, pointing_target, source) -> float:
    a = [float(pointing_target[i]) - float(origin[i]) for i in range(3)]
    b = [float(source[i]) - float(origin[i]) for i in range(3)]
    norm = math.sqrt(sum(x*x for x in a) * sum(x*x for x in b))
    if norm == 0:
        raise ValueError("Boresight or source direction has zero length")
    return math.degrees(math.acos(max(-1, min(1, sum(x*y for x, y in zip(a,b)) / norm))))
