# Paper Consistency Report

Status: **PASS**

- citations used / BibTeX entries: `19/19`
- figure assets resolved: `3/3`
- LaTeX labels / references: `9/4`
- registered numeric claims checked: `11`

## Numeric Claims

| claim | source | field | actual | source_match | manuscript_token | token_present |
| --- | --- | --- | --- | --- | --- | --- |
| classic selection speedup vs iterative surrogate | experiments/output/submission_main_table/one_shot_operator_summary.csv | median_selection_speedup_vs_iterative | 40.06223179680868 | True | $40.1\times$ | True |
| classic full graph speedup vs iterative surrogate | experiments/output/submission_main_table/one_shot_operator_summary.csv | median_total_speedup_vs_iterative | 7.771528039228121 | True | $7.77\times$ | True |
| classic selection speedup vs exact search | experiments/output/submission_main_table/one_shot_operator_summary.csv | median_selection_speedup_vs_exact_search | 157.24872488876508 | True | $157\times$ | True |
| classic full graph speedup vs exact search | experiments/output/submission_main_table/one_shot_operator_summary.csv | median_total_speedup_vs_exact_search | 22.86472609140089 | True | $22.9\times$ | True |
| held-out random extraction speedup | experiments/output/submission_main_table/one_shot_operator_summary.csv | median_selection_speedup_vs_iterative | 369.51494874470774 | True | $369.5\times$ | True |
| held-out random full graph speedup | experiments/output/submission_main_table/one_shot_operator_summary.csv | median_total_speedup_vs_iterative | 12.941598709270796 | True | $12.94\times$ | True |
| XL state compression | experiments/output/submission_main_table/one_shot_operator_summary.csv | median_state_compression | 192.0 | True | $192\times$ | True |
| XL total speedup vs sparse VI | experiments/output/submission_main_table/one_shot_operator_summary.csv | median_total_speedup_vs_sparse_vi | 0.0038629720190769294 | True | $0.00386\times$ | True |
| iterative RD graph planning speedup | experiments/output/submission_main_table/runtime_by_boundary_selector.csv | strong_planner_median_planning_speedup | 29.58248878740116 | True | $29.6\times$ | True |
| iterative RD single-task total speedup | experiments/output/submission_main_table/runtime_by_boundary_selector.csv | strong_planner_median_total_speedup | 0.0011552957727785707 | True | $0.00116\times$ | True |
| reranker/reference exact McNemar p-value | experiments/output/boundary_constraint_pairing/paired_summary.csv | exact_mcnemar_pvalue | 0.06391465663909912 | True | $p=0.0639$ | True |

## Errors

- none

## Warnings

- none
