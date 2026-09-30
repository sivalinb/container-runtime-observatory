# Container Runtime Observatory

[![Verify](https://github.com/sivalinb/container-runtime-observatory/actions/workflows/ci.yml/badge.svg)](https://github.com/sivalinb/container-runtime-observatory/actions/workflows/ci.yml)

Application metrics do not fully explain VM startup, resource pressure, or interference. This project observes runtime behavior and separates guest measurements from host-wide observations.

Python · Streamlit · Pkl · Apple Container · evaluation evidence · OpenTelemetry

## Start here

```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
streamlit run app.py --server.port 8505
```

The interface opens at http://127.0.0.1:8505. Portable demos work without a model, API key, Pkl executable, or container runtime. The configuration fallback is a checked export whose source hash must match the committed Pkl source. Every report identifies its mode.

## Walkthrough

1. Open Anomaly analysis and run the labeled synthetic fixture. Inspect the reference/evaluation split and flags.
2. Fetch NAB CPU or taxi observations and select Fetched public source. These flags indicate unusual values, not confirmed incidents.
3. Prepare the Python container image. Run a memory experiment with three repeats.
4. Compare readiness timings, guest peak RSS, and observed container memory.
5. Run the CPU workload alone and with a neighboring CPU workload. Preserve both reports.
6. Change CPU or memory allocations, rerun, and explain the observed differences using the measurement definitions.

## Architecture

Pkl workload definition → repeated VM launches → workload READY signal → runtime JSON statistics + guest resource measurements + host memory context → cleanup → evidence report. Independent public-series analysis trains an Isolation Forest on an initial reference window and scores held-out observations.

The Streamlit UI calls pure Python engines; each repository vendors a small `labcore` package so cloning this repository is sufficient. No sibling repository is required.

## CLI and checks

```bash
python scripts/run.py
python scripts/run.py --live --kind memory
python scripts/run.py --live --kind cpu --contended
pytest -q
python scripts/evaluate.py
python scripts/export_config.py   # requires pkl on PATH or PKL_BIN
```

## Observed verification

23 automated tests passed locally. Real memory and CPU probes completed, including a neighboring-workload comparison. Public NAB data was evaluated with a chronological split. See [verified results and evidence](docs/VALIDATION.md) for settings, provenance, and limitations.

## Documentation

- [Setup and live runtime](docs/SETUP.md)
- [Architecture and decisions](docs/ARCHITECTURE.md)
- [Learning walkthrough](docs/WALKTHROUGH.md)
- [Evaluation methodology](docs/EVALUATION.md)
- [Public sources and licenses](docs/DATA_SOURCES.md)
- [Observability and AI](docs/OPERATIONS.md)
- [Security and limitations](docs/SECURITY.md)
- [Verified results](docs/VALIDATION.md)

MIT-licensed project code. External datasets and references retain their own terms. Public inputs are fetched explicitly and kept under ignored `artifacts/`; no private production telemetry is included.
