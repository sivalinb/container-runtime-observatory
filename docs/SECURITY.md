# Security and limitations

Host used memory covers the entire machine and cannot be attributed to one VM. Guest peak RSS is a high-water mark and cannot show memory reclamation after free. Current runtime limitations may retain freed guest pages at the host. Very short probes can finish before a resource sample; evidence reports that gap. Isolation Forest is exploratory, not an incident classifier; its reference period may itself contain anomalies. This project does not include guest eBPF probes or a Swift-native exporter in its implemented scope.

## Shared boundaries

The app is intended for a trusted local user. It has no multi-user authentication or tenant isolation at the Streamlit layer. Public deployment requires a separate access-control and execution-service design. The Pkl evaluator only loads the repository's trusted module. Public sources are allowlisted and not executed. Input sizes, resource settings, subprocess output, and execution durations are bounded where implemented. The detailed report distinguishes active enforcement from documentation and experimental assumptions.

Source and model content may include misleading instructions; retrieval and model outputs have no authority to change application policy. Citation membership alone does not prove correctness. Never publish private production logs or credentials as example data. Report suspected security defects privately through the repository owner's GitHub contact channels; do not include working credentials in an issue.
