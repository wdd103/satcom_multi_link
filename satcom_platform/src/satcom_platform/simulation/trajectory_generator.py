from __future__ import annotations

import csv
import hashlib
import math
import os
import tempfile
from datetime import timedelta
from pathlib import Path

import yaml

from .run_plan import parse_utc


def generate_track(project_dir: str | Path, *, aircraft_id: str, start_utc: str, stop_utc: str,
                   step_s: float, start_lat_deg: float, start_lon_deg: float,
                   stop_lat_deg: float, stop_lon_deg: float, altitude_m: float) -> tuple[Path, Path]:
    """Create a WGS84 great-circle interpolated sample track and its provenance YAML."""
    from satcom_platform.config.validate import ID

    if not ID.fullmatch(aircraft_id):
        raise ValueError("Invalid aircraft ID")
    start, stop = parse_utc(start_utc), parse_utc(stop_utc)
    if stop <= start or not math.isfinite(step_s) or step_s <= 0:
        raise ValueError("Invalid time range or step")
    for lat, lon in ((start_lat_deg, start_lon_deg), (stop_lat_deg, stop_lon_deg)):
        if not (-90 <= lat <= 90 and -180 <= lon <= 180):
            raise ValueError("Latitude/longitude out of range")
    if not math.isfinite(altitude_m):
        raise ValueError("Invalid altitude")
    count = int((stop - start).total_seconds() // step_s) + 1
    include_stop = start + timedelta(seconds=(count - 1) * step_s) < stop
    if include_stop:
        count += 1
    if count > 1_000_000:
        raise ValueError("Track exceeds 1,000,000 points")

    def vector(lat: float, lon: float) -> tuple[float, float, float]:
        a, b = math.radians(lat), math.radians(lon)
        return math.cos(a) * math.cos(b), math.cos(a) * math.sin(b), math.sin(a)

    a, b = vector(start_lat_deg, start_lon_deg), vector(stop_lat_deg, stop_lon_deg)
    omega = math.acos(max(-1, min(1, sum(x * y for x, y in zip(a, b)))))
    if abs(math.pi - omega) < 1e-9:
        raise ValueError("Antipodal endpoints need an explicit route")
    project = Path(project_dir).resolve()
    input_dir = project / "input"
    input_dir.mkdir(parents=True, exist_ok=True)
    track_file = input_dir / "aircraft_track.csv"
    metadata_file = input_dir / "aircraft_generation.yaml"
    fd, temp_name = tempfile.mkstemp(prefix=".track-", suffix=".csv", dir=input_dir)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="") as stream:
            writer = csv.writer(stream)
            writer.writerow(("schema_version", "aircraft_id", "time_utc", "lat_deg", "lon_deg", "alt_m", "heading_deg", "pitch_deg", "roll_deg"))
            for i in range(count):
                when = stop if include_stop and i == count - 1 else start + timedelta(seconds=i * step_s)
                fraction = (when - start).total_seconds() / (stop - start).total_seconds()
                if omega < 1e-12:
                    xyz = a
                else:
                    u = math.sin((1 - fraction) * omega) / math.sin(omega)
                    v = math.sin(fraction * omega) / math.sin(omega)
                    xyz = tuple(u * x + v * y for x, y in zip(a, b))
                lat = math.degrees(math.atan2(xyz[2], math.hypot(xyz[0], xyz[1])))
                lon = math.degrees(math.atan2(xyz[1], xyz[0]))
                writer.writerow(("1.0", aircraft_id, when.isoformat(timespec="milliseconds").replace("+00:00", "Z"),
                                 f"{lat:.8f}", f"{lon:.8f}", f"{altitude_m:.3f}", "", "", ""))
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temp_name, track_file)
    finally:
        if os.path.exists(temp_name):
            os.unlink(temp_name)
    digest = hashlib.sha256(track_file.read_bytes()).hexdigest()
    metadata = {"schema_version": "1.0", "method": "GREAT_CIRCLE_SPHERE_INTERPOLATION",
                "aircraft_id": aircraft_id, "start_utc": start_utc, "stop_utc": stop_utc,
                "step_s": step_s, "start_lat_deg": start_lat_deg, "start_lon_deg": start_lon_deg,
                "stop_lat_deg": stop_lat_deg, "stop_lon_deg": stop_lon_deg,
                "altitude_m": altitude_m, "track_sha256": digest,
                "note": "Simulation input only; position is not a measured flight path or aircraft attitude."}
    fd, temp_name = tempfile.mkstemp(prefix=".generation-", suffix=".yaml", dir=input_dir)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            yaml.safe_dump(metadata, stream, allow_unicode=True, sort_keys=False)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temp_name, metadata_file)
    finally:
        if os.path.exists(temp_name):
            os.unlink(temp_name)
    return track_file, metadata_file
