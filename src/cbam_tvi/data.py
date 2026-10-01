"""Loading and validating the input data.

Every number used by the model comes from a file in ``data/``. This module
reads those files into one immutable :class:`Inputs` object that the other
modules receive as an argument.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

import pandas as pd

DEFAULT_DATA_DIR = Path(__file__).resolve().parents[2] / "data"


@dataclass(frozen=True)
class Inputs:
    config: dict
    defaults: pd.DataFrame          # index: sector
    benchmarks: pd.DataFrame        # index: sector
    actual_routes: pd.DataFrame
    prices: pd.Series               # USD/t, index: sector
    eu_imports: pd.DataFrame        # columns: sector, year, eu_imports_usd
    world_exports: pd.DataFrame     # columns: sector, year, world_exports_usd
    world_alternatives: pd.DataFrame
    free_allocation: pd.Series      # index: year
    eua: pd.Series                  # EUR/tCO2, index: year
    markups: pd.DataFrame
    data_dir: Path = field(default=DEFAULT_DATA_DIR)

    # ---- convenience accessors -------------------------------------------------
    @property
    def sectors(self) -> list[str]:
        return list(self.config["sectors"])

    @property
    def eur_usd(self) -> float:
        return float(self.config["eur_usd"])

    def fa(self, year: int) -> float:
        """Surviving free-allocation share; 0 after the last listed year."""
        return float(self.free_allocation.get(year, 0.0))

    def markup(self, sector: str, year: int) -> float:
        """Mark-up in force in ``year``: sector-specific row if present, else 'default'."""
        m = self.markups
        rows = m[m.sector == sector]
        if rows.empty:
            rows = m[m.sector == "default"]
        rows = rows[rows.from_year <= year].sort_values("from_year")
        if rows.empty:
            raise ValueError(f"No mark-up defined for {sector} in {year}")
        return float(rows.iloc[-1].markup)

    def eu_imp(self, year: int) -> pd.Series:
        d = self.eu_imports[self.eu_imports.year == year].set_index("sector")["eu_imports_usd"]
        return d.reindex(self.sectors).fillna(0.0)

    def world_exp(self, year: int, variant: str | None = None) -> pd.Series:
        base = self.world_exports[self.world_exports.year == year].set_index("sector")["world_exports_usd"]
        base = base.reindex(self.sectors).fillna(0.0)
        if variant:
            alt = self.world_alternatives
            alt = alt[(alt.year == year) & (alt.variant == variant)].set_index("sector")["world_exports_usd"]
            base.update(alt)
        return base


def _csv(p: Path, **kw) -> pd.DataFrame:
    if not p.exists():
        raise FileNotFoundError(f"Required input file missing: {p}")
    return pd.read_csv(p, **kw)


def load_inputs(data_dir: str | Path | None = None) -> Inputs:
    d = Path(data_dir) if data_dir else DEFAULT_DATA_DIR
    config = json.loads((d / "config.json").read_text(encoding="utf-8"))
    inp = Inputs(
        config=config,
        defaults=_csv(d / "cbam_defaults_iran.csv", index_col="sector"),
        benchmarks=_csv(d / "eu_benchmarks.csv", index_col="sector"),
        actual_routes=_csv(d / "actual_route_benchmarks.csv"),
        prices=_csv(d / "product_prices.csv", index_col="sector")["price_usd_per_t"],
        eu_imports=_csv(d / "eu_imports.csv"),
        world_exports=_csv(d / "world_exports.csv"),
        world_alternatives=_csv(d / "world_exports_alternatives.csv"),
        free_allocation=_csv(d / "free_allocation.csv", index_col="year")["share"],
        eua=_csv(d / "eua_prices.csv", index_col="year")["eur_per_tco2"],
        markups=_csv(d / "markups.csv"),
        data_dir=d,
    )
    validate(inp)
    return inp


def validate(inp: Inputs) -> None:
    """Fail early with a clear message if the data folder is incomplete."""
    s = set(inp.sectors)
    for name, idx in [("cbam_defaults_iran.csv", inp.defaults.index),
                      ("eu_benchmarks.csv", inp.benchmarks.index),
                      ("product_prices.csv", inp.prices.index)]:
        missing = s - set(idx)
        if missing:
            raise ValueError(f"{name}: missing sectors {sorted(missing)}")
    for y in inp.config["report_years"]:
        if y not in inp.eua.index:
            raise ValueError(f"eua_prices.csv: no price for report year {y}")
    fa = inp.free_allocation
    if ((fa < 0) | (fa > 1)).any():
        raise ValueError("free_allocation.csv: shares must lie in [0, 1]")
    if (inp.defaults.default_min > inp.defaults.default_max).any():
        raise ValueError("cbam_defaults_iran.csv: default_min > default_max")
