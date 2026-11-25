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
| T9 | Contracts with 25%+ of members in a FEMA Individual Assistance area get the higher of the 2026 or 2027 measure stars, plus a with/without hold-harmless for new measures at the overall level. | p. 8 and 9 | 2027 Tech Notes | Verified (document) | 2026-11-23 |
| T10 | Appeals measures C30/C31 can receive scaled reductions when IRE data are incomplete. | p. 7 | 2027 Tech Notes | Verified (document) | 2026-11-23 |
| T11 | For Puerto Rico-only contracts, the adherence measure weights are set to zero. | Attachment G footnote on p. 137 | 2027 Tech Notes | Verified (document) | 2026-11-23 |
| T12 | Measures C27/D02 and C28/D03 are shared across Parts C and D and count once in the overall rating. | Page 13 and Attachment G (p. 136) | 2027 Tech Notes | Verified (document) | 2026-11-23 |
| T13 | Which measures count as "new": p. 2 lists four measures as new with weight 1 (FSA, Colorectal respecified, COB, Poly-ACH); p. 9 says three (omits Colorectal)| p. 2 and 9 | 2027 Tech Notes | Verified (document) | 2026-11-23 |
| T14 | MA-PD weights: improvement measures 5, outcome and intermediate outcome 3, experience/complaints and access 2, process 1. | Attachment G, p. 136–137 | 2027 Tech Notes | Verified (document) | 2026-11-21 |
| T15 | Reward factor is 0.4, 0.3, 0.2, 0.1 or 0, set by variance band (low below 30th percentile, medium 30th to 70th, high 70th and above) and mean percentile band (85th and above, or 65th to 85th); thresholds are in Tables 8–9. | p. 15–17 | 2027 Tech Notes | Verified (document) | 2026-11-21 |
| T16 | The CAI for the overall rating is one value per final category (1–7), rising from −0.069659 to 0.108248. | Table 12, p. 19 | 2027 Tech Notes | Verified (document) | 2026-11-21 |
| T17 | An MA-PD overall is computed with and without both improvement measures, each run including reward factor and CAI. If the without result is 4 or more stars and the with result is lower, the without result is used; otherwise the with result. | p. 15, 17 | 2027 Tech Notes | Verified (document) | 2026-11-21 |
| T18 | CMS says summary and overall ratings use at least six decimal digits of precision, and that its calculations cannot be replicated exactly (published data use different rounding; some contracts are excluded from public data). | p. 24 | 2027 Tech Notes | Verified (document) | 2026-11-23 |
| E1 | Recomputing non-CAHPS stars from scores and cut points matches published stars for 99.2% of rows. | layer0.py output | data/interim parquet | Verified (data) | 2026-11-23 |
| E2 | Non-CAHPS star mismatches: 8 of 13,653 rows in unflagged contracts vs. 127 of 3,083 in disaster-flagged contracts. | diagnose_layer0_2027.txt | data/interim parquet | Verified (data) | 2026-11-23 |
| E3 | Disaster-flagged mismatches are probably published better-of-2026/2027 stars. Correlation only; consistent with T9. | diagnose_layer0_2027.txt | data and T9 | Hypothesis | 2026-11-23 |
| E4 | CAHPS-type stars (C03, C21–C26, D05, D06) match a cut-point recompute only 87.4% of the time. Expected, since CAHPS uses percentile and significance rules; I take published stars as given. | layer0.py output | data/interim parquet | Verified (data) | 2026-11-23 |
| E5 | For C29/D04, the public file gives a published star and no numeric score (the score cell reads "Medicare shows only a Star Rating for this topic"): 1,018 contract-measure rows (D04 556, C29 462). I take these stars as given. | ingest output (non-numeric tokens; star-but-no-score tally) | data/interim parquet | Verified (data) | 2026-11-23 |
| E6 | Appeals measures C30/C31 show large star gaps in Layer-0. Probably the scaled reductions in T10. | layer0.py output | data and T10 | Hypothesis | 2026-11-23 |
| E7 | The file has 735 contracts; 508 have a numeric Overall (490 Local CCP, 12 Regional CCP, 4 PFFS, 2 1876 Cost). | population.py, ingest.py | data/interim parquet | Verified (data) | 2026-11-17 |
| E8 | Disaster columns run 0–100 (min 0, max 100). Flagged (>=25 on either column): 92. Puerto Rico-only: 5. No overlap; headline population 411. | population.py | data/interim parquet | Verified (data) | 2026-11-17 |