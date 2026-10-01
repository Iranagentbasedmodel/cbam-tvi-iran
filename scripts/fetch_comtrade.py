#!/usr/bin/env python3
"""Download the trade inputs from the UN Comtrade public preview API (no key needed).

    python scripts/fetch_comtrade.py eu 2022 2023 2024      # EU-27 imports from Iran
    python scripts/fetch_comtrade.py world 2024             # Iran world exports (mirror)

HS codes are read from data/hs_scope.csv (action = include / exclude).
Results are written to data/raw/comtrade_<mode>_<year>.csv. Review them, then copy
the sector totals into data/eu_imports.csv or data/world_exports.csv.

EU mode : reporter 97 (EU-27), partner 364 (Iran), flow M, CIF USD.
World   : all reporters, partner 364, flow M, summed server-side
          (aggregateBy=reporterCode,cmdCode). Values are importer-reported (mostly CIF),
          so they are on the same basis as EU imports and need no CIF-FOB adjustment.
          Mirror totals are lower bounds of true exports (non-reporting partners,
          transit-hub origin recording).
"""
import csv
import json
import sys
import time
import urllib.request
from pathlib import Path

BASE = "https://comtradeapi.un.org/public/v1/preview/C/A/HS"
ROOT = Path(__file__).resolve().parents[1]


def scope():
    s = {}
    with open(ROOT / "data" / "hs_scope.csv", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            s.setdefault(r["sector"], {"include": [], "exclude": []})[r["action"]].append(r["hs_code"])
    return s


def total(year, codes, mode):
    q = f"period={year}&partnerCode=364&cmdCode={','.join(codes)}&flowCode=M&partner2Code=0&customsCode=C00&motCode=0"
    q += "&reporterCode=97" if mode == "eu" else "&aggregateBy=reporterCode,cmdCode"
    with urllib.request.urlopen(f"{BASE}?{q}", timeout=120) as r:
        data = json.load(r).get("data", [])
    time.sleep(1.0)                       # be polite to the public endpoint
    return sum(d["primaryValue"] or 0 for d in data)


def main(mode, years):
    out = ROOT / "data" / "raw"
    out.mkdir(parents=True, exist_ok=True)
    for y in years:
        rows = []
        for sector, c in scope().items():
            v = total(y, c["include"], mode)
            if c["exclude"]:
                v -= total(y, c["exclude"], mode)
            rows.append({"sector": sector, "year": y, "value_usd": round(v, 2)})
            print(y, sector, f"{v / 1e6:,.2f} M USD")
        with open(out / f"comtrade_{mode}_{y}.csv", "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=["sector", "year", "value_usd"]); w.writeheader(); w.writerows(rows)


if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1] not in ("eu", "world"):
        sys.exit(__doc__)
    main(sys.argv[1], sys.argv[2:] or ["2024"])
