from __future__ import annotations

import argparse
import json
import sys

from . import load_project, validate_project
from .simulation.trajectory_generator import generate_track


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="satcom", description="Satellite communications project configuration tools")
    sub = parser.add_subparsers(dest="command", required=True)
    validate = sub.add_parser("validate", help="Validate project configuration and inputs")
    validate.add_argument("--project", required=True)
    mode = validate.add_mutually_exclusive_group()
    mode.add_argument("--offline", action="store_true")
    mode.add_argument("--preflight", action="store_true")
    validate.add_argument("--json", action="store_true")
    generate = sub.add_parser("generate-track", help="Write a normalized simulated aircraft track")
    generate.add_argument("--project", required=True)
    generate.add_argument("--aircraft-id", required=True)
    for field in ("start-utc", "stop-utc"):
        generate.add_argument(f"--{field}", required=True)
    for field in ("step-s", "start-lat-deg", "start-lon-deg", "stop-lat-deg", "stop-lon-deg", "altitude-m"):
        generate.add_argument(f"--{field}", required=True, type=float)
    args = parser.parse_args(argv)
    try:
        if args.command == "validate":
            report = validate_project(load_project(args.project), level="preflight" if args.preflight else "offline")
            if args.json:
                print(json.dumps(report.as_dict(), ensure_ascii=False, indent=2))
            else:
                for issue in report.issues:
                    print(f"{issue.severity} {issue.code} {issue.location}: {issue.message}")
                print("VALID" if report.ok else "INVALID")
            return report.exit_code
        if args.command == "generate-track":
            track, meta = generate_track(args.project, aircraft_id=args.aircraft_id,
                                         start_utc=args.start_utc, stop_utc=args.stop_utc,
                                         step_s=args.step_s, start_lat_deg=args.start_lat_deg,
                                         start_lon_deg=args.start_lon_deg, stop_lat_deg=args.stop_lat_deg,
                                         stop_lon_deg=args.stop_lon_deg, altitude_m=args.altitude_m)
            print(track)
            print(meta)
            return 0
    except FileNotFoundError as exc:
        print(f"INPUT_INVALID: {exc}", file=sys.stderr)
        return 3
    except (ValueError, TypeError) as exc:
        print(f"CONFIG_INVALID: {exc}", file=sys.stderr)
        return 2
    return 8
