"""Aggregate certificate burden, break-even carbon prices and the default-versus-actual threshold."""
from __future__ import annotations

import pandas as pd

from .ave import ave, emission_gap
from .data import Inputs


def burden_table(inp: Inputs) -> pd.DataFrame:
    """Annual certificate cost on current EU-bound flows (USD million)."""
    eu = inp.eu_imp(inp.config["trade_year"])
    rows = []
    for y in inp.config["report_years"]:
        p = float(inp.eua[y])
        rows.append({"Year": y, "EUA (EUR)": p,
                     "Full (M USD)": sum(eu[s] * ave(inp, s, y, p) / 100 for s in inp.sectors) / 1e6,
                     "Direct-only (M USD)": sum(eu[s] * ave(inp, s, y, p, scope="direct") / 100 for s in inp.sectors) / 1e6})
    return pd.DataFrame(rows).round(2)


def burden_sensitivity(inp: Inputs) -> pd.DataFrame:
    y, eu = inp.config["base_year"], inp.eu_imp(inp.config["trade_year"])
    return pd.DataFrame([{"EUA (EUR)": p, f"Burden {y} (M USD)":
                          round(sum(eu[s] * ave(inp, s, y, p) / 100 for s in inp.sectors) / 1e6, 2)}
                         for p in inp.config["eua_sensitivity_prices"]])


def breakeven_table(inp: Inputs) -> pd.DataFrame:
    """EUA price at which the certificate cost absorbs the export margin."""
    b = inp.config["breakeven"]
    cur = float(inp.eua[inp.config["base_year"]])
    rows = {}
    for s in inp.sectors:
        gap = max(emission_gap(inp, s, b["year"]), 1e-9)
        p = b["margin"] * float(inp.prices[s]) / (gap * inp.eur_usd)
        rows[s] = {"Break-even (EUR/tCO2)": round(p, 1), "Current EUA": round(cur, 1), "Viable": "YES" if p > cur else "NO"}
    return pd.DataFrame(rows).T


def threshold_table(inp: Inputs) -> pd.DataFrame:
    """Verified intensity below which actual data beat the default.

    thr(t) = ci_ref * (1 + mu(t)) - (BM_default - BM_actual) * FA(t)
    """
    t = inp.config["threshold"]
    s = t["sector"]
    ref = inp.defaults.at[s, "reference_default"]
    ci = float(ref) if pd.notna(ref) else float(inp.defaults.at[s, "default_weighted"])
    bm_def = float(inp.benchmarks.at[s, "benchmark"])
    r = inp.actual_routes
    bm_act = float(r[(r.sector == s) & (r.route == t["actual_route"])].benchmark.iloc[0])
    return pd.DataFrame([{"Year": y, "Threshold (tCO2e/t)": round(ci * (1 + inp.markup(s, y)) - (bm_def - bm_act) * inp.fa(y), 3)}
                         for y in t["years"]])
