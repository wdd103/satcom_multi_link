# Setup and offline use

Use Python 3.10 or newer on Windows. From the `satcom_platform` directory,
install PyYAML and the package with `python -m pip install -e .`. pywin32 is
needed for all native STK runs and probes, not offline validation.

Copy `examples/minimal_project` to a project directory and place a real local
TLE at `input/satellites.tle`. Update `satellite_config.csv` and the scenario
UTC range to match it. The example radio values are format illustrations, not
verified hardware parameters.

Run `python -m satcom_platform validate --project <project> --offline --json`.
Exit code 0 means valid offline inputs, 2 means invalid configuration, and 3
means invalid input files or references. `--preflight` adds model-assumption warnings; it does not perform a complete native STK license/provider inspection. Validate the native runtime through the STK probes and an actual run.

Run the tests with `python -m unittest discover -s tests -v` after installing
the package, or set `PYTHONPATH=src` for a source checkout.

For the local browser interface, run `python -m satcom_platform.web --project
<project> --port 8765`, then visit `http://127.0.0.1:8765/`. Keep the terminal
running while inspecting the UI. The server listens only on `127.0.0.1`.

Current usage and feature scope: [platform README](../README.md) and [delivery status](产品交付说明_当前状态_2026-11-25.md).
