"""Monte Carlo robustness of the TVI ranking.

Default intensities are drawn from lognormal distributions whose mean equals the
trade-weighted default and whose log-standard deviation is

    sigma_i = max( ln(max_i / min_i) / (2 * z_90), sigma_floor )

i.e. the CN-level range of official defaults is treated as a 90% interval.
Trade data and benchmarks are held fixed.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from .data import Inputs


def _norm(x: np.ndarray, method: str) -> np.ndarray:
    mn, mx = x.min(axis=1, keepdims=True), x.max(axis=1, keepdims=True)
    same = (mx == mn)
    with np.errstate(invalid="ignore", divide="ignore"):
        out = x / mx if method == "max" else (x - mn) / (mx - mn)
    return np.where(same, 0.5, out)


def simulate(inp: Inputs, correlated: bool = False, method: str | None = None) -> pd.DataFrame:
    cfg, mc = inp.config, inp.config["monte_carlo"]
    method = method or cfg["normalisation"]
    w = cfg["weights"]
    sectors, k = inp.sectors, len(inp.sectors)
    year, ty = cfg["base_year"], cfg["trade_year"]
    eua = float(inp.eua[year])

    d = inp.defaults.reindex(sectors)
    sigma = np.maximum(np.log(d.default_max / d.default_min) / (2 * mc["z_90"]), mc["sigma_floor"]).values
    mu = np.log(d.default_weighted.values) - 0.5 * sigma ** 2

    corr = np.eye(k)
    if correlated:
        a, b = (sectors.index(s) for s in mc["alt_correlation"]["pair"])
        corr[a, b] = corr[b, a] = mc["alt_correlation"]["rho"]
    chol = np.linalg.cholesky(corr)

    rng = np.random.RandomState(mc["seed"])
    z = rng.standard_normal((mc["n_draws"], k)) @ chol.T
    ci = np.exp(mu + sigma * z)                                        # draws x sectors

    eu = inp.eu_imp(ty).values
    world = inp.world_exp(ty).values
    exposure = np.tile(eu / np.maximum(world, 1), (len(ci), 1))
    composition = np.tile(eu / max(eu.sum(), 1), (len(ci), 1))
    bm = inp.benchmarks.benchmark.reindex(sectors).values
    fa = inp.fa(year)
    mk = np.array([inp.markup(s, year) for s in sectors])
    price = inp.prices.reindex(sectors).values
    gap = np.maximum(ci - bm, 0) / np.maximum(ci, 0.01)
    ave = np.maximum(ci * (1 + mk) - bm * fa, 0) * eua * inp.eur_usd / price * 100

    E = w["exposure_within_E"] * _norm(exposure, method) + (1 - w["exposure_within_E"]) * _norm(composition, method)
    S = w["gap_within_S"] * _norm(gap, method) + (1 - w["gap_within_S"]) * _norm(ave, method)
    tvi = E ** w["E_exponent"] * S ** (1 - w["E_exponent"])

    first = np.bincount(tvi.argmax(axis=1), minlength=k) / len(tvi) * 100
    lo, hi = np.percentile(tvi, 5, axis=0), np.percentile(tvi, 95, axis=0)
    return pd.DataFrame({"P(rank=1) (%)": first.round(1), "TVI mean": tvi.mean(0), "TVI median": np.median(tvi, 0),
                         "CI 90% low": lo, "CI 90% high": hi, "CI half-width": (hi - lo) / 2},
                        index=sectors).round(4)
