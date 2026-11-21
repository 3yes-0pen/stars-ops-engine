Status vocabulary: Verified (data) · Verified (document) · Secondary source · Hypothesis · Pending · Unknown
Page numbers are the printed footer number (PDF page = printed + 9).

| ID | Claim | Evidence | Source | Status | Checked |
|---|---|---|---|---|---|
| T1 | My copy of the 2027 Tech Notes is the 09/30/2026 version (SHA-256 93c12ef7…). | Cover page and footer | raw/tech_notes/ file | Verified (document) | 2026-11-16 |
| T2 | A later 11/04/2026 version exists, with minor changes to Complaints details and Attachment L. | My earlier read of the CMS page | Claude's summary | Secondary source (verify by downloading and comparing the change log) | 2026-11-16 |
| T3 | Summary and overall ratings are the weight-times-star sum divided by the sum of weights of rated measures; unrated measures are excluded. | p. 12 | 2027 Tech Notes | Verified (document) | 2026-11-16 |
| T4 | Improvement measures (C29/D04) are not counted toward the minimum number of rated measures. | p. 12 | 2027 Tech Notes | Verified (document) | 2026-11-16 |
| T5 | The minimum number of rated measures is half the required count for the organization type, rounded to a whole number if odd. | p. 13 | 2027 Tech Notes | Verified (document) | 2026-11-16 |
| T6 | An MA-PD overall rating is a weighted average of Part C and Part D measure stars, using Attachment G weights. | p. 13 | 2027 Tech Notes | Verified (document) | 2026-11-16 |
| T7 | An MA-PD contract gets an overall rating only if it has both a Part C and a Part D summary rating. | p. 13 | 2027 Tech Notes | Verified (document) | 2026-11-16 |
| T8 | Only rated-as-MA-PD organization types receive an Overall rating (CCP, PFFS offering drugs, 1876 Cost offering drugs). | Table 3, p. 4 | 2027 Tech Notes | Verified (document) | 2026-11-17 |
| T9 | Contracts with 25%+ of members in a FEMA Individual Assistance area get the higher of the 2026 or 2027 measure stars, plus a with/without hold-harmless for new measures at the overall level. | pp. 8–9 | 2027 Tech Notes | Pending (open the pages and confirm) | |
| T10 | Appeals measures C30/C31 can receive scaled reductions when IRE data are incomplete. | p. 7 | 2027 Tech Notes | Pending (open the page and confirm) | |
| T11 | For Puerto Rico-only contracts, the adherence measure weights are set to zero. | Attachment G footnote (PDF p. 146) | 2027 Tech Notes | Pending (found by text search; open the page) | |
| T12 | Measures C27/D02 and C28/D03 are shared across Parts C and D and count once in the overall rating. | Page not yet located | 2027 Tech Notes | Pending | |
| T13 | Which measures count as "new" for the new-measures column of Tables 8–9 (three on p. 9, or four in the p. 2 list) is not yet settled. | pp. 2 and 9 | 2027 Tech Notes | Unknown | |
| E1 | Recomputing non-CAHPS stars from scores and cut points matches published stars for 99.2% of rows. | layer0.py output | data/interim parquet | Verified (data) | |
| E2 | Non-CAHPS star mismatches: 8 of 13,653 rows in unflagged contracts vs. 127 of 3,083 in disaster-flagged contracts. | diagnose_layer0_2027.txt | data/interim parquet | Verified (data) | |
| E3 | Disaster-flagged mismatches are probably published better-of-2026/2027 stars. Correlation only; consistent with T9. | diagnose_layer0_2027.txt | data and T9 | Hypothesis | |
| E4 | CAHPS-type stars (C03, C21–C26, D05, D06) match a cut-point recompute only 87.4% of the time. Expected, since CAHPS uses percentile and significance rules; I take published stars as given. | layer0.py output | data/interim parquet | Verified (data) | |
| E5 | C29/D04 improvement stars: the number in my Layer-0 output (1,018) cannot be recomputed because numeric improvement scores are not public. | layer0.py output | data/interim parquet | Verified (data); confirm what the 1,018 counts | |
| E6 | Appeals measures C30/C31 show large star gaps in Layer-0. Probably the scaled reductions in T10. | layer0.py output | data and T10 | Hypothesis | |
| E7 | The file has 735 contracts; 508 have a numeric Overall (490 Local CCP, 12 Regional CCP, 4 PFFS, 2 1876 Cost). | population.py, ingest.py | data/interim parquet | Verified (data) | 2026-11-17 |
| E8 | Disaster columns run 0–100 (min 0, max 100). Flagged (>=25 on either column): 92. Puerto Rico-only: 5. No overlap; headline population 411. | population.py | data/interim parquet | Verified (data) | 2026-11-17 |