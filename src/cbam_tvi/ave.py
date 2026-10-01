"""Ad valorem equivalent (AVE) of the CBAM certificate cost.

    AVE_i(t) = max(ci_i * (1 + mu_i(t)) - BM_i * FA(t), 0) * P_EUA(t) * EURUSD / price_i

``scope='direct'`` multiplies the default by its direct-emission share.
"""
from __future__ import annotations

import pandas as pd

from .data import Inputs


def emission_gap(inp: Inputs, sector: str, year: int, ci: float | None = None,
                 scope: str = "full") -> float:
    ci = float(inp.defaults.at[sector, "default_weighted"]) if ci is None else ci
    eff = ci * (1 + inp.markup(sector, year))
    if scope == "direct":
        eff *= float(inp.defaults.at[sector, "direct_share"])
    return max(eff - float(inp.benchmarks.at[sector, "benchmark"]) * inp.fa(year), 0.0)


def ave(inp: Inputs, sector: str, year: int, eua: float, ci: float | None = None,
        scope: str = "full") -> float:
    """AVE in percent."""
    gap = emission_gap(inp, sector, year, ci, scope)
    return gap * eua * inp.eur_usd / float(inp.prices[sector]) * 100


def ave_table(inp: Inputs, scope: str = "full") -> pd.DataFrame:
    years = inp.config["report_years"]
    return pd.DataFrame({y: {s: ave(inp, s, y, float(inp.eua[y]), scope=scope) for s in inp.sectors}
                         for y in years}).round(2)
