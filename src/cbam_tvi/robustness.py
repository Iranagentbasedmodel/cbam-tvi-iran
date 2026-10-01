"""Rank stability across normalisation schemes and weights."""
from __future__ import annotations

import itertools

import numpy as np
import pandas as pd

from .data import Inputs
from .tvi import aggregate, components, tvi_raw


def spearman(x: pd.Series, y: pd.Series) -> float:
    """Spearman rank correlation without SciPy (Pearson correlation of average ranks)."""
    return float(np.corrcoef(x.rank().values, y.rank().values)[0, 1])


def normalisation_table(inp: Inputs) -> pd.DataFrame:
    raw = components(inp)
    w = inp.config["weights"]
    args = (w["exposure_within_E"], w["gap_within_S"], w["E_exponent"])
    out = pd.DataFrame({"TVI x/max": aggregate(raw, "max", *args)["TVI"],
                        "TVI min-max": aggregate(raw, "minmax", *args)["TVI"],
                        "TVI raw": tvi_raw(raw)}, index=raw.index)
    for c in list(out):
        out["rank " + c[4:]] = out[c].rank(ascending=False, method="min").astype(int)
    return out.sort_values("TVI x/max", ascending=False).round(4)


def weight_grid(inp: Inputs) -> tuple[pd.DataFrame, pd.DataFrame]:
    raw = components(inp)
    g = inp.config["weight_grid"]
    ranks, rows = {}, []
    for a, we, ws in itertools.product(g, g, g):
        t = aggregate(raw, inp.config["normalisation"], we, ws, a)["TVI"]
        r = t.rank(ascending=False, method="min").astype(int)
        ranks[(a, we, ws)] = r
        rows.append({"E_exponent": a, "w_exposure": we, "w_gap": ws, **{f"rank {k}": v for k, v in r.items()}})
    R = pd.DataFrame(ranks).T
    w = inp.config["weights"]
    base = R.loc[(w["E_exponent"], w["exposure_within_E"], w["gap_within_S"])]
    rho = [spearman(R.loc[i], base) for i in R.index]
    summary = pd.DataFrame({"modal rank": R.mode().iloc[0].astype(int), "min rank": R.min(), "max rank": R.max(),
                            "share at modal rank (%)": [(R[c] == R[c].mode()[0]).mean() * 100 for c in R]})
    summary.attrs["spearman_mean"], summary.attrs["spearman_min"] = float(pd.Series(rho).mean()), float(min(rho))
    return pd.DataFrame(rows), summary.sort_values("modal rank").round(1)
