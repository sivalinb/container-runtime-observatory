# Architecture

## Data flow

Pkl workload definition → repeated VM launches → workload READY signal → runtime JSON statistics + guest resource measurements + host memory context → cleanup → evidence report. Independent public-series analysis trains an Isolation Forest on an initial reference window and scores held-out observations.

## Implementation decisions

The workload prints READY after interpreter startup. Host timing therefore includes CLI/VM launch and readiness polling. Memory probes allocate and touch pages, free them halfway through, and report Linux ru_maxrss. CPU probes count SHA-256 operations in a fixed monotonic interval. Container stats are normalized from Apple's JSON schema; missing observations are never represented as zero usage. A neighboring VM competes for shared host resources. Isolation Forest uses a fixed random seed, fits the first 60 percent of a series, and labels later points; synthetic ground-truth flags support precision/recall on the held-out section.

## Modules

`app.py` renders Streamlit controls and stores the current report in session state. `engine.py` contains domain logic and typed runtime models. `config/` stores Pkl source and its verified export. `labcore/runtime.py` issues argument-array subprocess calls, captures bounded output, and scopes cleanup to generated job names. `labcore/observability.py` writes event metadata and experiment reports. `labcore/ai.py` retrieves reference evidence and optionally synthesizes a cited answer. `data/sources.json` declares the public inputs and their terms. `workloads/` contains trusted workload entrypoints, where needed. `tests/` covers failure cases and Streamlit workflows.

## Trust boundaries

UI uploads and downloaded source content are data. They do not become system commands or Pkl modules. The sandbox project explicitly permits user Python inside a VM. Other tools execute only checked-in workload entrypoints. Subprocess calls use argument lists without a shell. Source URLs come from a fixed HTTPS catalogue with redirects disabled. Model responses are advisory and cannot trigger container actions.

## Persistence and reproducibility

Run artifacts are local and ignored by Git. Reports retain the mode, input/contract settings, source/config hashes where applicable, raw observations, and calculated decisions. Reproduce a finding by saving the report, pinning runtime/image/model versions, rerunning with the same workload, and comparing independent trials. Generated configuration and dependency versions are committed. For formal benchmarks replace mutable image tags with verified OCI digests.
