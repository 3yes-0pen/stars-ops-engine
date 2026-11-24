import math
import pandas as pd


def round_half(x):
    """Round a raw summary/overall score to the nearest half star (Table 22, p. 24)."""
    return math.floor( ______ ) / 2

def weighted_mean(stars, weights):
    """Sum of weight*star over the sum of weights, skipping missing stars (p. 12)."""
    raise NotImplementedError


def weighted_variance(stars, weights):
    """n * sum(w*(x - mean)^2) / ((n - 1) * sum(w)), rated measures only (Attachment H, p. 138)."""
    raise NotImplementedError


def reward_factor(mean, variance, mean_p65, mean_p85, var_p30, var_p70):
    """0.4, 0.3, 0.2, 0.1 or 0 from the variance and mean bands (p. 15)."""
    raise NotImplementedError


def cai_value(category):
    """CAI for the overall rating, looked up in data/reference/cai_2027.csv (Table 12)."""
    raise NotImplementedError