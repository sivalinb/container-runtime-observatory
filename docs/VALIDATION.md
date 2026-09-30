# Verified results

Verified on 2026-09-30 UTC (2026-09-29 Mountain Time). This page reports observed development checks, not production reliability guarantees. The committed JSON evidence contains synthetic workloads, public-source metadata, and measured results. Secrets, local usernames, and source-cache contents are excluded.

## Portable checks

- `pytest -q`: **23 passed**, including the Streamlit primary workflow.
- `python scripts/evaluate.py`: all domain checks passed; retrieval hit@3 was 1.0 on five authored questions, and the unrelated-question abstention check passed.
- Pkl 0.32.1: valid configuration tests passed; invalid CPU allocation is rejected by the Python test suite.
- `ruff check .`: passed.

[portable-checks.json](evidence/portable-checks.json) preserves command results. The five retrieval questions are a small diagnostic suite, not a broad RAG quality benchmark. The default reviewer performs deterministic retrieval; no LLM is required for portable checks.

[Environment and OCI digests](evidence/environment.json) identify the tested dependencies and live image revisions. [GitHub Actions](https://github.com/sivalinb/container-runtime-observatory/actions) independently reports the current portable CI status. Ordinary Linux CI does not run Apple Container workloads.

## Actual runtime measurements

Three memory probes ran in Apple Container with one configured CPU, 256 MiB memory, a 64 MiB allocation, and a three-second workload. The cached-image startup median was 1008.54 ms and maximum 1718.23 ms; startup includes CLI overhead through workload readiness. Six runtime-stat observations were collected, and guest high-water RSS was approximately 85.9 MB. See [memory-probe.json](evidence/memory-probe.json).

Separate CPU probes completed with and without a neighboring CPU workload. Their raw observations are in [cpu-baseline.json](evidence/cpu-baseline.json) and [cpu-contended.json](evidence/cpu-contended.json). These short, uncontrolled trials demonstrate the measurement path. They do not establish an Apple Container performance ranking or a causal estimate of contention overhead.

Host used-memory samples describe the whole Mac, including unrelated activity. Guest `ru_maxrss` is a high-water mark and cannot show memory falling after free. Runtime statistics can lag a short-lived guest allocation; those quantities are intentionally kept distinct. More repetitions, a quiet host, randomized trial order, and confidence intervals are needed for comparative claims.

## Public anomaly input

The NAB CPU series was split chronologically into 2,419 reference/training points and 1,613 held-out evaluation points. The fitted IsolationForest flagged 974 evaluation points for this input. These are model flags, not verified incidents: the public run does not load NAB anomaly labels. Precision/recall are reported only for the built-in synthetic series with known injected labels. See [public-consumption.json](evidence/public-consumption.json).

## Reproduce

Run `python scripts/run.py --live --kind memory`, then `--kind cpu`, or use the VM experiment tab. Use Anomaly analysis for synthetic or uploaded CSV input. Fetch the public NAB CPU series from Public sources before selecting the latest public CSV.

## Public source verification

All ten catalogue entries downloaded successfully during verification, including USGS, NAB CPU/taxi, GSM8K, OpenMetrics, OTel semantic conventions, Pkl/Container releases, Apple runtime resource documentation, and node_exporter documentation. [public-sources.json](evidence/public-sources.json) records retrieval times, byte counts, hashes, URLs, and upstream terms. Documentation and release metadata are reference material, not empirical workload measurements. Downloaded source contents remain untracked and are not relicensed by this repository.
