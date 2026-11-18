# Pre-registration: 2027 overall-rating replication
STATUS: FROZEN at git tag `prereg-frozen`. Written 2026-11-17. Repo state before this commit: <ef7651c>.
Rule: no full-population match rate is computed before this file is committed.
(Developing and unit-testing on a handful of hand-checked contracts is allowed.)
Layer-0 (stars from scores) was exploratory; this plan covers what I have NOT run.

**Question:** Can my engine reproduce CMS's published 2027 overall rating from public inputs?
**Inputs (pinned; see provenance.md):**
  - 2027 data-tables ZIP, SHA-256 2704032d3f72e71a763aac075a8449e382ca07834417b1da53995b70d54e9967
  - 2027 Tech Notes, cover-page date 09-30-2026, SHA-256 93c12ef74a70e026f09f707ed57feb4ba90f2ee8a5d3f15d3c612e36476b5f4c
  Reference tables are keyed from this Tech Notes copy. Any keying correction after freeze goes under Deviations.
**Taken as given:** published measure stars, including CAHPS-type and improvement-measure (C29/D04) stars.
**Population:** 508 contracts with a numeric published Overall (490 Local CCP, 12 Regional CCP, 4 PFFS,
  2 1876 Cost; counts from src/population.py). Per Table 3 (Tech Notes p. 4) only rated-as-MA-PD types
  receive an Overall, so all 508 are treated as MA-PD. Selection depends on CMS having published an Overall;
  contracts CMS did not rate are not tested.
**Exclusions (each reported separately; headline AND all-in results both reported):**
  - disaster-flagged: >= 25 on either disaster column (columns run 0-100; policy: Tech Notes pp. 8-9): 92
  - Puerto Rico-only: 5
  - no overlap; headline population = 411
  - All-in uses the same engine with no disaster or Puerto Rico special-casing. Special-case rules added later are logged under Deviations.
  - anything found later goes under Deviations, never silently dropped
**Stages (reported cumulatively):** (1) weighted mean of stars, shared measures counted once;
  (2) with / without improvement measures; (3) + reward factor; (4) + CAI; (5) 4+ comparison rule;
  (6) rounding (Table 22). Where the Tech Notes are silent I decide here: full float precision,
  Table 22 applied to unrounded scores, and I report how many contracts fall within 1e-6 of a boundary.
**Metrics:** exact = my rounded Overall equals the published one; within 0.5; 4.0 agreement =
  (mine >= 4.0) equals (published >= 4.0); error vs. distance to the nearest rounding boundary.
**Thresholds (headline population, n = 411):** exact match >= 97%; 4.0 agreement >= 98%
  (must be higher than exact, since exact match implies 4.0 agreement).
  Why (exact): Inputs are published and the procedure is deterministic, so a miss most likely means a
  misunderstood rule. I still allow up to 12 of 411 (>= 399 exact) for undocumented edge cases, like the
  8 unexplained Layer-0 star mismatches among unflagged contracts.
  Why (4.0): Case studies depend on the right side of the 4.0 line, so this bar is stricter: >= 403 of 411
  agree, at most 8 wrong calls.
**If I miss:** investigate by stage and subgroup; do not change the threshold; report the miss.
**Case-study rule:** reproduced exactly; unrounded score at least one star step on the contract's
  lowest-weight measure from a rounding boundary (robustness); and within 0.2 of 3.75 (relevance).
**Not tested here:** cost assumptions, drift forecasts, CAHPS recomputation.
**Results go in:** outputs/backtest_2027.md (this file stays frozen).