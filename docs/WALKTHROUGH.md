# Learning walkthrough

## Guided experiment

1. Open Anomaly analysis and run the labeled synthetic fixture. Inspect the reference/evaluation split and flags.
2. Fetch NAB CPU or taxi observations and select Fetched public source. These flags indicate unusual values, not confirmed incidents.
3. Prepare the Python container image. Run a memory experiment with three repeats.
4. Compare readiness timings, guest peak RSS, and observed container memory.
5. Run the CPU workload alone and with a neighboring CPU workload. Preserve both reports.
6. Change CPU or memory allocations, rerun, and explain the observed differences using the measurement definitions.

## Questions to answer in your portfolio write-up

1. What concrete failure does this experiment expose?
2. Which checks happen before execution, and which need runtime observations?
3. Which input, configuration, image, and model versions were used?
4. What did the positive and negative controls demonstrate?
5. Where could the measurements be misleading?
6. Which follow-up experiment would challenge your conclusion?

## Suggested demonstration

Record a three-minute walkthrough: explain the failure in one sentence, run a baseline, introduce one deliberate change, inspect the evidence, and explain the tradeoff. Include the downloadable report and the command needed to reproduce it. Prefer measured operational behavior over an unsupported claim of production readiness.

## Next extensions

Add one extension only after retaining a passing baseline: more realistic public workloads, an additional failure mode, stricter provenance, a larger evaluation set, or a runtime-version comparison. Preserve fixture/live distinctions and document negative results. The other four repositories in this portfolio can reuse the report schema without creating a runtime dependency on each other.
