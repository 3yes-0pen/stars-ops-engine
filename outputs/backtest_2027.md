# Backtest 2027: results

Frozen thresholds (headline only): see docs/preregistration.md. Other populations have no threshold.

## Final rating

| Population | n | Exact | Within 0.5 | 4.0 agreement | Within 1e-6 of a boundary |
|---|---|---|---|---|---|
| Headline | 411 | 410 (99.8%) | 411 (100.0%) | 411 (100.0%) | 0 |
| Disaster-flagged | 92 | 92 (100.0%) | 92 (100.0%) | 92 (100.0%) | 0 |
| Puerto Rico-only | 5 | 1 (20.0%) | 5 (100.0%) | 5 (100.0%) | 0 |
| All-in | 508 | 503 (99.0%) | 508 (100.0%) | 508 (100.0%) | 0 |

Headline exact match: 410 of 411; bar 399; MET.
Headline 4.0 agreement: 411 of 411; bar 403; MET.

## Stage ladder (cumulative; each rung rounded with Table 22 for comparison)

The preregistration lists the with/without run (stage 2) and the 4+ rule (stage 5) separately. The rule needs both runs complete through reward factor and CAI, so they are reported together as the last rung.

| Rung | Headline exact | Headline 4.0 agreement | All-in exact |
|---|---|---|---|
| 1. Weighted mean (with improvement measures) | 275 (66.9%) | 363 (88.3%) | 329 (64.8%) |
| 2. + reward factor | 336 (81.8%) | 388 (94.4%) | 411 (80.9%) |
| 3. + CAI | 376 (91.5%) | 391 (95.1%) | 455 (89.6%) |
| 4. + with/without improvement runs and the 4+ rule (final) | 410 (99.8%) | 411 (100.0%) | 503 (99.0%) |

## Deviation D1: Puerto Rico-only rule (added after the first run)

Adherence measures D08-D10 get weight zero for Puerto Rico-only contracts (Tech Notes p. 137). The preregistered runs above have no special-casing; this section adds the documented rule.

| Population | Exact, preregistered | Exact, with D1 | 4.0 agreement, with D1 |
|---|---|---|---|
| Puerto Rico-only (n=5) | 1 | 5 | 5 |
| All-in (n=508) | 503 | 507 | 508 |

## Contracts where my rating differs from the published rating (5)

| Contract | Mine | Published | Raw | Run chosen | Group |
|---|---|---|---|---|---|
| H4004 | 4.0 | 4.5 | 4.046520 | with | PR-only |
| H4005 | 4.0 | 4.5 | 4.219330 | with | PR-only |
| H5141 | 4.5 | 5.0 | 4.373083 | with | headline |
| H5577 | 4.5 | 5.0 | 4.568742 | with | PR-only |
| H5774 | 4.5 | 5.0 | 4.693433 | with | PR-only |
