"""Transient STK Communications capability probe; never saves the scene."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("scene", type=Path)
    args = parser.parse_args()
    import win32com.client

    scene = args.scene.resolve()
    app = win32com.client.Dispatch("STK12.Application")
    root = app.Personality2
    try:
        current = str(root.CurrentScenario.InstanceName)
    except Exception:
        current = ""
    if current:
        if not re.fullmatch(r"DemoSatcom_\d{8}T\d{6}Z_[0-9a-f]{8}", current):
            raise RuntimeError(f"Unrelated STK scenario is open: {current}")
        root.CloseScenario()
    root.LoadScenario(str(scene))
    root.ExecuteCommand("New / */Aircraft/AC1/Transmitter PROBE_TX")
    root.ExecuteCommand("New / */Satellite/SAT41917/Receiver PROBE_RX")
    tx = root.GetObjectFromPath("*/Aircraft/AC1/Transmitter/PROBE_TX")
    rx = root.GetObjectFromPath("*/Satellite/SAT41917/Receiver/PROBE_RX")
    access = tx.GetAccessToObject(rx)
    access.ComputeAccess()
    access.DataProviders.Item("Link Information")
    print(json.dumps({"scene_loaded": True, "communications_objects": True,
                      "link_information_provider": True}, indent=2))


if __name__ == "__main__":
    main()
