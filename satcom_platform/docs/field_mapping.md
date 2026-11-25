# M0 STK inventory and field mapping

Target machine inventory, 2026-11-12: Windows, Python 3.13.5 64-bit,
PyYAML 6.0.3 and pywin32 installed. Registry contains
`HKLM\SOFTWARE\AGI\STK\12.0`; `C:\Program Files\AGI\STK 12` exists.
The installed `AgUiApplication.exe` file version is **12.6.0.1270**.
The `STK12.Application` COM ProgID is registered, but no active STK 12
session was found during the probe.

Run `python scripts/probe_stk.py` for a fresh, read-only machine probe. This
inventory is not a successful COM scenario, license check, or Data Provider
verification. STK version, Communications entitlement, object APIs, AER and
budget element paths, units, and loss accounting still require an active STK
session and numerical cross-check before M2/M3.

| Standard field | STK source | Status |
| --- | --- | --- |
| Aircraft WGS84 position | External ephemeris `.e` | Pending round-trip |
| Satellite position | TLE/SGP4 | Pending import check |
| Range / AER / visibility | Access Data Providers | Pending provider check |
| Link budget values | Communications Data Providers | Pending license and numerical check |

No unverified STK field or unit mapping is assumed by the M1 validator.
