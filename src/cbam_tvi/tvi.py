"""Trade Vulnerability Index (TVI-CBAM).

    E_i   = w_e * n(exposure_i) + (1 - w_e) * n(composition_i)
    S_i   = w_s * n(gap_i)      + (1 - w_s) * n(AVE_i)
    TVI_i = E_i^a * S_i^(1 - a)            (a = 0.5 -> geometric mean)

exposure    = EU imports / world exports
composition = EU imports / total covered EU imports
gap         = max(default - benchmark, 0) / default
n(.)        = x / max (distance to best, baseline) or min-max
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from .ave import ave
from .data import Inputs


def normalise(x: pd.Series, method: str) -> pd.Series:
    mn, mx = x.min(), x.max()
    if mx == mn:
        return pd.Series(0.5, index=x.index)
    if method == "max":
        return x / mx
    if method == "minmax":
        return (x - mn) / (mx - mn)
    raise ValueError(f"unknown normalisation '{method}'")


def components(inp: Inputs, ci: pd.Series | None = None, year: int | None = None,
               trade_year: int | None = None, eua: float | None = None,
               world_variant: str | None = None) -> pd.DataFrame:
    """Raw (un-normalised) indicator values per sector."""
    cfg = inp.config
    year = year or cfg["base_year"]
    trade_year = trade_year or cfg["trade_year"]
    eua = float(inp.eua[year]) if eua is None else eua
    ci = inp.defaults["default_weighted"].reindex(inp.sectors) if ci is None else ci
    eu = inp.eu_imp(trade_year)
    world = inp.world_exp(trade_year, world_variant)
    bm = inp.benchmarks["benchmark"].reindex(inp.sectors)
    out = pd.DataFrame(index=inp.sectors)
    out["exposure"] = eu / world.clip(lower=1)
    out["composition"] = eu / max(eu.sum(), 1)
    out["intensity_gap"] = (ci - bm).clip(lower=0) / ci.clip(lower=0.01)
    out["AVE (%)"] = [ave(inp, s, year, eua, ci=float(ci[s])) for s in inp.sectors]
    return out


def aggregate(raw: pd.DataFrame, method: str = "max", w_e: float = 0.5, w_s: float = 0.5,
              a: float = 0.5) -> pd.DataFrame:
    n = raw.apply(lambda c: normalise(c, method))
    E = w_e * n["exposure"] + (1 - w_e) * n["composition"]
    S = w_s * n["intensity_gap"] + (1 - w_s) * n["AVE (%)"]
    return pd.DataFrame({"TVI": E ** a * S ** (1 - a), "E": E, "S": S})


def tvi_table(inp: Inputs, method: str | None = None, **kw) -> pd.DataFrame:
    w = inp.config["weights"]
    raw = components(inp, **kw)
    agg = aggregate(raw, method or inp.config["normalisation"],
                    w["exposure_within_E"], w["gap_within_S"], w["E_exponent"])
    return pd.concat([agg, raw], axis=1)


def tvi_raw(raw: pd.DataFrame) -> pd.Series:
    """Un-normalised robustness index: geometric mean of the four raw components."""
    return np.prod(raw[["exposure", "composition", "intensity_gap", "AVE (%)"]].values, axis=1) ** 0.25
