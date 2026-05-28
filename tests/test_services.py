"""
Tests for services module (portfolio_service, simulation_service).
Run with: pytest tests/test_services.py -v
"""
import numpy as np
import pandas as pd
import pytest

from services.portfolio_service import (
    PortfolioData,
    run_markowitz_optimization,
    compute_efficient_frontier,
)
from services.simulation_service import run_simulation


@pytest.fixture
def sample_portfolio_data_2():
    """Create PortfolioData with 2 assets for general property tests."""
    tickers = ["AAPL", "MSFT"]
    weights = [0.6, 0.4]
    dates = pd.bdate_range("2020-01-01", "2024-12-31")
    n = len(dates)
    prices = {}
    stats = {}
    for t in tickers:
        seed = abs(hash(t)) % (2**31)
        rg = np.random.default_rng(seed)
        rets = rg.normal(0.0004, 0.012, n)
        prices[t] = pd.Series(100 * np.exp(np.cumsum(rets)), index=dates, name=t)
        mu = float(np.mean(rets) * 252)
        sigma = float(np.std(rets) * np.sqrt(252))
        stats[t] = {"mu": mu, "sigma": sigma}
    returns_df = pd.DataFrame({t: prices[t].pct_change().dropna() for t in tickers})
    corr = returns_df.corr()
    return PortfolioData(tickers, weights, prices, stats, returns_df, corr)
    


@pytest.fixture
def sample_portfolio_data_3():
    """Create PortfolioData with 3 assets for optimization tests."""
    tickers = ["A", "B", "C"]
    weights = [1/3] * 3
    dates = pd.bdate_range("2020-01-01", "2024-12-31")
    n = len(dates)
    prices = {}
    stats = {}
    for t in tickers:
        seed = abs(hash(t)) % (2**31)
        rg = np.random.default_rng(seed)
        rets = rg.normal(0.0004, 0.012, n)
        prices[t] = pd.Series(100 * np.exp(np.cumsum(rets)), index=dates, name=t)
        mu = float(np.mean(rets) * 252)
        sigma = float(np.std(rets) * np.sqrt(252))
        stats[t] = {"mu": mu, "sigma": sigma}
    returns_df = pd.DataFrame({t: prices[t].pct_change().dropna() for t in tickers})
    corr = returns_df.corr()
    return PortfolioData(tickers, weights, prices, stats, returns_df, corr)
    


class TestPortfolioData:
    def test_portfolio_mu(self, sample_portfolio_data_2):
        mu = sample_portfolio_data_2.portfolio_mu
        assert isinstance(mu, float)
        assert mu != 0

    def test_portfolio_sigma(self, sample_portfolio_data_2):
        sigma = sample_portfolio_data_2.portfolio_sigma
        assert isinstance(sigma, float)
        assert sigma > 0

    def test_portfolio_sigma_nonzero(self, sample_portfolio_data_2):
        assert sample_portfolio_data_2.portfolio_sigma > 1e-8

    def test_portfolio_sharpe(self, sample_portfolio_data_2):
        sharpe = sample_portfolio_data_2.portfolio_sharpe
        assert isinstance(sharpe, float)
        assert -5 < sharpe < 10

    def test_portfolio_sharpe_calculation(self, sample_portfolio_data_2):
        pd_obj = sample_portfolio_data_2
        expected = (pd_obj.portfolio_mu - 0.035) / pd_obj.portfolio_sigma
        assert abs(pd_obj.portfolio_sharpe - expected) < 1e-10


class TestRiskProfileCheck:
    def test_conservador(self, sample_portfolio_data_2):
        result = sample_portfolio_data_2.risk_profile_check("conservador")
        assert "ok" in result
        assert "message" in result

    def test_moderado(self, sample_portfolio_data_2):
        result = sample_portfolio_data_2.risk_profile_check("moderado")
        assert "ok" in result

    def test_agresivo(self, sample_portfolio_data_2):
        result = sample_portfolio_data_2.risk_profile_check("agresivo")
        assert result["ok"] is True

    def test_unknown_profile_defaults_agresivo(self, sample_portfolio_data_2):
        result = sample_portfolio_data_2.risk_profile_check("unknown")
        assert result["ok"] is True  # unknown defaults to threshold 1.0


class TestMarkowitzOptimization:
    def test_max_sharpe_weights_sum_to_one(self, sample_portfolio_data_3):
        result = run_markowitz_optimization(sample_portfolio_data_3, "max_sharpe")
        assert abs(sum(result.weights) - 1.0) < 1e-5

    def test_max_sharpe_weights_non_negative(self, sample_portfolio_data_3):
        result = run_markowitz_optimization(sample_portfolio_data_3, "max_sharpe")
        assert all(w >= -1e-7 for w in result.weights)

    def test_max_sharpe_method_label(self, sample_portfolio_data_3):
        result = run_markowitz_optimization(sample_portfolio_data_3, "max_sharpe")
        assert result.method == "max_sharpe"

    def test_min_variance_weights_sum_to_one(self, sample_portfolio_data_3):
        result = run_markowitz_optimization(sample_portfolio_data_3, "min_variance")
        assert abs(sum(result.weights) - 1.0) < 1e-5

    def test_min_variance_method_label(self, sample_portfolio_data_3):
        result = run_markowitz_optimization(sample_portfolio_data_3, "min_variance")
        assert result.method == "min_variance"

    def test_min_variance_vol_lower_than_max_sharpe(self, sample_portfolio_data_3):
        mv = run_markowitz_optimization(sample_portfolio_data_3, "min_variance")
        ms = run_markowitz_optimization(sample_portfolio_data_3, "max_sharpe")
        assert mv.volatility <= ms.volatility + 1e-4


class TestEfficientFrontier:
    def test_returns_dataframe(self, sample_portfolio_data_3):
        df = compute_efficient_frontier(sample_portfolio_data_3)
        assert isinstance(df, pd.DataFrame)
        assert len(df) > 0

    def test_has_required_columns(self, sample_portfolio_data_3):
        df = compute_efficient_frontier(sample_portfolio_data_3)
        for col in ["volatility", "return", "sharpe"]:
            assert col in df.columns

    def test_returns_increase_with_volatility(self, sample_portfolio_data_3):
        df = compute_efficient_frontier(sample_portfolio_data_3)
        if len(df) >= 6:
            low = df.iloc[:3]["return"].mean()
            high = df.iloc[-3:]["return"].mean()
            assert high >= low - 0.05


class TestSimulationService:
    def test_run_simulation_returns_result(self, sample_portfolio_data_2):
        result = run_simulation(
            sample_portfolio_data_2,
            initial_capital=10000,
            projection_years=3,
            n_simulations=500,
        )
        assert result is not None
        assert result.final_values is not None
        assert len(result.final_values) == 500

    def test_simulation_metrics_present(self, sample_portfolio_data_2):
        result = run_simulation(
            sample_portfolio_data_2,
            initial_capital=10000,
            projection_years=5,
            n_simulations=500,
        )
        required = {
            "expected_capital", "median_capital", "var_95_value",
            "cvar_95", "max_drawdown", "prob_loss", "cagr_median",
            "total_invested", "var_95_loss",
        }
        assert required.issubset(set(result.metrics.keys()))

    def test_simulation_median_positive(self, sample_portfolio_data_2):
        result = run_simulation(
            sample_portfolio_data_2, initial_capital=10000,
            projection_years=3, n_simulations=200,
        )
        assert result.metrics["median_capital"] > 0

    def test_simulation_with_dca(self, sample_portfolio_data_2):
        no_dca = run_simulation(
            sample_portfolio_data_2, initial_capital=10000,
            monthly_dca=0, projection_years=5, n_simulations=200,
        )
        with_dca = run_simulation(
            sample_portfolio_data_2, initial_capital=10000,
            monthly_dca=500, projection_years=5, n_simulations=200,
        )
        assert with_dca.metrics["median_capital"] > no_dca.metrics["median_capital"]

    def test_percentiles_ordered(self, sample_portfolio_data_2):
        result = run_simulation(
            sample_portfolio_data_2, initial_capital=10000,
            projection_years=3, n_simulations=500,
        )
        p = result.percentiles
        assert p[5] <= p[25] <= p[50] <= p[75] <= p[95]
