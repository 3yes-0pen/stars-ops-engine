STATUS: DRAFT, not frozen. Freeze commit comes before the full-population backtest.

# Pre-registration: 2027 overall-rating replication
Written: 2026-11-15. Repo state when written: <git rev-parse --short HEAD>.
Rule: no full-population match rate is computed before this file is committed.
(Developing and unit-testing on a handful of hand-checked contracts is allowed.)
Layer-0 (stars from scores) was exploratory; this plan covers what I have NOT run.

**Question:** Can my engine reproduce CMS's published 2027 overall rating from public inputs?
**Inputs (pinned, see provenance.md):** 2027 data-tables ZIP; the 2027 Tech Notes copy the reference tables were keyed from (cover-page date: <fill in>).
**Taken as given:** published measure stars (all CAHPS-type included); published C29/D04 stars.
**Population:** MA-PD contracts with a numeric published Overall (508 in the file before exclusions).
  TBD: confirm all 508 are rated-as MA-PD (Tech Notes Table 3).
**Exclusions (each reported separately; headline AND all-in results both reported):**
  - disaster-flagged: >= 25 on either disaster column (TBD: confirm the 0-100 scale)
  - Puerto Rico-only contracts
  - anything found later goes under Deviations, never silently dropped
**Stages (reported cumulatively):** (1) weighted mean of stars, shared measures counted once;
  (2) with / without improvement measures; (3) + reward factor; (4) + CAI; (5) 4+ comparison rule;
  (6) rounding (Table 22). Where the Tech Notes are silent I decide here: full float precision,
  Table 22 applied to unrounded scores, and I report how many contracts fall within 1e-6 of a boundary.
**Metrics:** exact = my rounded Overall equals the published one; within 0.5; 4.0 agreement =
  (mine >= 4.0) equals (published >= 4.0); error vs. distance to the nearest rounding boundary.
**Thresholds (headline population):** exact >= __%; 4.0 agreement >= __%.
  Why: <one sentence each>.
**If I miss:** investigate by stage and subgroup; do not change the threshold; report the miss.
**Case-study rule:** only contracts reproduced exactly and >= __ from a rounding boundary.
**Not tested here:** cost assumptions, drift forecasts, CAHPS recomputation.
**Results go in:** outputs/backtest_2027.md (this file stays frozen).

## Deviations
| Date | What changed | Why | Effect on results |
|---|---|---|---|