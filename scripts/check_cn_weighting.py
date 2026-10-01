#!/usr/bin/env python3
"""Recompute the tonnage-weighted defaults and unit values from the CN-level tables
and compare them with data/cbam_defaults_iran.csv and data/product_prices.csv."""
from pathlib import Path

import pandas as pd

D = Path(__file__).resolve().parents[1] / "data"
dft = pd.read_csv(D / "cbam_defaults_iran.csv", index_col="sector")
prc = pd.read_csv(D / "product_prices.csv", index_col="sector")
for sector, f in [("Iron & Steel", "cn_weighting_steel_2024.csv"), ("Aluminium", "cn_weighting_aluminium_2024.csv")]:
    t = pd.read_csv(D / f)
    ci = (t.tonnes * t.iran_default).sum() / t.tonnes.sum()
    uv = t.value_usd.sum() / t.tonnes.sum()
    print(f"{sector:14s} weighted default {ci:.3f} (file {dft.at[sector, 'default_weighted']}) | "
          f"unit value {uv:,.0f} USD/t (file {prc.at[sector, 'price_usd_per_t']})")
