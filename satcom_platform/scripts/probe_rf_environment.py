"""Verify native RF environment integration in an isolated, unsaved STK scene."""
from __future__ import annotations

import json

from satcom_platform.simulation.rf_environment import MODELS, configure_environment, configure_receiver_rain


def main():
    import win32com.client

    app = win32com.client.DispatchEx("STK12.Application")
    root = app.Personality2
    try:
        root.NewScenario("SatcomRFProbe")
        root.CurrentScenario.SetTimePeriod("12 Nov 2026 02:00:00.000", "12 Nov 2026 02:10:00.000")
        root.UnitPreferences.Item("Distance").SetCurrentUnit("m")
        propagation = {key: spec[0] for key, spec in MODELS.items()}
        propagation["scintillation_outage_percent"] = 0.2
        result = configure_environment(root, propagation)
        print(json.dumps(result, indent=2), flush=True)
        root.ExecuteCommand("New / Facility RFProbe")
        root.ExecuteCommand("New / */Facility/RFProbe/Receiver RX")
        path = "*/Facility/RFProbe/Receiver/RX"
        readback = root.ExecuteCommand(f"Receiver_RM {path} GetValue Model")
        print("\n".join(str(readback.Item(i)) for i in range(readback.Count)), flush=True)
        configure_receiver_rain(root, path, propagation)
        print("RECEIVER_RAIN_OK", flush=True)
        root.ExecuteCommand("New / Satellite SAT")
        root.ExecuteCommand('SetState */Satellite/SAT Classical TwoBody UseScenarioInterval 60 ICRF "12 Nov 2026 02:00:00.000" 42164000 0 0 0 0 0')
        root.UnitPreferences.Item("DateFormat").SetCurrentUnit("EpSec")
        sat = root.GetObjectFromPath("*/Satellite/SAT")
        lla = sat.DataProviders.Item("LLA State").Group.Item("Fixed").ExecSingle(0)
        lat = lla.DataSets.GetDataSetByName("Lat").GetValues()[0]
        lon = lla.DataSets.GetDataSetByName("Lon").GetValues()[0]
        root.ExecuteCommand(f"SetPosition */Facility/RFProbe Geodetic {lat} {lon} 0")
        root.ExecuteCommand("New / */Satellite/SAT/Transmitter TX")
        tx_path = "*/Satellite/SAT/Transmitter/TX"
        root.ExecuteCommand(f"Transmitter {tx_path} SetValue Model.Frequency 12000000000 Hz")
        root.ExecuteCommand(f"Transmitter {tx_path} SetValue Model.EIRP 24 dBW")
        root.ExecuteCommand(f"Transmitter {tx_path} SetValue Model.DataRate 500000 b*sec^-1")
        root.ExecuteCommand(f"Receiver {path} SetValue Model.FrequencyAutoTracking false")
        root.ExecuteCommand(f"Receiver {path} SetValue Model.Frequency 12000000000 Hz")
        root.ExecuteCommand(f"Receiver {path} SetValue Model.AutoScaleBandwidth false")
        root.ExecuteCommand(f"Receiver {path} SetValue Model.Bandwidth 1000000 Hz")
        root.ExecuteCommand(f"Receiver {path} SetValue Model.GOverT 10 dB/K")
        access = root.GetObjectFromPath(tx_path).GetAccessToObject(root.GetObjectFromPath(path))
        def budget(settings):
            configure_environment(root, settings)
            configure_receiver_rain(root, path, settings)
            access.ComputeAccess()
            point = access.DataProviders.Item("Link Information").ExecSingle(0)
            return {name: float(point.DataSets.GetDataSetByName(name).GetValues()[0])
                    for name in ("C/N", "Eb/No", "BER", "Rain Loss", "Atmos Loss", "CloudsFog Loss", "TropoScintill Loss")}
        baseline = budget({})
        measurements = {"baseline": baseline}
        for key, spec in MODELS.items():
            enabled = budget({key: spec[0]})
            assert enabled["C/N"] < baseline["C/N"], (key, baseline, enabled)
            measurements[key] = enabled
        measurements["all_enabled"] = budget(propagation)
        assert measurements["all_enabled"]["C/N"] < baseline["C/N"]
        measurements["disabled_again"] = budget({})
        assert abs(measurements["disabled_again"]["C/N"] - baseline["C/N"]) < 1e-6
        print(json.dumps(measurements, indent=2), flush=True)
        print("RF_BUDGET_VERIFIED", flush=True)
    finally:
        root.CloseScenario()
        app.Quit()


if __name__ == "__main__":
    main()
