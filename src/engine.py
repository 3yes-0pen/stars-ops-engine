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