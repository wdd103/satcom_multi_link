# Satcom platform: configuration and STK link budgets

Current handoff: [产品交付说明（2026-11-25）](docs/产品交付说明_当前状态_2026-11-25.md). The [2026-11-16 handoff](docs/产品交付说明_当前状态_2026-11-16.md) and original [M1 handoff](docs/产品交付说明_M1与STK场景准备_2026-11-15.md) are retained as historical snapshots. STK implementation: [M2 notes](docs/stk_m2.md).

Gateway feeder links and the versioned OMNeT++ timeline export are described in [the interface note](docs/omnet_interface_v1.md).

The scenario page includes independent switches for native STK rain, gaseous absorption, cloud/fog, and tropospheric scintillation. Configuration, parameters, and validation are described in [大气传播模型](docs/rf_environment.md).

Downlink co-channel interference, ideal Doppler compensation, and the user-provided APENST818V01 antenna pattern are documented in [下行干扰与统一方向图](docs/downlink_interference.md). The example enables the full-load model for visible non-serving satellites. STK supplies path budgets; platform-side off-axis aggregation exports SINR and per-emitter contributions separately from the original STK C/N.

The browser also supports native aircraft/sensor import, batch aircraft and link cloning, and per-sensor `.bmsk` selection. See [飞机、传感器与机体遮挡](docs/fleet_body_mask.md) for the imported settings, visibility rules, and limitations.

Install from this directory with `python -m pip install -e .`, or set
`PYTHONPATH=src`. The current implementation provides offline configuration
loading, YAML/CSV/TLE validation, simulated aircraft track generation, a
fixed time-grid run plan, and a local browser console. The STK runner connects
to STK 12 through COM on Windows and exports geometry and Simple-model link
budgets. The PySide6 GUI remains a separate milestone.

```powershell
python -m satcom_platform validate --project examples/minimal_project --offline --json
python -m satcom_platform generate-track --project examples/minimal_project --aircraft-id AC1 --start-utc 2026-11-12T02:00:00Z --stop-utc 2026-11-12T02:10:00Z --step-s 10 --start-lat-deg 31.2304 --start-lon-deg 121.4737 --stop-lat-deg 32.2304 --stop-lon-deg 122.4737 --altitude-m 10000
python scripts/probe_stk.py
```

The example contains a local TLE and a saved satellite CSV. Align the
configured NORAD IDs and UTC interval when replacing either input. `validate --preflight`
checks the saved configuration and reports the Simple-model assumptions;
numeric STK results are checked during a run.

`save_project` validates then atomically replaces `scenario.yaml`; the browser
provides a separate project Save As operation that copies project inputs and
configuration. IDs are case sensitive. A generated
track is a spherical great-circle interpolation for test scenarios and carries
no inferred aircraft attitude.

## Browser console

Start the local interface from this directory:

```powershell
python -m satcom_platform.web --project examples/minimal_project --port 8765
```

Open [http://127.0.0.1:8765/](http://127.0.0.1:8765/) in a browser. The
server binds only to the local loopback interface. It shows the ten navigation
areas and supports project opening/creation, draft editing, offline validation,
CSV/TLE upload, simulated track generation, validated saving, and STK runs.
The Run page defaults to 0, meaning all enabled satellites; a smaller number
can be entered for a quick check. The Results page shows status and downloads.

During a run, STK automatically opens its Message Viewer and displays `[SATCOM run_id]` progress messages with the stage, percentage, current object/link and completed count. Use **View → Message Viewer → All Messages** if the panel has been closed or filtered. The web Run and Results pages show the same progress, refreshed about every 2.5 seconds. Percentages are weighted work estimates; per-stage counts follow actual objects or samples. Progress reaches 100% after the scene and result archive have been saved, and failures retain their last percentage with an error message.

Each successful run is stored under the project's `output.root_dir` and contains
`scenario_bundle.zip` (the STK scene with sidecar files), `scenario.sc`,
`aircraft_state.csv`, `link_geometry.csv`, `link_budget.csv`, `manifest.json`, and one `.e` file per
aircraft. STK may retain the source TLE's absolute path inside satellite sidecar
files, so inspect or relink that path when moving the archive to another machine.
The CSV values are read from STK Data Providers. `access=false` rows
may have blank azimuth, elevation and range when STK reports no access.
The runner maps transmit power, antenna peak gain, feeder/other loss, and
receiver noise to STK Simple Transmitter EIRP and Simple Receiver G/T. It
replicates the configured satellite device template to every enabled satellite
and reads C/N, Eb/No and BER from STK `Link Information`. `TARGET_TRACKING`
means ideal constant peak gain: beamwidth and mount angles are not simulated.
The example TLE is about 30 days older than the scenario, so these numbers
demonstrate the interface and output format, not trusted flight performance.
See [STK M2 notes](docs/stk_m2.md).

The verified 80-satellite example run is in
`examples/minimal_project/runs/20261115T144039Z-e1bf92d3` (9,760 budget
rows, including 218 access samples).

When `config/satellite_config.csv` is absent, opening a project with an existing
TLE fills the satellite list from its unique NORAD IDs with every satellite
enabled by default. Saving the selection creates the CSV. Once the CSV exists,
the page always loads its satellite list from the CSV, including after a TLE
upload or path change. TLE parsing results remain visible separately. Checkboxes
select which satellites enter the scene; saving writes those choices to the CSV.
Editing this list never rewrites the TLE file.
Links to disabled satellites remain configured and are reported as inactive.
The satellite page also has a dedicated save button so the selection can be
stored while unrelated device references still need repair. Full project save
continues to require complete validation.
