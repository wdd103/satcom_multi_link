from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path


@dataclass(frozen=True)
class TLERecord:
    norad_id: int
    name: str
    epoch_utc: datetime
    line1_number: int
    line2_number: int


class TLEError(ValueError):
    pass


def _checksum(line: str) -> bool:
    return len(line) == 69 and line[68].isdigit() and sum(
        int(ch) if ch.isdigit() else (1 if ch == "-" else 0) for ch in line[:68]
    ) % 10 == int(line[68])


def parse_tle(path: str | Path) -> list[TLERecord]:
    path = Path(path)
    with path.open("r", encoding="utf-8-sig") as stream:
        lines = [(number, line.rstrip("\r\n")) for number, line in enumerate(stream, 1) if line.strip()]
    records: list[TLERecord] = []
    i = 0
    while i < len(lines):
        name = ""
        if not lines[i][1].startswith("1 "):
            name = lines[i][1].removeprefix("0 ").strip()
            i += 1
        if i + 1 >= len(lines):
            raise TLEError(f"{path}:{lines[-1][0]}: incomplete TLE pair")
        n1, line1 = lines[i]
        n2, line2 = lines[i + 1]
        if not line1.startswith("1 ") or not line2.startswith("2 "):
            raise TLEError(f"{path}:{n1}-{n2}: expected TLE lines 1 and 2")
        if not _checksum(line1) or not _checksum(line2):
            raise TLEError(f"{path}:{n1}-{n2}: checksum or line length invalid")
        try:
            id1, id2 = int(line1[2:7]), int(line2[2:7])
            if id1 != id2:
                raise ValueError("NORAD IDs differ")
            year = int(line1[18:20])
            year += 2000 if year < 57 else 1900
            epoch = datetime(year, 1, 1, tzinfo=timezone.utc) + timedelta(days=float(line1[20:32]) - 1)
        except ValueError as exc:
            raise TLEError(f"{path}:{n1}-{n2}: invalid ID or epoch: {exc}") from exc
        records.append(TLERecord(id1, name or str(id1), epoch, n1, n2))
        i += 2
    if not records:
        raise TLEError(f"{path}: no TLE records")
    return records
