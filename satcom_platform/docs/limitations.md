# Current implementation limits

Current delivery status is recorded in [产品交付说明（2026-11-25）](产品交付说明_当前状态_2026-11-25.md).

- STK 12 COM scene construction, SGP4 satellite import, external aircraft ephemeris, Access geometry, and Simple TX/RX link budget export are available on the verified local machine. They require a working STK installation and Communications capability on any other machine.
- The sample TLE is roughly 30 days older than the scene time. Its output verifies the processing chain, not the accuracy of coverage or link performance.
- `SIMPLE` and the configured `APENST818V01` formula are supported. STK Simple equivalents provide on-axis budgets; platform-side downlink aggregation applies both off-axis patterns. The saved scene does not contain native directional Antenna objects or a CommSystem interference report. See [下行干扰与统一方向图](downlink_interference.md). Communication antenna mount-angle effects and automatic real-attitude inference remain unsupported; native imported sensor orientation is used for sensor visibility.
- BER is read from the STK default modulation model; no modulation or coding selection is currently stored in the platform configuration. The planned simplified control will select a supported modulation and record it in the result. BER is not packet loss.
- Aircraft and ground-gateway uplink/downlink budgets and an OMNeT++ timeline interface are implemented. The OMNeT++ model has one aircraft, one satellite and one gateway, with packet traffic and finite relay queues. Multi-aircraft network topology, routing/handover and BER-driven random packet loss remain unsupported; filter fleet timelines to the selected four links before importing.
- Results use a fixed time grid. Exact access boundary events are not exported, and short interruptions may occur between samples.
- Native STK rain, gaseous absorption, cloud/fog, and tropospheric scintillation are configurable from the web console. See [大气传播模型](rf_environment.md). These are statistical attenuation models with fixed receiver G/T, not random weather/fading time series.
- The web console supports project creation and Save As by copying project files. The lower-level `save_project` API only atomically saves the validated scenario YAML. The PySide6 desktop GUI is not implemented.
- CSV imports require normalized field names and units; arbitrary source file mappings are not implemented.

- Existing `.bmsk` files can be imported and applied through native sensor Access. Automatic mask generation from arbitrary aircraft models and automatic pitch/roll histories are not implemented. See [fleet and masking](fleet_body_mask.md).
- Configured data rates remain fixed rather than following Shannon capacity or SINR. The interference-aware BPSK BER is a platform-side approximation, distinct from the original STK BER.
