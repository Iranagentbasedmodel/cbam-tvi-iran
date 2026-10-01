"""Input-output layer: Leontief inverse, output multipliers and Rasmussen linkages
from the Central Bank of Iran 1395 (2016/17) 89x89 activity table at basic prices."""
from __future__ import annotations

import numpy as np
import pandas as pd

from .data import Inputs


def _num(v) -> float:
    s = str(v).replace(",", "").strip()
    try:
        return float(s) if s else 0.0
    except ValueError:
        return 0.0


def load_table(inp: Inputs):
    c = inp.config["io"]
    raw = pd.read_csv(inp.data_dir / c["file"], header=None, dtype=str, encoding="utf-8-sig", keep_default_na=False)
    n, r0, c0 = c["n"], c["first_row"], c["first_col"]
    Z = raw.iloc[r0:r0 + n, c0:c0 + n].map(_num).values
    x = raw.iloc[c["total_output_row"], c0:c0 + n].map(_num).values
    names = raw.iloc[r0:r0 + n, 0].tolist()
    return Z, x, names


def io_table(inp: Inputs) -> tuple[pd.DataFrame, dict]:
    Z, x, names = load_table(inp)
    n = len(x)
    A = Z / x
    L = np.linalg.inv(np.eye(n) - A)
    B = Z / x[:, None]                                   # Ghosh allocation coefficients
    G = np.linalg.inv(np.eye(n) - B)
    om = L.sum(0)
    bl = om / om.mean()
    fl = G.sum(1) / G.sum(1).mean()
    fl_leontief = L.sum(1) / L.sum(1).mean()
    m = pd.read_csv(inp.data_dir / "io" / "io_sector_map.csv").drop_duplicates("io_activity")
    rows = []
    for _, r in m.iterrows():
        j = int(r.io_activity) - 1
        rows.append({"io_activity": int(r.io_activity), "activity_name": r.activity_name,
                     "output_multiplier": om[j], "backward_linkage": bl[j],
                     "rank_BL_of_n": int((bl > bl[j]).sum() + 1),
                     "forward_linkage_ghosh": fl[j], "forward_linkage_leontief": fl_leontief[j]})
    checks = {"n": n, "total_output": float(x.sum()), "max_colsum_A": float(A.sum(0).max()),
              "min_diag_L": float(np.diag(L).min())}
    return pd.DataFrame(rows).round(3), checks
