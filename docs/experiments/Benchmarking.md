# Benchmarking and Regression

Reusable suites should use stable names and explicit versions, such as
`RUSSIAN_COPYWRITING_V1` or `CODE_GENERATION_V1`. Results from materially different
versions must not be treated as directly comparable without a limitation disclosure.

Regression runs are distinct experiments linked through events; previous scores are
never overwritten. Comparisons intersect shared metrics, preserve each normalized
result, report ties/missing values as no metric winner, and aggregate limitations.
