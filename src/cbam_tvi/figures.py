"""Figures 1-5 of the paper, drawn only from computed results and data files."""
from __future__ import annotations

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402

from .data import Inputs  # noqa: E402

BLUE, RED, GREY = "#35618f", "#c0392b", "#b0b8c4"


def make_all(inp: Inputs, res: dict, out: Path) -> None:
    out.mkdir(parents=True, exist_ok=True)
    plt.rcParams.update({"font.family": "serif", "font.size": 10, "figure.dpi": 200})
    ty = inp.config["trade_year"]

    # Fig. 1 - EU imports by sector and by year
    fig, ax = plt.subplots(1, 2, figsize=(10, 4))
    s = (inp.eu_imp(ty) / 1e6)
    s = s[s > 0].sort_values()
    ax[0].barh(s.index, s.values, color=BLUE)
    for i, v in enumerate(s.values):
        ax[0].text(v, i, f" {v:.2f}", va="center", fontsize=8)
    ax[0].set_xlabel("USD million"); ax[0].set_title(f"(a) EU-27 imports from Iran, {ty}")
    p = inp.eu_imports.pivot(index="year", columns="sector", values="eu_imports_usd").fillna(0) / 1e6
    p = p.reindex(columns=[c for c in inp.sectors if c in p.columns])
    p.plot(kind="bar", stacked=True, ax=ax[1], colormap="tab10", width=0.6)
    ax[1].set_ylabel("USD million"); ax[1].set_xlabel(""); ax[1].legend(fontsize=7); ax[1].set_title("(b) Covered EU imports by year")
    ax[1].tick_params(axis="x", rotation=0)
    plt.tight_layout(); plt.savefig(out / "fig1_trade.png"); plt.close()

    # Fig. 2 - AVE paths
    a = res["ave_full"]
    fig, ax = plt.subplots(figsize=(7, 4.2))
    for sct in a.index:
        if (a.loc[sct] > 0).any():
            ax.plot(a.columns, a.loc[sct], marker="o", label=sct)
    ax.set_yscale("log"); ax.set_ylabel("AVE (%, log scale)"); ax.set_xlabel("Year"); ax.legend(fontsize=8, ncol=2); ax.grid(alpha=.3)
    plt.tight_layout(); plt.savefig(out / "fig2_ave.png"); plt.close()

    # Fig. 3 - TVI with Monte Carlo intervals
    tv = res["tvi"].sort_values("TVI"); mc = res["mc"].reindex(tv.index)
    fig, ax = plt.subplots(figsize=(7, 3.8)); y = range(len(tv))
    ax.barh(y, tv["TVI"], color=BLUE, label="TVI-CBAM (baseline)")
    ax.errorbar(mc["TVI median"], y, xerr=[mc["TVI median"] - mc["CI 90% low"], mc["CI 90% high"] - mc["TVI median"]],
                fmt="o", color=RED, capsize=3, label="Monte Carlo median, 90% interval")
    ax.set_yticks(list(y)); ax.set_yticklabels([f"{i}  (P1={mc.loc[i, 'P(rank=1) (%)']:.1f}%)" for i in tv.index])
    ax.set_xlabel("Index value"); ax.legend(fontsize=8, loc="lower right")
    plt.tight_layout(); plt.savefig(out / "fig3_tvi.png"); plt.close()

    # Fig. 4 - burden
    b = res["burden"]
    fig, ax = plt.subplots(figsize=(6.5, 3.8)); x = b["Year"].astype(str)
    ax.bar(x, b["Full (M USD)"], color=BLUE)
    for i, v in enumerate(b["Full (M USD)"]):
        ax.text(i, v, f"{v:.1f}", ha="center", va="bottom", fontsize=8)
    ax2 = ax.twinx(); ax2.plot(x, b["EUA (EUR)"], color=RED, marker="s"); ax2.set_ylabel("EUA price (EUR/tCO2)", color=RED)
    ax.set_ylabel("Certificate burden (USD million)")
    plt.tight_layout(); plt.savefig(out / "fig4_burden.png"); plt.close()

    # Fig. 5 - threshold
    t = res["threshold"]
    fig, ax = plt.subplots(figsize=(6.5, 3.8))
    ax.plot(t["Year"], t["Threshold (tCO2e/t)"], marker="o", color=BLUE)
    ax.fill_between(t["Year"], 0, t["Threshold (tCO2e/t)"], alpha=.15, color=BLUE)
    ax.set_ylabel("Threshold verified intensity (tCO2e/t)"); ax.set_xlabel("Year"); ax.grid(alpha=.3)
    ax.text(t["Year"].iloc[0] + 0.2, 0.35, f"Verified actual data ({inp.config['threshold']['actual_route']} benchmark)\n"
            "lowers liability below the line", fontsize=8)
    plt.tight_layout(); plt.savefig(out / "fig5_threshold.png"); plt.close()
