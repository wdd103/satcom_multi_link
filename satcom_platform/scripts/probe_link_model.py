"""Inspect one visible STK link without saving changes to the source scene."""
from pathlib import Path
import re
import sys
import pywintypes
import win32com.client

scene = Path(sys.argv[1]).resolve()
app = win32com.client.Dispatch("STK12.Application")
root = app.Personality2
try:
    existing = str(root.CurrentScenario.InstanceName)
    if existing:
        if not re.fullmatch(r"DemoSatcom_\d{8}T\d{6}Z_[0-9a-f]{8}", existing):
            raise RuntimeError(f"Unrelated scenario already open: {existing}")
        root.CloseScenario()
except (AttributeError, pywintypes.com_error):
    pass
root.LoadScenario(str(scene))
tx_path = "*/Aircraft/AC1/Transmitter/TEST_TX"
rx_path = "*/Satellite/SAT41918/Receiver/TEST_RX"
root.ExecuteCommand("New / */Aircraft/AC1/Transmitter TEST_TX")
root.ExecuteCommand("New / */Satellite/SAT41918/Receiver TEST_RX")
commands = [
    f"Transmitter {tx_path} SetValue Model.Frequency 14000000000 Hz",
    f"Transmitter {tx_path} SetValue Model.EIRP 24 dBW",
    f"Transmitter {tx_path} SetValue Model.DataRate 500000 b*sec^-1",
    f"Receiver {rx_path} SetValue Model.FrequencyAutoTracking false",
    f"Receiver {rx_path} SetValue Model.Frequency 14000000000 Hz",
    f"Receiver {rx_path} SetValue Model.GOverT -13 dB/K",
]
for command in commands:
    print(command, flush=True)
    root.ExecuteCommand(command)
root.UnitPreferences.Item("DateFormat").SetCurrentUnit("EpSec")
root.UnitPreferences.Item("Distance").SetCurrentUnit("m")
tx = root.GetObjectFromPath(tx_path)
rx = root.GetObjectFromPath(rx_path)
access = tx.GetAccessToObject(rx)
access.ComputeAccess()
print("intervals", access.ComputedAccessIntervalTimes.Count, flush=True)
provider = access.DataProviders.Item("Link Information")
print("elements", [provider.Elements.Item(i).Name for i in range(provider.Elements.Count)], flush=True)
point = provider.ExecSingle(240.0)
for name in ("C/No", "C/N", "Eb/No", "EIRP", "Bandwidth", "Rcvd. Frequency", "g/T", "Range", "Free Space Loss", "Carrier Power at Rcvr Input", "Tequivalent"):
    try:
        print(name, point.DataSets.GetDataSetByName(name).GetValues(), flush=True)
    except Exception as exc:
        print(name, type(exc).__name__, flush=True)
for command in (f"Transmitter_RM {tx_path} GetValue Model.Frequency",
                f"Transmitter_RM {tx_path} GetValue Model.DataRate",
                f"Receiver_RM {rx_path} GetValue Model.GOverT",
                f"Receiver_RM {rx_path} GetValue Model.Frequency"):
    result = root.ExecuteCommand(command)
    print(command, [str(result.Item(i)) for i in range(result.Count)], flush=True)
