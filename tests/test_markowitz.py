"""
Tests for Markowitz Portfolio Optimization.
Run with: pytest tests/test_markowitz.py -v
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import numpy as np
import pytest
from core.finance.markowitz import (
    optimize_max_sharpe,
    optimize_min_variance,
    generate_efficient_frontier,
)


def _sample_inputs(n: int = 3):
    rng = np.random.default_rng(0)
    mu  = rng.uniform(0.04, 0.15, n)
    vols = rng.uniform(0.10, 0.35, n)
    # Build valid correlation matrix
    A = rng.standard_normal((n, n))
    corr = A @ A.T
    np.fill_diagonal(corr, 1.0)
    d = np.sqrt(np.diag(corr))
    corr = corr / np.outer(d, d)
    cov  = np.outer(vols, vols) * corr
    tickers = [f"ASSET{i}" for i in range(n)]
    return mu, cov, tickers


class TestMaxSharpe:
    def test_weights_sum_to_one(self):
        mu, cov, tickers = _sample_inputs(4)
        result = optimize_max_sharpe(mu, cov, tickers=tickers)
        assert abs(result.weights.sum() - 1.0) < 1e-5

    def test_weights_non_negative(self):
        mu, cov, tickers = _sample_inputs(4)
        result = optimize_max_sharpe(mu, cov, tickers=tickers)
        assert np.all(result.weights >= -1e-7)

    def test_sharpe_positive(self):
        mu  = np.array([0.10, 0.08, 0.12])
        vols = np.array([0.15, 0.10, 0.20])
        corr = np.eye(3)
        cov  = np.outer(vols, vols) * corr
        result = optimize_max_sharpe(mu, cov, rf=0.03)
        assert result.sharpe_ratio > 0

    def test_method_label(self):
        mu, cov, _ = _sample_inputs(3)
        result = optimize_max_sharpe(mu, cov)
        assert result.method == "max_sharpe"

    def test_tickers_preserved(self):
        mu, cov, tickers = _sample_inputs(5)
        result = optimize_max_sharpe(mu, cov, tickers=tickers)
        assert result.tickers == tickers

    def test_two_assets(self):
        mu  = np.array([0.08, 0.12])
        vols = np.array([0.10, 0.20])
        cov  = np.outer(vols, vols)
        result = optimize_max_sharpe(mu, cov)
        assert abs(result.weights.sum() - 1.0) < 1e-5

    def test_single_asset(self):
        mu  = np.array([0.10])
        cov = np.array([[0.04]])
        result = optimize_max_sharpe(mu, cov)
        np.testing.assert_allclose(result.weights, [1.0], atol=1e-5)


class TestMinVariance:
    def test_weights_sum_to_one(self):
        mu, cov, tickers = _sample_inputs(4)
        result = optimize_min_variance(mu, cov, tickers=tickers)
        assert abs(result.weights.sum() - 1.0) < 1e-5

    def test_weights_non_negative(self):
        mu, cov, tickers = _sample_inputs(5)
        result = optimize_min_variance(mu, cov, tickers=tickers)
        assert np.all(result.weights >= -1e-7)

    def test_method_label(self):
        mu, cov, _ = _sample_inputs(3)
        result = optimize_min_variance(mu, cov)
        assert result.method == "min_variance"

    def test_min_variance_lower_than_max_sharpe(self):
        mu, cov, _ = _sample_inputs(5)
        mv = optimize_min_variance(mu, cov)
        ms = optimize_max_sharpe(mu, cov)
        # min-variance portfolio should have vol <= max-sharpe vol (or close)
        assert mv.volatility <= ms.volatility + 1e-4


class TestEfficientFrontier:
    def test_returns_dataframe(self):
        import pandas as pd
        mu  = np.array([0.08, 0.12, 0.10])
        vols = np.array([0.12, 0.22, 0.16])
        cov  = np.outer(vols, vols) * np.eye(3)
        df = generate_efficient_frontier(mu, cov, n_points=20)
        assert isinstance(df, pd.DataFrame)

    def test_has_required_columns(self):
        mu  = np.array([0.07, 0.13])
        cov = np.diag([0.01, 0.04])
        df = generate_efficient_frontier(mu, cov, n_points=10)
        for col in ["volatility", "return", "sharpe"]:
            assert col in df.columns

    def test_returns_increase_with_volatility(self):
        mu   = np.array([0.06, 0.10, 0.14])
        vols = np.array([0.10, 0.16, 0.24])
        cov  = np.outer(vols, vols) * np.eye(3)
        df   = generate_efficient_frontier(mu, cov, n_points=30).sort_values("volatility")
        if len(df) >= 5:
            # Broadly check monotonicity (some tolerance)
            low_vol  = df.iloc[:3]["return"].mean()
            high_vol = df.iloc[-3:]["return"].mean()
            assert high_vol >= low_vol - 0.01
