"""Downlink co-channel aggregation using STK path budgets and off-axis gains.

STK Simple devices supply on-axis path/environment budgets. Directional
corrections and SINR are computed here; they are not native CommSystem reports.
"""
from __future__ import annotations

import math

from .antenna_pattern import gain_delta, separation_deg


RESULT_COLUMNS = ["carrier_power_dbw", "interference_power_w", "interference_power_dbw", "interferer_count",
                  "ci_db", "in_db", "sinr_db", "ebni_db", "ber_with_interference", "meets_min_sinr"]
DETAIL_COLUMNS = ["link_id", "satellite_id", "time_utc", "receiver_id", "interferer_satellite_id",
                  "interferer_tx_id", "interferer_link_id", "tx_off_axis_deg", "rx_off_axis_deg",
                  "tx_gain_dbi", "rx_gain_dbi", "spectral_overlap", "received_power_dbw", "received_power_w"]


def spectral_overlap(source: dict, receiver: dict) -> float:
    f, b = float(source["frequency_hz"]), float(source["bandwidth_hz"])
    rf, rb = float(receiver["frequency_hz"]), float(receiver["bandwidth_hz"])
    return max(0, min(f+b/2, rf+rb/2) - max(f-b/2, rf-rb/2)) / b


def aggregate_downlink(budget: dict, link: dict, receiver: dict, rx_antenna: dict,
                       emissions: list[dict], positions: dict, path_samples: dict) -> tuple[dict, list[dict]]:
    """Each path sample is keyed by (tx_id, satellite_id, receiver_id, UTC).

    It must be geometrically visible AND have a valid STK on-axis RIP value.
    Emissions are deduplicated physical TX devices with a configured beam target.
    """
    if budget["access"] != "true":
        return {key: "" for key in RESULT_COLUMNS}, []
    sid, instant, rid = budget["satellite_id"], budget["time_utc"], receiver["device_id"]
    victim = positions[(receiver["platform_type"], receiver["platform_id"], instant)]
    serving = positions[("SATELLITE", sid, instant)]
    receiver_gain = float(rx_antenna["peak_gain_dbi"]) - float(receiver["feeder_loss_db"])
    carrier = float(budget["received_iso_power_dbw"]) + receiver_gain
    details, powers = [], []
    for emission in emissions:
        source, jsid = emission["tx"], emission["satellite_id"]
        if jsid == sid:
            continue
        if abs(float(source["frequency_hz"]) - float(receiver["frequency_hz"])) > 1:
            continue
        overlap = spectral_overlap(source, receiver)
        sample = path_samples.get((source["device_id"], jsid, rid, instant))
        if overlap <= 0 or sample is None or not sample["visible"]:
            continue
        sat_position = positions[("SATELLITE", jsid, instant)]
        target = positions[(*emission["target"], instant)]
        tx_angle = separation_deg(sat_position, target, victim)
        rx_angle = separation_deg(victim, serving, sat_position)
        tx_delta = gain_delta(emission["antenna"], tx_angle)
        rx_delta = gain_delta(rx_antenna, rx_angle)
        # Cross-path STK budgets already include spectral overlap and path losses.
        power_dbw = float(sample["rip_dbw"]) + receiver_gain + tx_delta + rx_delta
        power_w = 10 ** (power_dbw / 10)
        powers.append(power_w)
        details.append({"link_id": link["link_id"], "satellite_id": sid, "time_utc": instant,
                        "receiver_id": rid, "interferer_satellite_id": jsid,
                        "interferer_tx_id": source["device_id"], "interferer_link_id": emission["link_id"],
                        "tx_off_axis_deg": tx_angle, "rx_off_axis_deg": rx_angle,
                        "tx_gain_dbi": float(emission["antenna"]["peak_gain_dbi"]) + tx_delta,
                        "rx_gain_dbi": float(rx_antenna["peak_gain_dbi"]) + rx_delta,
                        "spectral_overlap": overlap, "received_power_dbw": power_dbw, "received_power_w": power_w})
    total_i = math.fsum(powers)
    cn, ebno = float(budget["cn_db"]), float(budget["ebno_db"])
    if total_i:
        interference_dbw = 10 * math.log10(total_i)
        ci = carrier - interference_dbw
        in_db = cn - ci
        degradation = 10 * math.log10(1 + 10 ** (in_db / 10))
        sinr, ebni = cn - degradation, ebno - degradation
        ber = 0.5 * math.erfc(math.sqrt(10 ** (min(ebni, 50) / 10)))
    else:
        interference_dbw = ci = in_db = ""  # zero I => -infinity I power; +infinity C/I
        sinr, ebni, ber = cn, ebno, float(budget["ber"])
    threshold = link.get("min_sinr_db")
    if threshold in (None, ""):
        threshold = link.get("min_cn_db")
    return {"carrier_power_dbw": carrier, "interference_power_w": total_i,
            "interference_power_dbw": interference_dbw, "interferer_count": len(powers),
            "ci_db": ci, "in_db": in_db, "sinr_db": sinr, "ebni_db": ebni,
            "ber_with_interference": ber,
            "meets_min_sinr": str(sinr >= float(threshold)).lower() if threshold not in (None, "") else ""}, details
