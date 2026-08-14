# Experiment Model

The domain contains experiments, protocols, test cases, environments, itemized cost,
metrics, rubrics, evidence references, normalized results, comparisons, and versioned
history. Enums define lifecycle, approval, risk, confidence, experiment types, and
evidence categories. Required protocol fields are validated before persistence.

The environment records the dated tool/model/API/browser versions, tier, region,
language, dependencies, inputs, and exact settings. Test-case repeat counts must sum
to the declared protocol sample size.
