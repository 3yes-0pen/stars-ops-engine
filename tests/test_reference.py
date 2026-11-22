from pathlib import Path
import pandas as pd
import pytest

REF = Path("data/reference")

def load(name):
    return pd.read_csv(REF / name)

@pytest.mark.parametrize("name", ["weights_2027.csv", "rfactor_thresholds_2027.csv", "cai_2027.csv"])
def test_every_row_has_a_source(name):
    df = load(name)
    assert df["source_doc"].notna().all() and df["source_page"].notna().all()

def test_weights_cover_all_45_measures_once():
    w = load("weights_2027.csv")
    expected = [f"C{i:02d}" for i in range(1, 33)] + [f"D{i:02d}" for i in range(1, 14)]
    assert sorted(w["measure_code"]) == sorted(expected)

def test_weight_depends_only_on_category():
    w = load("weights_2027.csv")
    assert (w.groupby("weight_category")["weight"].nunique() == 1).all()
    assert w["weight_category"].nunique() == 6

def test_weights_source_page_matches_part():
    w = load("weights_2027.csv")
    expected = w["measure_code"].str.startswith("C").map({True: 136, False: 137})
    assert (w["source_page"] == expected).all()

def test_rfactor_tables_are_complete_and_ordered():
    r = load("rfactor_thresholds_2027.csv")
    assert len(r) == 8
    assert set(r["improvement"]) == {"With", "Without"}
    assert set(r.loc[r["table"] == 8, "percentile"]) == {65, 85}
    assert set(r.loc[r["table"] == 9, "percentile"]) == {30, 70}
    for _, g in r.groupby(["table", "improvement"]):
        g = g.sort_values("percentile")
        assert len(g) == 2 and g["value"].is_monotonic_increasing
    assert r.loc[r["table"] == 8, "value"].between(3.0, 4.5).all()
    assert r.loc[r["table"] == 9, "value"].between(0.5, 2.0).all()
    assert (r["source_page"] == r["table"].map({8: 16, 9: 17})).all()

def test_cai_is_monotonic():
    c = load("cai_2027.csv")
    assert list(c["final_category"]) == [1, 2, 3, 4, 5, 6, 7]
    assert c["cai_value"].is_monotonic_increasing   # built to be monotonic (p. 18)
    assert c["cai_value"].abs().max() < 0.2

def test_weights_match_loaded_measure_codes():
    p = Path("data/interim/fact_measure_2027.parquet")
    if not p.exists():
        pytest.skip("interim data not built")
    codes = set(pd.read_parquet(p, columns=["measure_code"])["measure_code"])
    assert codes == set(load("weights_2027.csv")["measure_code"])