"""Regression tests: the published results must be reproduced from data/."""
import pytest

from cbam_tvi.ave import ave_table
from cbam_tvi.burden import breakeven_table, burden_table, threshold_table
from cbam_tvi.data import load_inputs
from cbam_tvi.montecarlo import simulate
from cbam_tvi.tvi import tvi_table


@pytest.fixture(scope="module")
def inp():
    return load_inputs()


def test_ave(inp):
    a = ave_table(inp)
    assert a.loc["Iron & Steel", 2026] == pytest.approx(13.02, abs=0.01)
    assert a.loc["Iron & Steel", 2034] == pytest.approx(78.71, abs=0.01)
    assert a.loc["Cement", 2034] == pytest.approx(315.31, abs=0.01)


def test_tvi_ranking(inp):
    t = tvi_table(inp).sort_values("TVI", ascending=False)
    assert list(t.index[:3]) == ["Iron & Steel", "Steel Articles", "Aluminium"]
    assert t.loc["Iron & Steel", "TVI"] == pytest.approx(0.5654, abs=1e-4)


def test_monte_carlo(inp):
    mc = simulate(inp)
    assert mc.loc["Iron & Steel", "P(rank=1) (%)"] == pytest.approx(79.8, abs=0.05)


def test_burden_breakeven_threshold(inp):
    b = burden_table(inp).set_index("Year")
    assert b.loc[2026, "Full (M USD)"] == pytest.approx(9.15, abs=0.01)
    assert b.loc[2034, "Full (M USD)"] == pytest.approx(55.71, abs=0.01)
    assert breakeven_table(inp).loc["Aluminium", "Break-even (EUR/tCO2)"] == pytest.approx(101.4, abs=0.05)
    th = threshold_table(inp).set_index("Year")["Threshold (tCO2e/t)"]
    assert th[2026] == pytest.approx(1.273, abs=1e-3) and th[2034] == pytest.approx(2.522, abs=1e-3)


def test_markup_rules(inp):
    assert inp.markup("Iron & Steel", 2026) == 0.10
    assert inp.markup("Iron & Steel", 2031) == 0.30
    assert inp.markup("Fertilisers", 2034) == 0.01
