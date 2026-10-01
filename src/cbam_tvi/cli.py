"""Command-line entry point: ``python -m cbam_tvi.cli [--data DIR] [--out DIR]``.

Runs every analysis of the paper and writes tables (CSV) and figures (PNG).
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd

from . import __version__
from .ave import ave_table
from .burden import breakeven_table, burden_sensitivity, burden_table, threshold_table
from .data import load_inputs
from .figures import make_all
from .io_model import io_table
from .montecarlo import simulate
from .robustness import normalisation_table, weight_grid
from .tvi import aggregate, components, tvi_table

ROOT = Path(__file__).resolve().parents[2]


def run(data_dir=None, out_dir=None, figures=True, verbose=True) -> dict:
    inp = load_inputs(data_dir)
    out = Path(out_dir) if out_dir else ROOT / "results"
    out.mkdir(parents=True, exist_ok=True)
    res = {
        "defaults": inp.defaults.reindex(inp.sectors)[["default_min", "default_max", "default_weighted", "direct_share", "n_cn_codes"]]
                    .join(inp.benchmarks["benchmark"]).join(inp.prices),
        "ave_full": ave_table(inp, "full"),
        "ave_direct": ave_table(inp, "direct"),
        "tvi": tvi_table(inp).sort_values("TVI", ascending=False).round(4),
        "tvi_minmax": tvi_table(inp, method="minmax").sort_values("TVI", ascending=False).round(4),
        "normalisation": normalisation_table(inp),
        "mc": simulate(inp),
        "mc_correlated": simulate(inp, correlated=True),
        "mc_minmax": simulate(inp, method="minmax"),
        "burden": burden_table(inp),
        "burden_sensitivity": burden_sensitivity(inp),
        "breakeven": breakeven_table(inp),
        "threshold": threshold_table(inp),
    }
    res["weights_grid"], res["weights_summary"] = weight_grid(inp)
    alt = inp.world_alternatives
    for v in sorted(alt.variant.unique()):
        w = inp.config["weights"]
        t = aggregate(components(inp, world_variant=v), inp.config["normalisation"],
                      w["exposure_within_E"], w["gap_within_S"], w["E_exponent"])["TVI"]
        res[f"tvi_world_{v}"] = pd.DataFrame({"TVI": t, "rank": t.rank(ascending=False, method="min").astype(int)}).sort_values("TVI", ascending=False).round(4)
    res["io"], checks = io_table(inp)

    names = {"defaults": "table1_defaults", "ave_full": "table2_ave_full", "ave_direct": "table3_ave_direct",
             "tvi": "table4_tvi", "tvi_minmax": "table4_tvi_minmax", "normalisation": "table4a_normalisation",
             "weights_grid": "table4b_weights_grid", "weights_summary": "table4b_weights_summary",
             "burden": "table5_burden", "burden_sensitivity": "table5a_burden_eua_sensitivity",
             "breakeven": "table6_breakeven", "threshold": "table6a_threshold",
             "mc": "table7_montecarlo", "mc_correlated": "table7a_montecarlo_correlated", "mc_minmax": "table7b_montecarlo_minmax",
             "io": "table8_io_multipliers"}
    names.update({k: f"table4c_{k}" for k in res if k.startswith("tvi_world_")})
    for k, f in names.items():
        res[k].to_csv(out / f"{f}.csv", index=k not in ("burden", "burden_sensitivity", "threshold", "io", "weights_grid"))
    meta = {"version": __version__, "io_checks": checks,
            "weights_spearman": {"mean": res["weights_summary"].attrs["spearman_mean"], "min": res["weights_summary"].attrs["spearman_min"]}}
    (out / "run_metadata.json").write_text(json.dumps(meta, indent=2))
    if figures:
        make_all(inp, res, ROOT / "figures" if out_dir is None else out / "figures")
    if verbose:
        pd.set_option("display.width", 160)
        for k in ["ave_full", "tvi", "mc", "mc_correlated", "normalisation", "weights_summary", "burden", "breakeven", "threshold", "io"]:
            print(f"\n=== {names[k]} ===\n{res[k].to_string()}")
    return res


def main() -> None:
    p = argparse.ArgumentParser(description="TVI-CBAM: Iran's export vulnerability to the EU CBAM")
    p.add_argument("--data", default=None, help="data folder (default: ./data)")
    p.add_argument("--out", default=None, help="output folder (default: ./results)")
    p.add_argument("--no-figures", action="store_true")
    a = p.parse_args()
    run(a.data, a.out, figures=not a.no_figures)


if __name__ == "__main__":
    main()
