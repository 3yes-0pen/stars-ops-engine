#!/usr/bin/env python3
"""Profile raw CMS Star Ratings CSVs and write a markdown draft of facts.
Exploration helper (not part of the pipeline).
Usage: python src/profile_raw.py raw/data_tables/2027 docs/raw_profile_2027.md
"""
import csv
import hashlib
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

ENCODINGS = ("utf-8", "cp1252", "latin-1")
ID_RE = re.compile(r"^[A-Z]\d{4}$")
CODE_RE = re.compile(r"^([CD]\d{2}):\s*(.+)$")
NUM_RE = re.compile(r"^-?\d+(\.\d+)?$")


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def read_rows(path):
    for enc in ENCODINGS:
        try:
            with open(path, newline="", encoding=enc) as f:
                return list(csv.reader(f)), enc
        except UnicodeDecodeError:
            continue
    raise ValueError(f"could not decode {path}")


def cell(row, j):
    return row[j] if j < len(row) else ""


def clip(s, n=40):
    s = s.strip().replace("|", "/").replace("\n", " ")
    return s if len(s) <= n else s[: n - 1] + "…"


def to_num(s):
    s = s.strip().replace(",", "").rstrip("%")
    return float(s) if NUM_RE.match(s) else None


def is_id(row):
    return bool(row) and bool(ID_RE.match(row[0].strip()))


def ffill(row, ncols):
    out, last = [], ""
    for j in range(ncols):
        c = cell(row, j).strip()
        if c:
            last = c
        out.append(last)
    return out


def short_name(p):
    return p.stem.split(" - ", 1)[-1]


def profile_csv(p, rows, enc, L, names_by_code, sn):
    ncols = max((len(r) for r in rows), default=0)
    data_start = next((i for i, r in enumerate(rows) if is_id(r)), None)
    n_id_rows = sum(1 for r in rows if is_id(r))
    contract_like = data_start is not None and n_id_rows >= 0.5 * max(1, len(rows) - 2)
    header_rows = rows[:data_start] if contract_like else rows[:8]

    codes = set()
    for r in header_rows:
        for c in r:
            m = CODE_RE.match(c.strip())
            if m:
                codes.add(m.group(1))
                names_by_code[m.group(1)][m.group(2).strip()].add(sn)

    na = Counter(ch for r in rows for c in r for ch in c if ord(ch) > 127)
    L += [f"### {sn}", "",
          f"- **Path:** `{p}`",
          f"- **Size / SHA-256:** {p.stat().st_size:,} bytes / `{sha256(p)}`",
          f"- **Encoding that decodes it:** {enc}"]
    if na:
        L.append("- **Non-ASCII characters:** " +
                 ", ".join(f"{ch!r} U+{ord(ch):04X} x{n}" for ch, n in na.most_common(8)))
    title = rows[0][0] if rows and rows[0] else ""
    L += [f"- **Records / max width:** {len(rows)} / {ncols}",
          f"- **Title row (line 1):** `{clip(title, 120)}`"]

    info = {"ids": None, "codes": codes, "hdr": "-", "n_data": "-",
            "n_ids": "-", "dups": "-", "cols": ncols}

    if contract_like:
        header = rows[:data_start]
        data = [r for r in rows[data_start:] if is_id(r)]
        extra = [r for r in rows[data_start:] if not is_id(r)]
        trimmed = [r[0].strip() for r in data]
        dup = sorted(k for k, v in Counter(trimmed).items() if v > 1)
        notes = [clip(" ".join(c for c in r if c.strip()), 100)
                 for r in extra if any(c.strip() for c in r)]
        L += [f"- **Layout:** contract-level. Lines before data (incl. title): {data_start}; data starts on line {data_start + 1}",
              f"- **Data rows:** {len(data)} | **distinct IDs (trimmed):** {len(set(trimmed))} | **duplicate IDs:** {len(dup)} {dup[:5]}",
              f"- **IDs with leading/trailing spaces:** {sum(1 for r in data if r[0] != r[0].strip())}",
              f"- **ID first letters:** {dict(Counter(x[0] for x in trimmed))}",
              f"- **Non-ID rows after the header (blank/footnote):** {len(extra)}; non-blank examples: {notes[:5]}",
              f"- **First 2 data rows (first 12 cells):** {[[clip(c, 20) for c in r[:12]] for r in data[:2]]}",
              f"- **Last 2 records in file:** {[[clip(c, 20) for c in r[:6]] for r in rows[-2:]]}",
              "", "Header lines (non-empty cells as (column index, text)):", "```"]
        for k, h in enumerate(header[1:], start=2):
            L.append(f"line {k}: " + str([(j, clip(c, 45)) for j, c in enumerate(h) if c.strip()]))
        L += ["```", "",
              "| col | header cells | non-empty | numeric | min | max | notes |",
              "|---|---|---|---|---|---|---|"]
        grp = ffill(header[1], ncols) if len(header) > 2 else None
        empty_cols, ws_cells = 0, 0
        for j in range(ncols):
            raw_h = [cell(h, j).strip() for h in header[1:]]
            hdr = list(raw_h)
            if grp is not None and hdr:
                hdr[0] = grp[j] if any(raw_h) else ""
            vals = [cell(r, j) for r in data]
            ne = [v for v in vals if v.strip()]
            if not ne and not any(raw_h):
                empty_cols += 1
                continue
            ws_cells += sum(1 for v in ne if v != v.strip())
            nums = [to_num(v) for v in ne]
            numeric = [x for x in nums if x is not None]
            htxt = " / ".join(clip(v, 45) for v in hdr if v)
            if numeric:
                tally = Counter(v.strip() for v, x in zip(ne, nums) if x is None)
                note = "; ".join(f"{clip(t, 40)} x{n}" for t, n in tally.most_common(4))
                L.append(f"| {j} | {htxt} | {len(ne)} | {len(numeric)} | {min(numeric):g} | {max(numeric):g} | {note} |")
            else:
                uniq = list(dict.fromkeys(v.strip() for v in ne))
                ex = ", ".join(clip(v, 25) for v in uniq[:2])
                L.append(f"| {j} | {htxt} | {len(ne)} | 0 | | | text, {len(uniq)} distinct, e.g. {ex} |")
        L += ["", f"- Fully empty columns (no header, no data): {empty_cols}; data cells with leading/trailing spaces: {ws_cells}"]
        info.update(ids=set(trimmed), hdr=data_start, n_data=len(data),
                    n_ids=len(set(trimmed)), dups=len(dup), cols=ncols - empty_cols)
    else:
        L += ["- **Layout:** not contract-level (first column is not contract-ID-like); transposed view below",
              "", "```", "one line per column; cells from lines 2-26 joined with ' || '"]
        for j in range(ncols):
            cells = [clip(cell(r, j), 30) for r in rows[1:26]]
            if any(cells):
                L.append(f"col {j}: " + " || ".join(cells))
        L += ["```", f"- **Last 4 records:** {[[clip(c, 20) for c in r[:6]] for r in rows[-4:]]}"]
    return info


def main(folder, out_path):
    L = [f"# Raw profile: {folder}", "",
         "_Generated by src/profile_raw.py. Facts only; interpretation belongs in the data dictionary._", ""]
    summary, id_sets, codes_by_file, others = [], {}, {}, []
    names_by_code = defaultdict(lambda: defaultdict(set))

    for p in sorted(x for x in Path(folder).rglob("*") if x.is_file()):
        if p.suffix.lower() != ".csv":
            others.append(p)
            continue
        rows, enc = read_rows(p)
        sn = short_name(p)
        info = profile_csv(p, rows, enc, L, names_by_code, sn)
        summary.append((sn, enc, len(rows), info))
        if info["ids"] is not None:
            id_sets[sn] = info["ids"]
        codes_by_file[sn] = info["codes"]
        L.append("")

    if id_sets:
        ref_name = max(id_sets, key=lambda k: len(id_sets[k]))
        ref = id_sets[ref_name]
        L += ["## Cross-file contract ID overlap", "",
              f"Reference file (most IDs): {ref_name} ({len(ref)} IDs)", "",
              "| file | IDs | in reference | not in reference | reference IDs missing here |",
              "|---|---|---|---|---|"]
        for name, s in id_sets.items():
            L.append(f"| {name} | {len(s)} | {len(s & ref)} | {len(s - ref)} {sorted(s - ref)[:3]} | {len(ref - s)} |")
        L.append("")

    L += ["## Measure codes found in headers, by file", ""]
    all_codes = set().union(*codes_by_file.values()) if codes_by_file else set()
    for name, cs in codes_by_file.items():
        L.append(f"- {name}: {len(cs)} codes; missing vs. union ({len(all_codes)}): {sorted(all_codes - cs)}")
    drift = {c: d for c, d in names_by_code.items() if len(d) > 1}
    L += ["", "### Same code, different names across files", ""]
    if drift:
        for c, d in sorted(drift.items()):
            L.append(f"- {c}: " + " | ".join(f"{n!r} in {sorted(fs)}" for n, fs in d.items()))
    else:
        L.append("- none found")

    if others:
        L += ["", "## Non-CSV files in this folder (inspect separately)", ""]
        for p in others:
            L.append(f"- `{p.name}`: {p.stat().st_size:,} bytes, SHA-256 `{sha256(p)}`")

    Path(out_path).write_text("\n".join(L) + "\n", encoding="utf-8")

    print(f"{'file':42} {'enc':7} {'lines':>6} {'hdr':>4} {'rows':>5} {'ids':>5} {'dups':>4} {'cols':>4}")
    for sn, enc, n, i in summary:
        print(f"{sn[:42]:42} {enc:7} {n:>6} {str(i['hdr']):>4} {str(i['n_data']):>5} "
              f"{str(i['n_ids']):>5} {str(i['dups']):>4} {str(i['cols']):>4}")
    print(f"\nwrote {out_path} ({len(L)} lines); non-CSV files skipped: {[p.name for p in others]}")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])