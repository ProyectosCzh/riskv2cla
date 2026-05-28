"""
Tests for Monte Carlo simulation engine.
Run with: pytest tests/test_monte_carlo.py -v
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import numpy as np
import pytest

from core.finance.monte_carlo import (
    SimulationConfig,
    run_monte_carlo,
)


def _simple_config(**overrides) -> SimulationConfig:
    defaults = dict(
        tickers=["SPY", "BND"],
        weights=[0.6, 0.4],
        mu_vec=np.array([0.10, 0.04]),
        sigma_vec=np.array([0.18, 0.05]),
        corr_matrix=np.array([[1.0, -0.1], [-0.1, 1.0]]),
        initial_capital=10_000.0,
        monthly_dca=0.0,
        projection_years=5.0,
        n_simulations=500,
        seed=42,
    )
    defaults.update(overrides)
    return SimulationConfig(**defaults)


# ── Test-only helpers (moved from core/finance/monte_carlo.py) ──────────

def compute_sharpe(
    mu: float,
    sigma: float,
    risk_free_rate: float = 0.035,
) -> float:
    """Compute annualized Sharpe ratio from model parameters."""
    if sigma <= 0:
        return 0.0
    return (mu - risk_free_rate) / sigma


def compute_sortino(
    returns: np.ndarray,
    risk_free_rate: float = 0.035,
) -> float:
    """Compute Sortino ratio from array of returns."""
    annual_ret = float(np.mean(returns) * 252)
    downside = returns[returns < 0]
    if len(downside) == 0:
        return float("inf")
    downside_std = float(np.std(downside) * np.sqrt(252))
    if downside_std == 0:
        return 0.0
    return (annual_ret - risk_free_rate) / downside_std


class TestMonteCarloBasics:
    def test_paths_shape(self):
        cfg = _simple_config(n_simulations=200, projection_years=3.0)
        result = run_monte_carlo(cfg)
        expected_steps = int(3.0 * 252) + 1
        assert result.paths.shape == (200, expected_steps)

    def test_initial_value_equals_capital(self):
        cfg = _simple_config(initial_capital=15_000.0)
        result = run_monte_carlo(cfg)
        np.testing.assert_allclose(result.paths[:, 0], 15_000.0, rtol=1e-6)

    def test_final_values_match_last_column(self):
        cfg = _simple_config()
        result = run_monte_carlo(cfg)
        np.testing.assert_array_equal(result.final_values, result.paths[:, -1])

    def test_all_paths_positive(self):
        cfg = _simple_config()
        result = run_monte_carlo(cfg)
        assert np.all(result.paths > 0), "All path values must be positive (GBM property)"

    def test_percentiles_ordered(self):
        cfg = _simple_config()
        result = run_monte_carlo(cfg)
        p = result.percentiles
        assert p[5] <= p[25] <= p[50] <= p[75] <= p[95]

    def test_reproducibility_with_seed(self):
        cfg1 = _simple_config(seed=99)
        cfg2 = _simple_config(seed=99)
        r1 = run_monte_carlo(cfg1)
        r2 = run_monte_carlo(cfg2)
        np.testing.assert_array_equal(r1.final_values, r2.final_values)

    def test_different_seeds_differ(self):
        cfg1 = _simple_config(seed=1)
        cfg2 = _simple_config(seed=2)
        r1 = run_monte_carlo(cfg1)
        r2 = run_monte_carlo(cfg2)
        assert not np.allclose(r1.final_values, r2.final_values)


class TestMonteCarloMetrics:
    def setup_method(self):
        self.result = run_monte_carlo(_simple_config(n_simulations=1000))

    def test_metrics_keys_present(self):
        required = {
            "expected_capital", "median_capital", "var_95_value", "var_95_loss",
            "cvar_95", "max_drawdown", "prob_loss", "cagr_median", "total_invested",
        }
        assert required.issubset(set(self.result.metrics.keys()))

    def test_median_capital_positive(self):
        assert self.result.metrics["median_capital"] > 0

    def test_var_less_than_median(self):
        assert self.result.metrics["var_95_value"] <= self.result.metrics["median_capital"]

    def test_cvar_less_than_or_equal_var(self):
        assert self.result.metrics["cvar_95"] <= self.result.metrics["var_95_value"]

    def test_prob_loss_between_0_and_1(self):
        p = self.result.metrics["prob_loss"]
        assert 0.0 <= p <= 1.0

    def test_max_drawdown_negative_or_zero(self):
        assert self.result.metrics["max_drawdown"] <= 0.0


class TestDCAEffect:
    def test_dca_increases_final_capital(self):
        cfg_no_dca  = _simple_config(monthly_dca=0.0,   n_simulations=500)
        cfg_with_dca = _simple_config(monthly_dca=500.0, n_simulations=500)
        r_no  = run_monte_carlo(cfg_no_dca)
        r_dca = run_monte_carlo(cfg_with_dca)
        assert np.median(r_dca.final_values) > np.median(r_no.final_values)


class TestSharpeAndSortino:
    def test_sharpe_positive_for_good_portfolio(self):
        s = compute_sharpe(mu=0.12, sigma=0.18, risk_free_rate=0.04)
        assert s > 0

    def test_sharpe_zero_sigma_returns_zero(self):
        assert compute_sharpe(mu=0.10, sigma=0.0) == 0.0

    def test_sortino_with_no_downside_returns_inf(self):
        returns = np.array([0.01, 0.02, 0.03, 0.05])
        s = compute_sortino(returns, risk_free_rate=0.0)
        assert s == float("inf")

    def test_sortino_negative_returns_portfolio(self):
        rng = np.random.default_rng(7)
        returns = rng.normal(-0.001, 0.015, 250)
        s = compute_sortino(returns, risk_free_rate=0.04)
        assert s < 0
