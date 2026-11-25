# Setup and offline use

Use Python 3.10 or newer on Windows. From the `satcom_platform` directory,
install PyYAML and the package with `python -m pip install -e .`. pywin32 is
needed only for the optional M0 probe, not offline validation.

Copy `examples/minimal_project` to a project directory and place a real local
TLE at `input/satellites.tle`. Update `satellite_config.csv` and the scenario
UTC range to match it. The example radio values are format illustrations, not
verified hardware parameters.

Run `python -m satcom_platform validate --project <project> --offline --json`.
Exit code 0 means valid offline inputs, 2 means invalid configuration, and 3
means invalid input files or references. `--preflight` currently returns 4
for otherwise valid projects because license/provider inspection is pending.

Run the tests with `python -m unittest discover -s tests -v` after installing
the package, or set `PYTHONPATH=src` for a source checkout.

For the local browser interface, run `python -m satcom_platform.web --project
<project> --port 8765`, then visit `http://127.0.0.1:8765/`. Keep the terminal
running while inspecting the UI. The server listens only on `127.0.0.1`.
