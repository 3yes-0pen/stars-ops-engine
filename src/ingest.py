"""ingest.py: raw CMS Star Ratings CSVs -> clean tables in data/interim/.

Usage:   python src/ingest.py 2027
Reads:   raw/data_tables/<year>/...   (never modified)
Writes:  data/interim/<table>_<year>.parquet
Design:  keep raw text next to every parsed value; interpret nothing yet.
"""
import csv
import re
import sys
from collections import Counter
from pathlib import Path

import pandas as pd

RAW = Path("raw/data_tables")
OUT = Path("data/interim")

ENCODINGS = ("utf-8-sig", "cp1252", "latin-1")
ID_RE = re.compile(r"^[A-Z]\d{4}$")
CODE_RE = re.compile(r"^([CD]\d{2}):\s*(.+)$")
GROUP_RE = re.compile(r"^(?:HD|DD)\d:")
NUM_RE = re.compile(r"^-?\d+(\.\d+)?$")
ID_HEADERS = ["contract", "organization type", "contract name",
              "organization marketing name", "parent organization"]

# One small config per year. To add a year: add an entry here, then run the script.
CONFIG = {
    2027: {
        "measure_data": "*Measure Data*.csv",
        "measure_stars": "*Measure Stars*.csv",
        "cut_c": "*Part C Cut Points*.csv",
        "cut_d": "*Part D Cut Points*.csv",
        "summary": "*Summary Ratings*.csv",
        "cai": "*CAI*.csv",
    },
}
EXPECTED_MEASURES = {2027: 45}  # Tech Notes: max 45 measures (32 Part C + 13 Part D)


# ---------- low-level helpers ----------
def find_one(year, pattern):
    hits = [p for p in (RAW / str(year)).rglob(pattern) if "__MACOSX" not in p.parts]
    if len(hits) != 1:
        raise FileNotFoundError(f"{year}: expected 1 file for {pattern!r}, found {len(hits)}: {hits}")
    return hits[0]


def read_rows(path):
    for enc in ENCODINGS:
        try:
            with open(path, newline="", encoding=enc) as f:
                return list(csv.reader(f)), enc
        except UnicodeDecodeError:
            continue
    raise ValueError(f"could not decode {path}")


def cell(row, j):
    return row[j].strip() if j < len(row) else ""


def is_id(row):
    return bool(row) and bool(ID_RE.match(row[0].strip()))


def parse_value(raw):
    """Return (number, message). Exactly one of them is None unless the cell is blank."""
    s = (raw or "").strip()
    if not s:
        return None, None
    t = s.replace(",", "").replace("%", "").strip()
    if NUM_RE.match(t):
        return float(t), None
    return None, s


def pick(header, pattern):
    hits = [h for h in header if h and re.search(pattern, h, re.I)]
    if len(hits) != 1:
        raise ValueError(f"expected one header matching {pattern!r}, found {hits}")
    return hits[0]


# ---------- readers ----------
def read_measure_file(path, kind):
    """Wide contract x measure file with a multi-row header -> long table."""
    rows, enc = read_rows(path)
    start = next((i for i, r in enumerate(rows) if is_id(r)), None)
    if start is None or start < 3:
        raise ValueError(f"{path.name}: cannot locate header block (data starts at index {start})")
    header = rows[:start]
    for j, want in enumerate(ID_HEADERS):
        got = cell(header[1], j).lower()
        if want not in got:
            raise ValueError(f"{path.name}: id header {j} is {got!r}, expected to contain {want!r}")

    ncols = max(len(r) for r in rows)
    group, group_by_col = "", {}
    for j in range(ncols):
        g = cell(header[1], j)
        if GROUP_RE.match(g):
            group = g
        group_by_col[j] = group

    cols = {}
    for j in range(5, ncols):
        for h in header[1:]:
            m = CODE_RE.match(cell(h, j))
            if m:
                cols[j] = dict(measure_code=m.group(1), measure_name=m.group(2).strip(),
                               domain=group_by_col[j], timeframe_raw=cell(header[-1], j))
                break
    if not cols:
        raise ValueError(f"{path.name}: no measure columns found")

    data = [r for r in rows[start:] if is_id(r)]
    ids = pd.DataFrame([{"contract_id": r[0].strip(), "organization_type": cell(r, 1),
                         "contract_name": cell(r, 2), "marketing_name": cell(r, 3),
                         "parent_org": cell(r, 4)} for r in data])
    recs = []
    for r in data:
        for j, meta in cols.items():
            raw = cell(r, j)
            num, msg = parse_value(raw)
            recs.append((r[0].strip(), meta["measure_code"], raw, num, msg))
    df = pd.DataFrame(recs, columns=["contract_id", "measure_code",
                                     f"{kind}_raw", kind, f"{kind}_message"])
    return df, ids, pd.DataFrame(list(cols.values())), enc


def read_cutpoints(path, part):
    """Cut-point file: star-level rows x measure columns. Cell text kept RAW for now."""
    rows, enc = read_rows(path)
    code_rows = [i for i, r in enumerate(rows[:8]) if any(CODE_RE.match(c.strip()) for c in r)]
    if not code_rows:
        raise ValueError(f"{path.name}: no measure-code row in first 8 lines")
    ci = code_rows[0]
    tf_row = rows[ci + 1]
    ncols = max(len(r) for r in rows)
    cols = {}
    for j in range(ncols):
        m = CODE_RE.match(cell(rows[ci], j))
        if m:
            cols[j] = (m.group(1), m.group(2).strip(), cell(tf_row, j))
    out, last_org = [], ""
    for r in rows[ci + 2:]:
        if not any(c.strip() for c in r):
            continue
        if part == "D":
            org = cell(r, 0) or last_org
            last_org = org
            label = cell(r, 1)
        else:
            org, label = None, cell(r, 0)
        for j, (code, name, tf) in cols.items():
            out.append(dict(part=part, org_type=org, star_label_raw=label, measure_code=code,
                            measure_name=name, timeframe_raw=tf, cell_text=cell(r, j) or None))
    return pd.DataFrame(out), enc


def read_flat_table(path):
    """Title row + one header row + data (Summary, CAI)."""
    rows, enc = read_rows(path)
    start = next((i for i, r in enumerate(rows) if is_id(r)), None)
    if start is None or start < 1:
        raise ValueError(f"{path.name}: cannot locate header row")
    header = [c.strip() for c in rows[start - 1]]
    recs = [{h: cell(r, j) for j, h in enumerate(header) if h} for r in rows[start:] if is_id(r)]
    return recs, header, enc


def build_summary(path, year):
    recs, header, enc = read_flat_table(path)
    c_org = pick(header, r"^Organization Type$")
    c_snp = pick(header, r"^SNP$")
    rating_cols = (("part_c", pick(header, rf"^{year} Part C Summary$")),
                   ("part_d", pick(header, rf"^{year} Part D Summary$")),
                   ("overall", pick(header, rf"^{year} Overall$")))
    c_dis = [h for h in header if re.match(r"^\d{4} Disaster %$", h)]
    out = []
    for r in recs:
        d = {"contract_id": r[header[0]], "organization_type": r[c_org], "snp": r[c_snp]}
        for key, col in rating_cols:
            num, msg = parse_value(r[col])
            d[f"{key}_raw"], d[key], d[f"{key}_message"] = r[col], num, msg
        for col in c_dis:
            num, _ = parse_value(r[col])
            d[f"disaster_{col[:4]}_raw"], d[f"disaster_{col[:4]}_pct"] = r[col], num
        out.append(d)
    return pd.DataFrame(out), enc


def build_cai(path):
    recs, header, enc = read_flat_table(path)
    pr = pick(header, r"^Puerto Rico Only$")
    cols = {"fac_part_c": pick(header, r"^Part C FAC$"),
            "fac_part_d_mapd": pick(header, r"^Part D MA-PD FAC$"),
            "fac_part_d_pdp": pick(header, r"^Part D PDP FAC$"),
            "fac_overall": pick(header, r"^Overall FAC$")}
    out = []
    for r in recs:
        d = {"contract_id": r[header[0]], "puerto_rico_only": r[pr]}
        for key, col in cols.items():
            num, msg = parse_value(r[col])
            d[f"{key}_raw"], d[key], d[f"{key}_message"] = r[col], num, msg
        out.append(d)
    return pd.DataFrame(out), enc


# ---------- checks ----------
def run_checks(year, fact, ids_md, ids_ms, summary, cai, cuts, meta_md, meta_ms):
    results = []

    def check(name, ok, detail=""):
        results.append(bool(ok))
        print(f"  [{'PASS' if ok else 'FAIL'}] {name}" + (f": {detail}" if detail else ""))

    print("\nCHECKS")
    # 1. uniqueness
    d1 = int(fact.duplicated(["contract_id", "measure_code"]).sum())
    d2 = int(summary["contract_id"].duplicated().sum())
    d3 = int(cai["contract_id"].duplicated().sum())
    d4 = int(cuts.duplicated(["part", "org_type", "star_label_raw", "measure_code"]).sum())
    check("1. unique keys", d1 == d2 == d3 == d4 == 0,
          f"fact {d1}, summary {d2}, cai {d3}, cutpoints {d4} duplicates")
    # 2. same contracts in every contract-level file
    sets = {"measure_data": set(ids_md["contract_id"]), "measure_stars": set(ids_ms["contract_id"]),
            "summary": set(summary["contract_id"]), "cai": set(cai["contract_id"])}
    union = set().union(*sets.values())
    miss = {k: len(union - v) for k, v in sets.items()}
    check("2. contract sets agree across files", all(v == 0 for v in miss.values()),
          f"union {len(union)}; missing per file {miss}")
    # 3. star values
    bad = fact[fact["star"].notna() & ~fact["star"].isin([1, 2, 3, 4, 5])]
    check("3. numeric stars are in 1-5", bad.empty, f"{len(bad)} out-of-range values")
    # extra: measure codes
    codes_md, codes_ms = set(meta_md["measure_code"]), set(meta_ms["measure_code"])
    exp = EXPECTED_MEASURES.get(year)
    ok = codes_md == codes_ms and (exp is None or len(codes_md) == exp)
    check("extra. measure codes match between Data and Stars", ok,
          f"{len(codes_md)} vs {len(codes_ms)}; expected {exp}")
    return all(results)


def tally(label, series, n=20):
    c = Counter(v for v in series if isinstance(v, str) and v)
    print(f"  {label}: " + ("; ".join(f"{k!r} x{v}" for k, v in c.most_common(n)) or "none"))

def main(year):
    if year not in CONFIG:
        print(f"no config for {year}; add one to CONFIG")
        return 1
    OUT.mkdir(parents=True, exist_ok=True)
    paths = {k: find_one(year, v) for k, v in CONFIG[year].items()}
    print(f"INGEST {year}")
    for k, p in paths.items():
        print(f"  {k:14} {p.name}")

    scores, ids_md, meta_md, e1 = read_measure_file(paths["measure_data"], "score")
    stars, ids_ms, meta_ms, e2 = read_measure_file(paths["measure_stars"], "star")
    cut_c, e3 = read_cutpoints(paths["cut_c"], "C")
    cut_d, e4 = read_cutpoints(paths["cut_d"], "D")
    summary, e5 = build_summary(paths["summary"], year)
    cai, e6 = build_cai(paths["cai"])
    print(f"\nENCODINGS: data {e1}, stars {e2}, cut C {e3}, cut D {e4}, summary {e5}, cai {e6}")

    fact = scores.merge(stars, on=["contract_id", "measure_code"], how="outer", indicator=True)
    unmatched = int((fact["_merge"] != "both").sum())
    fact = fact.drop(columns="_merge")
    fact.insert(0, "star_year", year)
    fact = fact.merge(meta_md[["measure_code", "measure_name", "domain"]], on="measure_code", how="left")
    cuts = pd.concat([cut_c, cut_d], ignore_index=True)

    tables = {"dim_contract": ids_md, "dim_measure": meta_md, "fact_measure": fact,
              "cutpoint_raw": cuts, "summary": summary, "cai": cai}
    print("\nWROTE")
    for name, df in tables.items():
        df.to_parquet(OUT / f"{name}_{year}.parquet", index=False)
        print(f"  {name}_{year}.parquet: {len(df)} rows x {df.shape[1]} cols")
    print(f"  score/star rows that did not match across the two files: {unmatched}")

    print("\nNON-NUMERIC TOKENS (candidates for NULL + message)")
    tally("score", fact["score_message"])
    tally("star", fact["star_message"])
    tally("summary part_c", summary["part_c_message"])
    tally("summary part_d", summary["part_d_message"])
    tally("summary overall", summary["overall_message"])
    tally("cai overall FAC", cai["fac_overall_message"])
    print(f"  blank score cells: {int((fact['score_raw'] == '').sum())}; "
          f"blank star cells: {int((fact['star_raw'] == '').sum())}")

    print("\nCUT-POINT CELL SAMPLES (raw text; parse only after you've looked)")
    for label, df, idx in (("Part C", cut_c, ["star_label_raw"]), ("Part D", cut_d, ["org_type", "star_label_raw"])):
        try:
            codes = list(dict.fromkeys(df["measure_code"]))[:4]
            sub = df[df["measure_code"].isin(codes)]
            print(f"  {label}:")
            print(sub.pivot_table(index=idx, columns="measure_code", values="cell_text",
                                  aggfunc="first").to_string())
        except Exception as e:
            print(f"  {label}: could not pivot ({e})")

    ok = run_checks(year, fact, ids_md, ids_ms, summary, cai, cuts, meta_md, meta_ms)
    print("\nRESULT:", "ALL CHECKS PASSED" if ok else "CHECKS FAILED, read the FAIL lines above")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main(int(sys.argv[1]) if len(sys.argv) > 1 else 2027))