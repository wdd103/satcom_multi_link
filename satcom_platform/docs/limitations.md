# Current implementation limits

Current delivery status is recorded in [产品交付说明（2026-11-16）](产品交付说明_当前状态_2026-11-16.md).

- STK 12 COM scene construction, SGP4 satellite import, external aircraft ephemeris, Access geometry, and Simple TX/RX link budget export are available on the verified local machine. They require a working STK installation and Communications capability on any other machine.
- The sample TLE is roughly 30 days older than the scene time. Its output verifies the processing chain, not the accuracy of coverage or link performance.
- `SIMPLE` and the configured `APENST818V01` formula are supported. STK Simple equivalents provide on-axis budgets; platform-side downlink aggregation applies both off-axis patterns. The saved scene does not contain native directional Antenna objects or a CommSystem interference report. See [下行干扰与统一方向图](downlink_interference.md). Mount angles and real attitude remain unsupported.
- BER is read from the STK default modulation model; no modulation or coding selection is currently stored in the platform configuration. The planned simplified control will select a supported modulation and record it in the result. BER is not packet loss.
- The budget covers aircraft-to-satellite uplink and downlink. No ground gateway, feeder link, network routing, traffic, handover, or OMNeT++ integration is implemented.
- Results use a fixed time grid. Exact access boundary events are not exported, and short interruptions may occur between samples.
- Native STK rain, gaseous absorption, cloud/fog, and tropospheric scintillation are configurable from the web console. See [大气传播模型](rf_environment.md). These are statistical attenuation models with fixed receiver G/T, not random weather/fading time series.
- The web console supports project creation and Save As by copying project files. The lower-level `save_project` API only atomically saves the validated scenario YAML. The PySide6 desktop GUI is not implemented.
- CSV imports require normalized field names and units; arbitrary source file mappings are not implemented.
