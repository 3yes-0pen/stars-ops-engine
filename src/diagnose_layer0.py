#!/usr/bin/env python3
"""diagnose_layer0.py: why do published stars differ from score + cut-point bands?

Readable report. Prints to the terminal AND saves a copy to docs/diagnose_layer0_<year>.txt
Usage: python src/diagnose_layer0.py 2027      (run ingest.py and layer0.py first)
"""
import re
import sys
import textwrap
from pathlib import Path

import pandas as pd

from layer0 import INTERIM, STAR_RE, in_band, parse_band

CAHPS = {"C03", "C21", "C22", "C23", "C24", "C25", "C26", "D05", "D06"}
APPEALS = {"C30", "C31"}
DISASTER_THRESHOLD = 25   # Tech Notes: "25% or more" of members affected. ASSUMES the pct columns are 0-100.
WIDTH = 78

LINES = []


def out(s=""):
    print(s)
    LINES.append(s)


def pct(x):
    return "-" if pd.isna(x) else f"{x:.1%}"


def title(n, text):
    if LINES and LINES[-1] != "":
        out()
    out("=" * WIDTH)
    out(f"{n}. {text}")
    out("=" * WIDTH)


def note(text):
    out()
    out(textwrap.fill("How to read: " + text, width=WIDTH, initial_indent="   ", subsequent_indent="      "))
    out()


def show(headers, rows, align=None):
    if not rows:
        out("   (none)")
        return
    cols = list(zip(*([headers] + [[str(c) for c in r] for r in rows])))
    widths = [max(len(str(c)) for c in col) for col in cols]
    align = align or ["<"] + [">"] * (len(headers) - 1)

    def fmt(r):
        return "   " + "  ".join(f"{str(v):{a}{w}}" for v, a, w in zip(r, align, widths))

    out(fmt(headers))
    out("   " + "  ".join("-" * w for w in widths))
    for r in rows:
        out(fmt(r))


def nums(t):
    return [float(x) for x in re.findall(r"-?\d+(?:\.\d+)?", (t or "").replace(",", ""))]


def group_stats(d):
    n = len(d)
    k = int(d["match"].sum())
    return n, k, n - k, (k / n if n else float("nan"))


def main(year):
    fact = pd.read_parquet(INTERIM / f"fact_measure_{year}.parquet")
    dimc = pd.read_parquet(INTERIM / f"dim_contract_{year}.parquet")[["contract_id", "organization_type"]]
    summ = pd.read_parquet(INTERIM / f"summary_{year}.parquet")
    cuts = pd.read_parquet(INTERIM / f"cutpoint_raw_{year}.parquet")
    dcols = [c for c in summ.columns if re.match(r"disaster_\d{4}_pct$", c)]
    names = fact.drop_duplicates("measure_code").set_index("measure_code")["measure_name"]

    bands, text = {}, {}
    for r in cuts.itertuples():
        m, b = STAR_RE.match(r.star_label_raw or ""), parse_band(r.cell_text)
        if m and b:
            key = (r.part, r.org_type if r.part == "D" else "ANY", r.measure_code)
            bands.setdefault(key, []).append((int(m.group(1)), b))
            text[(key, int(m.group(1)))] = r.cell_text

    df = fact.merge(dimc, on="contract_id").merge(summ[["contract_id"] + dcols], on="contract_id", how="left")
    df = df[df["score"].notna() & df["star"].notna()].copy()
    comp, edge = [], []
    for r in df.itertuples():
        pdp = "PDP" in str(r.organization_type).upper()
        key = ("C", "ANY", r.measure_code) if r.measure_code.startswith("C") else (
            "D", "PDP" if pdp else "MA-PD", r.measure_code)
        hits = [s for s, b in bands.get(key, []) if in_band(r.score, b)]
        cs = hits[0] if len(hits) == 1 else None
        comp.append(cs)
        edge.append(cs is not None and r.score in nums(text.get((key, cs))))
    df["computed"] = pd.to_numeric(pd.Series(comp, index=df.index))
    df["on_edge"] = edge
    df["match"] = df["computed"] == df["star"]
    df["group"] = ["CAHPS-type" if c in CAHPS else "Other measures" for c in df["measure_code"]]
    df["flagged"] = (df[dcols].max(axis=1) >= DISASTER_THRESHOLD) if dcols else False
    df["gap"] = df["star"] - df["computed"]          # published minus computed
    mis = df[~df["match"] & df["computed"].notna()].copy()
    groups = ["CAHPS-type", "Other measures"]

    out(f"DIAGNOSE {year}: why do published stars differ from score + cut-point bands?")
    out(f"   Rows tested (numeric score AND published star): {len(df):,}")
    n, k, bad, r = group_stats(df)
    out(f"   Matched: {k:,} ({pct(r)})   Mismatched: {bad:,}")
    out(f"   Rows with no single band found (should be 0): {int(df['computed'].isna().sum())}")
    fl = int(df.drop_duplicates("contract_id")["flagged"].sum())
    out(f"   Contracts flagged as disaster-affected (>= {DISASTER_THRESHOLD}% on either column): {fl} "
        f"of {df['contract_id'].nunique()} tested")
    for c in dcols:
        out(f"   Check the scale: {c} runs {summ[c].min():g} to {summ[c].max():g} (assumed to be percent, 0-100)")
    out(f"   'CAHPS-type' = {', '.join(sorted(CAHPS))}")

    title(1, "HOW OFTEN DOES THE RECOMPUTED STAR MATCH THE PUBLISHED STAR?")
    show(["Group", "Rows", "Matched", "Mismatched", "Match rate"],
         [[g, f"{group_stats(df[df['group'] == g])[0]:,}", f"{group_stats(df[df['group'] == g])[1]:,}",
           f"{group_stats(df[df['group'] == g])[2]:,}", pct(group_stats(df[df['group'] == g])[3])] for g in groups])
    note("CAHPS-type stars come from percentile ranks and significance tests (Tech Notes), so a score alone "
         "cannot fully determine them. Judge your cut-point logic on 'Other measures'.")

    title(2, "DO MISMATCHES CLUSTER IN DISASTER-FLAGGED CONTRACTS?")
    rows = []
    for g in groups:
        for flag, label in ((False, "not flagged"), (True, "flagged")):
            s = group_stats(df[(df["group"] == g) & (df["flagged"] == flag)])
            rows.append([g, label, f"{s[0]:,}", f"{s[2]:,}", pct(s[3])])
    show(["Group", "Contract", "Rows", "Mismatched", "Match rate"], rows, ["<", "<", ">", ">", ">"])
    tot = int((mis["group"] == "Other measures").sum())
    inflag = int(((mis["group"] == "Other measures") & mis["flagged"]).sum())
    note(f"Of {tot} mismatches in 'Other measures', {inflag} are in flagged contracts. That is a correlation; "
         "the mechanism (published = better of this year and last year) still needs testing with 2026 data.")

    title(3, "WHICH WAY DO THE MISMATCHES GO?")
    rows = []
    for g in groups:
        d = mis[mis["group"] == g]
        hi, lo = int((d["gap"] > 0).sum()), int((d["gap"] < 0).sum())
        t = hi + lo
        rows.append([g, f"{t:,}", f"{hi:,} ({pct(hi / t) if t else '-'})", f"{lo:,} ({pct(lo / t) if t else '-'})"])
    show(["Group", "Mismatches", "Published HIGHER", "Published LOWER"], rows)
    note("Opposite directions in the two groups point to different mechanisms. 'Higher' fits a better-of "
         "disaster rule; 'lower' fits extra conditions that withhold stars.")

    title(4, "HOW BIG ARE THE MISMATCHES? (stars apart)")
    rows = []
    for g in groups:
        d = mis[mis["group"] == g]["gap"].abs()
        rows.append([g, f"{int((d == 1).sum()):,}", f"{int((d == 2).sum()):,}", f"{int((d >= 3).sum()):,}"])
    show(["Group", "1 star", "2 stars", "3+ stars"], rows)
    note("1-star gaps can come from rounding or edge cases. Gaps of 2+ stars need a rule, not rounding.")

    title(5, "WHICH MEASURES HAVE THE MOST MISMATCHES? (Other measures only)")
    d = mis[mis["group"] == "Other measures"]
    rows = []
    for code, g in d.groupby("measure_code"):
        rows.append([code, str(names.get(code, ""))[:34], int(len(g)), int(g["flagged"].sum()), int((~g["flagged"]).sum())])
    rows.sort(key=lambda r: -r[2])
    show(["Code", "Measure", "Mismatches", "Flagged", "Not flagged"],
         [[a, b, f"{c:,}", f"{e:,}", f"{f:,}"] for a, b, c, e, f in rows[:12]], ["<", "<", ">", ">", ">"])
    note("A measure whose mismatches are mostly NOT flagged points to something other than the disaster rule. "
         "Appeals measures (C30, C31) are one candidate (scaled reductions in the Tech Notes).")

    title(6, "LARGEST DIFFERENCES (2+ stars), look at these by hand first")
    big = mis[mis["gap"].abs() >= 2].sort_values(["contract_id", "measure_code"])
    show(["Contract", "Measure", "Score", "Published", "Computed", "Gap", "Flagged"],
         [[r.contract_id, r.measure_code, r.score_raw, f"{r.star:g}", f"{r.computed:g}", f"{r.gap:+g}",
           "yes" if r.flagged else "no"] for r in big.itertuples()],
         ["<", "<", ">", ">", ">", ">", "<"])
    note("Gap = published minus computed. The same contract showing the same gap on both appeals measures "
         "would fit a shared reduction.")

    title(7, "OTHER-MEASURE MISMATCHES IN CONTRACTS NOT FLAGGED AS DISASTER-AFFECTED")
    un = mis[(mis["group"] == "Other measures") & ~mis["flagged"]].sort_values(["measure_code", "contract_id"])
    out(f"   {len(un)} rows (listing up to 25)")
    out()
    show(["Contract", "Measure", "Score", "Published", "Computed", "Gap"],
         [[r.contract_id, r.measure_code, r.score_raw, f"{r.star:g}", f"{r.computed:g}", f"{r.gap:+g}"]
          for r in un.head(25).itertuples()], ["<", "<", ">", ">", ">", ">"])
    note("These are the cases the disaster flag does not explain. Count them by measure before guessing a cause.")

    title(8, "CAUTION: SCORE EXACTLY ON A BAND EDGE")
    rows = []
    for g in groups:
        for e, label in ((False, "not on edge"), (True, "on edge")):
            s = group_stats(df[(df["group"] == g) & (df["on_edge"] == e)])
            rows.append([g, label, f"{s[0]:,}", pct(s[3])])
    show(["Group", "Score", "Rows", "Match rate"], rows, ["<", "<", ">", ">"])
    note("Whole-number scores land on band edges often, so being on an edge explains little on its own.")

    Path("docs").mkdir(exist_ok=True)
    path = Path("docs") / f"diagnose_layer0_{year}.txt"
    path.write_text("\n".join(LINES) + "\n", encoding="utf-8")
    out(f"Saved a copy to {path}")


if __name__ == "__main__":
    main(int(sys.argv[1]) if len(sys.argv) > 1 else 2027)