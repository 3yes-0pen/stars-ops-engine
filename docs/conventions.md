# Conventions (2027 pipeline)
1. Keys: `star_year` (int), `contract_id` (trimmed text), `measure_code` (e.g. C01). A stable `measure_key` is added only when a second year is loaded.
2. Unit of analysis: MA-PD contracts with a numeric published Overall. (508 in 2027). Per Table 3 (Tech Notes p. 4), only rated-as-MA-PD organization types receive an Overall, so these are treated as MA-PD. Per p. 13, an Overall also requires both a Part C and a Part D summary rating.
3. Missing values: numeric column NULL, text in `*_message`, original text in `*_raw`. Tokens seen: "Plan too new to be measured", "Not enough data available", "Plan not required to report measure", "Plan too small to be measured", "No data available", "Medicare shows only a Star Rating for this topic", "CMS identified issues with this plan's data", "Benefit not offered by plan" (stars only), "Not Applicable" (Summary), "N/A" (CAI).
4. Scale: scores as published with `%` and commas stripped. TBD: confirm each measure's scale.
5. Direction: derived from band operators (a 5-star band with `<=` means lower is better), then spot-checked on two measures against Attachment K.
6. Boundaries: each band's operator decides inclusion.
7. Used as given: CAHPS-type stars (C03, C21–C26, D05, D06) and improvement stars (C29, D04).
8. Disaster flag: 25 or more on either disaster column in Summary Ratings (0–100 scale confirmed; policy pp. 8–9). A simplification, since the policy differs by data source.
9. Encoding fallback: utf-8-sig, cp1252, latin-1. Strings trimmed.
10. Vintage: the Oct 8 2026 CSVs are "as published" for 2027.