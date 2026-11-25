import math
import csv
import tempfile
import unittest
from pathlib import Path

from satcom_platform.simulation.antenna_pattern import Apenst818, separation_deg
from satcom_platform.simulation.interference import aggregate_downlink
from satcom_platform.simulation.omnet_export import export_timeline
from satcom_platform.simulation.run_plan import parse_utc


def antenna(gain=15, phi0=30):
    return {"model": "APENST818V01", "peak_gain_dbi": str(gain), "beamwidth_deg": str(phi0),
            "pointing_mode": "TARGET_TRACKING"}


class PatternTests(unittest.TestCase):
    def test_pdf_formula_continuity_peak_and_floor(self):
        for gain, phi0 in ((15, 30), (20, 20)):
            pattern = Apenst818.from_row(antenna(gain, phi0))
            self.assertEqual(pattern.gain(0), gain)
            curvature = .0025 * 10 ** (gain/10) / (.7 * math.pi**2)
            self.assertAlmostEqual(pattern.gain(phi0/2), gain-curvature*(phi0/2)**2)
            self.assertAlmostEqual(pattern.gain(phi0-1e-8), pattern.gain(phi0), places=6)
            self.assertEqual(pattern.gain(180), -10)
            self.assertTrue(pattern.metadata()["wide_beam_adaptation"])

    def test_invalid_pattern_is_rejected(self):
        for changes in ({"pattern_coefficient_b": "51"}, {"aperture_efficiency": "0"},
                        {"pattern_coefficient_a": "52"}, {"beamwidth_deg": "0"}):
            with self.subTest(changes=changes), self.assertRaises(ValueError):
                Apenst818.from_row({**antenna(), **changes})

    def test_coordinate_invariance(self):
        self.assertAlmostEqual(separation_deg((0,0,0), (1,0,0), (0,1,0)), 90)
        self.assertAlmostEqual(separation_deg((5,5,5), (6,5,5), (5,6,5)), 90)
        self.assertAlmostEqual(separation_deg((0,0,0), (1,0,0), (-1,0,0)), 180)

    def test_export_is_stk_symmetric_gain_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "pattern.ant"
            Apenst818.from_row(antenna()).export(path)
            lines = path.read_text().splitlines()
            self.assertIn("SymmetricPattern", lines)
            self.assertEqual(lines[lines.index("PatternData")+1], "0.00000000 15.0000000000")


class InterferenceTests(unittest.TestCase):
    def setUp(self):
        self.time = "2026-11-12T02:00:00Z"
        self.receiver = {"device_id": "RX", "platform_type": "AIRCRAFT", "platform_id": "AC1",
                         "frequency_hz": "12000000000", "bandwidth_hz": "1000000", "feeder_loss_db": "1"}
        self.budget = {"access": "true", "satellite_id": "S0", "time_utc": self.time,
                       "received_iso_power_dbw": -100, "cn_db": 20, "ebno_db": 23, "ber": 1e-9}
        self.positions = {("AIRCRAFT", "AC1", self.time): (0,0,0),
                          ("SATELLITE", "S0", self.time): (1,0,0),
                          ("SATELLITE", "S1", self.time): (0,1,0),
                          ("SATELLITE", "S2", self.time): (0,-1,0),
                          ("GATEWAY", "GW", self.time): (0,2,0)}
        self.emissions = [{"satellite_id": sid, "tx": {"device_id": "TX", "frequency_hz": "12000000000", "bandwidth_hz": "1000000"},
                           "antenna": antenna(20,20), "target": ("AIRCRAFT", "AC1"), "link_id": "D1"}
                          for sid in ("S0", "S1", "S2")]
        self.samples = {("TX", sid, "RX", self.time): {"visible": True, "rip_dbw": -100}
                        for sid in ("S0", "S1", "S2")}

    def calculate(self):
        return aggregate_downlink(self.budget, {"link_id": "D1", "min_cn_db": 19, "min_sinr_db": ""}, self.receiver,
                                  antenna(), self.emissions, self.positions, self.samples)

    def test_self_exclusion_linear_sum_and_sinr(self):
        result, details = self.calculate()
        self.assertEqual(result["interferer_count"], 2)
        self.assertEqual({d["interferer_satellite_id"] for d in details}, {"S1", "S2"})
        self.assertAlmostEqual(result["interference_power_w"], sum(d["received_power_w"] for d in details))
        one = details[0]["received_power_dbw"]
        self.assertAlmostEqual(result["interference_power_dbw"], one + 10*math.log10(2))
        carrier_w = 10 ** (result["carrier_power_dbw"]/10)
        noise_w = carrier_w / 100
        expected = 10*math.log10(carrier_w/(noise_w+result["interference_power_w"]))
        self.assertAlmostEqual(result["sinr_db"], expected)
        self.assertLess(result["sinr_db"], 20)
        self.assertEqual(result["meets_min_sinr"], "false")

    def test_geometrically_invisible_sources_contribute_zero(self):
        for sample in self.samples.values():
            sample["visible"] = False
        result, details = self.calculate()
        self.assertEqual(details, [])
        self.assertEqual(result["interference_power_w"], 0)
        self.assertEqual(result["sinr_db"], self.budget["cn_db"])
        self.assertEqual(result["ber_with_interference"], self.budget["ber"])
        self.assertEqual(result["ci_db"], "")

    def test_other_frequency_is_excluded(self):
        self.emissions[1]["tx"]["frequency_hz"] = "14000000000"
        self.assertEqual(self.calculate()[0]["interferer_count"], 1)

    def test_transmit_off_axis_changes_power(self):
        original = self.calculate()[1][0]
        self.emissions[1]["target"] = ("GATEWAY", "GW")
        changed = self.calculate()[1][0]
        self.assertAlmostEqual(changed["tx_off_axis_deg"], 180)
        self.assertAlmostEqual(original["received_power_dbw"] - changed["received_power_dbw"], 30)

    def test_candidate_receiver_boresight_changes(self):
        original = self.calculate()[1][0]
        self.positions[("SATELLITE", "S0", self.time)] = (0,1.5,0)
        changed = self.calculate()[1][0]
        self.assertAlmostEqual(changed["rx_off_axis_deg"], 0)
        self.assertGreater(changed["received_power_w"], original["received_power_w"])

    def test_unavailable_desired_link_has_blank_results(self):
        self.budget["access"] = "false"
        result, details = self.calculate()
        self.assertTrue(all(v == "" for v in result.values()))
        self.assertEqual(details, [])

    def test_network_timeline_applies_sinr_gate(self):
        row = {**self.budget, "link_id": "D1", "direction": "DOWNLINK", "aircraft_id": "AC1",
               "gateway_id": "", "range_m": 1000000, "meets_min_cn": "true", "sinr_db": -2,
               "ebni_db": 1, "ber_with_interference": .1, "meets_min_sinr": "false"}
        devices = {"TX": {"platform_type": "SATELLITE", "platform_id": "S0", "data_rate_bps": 500000},
                   "RX": self.receiver}
        links = [{"link_id": "D1", "direction": "DOWNLINK", "tx_id": "TX", "rx_id": "RX"}]
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "timeline.csv"
            export_timeline(path, "test", parse_utc(self.time), parse_utc("2026-11-12T02:01:00Z"),
                            60, [], [row], links, devices)
            with path.open() as stream:
                result = next(csv.DictReader(stream))
            self.assertEqual(result["available"], "false")
            self.assertEqual(result["capacity_bps"], "0")
            row.update(meets_min_sinr="true", sinr_db=5)
            export_timeline(path, "test", parse_utc(self.time), parse_utc("2026-11-12T02:01:00Z"),
                            60, [], [row], links, devices)
            with path.open() as stream:
                result = next(csv.DictReader(stream))
            self.assertEqual(result["available"], "true")
            self.assertEqual(float(result["sinr_db"]), 5)
            self.assertEqual(float(result["cn_db"]), 20)
