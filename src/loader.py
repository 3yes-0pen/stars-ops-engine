from pathlib import Path

import pandas as pd

from engine import cai_value, overall

ROOT = Path(__file__).resolve().parent.parent
INTERIM = ROOT / "data" / "interim"
REFERENCE = ROOT / "data" / "reference"

DISASTER_COLS = ["disaster_2024_pct", "disaster_2025_pct"]
DISASTER_THRESHOLD = 25  # percent of members in a FEMA Individual Assistance area (Tech Notes pp. 8-9)


def load_weights():
    """Measure code -> weight, from Attachment G."""
    table = pd.read_csv(REFERENCE / "weights_2027.csv")
    return dict(zip(table["measure_code"], table["weight"]))


def _threshold(table, which_table, run, percentile):
    row = table[(table["table"] == which_table)
                & (table["improvement"] == run)
                & (table["percentile"] == percentile)]
    if len(row) != 1:
        raise ValueError(f"expected one threshold for table {which_table}, {run}, {percentile}")
    return float(row["value"].iloc[0])


def load_thresholds():
    """{"with": {...}, "without": {...}}: reward-factor thresholds (Tables 8-9, pp. 16-17)."""
    table = pd.read_csv(REFERENCE / "rfactor_thresholds_2027.csv")
    return {
        run.lower(): {
            "mean_p65": _threshold(table, 8, run, 65),
            "mean_p85": _threshold(table, 8, run, 85),
            "var_p30": _threshold(table, 9, run, 30),
            "var_p70": _threshold(table, 9, run, 70),
        }
        for run in ("With", "Without")
    }


def load_contracts():
    """One row per contract with a numeric Overall, with the flags that define the population."""
    summary = pd.read_parquet(INTERIM / "summary_2027.parquet")
    cai = pd.read_parquet(INTERIM / "cai_2027.parquet")[["contract_id", "puerto_rico_only", "fac_overall"]]
    d = summary.merge(cai, on="contract_id", how="left")
    d = d[d["overall"].notna()].copy()
    d["flagged"] = d[DISASTER_COLS].max(axis=1) >= DISASTER_THRESHOLD
    d["pr_only"] = d["puerto_rico_only"].astype(str).str.strip().str.lower().eq("yes")
    d["headline"] = ~(d["flagged"] | d["pr_only"])
    return d.set_index("contract_id")


def load_stars():
    """Contract id -> {measure code -> published star (NaN if unrated)}."""
    facts = pd.read_parquet(INTERIM / "fact_measure_2027.parquet")[["contract_id", "measure_code", "star"]]
    return {cid: dict(zip(g["measure_code"], g["star"])) for cid, g in facts.groupby("contract_id")}


def run_contract(contract_id, contracts, stars, weights, thresholds):
    """Run the engine for one contract; returns overall()'s result."""
    cai = cai_value(contracts.loc[contract_id, "fac_overall"])
    return overall(stars[contract_id], weights, thresholds, cai)


def run_all(contracts, stars, weights, thresholds, ids):
    """Run the engine over many contracts. One row per contract, my results only (no published rating)."""
    rows = []
    for cid in ids:
        res = run_contract(cid, contracts, stars, weights, thresholds)
        used = res[res["chosen"]]
        rows.append({"contract_id": cid, "rating": res["rating"], "raw": res["raw"],
                     "chosen": res["chosen"], "r": used["r"], "mean": used["mean"]})
    return pd.DataFrame(rows).set_index("contract_id")