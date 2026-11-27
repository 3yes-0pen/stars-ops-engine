import pytest

from loader import load_contracts, load_stars, load_thresholds, load_weights


def test_population_counts_match_the_preregistration():
    c = load_contracts()
    assert len(c) == 508
    assert int(c["flagged"].sum()) == 92
    assert int(c["pr_only"].sum()) == 5
    assert int(c["headline"].sum()) == 411


def test_weights_cover_all_45_measures():
    w = load_weights()
    assert len(w) == 45
    assert w["C29"] == 5 and w["D04"] == 5


def test_thresholds_match_tables_8_and_9():
    t = load_thresholds()
    assert t["with"]["mean_p85"] == pytest.approx(3.871795)
    assert t["without"]["mean_p65"] == pytest.approx(3.602941)
    assert t["with"]["var_p70"] == pytest.approx(1.378508)
    assert t["without"]["var_p30"] == pytest.approx(0.999552)


def test_every_rated_contract_has_stars_and_a_cai_category():
    c = load_contracts()
    s = load_stars()
    assert set(c.index) <= set(s)
    assert c["fac_overall"].notna().all()