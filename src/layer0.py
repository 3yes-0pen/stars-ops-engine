#!/usr/bin/env python3
"""layer0.py: recompute measure stars from published scores + cut-point bands; compare.
Usage: python src/layer0.py 2027   (run ingest.py first)
"""
import re
import sys
from pathlib import Path

import pandas as pd

INTERIM = Path("data/interim")
OP_RE = re.compile(r"(>=|<=|>|<)\s*(-?\d+(?:\.\d+)?)")
EQ_RE = re.compile(r"^\s*(-?\d+(?:\.\d+)?)\s*%?\s*$")
STAR_RE = re.compile(r"^\s*(\d)\s*star", re.I)


def parse_band(text):
    """'>= 63 % to < 70 %' -> (lo, lo_inclusive, hi, hi_inclusive); None if unparseable."""
    if not isinstance(text, str) or not text.strip():
        return None
    t = text.replace(",", "")
    ops = OP_RE.findall(t)
    if ops:
        lo = hi = None
        lo_i = hi_i = False
        for op, val in ops:
            v = float(val)
            if op in (">", ">="):
                lo, lo_i = v, op == ">="
            else:
                hi, hi_i = v, op == "<="
        return lo, lo_i, hi, hi_i
    m = EQ_RE.match(t)
    if m:
        v = float(m.group(1))
        return v, True, v, True          # bare number means "equals"
    return None


def in_band(x, b):
    lo, lo_i, hi, hi_i = b
    if lo is not None and not (x >= lo if lo_i else x > lo):
        return False
    if hi is not None and not (x <= hi if hi_i else x < hi):
        return False
    return True


def main(year):
    fact = pd.read_parquet(INTERIM / f"fact_measure_{year}.parquet")
    dimc = pd.read_parquet(INTERIM / f"dim_contract_{year}.parquet")[["contract_id", "organization_type"]]
    cuts = pd.read_parquet(INTERIM / f"cutpoint_raw_{year}.parquet")

    bands, texts, unparsed = {}, {}, {}
    for r in cuts.itertuples():
        m = STAR_RE.match(r.star_label_raw or "")
        if not m:
            continue
        star = int(m.group(1))
        key = (r.part, r.org_type if r.part == "D" else "ANY", r.measure_code)
        b = parse_band(r.cell_text)
        if b is None:
            unparsed[r.measure_code] = unparsed.get(r.measure_code, 0) + 1
            continue
        bands.setdefault(key, []).append((star, b))
        texts[(key, star)] = r.cell_text
    print(f"LAYER-0 {year}: parsed {sum(len(v) for v in bands.values())} bands; "
          f"unparsed cells by measure: {unparsed or 'none'}")

    df = fact.merge(dimc, on="contract_id", how="left")
    both = df[df["score"].notna() & df["star"].notna()].copy()
    both["pdp"] = both["organization_type"].fillna("").str.contains("PDP", case=False)
    both["decimals"] = (both["score_raw"].astype(str).str.extract(r"\.(\d+)")[0]
                        .str.len().fillna(0).astype(int))

    comp, why, key_of = [], [], []
    for r in both.itertuples():
        key = (("C", "ANY", r.measure_code) if r.measure_code.startswith("C")
               else ("D", "PDP" if r.pdp else "MA-PD", r.measure_code))
        key_of.append(key)
        opts = bands.get(key)
        if not opts:
            comp.append(None); why.append("no_bands"); continue
        hits = [s for s, b in opts if in_band(r.score, b)]
        if len(hits) == 1:
            comp.append(hits[0]); why.append("ok")
        else:
            comp.append(None); why.append("no_band_matched" if not hits else "multi_band")
    both["computed_star"] = pd.to_numeric(pd.Series(comp, index=both.index))
    both["reason"] = why
    both["match"] = both["computed_star"] == both["star"]

    n, k = len(both), int(both["match"].sum())
    print(f"\nOVERALL: {k} of {n} match ({k / n:.2%})")
    print("reasons:", both["reason"].value_counts().to_dict())
    miss = both[~both["match"] & both["computed_star"].notna()]
    print("size of star difference when mismatched:",
          (miss["star"] - miss["computed_star"]).abs().value_counts().to_dict())

    g = both.groupby("measure_code").agg(n=("match", "size"), matched=("match", "sum"),
                                         max_decimals=("decimals", "max"))
    g["rate"] = (g["matched"] / g["n"]).round(4)
    names = fact.drop_duplicates("measure_code").set_index("measure_code")["measure_name"]
    g["measure"] = names.reindex(g.index).str[:38]
    print("\nBY MEASURE (lowest match rate first)")
    print(g.sort_values("rate").to_string())

    print("\nSTAR BUT NO SCORE (cannot be recomputed), by measure:")
    print(df[df["star"].notna() & df["score"].isna()].groupby("measure_code").size()
          .sort_values(ascending=False).head(8).to_dict())
    print("SCORE BUT NO STAR, by measure:")
    print(df[df["score"].notna() & df["star"].isna()].groupby("measure_code").size()
          .sort_values(ascending=False).head(8).to_dict())
    iss = df[df["score_message"].fillna("").str.startswith("CMS identified")]
    print(f"CMS-identified-issue cells: {len(iss)}; star values: {iss['star'].value_counts(dropna=False).to_dict()}")

    both["published_band"] = [texts.get((k_, int(s))) for k_, s in zip(key_of, both["star"])]
    out = both[~both["match"]][["contract_id", "measure_code", "score_raw", "star",
                                "computed_star", "reason", "published_band"]]
    out.to_parquet(INTERIM / f"layer0_mismatches_{year}.parquet", index=False)
    print(f"\nMISMATCH SAMPLE (full list in layer0_mismatches_{year}.parquet)")
    print(out.head(15).to_string(index=False))


if __name__ == "__main__":
    main(int(sys.argv[1]) if len(sys.argv) > 1 else 2027)