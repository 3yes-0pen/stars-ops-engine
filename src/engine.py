import math
from pathlib import Path

import pandas as pd

CAI_PATH = Path(__file__).resolve().parent.parent / "data" / "reference" / "cai_2027.csv"


def round_half(x):
    """Round a raw summary/overall score to the nearest half star (Table 22, p. 24)."""
    return math.floor(x * 2 + 0.5) / 2


def weighted_mean(stars, weights):
    """Sum of weight*star over the sum of weights, skipping missing stars (p. 12)."""
    top = 0.0
    bottom = 0.0
    for star, weight in zip(stars, weights):
        if pd.isna(star):
            continue
        top += weight * star
        bottom += weight
    if bottom == 0:
        raise ValueError("no rated measures")
    return top / bottom


def weighted_variance(stars, weights):
    """n * sum(w*(x - mean)^2) / ((n - 1) * sum(w)), rated measures only (Attachment H, p. 138)."""
    rated = [(s, w) for s, w in zip(stars, weights) if not pd.isna(s)]
    n = len(rated)
    if n < 2:
        raise ValueError("variance needs at least two rated measures")
    mean = weighted_mean(stars, weights)
    total_weight = sum(w for _, w in rated)
    spread = sum(w * (s - mean) ** 2 for s, w in rated)
    return n * spread / ((n - 1) * total_weight)


def reward_factor(mean, variance, mean_p65, mean_p85, var_p30, var_p70):
    """0.4, 0.3, 0.2, 0.1 or 0 from the variance and mean bands (p. 15)."""
    if variance >= var_p70 or mean < mean_p65:
        return 0.0
    low_variance = variance < var_p30
    if mean >= mean_p85:
        return 0.4 if low_variance else 0.3
    return 0.2 if low_variance else 0.1


def cai_value(category):
    """CAI for the overall rating, looked up in data/reference/cai_2027.csv (Table 12)."""
    if pd.isna(category):
        raise ValueError("missing CAI category")
    category = int(category)
    table = pd.read_csv(CAI_PATH)
    row = table[table["final_category"] == category]
    if len(row) != 1:
        raise ValueError(f"CAI category {category} not found exactly once")
    return float(row["cai_value"].iloc[0])


def _run(stars, weights, th, cai):
    """One pass: mean, variance, reward factor, CAI, rounding."""
    codes = [c for c in stars if c in weights]
    s = [stars[c] for c in codes]
    w = [weights[c] for c in codes]
    mean = weighted_mean(s, w)
    var = weighted_variance(s,w)
    r = reward_factor(mean, var, th["mean_p65"], th["mean_p85"], th["var_p30"], th["var_p70"])
    raw = mean + r + cai
    return {"mean": mean, "variance": var, "r": r, "raw": raw, "rating": round_half(raw)}


IMPROVEMENT = ("C29", "D04")
SHARED_DROPPED = ("D02", "D03")  # same data as C27/C28, counted once (Tech Notes p. 13)


def overall(stars, weights, thresholds, cai):
    """MA-PD overall rating for one contract (Tech Notes pp. 13-17).

    stars: dict of measure code -> published star (missing or NaN = unrated)
    weights: dict of measure code -> weight (Attachment G)
    thresholds: {"with": {...}, "without": {...}}, each holding
        mean_p65, mean_p85, var_p30, var_p70
    cai: the CAI value for this contract (already looked up)
    Returns a dict: rating, raw, chosen ("with" or "without"), plus both runs' details.
    """
    base = {c: v for c, v in stars.items() if c not in SHARED_DROPPED}
    without = _run({c: v for c, v in base.items() if c not in IMPROVEMENT}, weights, thresholds["without"], cai)
    with_ = _run(base, weights, thresholds["with"], cai)
    if without["rating"] >= 4 and with_["rating"] < without["rating"]:    # 4+ rule (p. 15).  
        chosen, final = "without", without
    else:
        chosen, final = "with", with_
    return {"rating": final["rating"], "raw": final["raw"], "chosen": chosen,
            "without": without, "with": with_}
