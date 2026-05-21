"""
Tests for Financial Metrics Library.
Run with: pytest tests/test_metrics.py -v
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import numpy as np
import pandas as pd
import pytest

from core.finance.metrics import (
    annualized_return,
    annualized_volatility,
    sharpe_ratio,
    sortino_ratio,
    max_drawdown,
    value_at_risk,
    conditional_var,
    calmar_ratio,
    compute_all_metrics,
)


# Use deterministic seeds — avoid unlucky random draws
RNG = np.random.default_rng(2024)
# Force genuinely positive drift: baseline + noise
_noise = RNG.normal(0, 0.010, 252)
GOOD_RETURNS    = np.full(252, 0.0005) + _noise          # ~12.6% annual mean
BAD_RETURNS     = np.full(252, -0.003) + RNG.normal(0, 0.015, 252)  # losing
NEUTRAL_RETURNS = np.zeros(252)


def _cum_prices(returns):
    return pd.Series(np.cumprod(1 + returns) * 100)


class TestAnnualizedReturn:
    def test_positive_drift_gives_positive_return(self):
        r = annualized_return(GOOD_RETURNS)
        assert r > 0

    def test_negative_drift_gives_negative_return(self):
        r = annualized_return(BAD_RETURNS)
        assert r < 0

    def test_zero_returns_give_zero(self):
        r = annualized_return(NEUTRAL_RETURNS)
        assert abs(r) < 1e-10

    def test_empty_returns_give_zero(self):
        assert annualized_return(np.array([])) == 0.0


class TestAnnualizedVolatility:
    def test_positive_for_noisy_returns(self):
        v = annualized_volatility(GOOD_RETURNS)
        assert v > 0

    def test_zero_for_constant_returns(self):
        v = annualized_volatility(NEUTRAL_RETURNS)
        assert v == 0.0

    def test_higher_noise_higher_vol(self):
        low  = RNG.normal(0, 0.005, 500)
        high = RNG.normal(0, 0.030, 500)
        assert annualized_volatility(high) > annualized_volatility(low)


class TestSharpeRatio:
    def test_positive_for_good_portfolio(self):
        s = sharpe_ratio(GOOD_RETURNS, rf=0.02)
        assert s > 0

    def test_negative_for_bad_portfolio(self):
        s = sharpe_ratio(BAD_RETURNS, rf=0.04)
        assert s < 0

    def test_zero_vol_returns_zero(self):
        s = sharpe_ratio(NEUTRAL_RETURNS)
        assert s == 0.0

    def test_higher_rf_lowers_sharpe(self):
        s1 = sharpe_ratio(GOOD_RETURNS, rf=0.02)
        s2 = sharpe_ratio(GOOD_RETURNS, rf=0.08)
        assert s1 > s2


class TestSortinoRatio:
    def test_inf_when_no_downside(self):
        all_positive = np.abs(RNG.normal(0.001, 0.005, 252))
        s = sortino_ratio(all_positive, rf=0.0)
        assert s == float("inf") or s > 10  # very high or inf

    def test_negative_for_consistently_losing_portfolio(self):
        s = sortino_ratio(BAD_RETURNS, rf=0.04)
        assert s < 0


class TestMaxDrawdown:
    def test_returns_negative_or_zero(self):
        prices = _cum_prices(GOOD_RETURNS)
        mdd = max_drawdown(prices)
        assert mdd <= 0

    def test_monotonic_prices_zero_drawdown(self):
        prices = pd.Series(np.linspace(100, 200, 252))
        assert max_drawdown(prices) == 0.0

    def test_crash_gives_large_drawdown(self):
        prices = pd.Series([100, 120, 140, 60, 70, 80])  # crash from 140 to 60
        mdd = max_drawdown(prices)
        assert mdd < -0.40  # at least -42%

    def test_numpy_array_input(self):
        arr = np.array([100, 110, 90, 95, 105])
        mdd = max_drawdown(arr)
        expected = (90 - 110) / 110
        assert abs(mdd - expected) < 1e-6


class TestVaR:
    def test_var_positive(self):
        v = value_at_risk(GOOD_RETURNS, 0.95)
        assert v >= 0

    def test_higher_confidence_higher_var(self):
        v90 = value_at_risk(GOOD_RETURNS, 0.90)
        v99 = value_at_risk(GOOD_RETURNS, 0.99)
        assert v99 >= v90

    def test_cvar_greater_than_or_equal_var(self):
        var  = value_at_risk(GOOD_RETURNS, 0.95)
        cvar = conditional_var(GOOD_RETURNS, 0.95)
        assert cvar >= var - 1e-10


class TestAllMetrics:
    def test_all_keys_present(self):
        returns = GOOD_RETURNS
        prices  = _cum_prices(returns)
        metrics = compute_all_metrics(returns, prices)
        required = {
            "annualized_return", "annualized_volatility", "sharpe_ratio",
            "sortino_ratio", "max_drawdown", "var_95", "cvar_95", "calmar_ratio",
        }
        assert required.issubset(metrics.keys())

    def test_values_are_finite(self):
        returns = GOOD_RETURNS
        prices  = _cum_prices(returns)
        metrics = compute_all_metrics(returns, prices)
        for k, v in metrics.items():
            if v != float("inf"):
                assert np.isfinite(v), f"{k} is not finite: {v}"
