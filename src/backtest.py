import math

import pandas as pd

import loader as L

OUT = L.ROOT / "outputs" / "backtest_2027.md"
EXACT_BAR = 0.97  # frozen in docs/preregistration.md
FOUR_BAR = 0.98   # frozen in docs/preregistration.md


def metrics(d):
    """Final-stage metrics from the preregistration, for one set of contracts."""
    n = len(d)
    steps = (d["raw"] - 0.25) / 0.5
    distance = (steps - steps.round()).abs() * 0.5  # distance from raw score to nearest rounding boundary
    return {
        "n": n,
        "exact": int((d["rating"] == d["overall"]).sum()),
        "within_half": int(((d["rating"] - d["overall"]).abs() <= 0.5).sum()),
        "four": int(((d["rating"] >= 4) == (d["overall"] >= 4)).sum()),
        "near_boundary": int((distance < 1e-6).sum()),
    }


def pct(k, n):
    return f"{100 * k / n:.1f}%"


def main():
    contracts = L.load_contracts()
    stars, weights, thresholds = L.load_stars(), L.load_weights(), L.load_thresholds()
    results = L.run_all(contracts, stars, weights, thresholds, contracts.index)
    d = results.join(contracts[["overall", "headline"]])

    head, allin = metrics(d[d["headline"]]), metrics(d)
    need_exact = math.ceil(EXACT_BAR * head["n"])
    need_four = math.ceil(FOUR_BAR * head["n"])

    lines = ["# Backtest 2027: final-stage results", "",
             "Frozen thresholds (headline only): see docs/preregistration.md. All-in has no threshold.", "",
             "| Population | n | Exact | Within 0.5 | 4.0 agreement | Within 1e-6 of a boundary |",
             "|---|---|---|---|---|---|"]
    for name, m in (("Headline", head), ("All-in", allin)):
        lines.append(f"| {name} | {m['n']} | {m['exact']} ({pct(m['exact'], m['n'])}) | "
                     f"{m['within_half']} ({pct(m['within_half'], m['n'])}) | "
                     f"{m['four']} ({pct(m['four'], m['n'])}) | {m['near_boundary']} |")
    lines += ["",
              f"Headline exact match: {head['exact']} of {head['n']}; bar {need_exact}; "
              f"{'MET' if head['exact'] >= need_exact else 'MISSED'}.",
              f"Headline 4.0 agreement: {head['four']} of {head['n']}; bar {need_four}; "
              f"{'MET' if head['four'] >= need_four else 'MISSED'}.", ""]

    misses = d[d["rating"] != d["overall"]].copy()
    misses["headline"] = misses["headline"].map({True: "yes", False: "no"})
    lines += [f"## Contracts where my rating differs from the published rating ({len(misses)})", "",
              "| Contract | Mine | Published | Raw | Run chosen | Headline |", "|---|---|---|---|---|---|"]
    for cid, r in misses.iterrows():
        lines.append(f"| {cid} | {r['rating']} | {r['overall']} | {r['raw']:.6f} | {r['chosen']} | {r['headline']} |")

    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text("\n".join(lines) + "\n")
    print("wrote", OUT)
    print(*lines[:12], sep="\n")


if __name__ == "__main__":
    main()