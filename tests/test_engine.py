import math

import pytest

from engine import (
    round_half,
    weighted_mean,
    weighted_variance,
    reward_factor,
    cai_value,
)

M65, M85 = 3.545455, 3.871795
V30, V70 = 1.036449, 1.378508


@pytest.mark.parametrize("raw, expected", [
    (0.0, 0.0), (0.249999, 0.0), (0.25, 0.5),
    (3.249999, 3.0), (3.25, 3.5),
    (3.749999, 3.5), (3.75, 4.0),
    (4.249999, 4.0), (4.25, 4.5),
    (4.749999, 4.5), (4.75, 5.0), (5.0, 5.0),
])
def test_round_half(raw, expected):
    assert round_half(raw) == expected


def test_weighted_mean():
    assert weighted_mean([4, 3, 5], [1, 3, 5]) == pytest.approx(38 / 9)


def test_weighted_mean_skips_missing():
    assert weighted_mean([4, math.nan, 5], [1, 3, 5]) == pytest.approx(29 / 6)


def test_variance_two_equal_weights():
    assert weighted_variance([5, 3], [1, 1]) == pytest.approx(2.0)


def test_variance_unequal_weights():
    assert weighted_variance([5, 2], [2, 1]) == pytest.approx(4.0)


def test_variance_all_equal_is_zero():
    assert weighted_variance([4, 4, 4], [1, 3, 5]) == pytest.approx(0.0)


def test_variance_ignores_missing():
    assert weighted_variance([5, 3, math.nan], [1, 1, 3]) == pytest.approx(2.0)


@pytest.mark.parametrize("mean, var, expected", [
    (4.0, 0.5, 0.4),            # low variance, mean >= 85th
    (4.0, 1.2, 0.3),            # medium variance, mean >= 85th
    (4.0, 1.5, 0.0),            # high variance is always 0
    (3.7, 0.5, 0.2),            # low variance, mean 65th-85th
    (3.7, 1.2, 0.1),            # medium variance, mean 65th-85th
    (3.7, 1.5, 0.0),
    (3.3, 0.5, 0.0),            # mean below 65th
    (3.3, 1.2, 0.0),
    (3.871795, 0.5, 0.4),       # exactly on the 85th: counts as high
    (3.871794, 0.5, 0.2),       # just below it
    (3.545455, 0.5, 0.2),       # exactly on the 65th
    (3.545454, 0.5, 0.0),       # just below it
    (4.0, 1.036449, 0.3),       # exactly on the 30th: medium
    (4.0, 1.036448, 0.4),       # just below it: low
    (4.0, 1.378508, 0.0),       # exactly on the 70th: high
    (4.0, 1.378507, 0.3),       # just below it: medium
])
def test_reward_factor(mean, var, expected):
    assert reward_factor(mean, var, M65, M85, V30, V70) == pytest.approx(expected)


def test_cai_value_first_and_last_category():
    assert cai_value(1) == pytest.approx(-0.069659)
    assert cai_value(7) == pytest.approx(0.108248)