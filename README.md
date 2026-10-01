# TVI-CBAM: Iran's Export Vulnerability to the EU Carbon Border Adjustment Mechanism

Replication code and data for the article *"Iran's Export Vulnerability to the EU Carbon Border
Adjustment Mechanism: A Composite Index and Input–Output Approach Using Official Default Values"*.

**All inputs are read from [`data/`](data/). The code contains no data.** To update the analysis
(new defaults, prices, trade year or input–output table), edit the CSV files and rerun.

## Quick start

```bash
git clone <repo-url> && cd cbam-tvi-iran
python -m venv .venv && source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
PYTHONPATH=src python -m cbam_tvi.cli                  # Windows (PowerShell): $env:PYTHONPATH="src"; python -m cbam_tvi.cli
pytest                                                  # checks that the published numbers are reproduced
```

Or install the package: `pip install -e .` and run `cbam-tvi`.
Options: `--data DIR` (alternative data folder), `--out DIR`, `--no-figures`.

## Repository layout

```
data/                 all inputs (see data/README.md)
  config.json         analysis settings only (years, weights, Monte Carlo, normalisation)
  *.csv               numerical inputs, one topic per file, each row with its source
  io/                 Central Bank of Iran 1395 input–output table and sector mapping
  raw/                raw downloads and source list (documentation, not read by the model)
src/cbam_tvi/
  data.py             loads and validates data/
  ave.py              ad valorem equivalent of the certificate cost
  tvi.py              TVI-CBAM index (exposure x sensitivity)
  montecarlo.py       lognormal Monte Carlo of the ranking
  burden.py           certificate burden, break-even prices, default-vs-actual threshold
  robustness.py       normalisation and weight sensitivity
  io_model.py         Leontief inverse, multipliers, linkages
  figures.py          Figures 1–5
  cli.py              runs everything
scripts/
  fetch_comtrade.py   downloads EU imports and world mirror exports (UN Comtrade)
  check_cn_weighting.py  recomputes weighted defaults and unit values from CN tables
tests/                regression tests against the published results
results/, figures/    outputs (generated)
```

## Outputs

| File | Paper |
|---|---|
| `table1_defaults.csv` | Table 1 |
| `table2_ave_full.csv`, `table3_ave_direct.csv` | Table 3, Figure 2 |
| `table4_tvi.csv`, `table7_montecarlo.csv`, `table7a_montecarlo_correlated.csv` | Table 4, Figure 3 |
| `table4a_normalisation.csv`, `table4_tvi_minmax.csv`, `table7b_montecarlo_minmax.csv` | Table 4a |
| `table4b_weights_grid.csv`, `table4b_weights_summary.csv` | weight sensitivity (Sec. 4.3) |
| `table4c_tvi_world_*.csv` | world-export sensitivity (Limitations) |
| `table5_burden.csv`, `table5a_burden_eua_sensitivity.csv` | Table 5, Figure 4 |
| `table6_breakeven.csv` | Table 6 |
| `table6a_threshold.csv` | Section 4.6, Figure 5 |
| `table8_io_multipliers.csv` | Table 8 |

## Method in brief

* **AVE** = max(ci·(1+μ(t)) − BM·FA(t), 0) · P_EUA(t) · EUR/USD / price
* **TVI** = E^a · S^(1−a), with E = w·exposure + (1−w)·composition and S = w·gap + (1−w)·AVE, each
  normalised by its maximum (baseline) or min–max.
* **Monte Carlo**: defaults drawn lognormally, σ = max(ln(max/min)/(2·1.645), 0.15); 10,000 draws, seed 42.
* **Threshold**: verified intensity below which actual data beat the default,
  thr(t) = ci_ref·(1+μ(t)) − (BM_default − BM_actual)·FA(t).

## Data notes

* Iran's default route indicator is (C) BF/BOF, so the BF/BOF benchmark (1.364) applies to default-based
  declarations although domestic production is mainly DRI-EAF; the DRI-EAF benchmark (0.481) is used only
  in the threshold analysis for verified actual data.
* World exports are partner-reported mirror data (lower bounds); fertilisers use a volume-based estimate.
  Alternatives are in `world_exports_alternatives.csv` and are run automatically.

## License

Code: MIT (see `LICENSE`). Data files reproduce public sources listed in each file's `source` column.
