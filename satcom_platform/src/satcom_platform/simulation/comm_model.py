"""Map the configured ideal tracking link to STK Simple TX/RX equivalents."""

from __future__ import annotations

import math


def simple_link_values(tx: dict[str, str], rx: dict[str, str],
                       tx_antenna: dict[str, str], rx_antenna: dict[str, str],
                       other_loss_db: float) -> dict[str, float]:
    """Represent constant peak gain as EIRP and G/T, with explicit scalar losses."""
    for antenna in (tx_antenna, rx_antenna):
        if antenna["model"] not in {"SIMPLE", "APENST818V01"} or antenna["pointing_mode"] not in {"TARGET_TRACKING", "ISOTROPIC"}:
            raise ValueError("Budget adapter supports SIMPLE/APENST818V01 ideal tracking or isotropic antennas only")
        if any(float(antenna[field]) != 0 for field in ("mount_yaw_deg", "mount_pitch_deg", "mount_roll_deg")):
            raise ValueError("Simple budget adapter cannot model nonzero antenna mount angles")
        if antenna["pointing_mode"] == "ISOTROPIC" and float(antenna["peak_gain_dbi"]) != 0:
            raise ValueError("Isotropic antenna peak gain must be 0 dBi")
    if tx["role"] != "TX" or rx["role"] != "RX":
        raise ValueError("Link must contain TX and RX devices")
    if abs(float(tx["frequency_hz"]) - float(rx["frequency_hz"])) / float(tx["frequency_hz"]) > .001:
        raise ValueError("TX and RX frequencies differ by over 0.1%")
    if rx.get("system_noise_temp_k"):
        noise_k = float(rx["system_noise_temp_k"])
    else:
        noise_k = 290.0 * 10 ** (float(rx["noise_figure_db"]) / 10.0)
    if noise_k <= 0:
        raise ValueError("Receiver noise temperature must be positive")
    eirp_dbw = (float(tx["power_dbw"]) + float(tx_antenna["peak_gain_dbi"])
                - float(tx["feeder_loss_db"]) - other_loss_db)
    g_over_t_dbk = (float(rx_antenna["peak_gain_dbi"])
                    - float(rx["feeder_loss_db"]) - 10 * math.log10(noise_k))
    return {"frequency_hz": float(tx["frequency_hz"]),
            "data_rate_bps": float(tx["data_rate_bps"]),
            "bandwidth_hz": float(rx["bandwidth_hz"]),
            "eirp_dbw": eirp_dbw, "g_over_t_dbk": g_over_t_dbk,
            "receiver_noise_temp_k": noise_k}
