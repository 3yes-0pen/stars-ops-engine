# Data dictionary (2027 inputs)
Source: the 2027 data-tables ZIP (see provenance.md). Counts from docs/raw_profile_2027.md and the ingest output.

## Files the engine uses
| File | Grain / key | Rows | Header layout | Engine uses it for | Quirks (verified by) |
|---|---|---|---|---|---|
| Measure Data | one row per contract; CONTRACT_ID | 735 | title + 3 header rows; data from line 5 | scores for Layer-0 and distance to line | 45 measure columns; cp1252; text messages mixed with numbers (ingest) |
| Measure Stars | same | 735 | same | published stars (Layer-0 target, ladder input) | 1,018 improvement stars (C29/D04) have no score (ingest tokens) |
| Part C Cut Points | one row per star level x 32 measures | 5 | title + 3 header rows | star bands | bands stored as text (raw profile) |
| Part D Cut Points | MA-PD / PDP x 5 stars x 13 measures | 10 | same | star bands | PDP and MA-PD bands differ (ingest sample) |
| Summary Ratings | one row per contract; Contract Number | 735 | title + 1 header | backtest target, disaster %, population filter | 508 numeric Overall; utf-8 |
| CAI | one row per contract; Contract Number | 735 | title + 1 header | CAI category lookup | FAC is an integer or "N/A" (verify with SELECT DISTINCT) |

## In the ZIP, not used by the engine
- Domain Stars (735 rows): domain averages, not an input to the overall calculation (Tech Notes p. 11).
- High Performing (15) and Low Performing (4): lists derived from the ratings.
- Report Card Master Table (xlsx): not opened. Every CSV's title names it, so the CSVs look like views of it (inference).
- PQA value sets (4 xlsx: ADH, COB, Poly-ACH, SUPD): not opened. By filename, Part D measure specifications, not contract-level.

# Data dictionary (2026 inputs)
# Data dictionary (2025 inputs)

# Differences across years (observed; causes not assumed)
| | 2025 | 2026 | 2027 |
|---|---|---|---|
| Contracts (Measure Data) | 789 | 769 | 735 |
| Total columns in Measure Data | 47 | 50 | 50 |
| Summary Ratings | csv | xlsx only (dated July 22 2026; not opened) | csv |
| Disenrollment Reasons | csv | csv | absent |
| CAI contracts | 762 | 769 | 735 |
| Part D cut-point columns | 38 | 14 | 38 |