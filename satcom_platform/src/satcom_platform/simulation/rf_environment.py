"""Configure native STK RF propagation models; retain readback for each run."""

from __future__ import annotations

import re


# Configuration names are independent of the installed STK model revision.
MODELS = {
    "atmosphere_model": ("ITU_R_P676", "UseAtmosAbsorptionModel", "AtmosAbsorptionModel", 676),
    "rain_model": ("ITU_R_P618", "UseRainModel", "RainModel", 618),
    "cloud_fog_model": ("ITU_R_P840", "UseCloudFogModel", "CloudFogModel", 840),
    "tropo_scintillation_model": ("ITU_R_P618", "UseTropoScintModel", "TropoScintModel", 618),
}

PARAMETERS = {
    "rain_outage_percent": (0.1, 0.001, 5),
    "cloud_ceiling_m": (3000, 0, 20000),
    "cloud_thickness_m": (500, 0, 20000),
    "cloud_temperature_k": (273.15, 200, 330),
    "cloud_liquid_water_density_g_m3": (0.5, 0, 10),
    "scintillation_outage_percent": (0.1, 0.01, 50),
}


def _lines(result) -> list[str]:
    return [line.strip() for i in range(result.Count)
            for line in str(result.Item(i)).splitlines() if line.strip()]


def configure_environment(root, propagation: dict) -> dict:
    """Select the latest installed revision of each requested ITU recommendation.

    Fail explicitly on unsupported models/parameters instead of silently running
    a clear-sky budget. New scenarios have no object-level environment overrides.
    """
    selected = {}
    for key, (enabled_value, flag, model, recommendation) in MODELS.items():
        enabled = propagation.get(key, "NONE") != "NONE"
        if enabled and propagation[key] != enabled_value:
            raise ValueError(f"Unsupported {key}: {propagation[key]}")
        root.ExecuteCommand(f"RFEnvironment * SetValue PropagationChannel.{flag} {str(enabled).lower()}")
        if not enabled:
            selected[key] = "NONE"
            continue
        choices = _lines(root.ExecuteCommand(f"RFEnvironment_RM * GetValue PropagationChannel.{model}:Choices"))
        pattern = re.compile(rf"(?:P|ITU[_-]?){recommendation}[-_](\d+)", re.I)
        candidates = [(int(match.group(1)), choice) for choice in choices
                      if (match := pattern.search(choice))]
        if not candidates:
            raise RuntimeError(f"STK has no ITU-R P.{recommendation} model for {key}: {choices}")
        chosen = max(candidates)[1]
        root.ExecuteCommand(f"RFEnvironment * SetValue PropagationChannel.{model} {chosen}")
        selected[key] = chosen

    def parameter(name: str, attribute: str, unit: str = "") -> None:
        value = float(propagation.get(name, PARAMETERS[name][0]))
        root.ExecuteCommand(f"RFEnvironment * SetValue {attribute} {value:g}{' ' + unit if unit else ''}")

    if selected["rain_model"] != "NONE":
        parameter("rain_outage_percent", "RainOutagePercent")
    if selected["cloud_fog_model"] != "NONE":
        for name, attribute, unit in (
            ("cloud_ceiling_m", "CloudCeiling", "m"),
            ("cloud_thickness_m", "CloudLayerThickness", "m"),
            ("cloud_temperature_k", "CloudTemp", "K"),
            ("cloud_liquid_water_density_g_m3", "CloudLiqWaterDensity", "g*m^-3"),
        ):
            parameter(name, f"PropagationChannel.CloudFogModel.{attribute}", unit)
    if selected["tropo_scintillation_model"] != "NONE":
        # STK stores the exceeded probability as a fraction, unlike RainOutagePercent.
        value = float(propagation.get("scintillation_outage_percent", PARAMETERS["scintillation_outage_percent"][0])) / 100
        attribute = "FadeExceeded" if selected["tropo_scintillation_model"].endswith("-12") else "FadeOutage"
        root.ExecuteCommand(f"RFEnvironment * SetValue PropagationChannel.TropoScintModel.{attribute} {value:g}")
    return {"requested": propagation.copy(), "selected_models": selected,
            "stk_readback": _lines(root.ExecuteCommand("RFEnvironment_RM * GetValue")),
            "interpretation": "ITU statistical attenuation; not a random weather time series. Receiver system noise temperature remains configured."}


def configure_receiver_rain(root, path: str, propagation: dict) -> None:
    """STK additionally requires the rain switch on each receiving device."""
    enabled = propagation.get("rain_model", "NONE") != "NONE"
    root.ExecuteCommand(f"Receiver {path} SetValue Model.UseRain {str(enabled).lower()}")
    if enabled:
        value = float(propagation.get("rain_outage_percent", PARAMETERS["rain_outage_percent"][0]))
        root.ExecuteCommand(f"Receiver {path} SetValue Model.RainOutagePercent {value:g}")
