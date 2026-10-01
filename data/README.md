# Data dictionary

Every number used by the model is in this folder. Each CSV has a `source` column (or the source is given below).

| File | Columns | Content | Source |
|---|---|---|---|
| `config.json` | – | analysis settings: sectors (order), base/trade year, report years, EUR/USD, weights, normalisation, Monte Carlo, break-even margin, threshold, weight grid, I-O layout | author choices |
| `cbam_defaults_iran.csv` | sector, default_weighted, default_min, default_max, direct_share, n_cn_codes, reference_default, reference_cn, weighting | official CBAM default intensities for Iran (tCO2e/t); weighted value, CN range, direct share | IR (EU) 2025/2621 amended by 2026/1740 |
| `eu_benchmarks.csv` | sector, benchmark, basis | CBAM benchmarks applied to default-based declarations (tCO2e/t) | IR (EU) 2025/2620 |
| `actual_route_benchmarks.csv` | sector, route, benchmark | route benchmarks for verified actual data (threshold analysis) | IR (EU) 2025/2620 |
| `product_prices.csv` | sector, price_usd_per_t | product prices (USD/t) | UN Comtrade unit values; reference prices |
| `eu_imports.csv` | sector, year, eu_imports_usd | EU-27 imports from Iran, Annex I scope, CIF | UN Comtrade (reporter 97, partner 364) |
| `world_exports.csv` | sector, year, world_exports_usd, method | Iran's world exports (exposure denominator) | UN Comtrade mirror; StoneX × World Bank for fertilisers |
| `world_exports_alternatives.csv` | sector, year, world_exports_usd, variant | alternative world-export values for sensitivity | mirror / earlier estimates |
| `free_allocation.csv` | year, share | surviving free allocation 2026–2034 | Reg. (EU) 2023/956 Art. 31 |
| `eua_prices.csv` | year, eur_per_tco2 | EUA price path | market average / forecasts |
| `markups.csv` | sector, from_year, markup | default-value mark-ups; `default` row applies unless a sector row exists; each value applies from `from_year` on | IR (EU) 2025/2621 |
| `cn_weighting_steel_2024.csv`, `cn_weighting_aluminium_2024.csv` | cn_code, value_usd, tonnes, iran_default | CN-level build-up of weighted defaults and unit values (checked by `scripts/check_cn_weighting.py`) | UN Comtrade; IR 2025/2621 |
| `hs_scope.csv` | sector, hs_code, action | CBAM Annex I HS codes used by `scripts/fetch_comtrade.py` (`exclude` = non-covered ferro-alloys) | Reg. (EU) 2023/956 Annex I |
| `io/cbi_io_1395_activity_89.csv` | – | Central Bank of Iran 1395 input–output table, sheet 8 (89×89 activities, basic prices; rows 4–92 / columns 3–91 = activities, row 101 = total output). UTF-8 | Central Bank of Iran |
| `io/io_sector_map.csv` | sector, io_activity, activity_name | CBAM sector → I-O activity | authors |
| `io/jafari_2023_total_co2.csv` | product_group, total_co2_t_per_bn_rials, output_multiplier, co2_per_output_growth | total CO2 coefficients (Table 7 of the paper) | Jafari-Taraji et al. (2023), Table 2 |
| `raw/` | – | raw Comtrade downloads and the full source list (not read by the model) | – |

## Updating

* **New default values**: edit `cbam_defaults_iran.csv` (and the CN tables if weights change).
* **New trade year**: run `python scripts/fetch_comtrade.py eu 2025` and `... world 2025`, add rows to
  `eu_imports.csv` / `world_exports.csv`, set `trade_year` in `config.json`.
* **New input–output table**: replace the file in `io/`, adjust `io` in `config.json` and `io_sector_map.csv`.
