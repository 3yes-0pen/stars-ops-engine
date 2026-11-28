import math

import pandas as pd

import loader as L
from engine import round_half

OUT = L.ROOT / "outputs" / "backtest_2027.md"
EXACT_BAR = 0.97  # frozen in docs/preregistration.md
FOUR_BAR = 0.98   # frozen in docs/preregistration.md


def metrics(d, rating):
    """Final-stage metrics from the preregistration. `rating` is the rating being tested."""
    n = len(d)
    steps = (d["raw"] - 0.25) / 0.5
    distance = (steps - steps.round()).abs() * 0.5  # distance from raw score to nearest rounding boundary
    return {
        "n": n,
        "exact": int((rating == d["overall"]).sum()),
        "within_half": int(((rating - d["overall"]).abs() <= 0.5).sum()),
        "four": int(((rating >= 4) == (d["overall"] >= 4)).sum()),
        "near_boundary": int((distance < 1e-6).sum()),
    }


def pct(k, n):
    return "n/a" if n == 0 else f"{100 * k / n:.1f}%"


def main():
    contracts = L.load_contracts()
    stars, weights, thresholds = L.load_stars(), L.load_weights(), L.load_thresholds()
    results = L.run_all(contracts, stars, weights, thresholds, contracts.index)
    d = results.join(contracts[["overall", "headline", "flagged", "pr_only"]])

    populations = [("Headline", d[d["headline"]]), ("Disaster-flagged", d[d["flagged"]]),
                   ("Puerto Rico-only", d[d["pr_only"]]), ("All-in", d)]
    head = metrics(populations[0][1], populations[0][1]["rating"])
    need_exact = math.ceil(EXACT_BAR * head["n"])
    need_four = math.ceil(FOUR_BAR * head["n"])

    lines = ["# Backtest 2027: results", "",
             "Frozen thresholds (headline only): see docs/preregistration.md. Other populations have no threshold.", "",
             "## Final rating", "",
             "| Population | n | Exact | Within 0.5 | 4.0 agreement | Within 1e-6 of a boundary |",
             "|---|---|---|---|---|---|"]
    for name, g in populations:
        m = metrics(g, g["rating"])
        lines.append(f"| {name} | {m['n']} | {m['exact']} ({pct(m['exact'], m['n'])}) | "
                     f"{m['within_half']} ({pct(m['within_half'], m['n'])}) | "
                     f"{m['four']} ({pct(m['four'], m['n'])}) | {m['near_boundary']} |")
    lines += ["",
              f"Headline exact match: {head['exact']} of {head['n']}; bar {need_exact}; "
              f"{'MET' if head['exact'] >= need_exact else 'MISSED'}.",
              f"Headline 4.0 agreement: {head['four']} of {head['n']}; bar {need_four}; "
              f"{'MET' if head['four'] >= need_four else 'MISSED'}.", ""]

    rungs = [("1. Weighted mean (with improvement measures)", d["mean_with"]),
             ("2. + reward factor", d["mean_with"] + d["r_with"]),
             ("3. + CAI", d["raw_with"])]
    lines += ["## Stage ladder (cumulative; each rung rounded with Table 22 for comparison)", "",
              "The preregistration lists the with/without run (stage 2) and the 4+ rule (stage 5) separately. "
              "The rule needs both runs complete through reward factor and CAI, so they are reported together as the last rung.", "",
              "| Rung | Headline exact | Headline 4.0 agreement | All-in exact |", "|---|---|---|---|"]
    head_d, head_idx = populations[0][1], populations[0][1].index
    for name, score in rungs + [("4. + with/without improvement runs and the 4+ rule (final)", d["raw"])]:
        rating = d["rating"] if name.startswith("4.") else score.map(round_half)
        hr, ar = rating.loc[head_idx], rating
        he = int((hr == head_d["overall"]).sum())
        hf = int(((hr >= 4) == (head_d["overall"] >= 4)).sum())
        ae = int((ar == d["overall"]).sum())
        lines.append(f"| {name} | {he} ({pct(he, len(head_d))}) | {hf} ({pct(hf, len(head_d))}) | {ae} ({pct(ae, len(d))}) |")

    d_pr = L.run_all(contracts, stars, weights, thresholds, contracts.index, pr_rule=True)
    d_pr = d_pr.join(contracts[["overall", "pr_only"]])
    lines += ["", "## Deviation D1: Puerto Rico-only rule (added after the first run)", "",
              "Adherence measures D08-D10 get weight zero for Puerto Rico-only contracts (Tech Notes p. 137). "
              "The preregistered runs above have no special-casing; this section adds the documented rule.", "",
              "| Population | Exact, preregistered | Exact, with D1 | 4.0 agreement, with D1 |", "|---|---|---|---|"]
    for name, mask in (("Puerto Rico-only", d["pr_only"]), ("All-in", d["overall"].notna())):
        g, gp = d[mask], d_pr[mask]
        e0, e1 = int((g["rating"] == g["overall"]).sum()), int((gp["rating"] == gp["overall"]).sum())
        f1 = int(((gp["rating"] >= 4) == (gp["overall"] >= 4)).sum())
        lines.append(f"| {name} (n={len(g)}) | {e0} | {e1} | {f1} |")
        
    misses = d[d["rating"] != d["overall"]].copy()
    misses["group"] = misses.apply(lambda r: "headline" if r["headline"] else ("disaster-flagged" if r["flagged"] else "PR-only"), axis=1)
    lines += ["", f"## Contracts where my rating differs from the published rating ({len(misses)})", "",
              "| Contract | Mine | Published | Raw | Run chosen | Group |", "|---|---|---|---|---|---|"]
    for cid, r in misses.iterrows():
        lines.append(f"| {cid} | {r['rating']} | {r['overall']} | {r['raw']:.6f} | {r['chosen']} | {r['group']} |")

    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text("\n".join(lines) + "\n")
    print("wrote", OUT)


if __name__ == "__main__":
    main()