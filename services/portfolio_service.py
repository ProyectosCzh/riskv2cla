"""
SmartRisk - Portfolio Service
Orchestrates market data download, statistics computation, and optimization.
"""
from typing import Optional
import numpy as np
import pandas as pd

from core.market.downloader import (
    download_multiple,
    compute_returns,
    compute_stats,
    build_correlation_matrix,
)
from core.finance.markowitz import (
    optimize_max_sharpe,
    optimize_min_variance,
    generate_efficient_frontier,
    OptimizationResult,
)
from core.finance.metrics import compute_all_metrics
from config.settings import RISK_FREE_RATE


class PortfolioData:
    """Container for all computed portfolio data."""

    def __init__(
        self,
        tickers: list[str],
        weights: list[float],
        prices: dict[str, pd.Series],
        stats: dict[str, dict],
        returns_df: pd.DataFrame,
        corr_matrix: pd.DataFrame,
    ):
        self.tickers = tickers
        self.weights = np.array(weights)
        self.prices = prices
        self.stats = stats
        self.returns_df = returns_df
        self.corr_matrix = corr_matrix

        self.mu_vec = np.array([stats[t]["mu"] for t in tickers])
        self.sigma_vec = np.array([stats[t]["sigma"] for t in tickers])
        self.corr_array = corr_matrix.values

    @property
    def portfolio_mu(self) -> float:
        return float(self.weights @ self.mu_vec)

    @property
    def portfolio_sigma(self) -> float:
        cov = np.outer(self.sigma_vec, self.sigma_vec) * self.corr_array
        return float(np.sqrt(self.weights @ cov @ self.weights))

    @property
    def portfolio_sharpe(self) -> float:
        sigma = self.portfolio_sigma
        if sigma <= 0:
            return 0.0
        return (self.portfolio_mu - RISK_FREE_RATE) / sigma

    def portfolio_returns(self) -> np.ndarray:
        """Weighted daily returns of the portfolio."""
        aligned = self.returns_df[self.tickers].dropna()
        return (aligned * self.weights).sum(axis=1).values

    def historical_metrics(self) -> dict:
        port_ret = self.portfolio_returns()
        # Weighted price series (approximate)
        first_prices = {t: self.prices[t] for t in self.tickers}
        df = pd.DataFrame(first_prices).dropna()
        normed = df / df.iloc[0]
        port_prices = sum(normed[t] * w for t, w in zip(self.tickers, self.weights))
        return compute_all_metrics(port_ret, port_prices, RISK_FREE_RATE)

    def risk_profile_check(self, user_profile: str) -> dict:
        """
        Check if portfolio volatility matches user's risk profile.
        Returns dict with 'ok', 'level', and 'message'.
        """
        vol = self.portfolio_sigma
        thresholds = {
            "conservador": 0.12,
            "moderado": 0.20,
            "agresivo": 1.0,
        }
        limit = thresholds.get(user_profile, 1.0)
        if vol <= limit:
            return {"ok": True, "message": "✅ La volatilidad del portafolio es compatible con tu perfil de riesgo."}
        else:
            msgs = {
                "conservador": f"⚠️ Tu portafolio tiene una volatilidad anual de {vol:.1%}, superior al límite del perfil Conservador (12%). Considera reducir activos de alto riesgo.",
                "moderado": f"⚠️ Tu portafolio tiene una volatilidad anual de {vol:.1%}, superior al límite del perfil Moderado (20%). Considera diversificar hacia bonos.",
            }
            return {"ok": False, "message": msgs.get(user_profile, "⚠️ Portafolio fuera del perfil de riesgo.")}


def build_portfolio_data(
    tickers: list[str],
    weights: list[float],
    history_years: int = 5,
) -> Optional[PortfolioData]:
    """
    Download market data and compute all portfolio statistics.
    Returns None if data is unavailable.
    """
    prices_dict = download_multiple(tickers, history_years)
    missing = [t for t in tickers if t not in prices_dict]
    if missing:
        return None

    stats = {t: compute_stats(prices_dict[t]) for t in tickers}
    returns_df, corr_matrix = build_correlation_matrix(prices_dict)

    # Ensure corr has all requested tickers
    available = [t for t in tickers if t in corr_matrix.columns]
    corr_matrix = corr_matrix.loc[available, available]

    return PortfolioData(
        tickers=available,
        weights=[weights[i] for i, t in enumerate(tickers) if t in available],
        prices=prices_dict,
        stats=stats,
        returns_df=returns_df,
        corr_matrix=corr_matrix,
    )


def run_markowitz_optimization(
    portfolio_data: PortfolioData,
    method: str = "max_sharpe",
) -> OptimizationResult:
    """Run Markowitz optimization on existing portfolio data."""
    mu = portfolio_data.mu_vec
    sigma = portfolio_data.sigma_vec
    corr = portfolio_data.corr_array
    cov = np.outer(sigma, sigma) * corr

    if method == "max_sharpe":
        return optimize_max_sharpe(mu, cov, RISK_FREE_RATE, portfolio_data.tickers)
    else:
        return optimize_min_variance(mu, cov, RISK_FREE_RATE, portfolio_data.tickers)


def compute_efficient_frontier(portfolio_data: PortfolioData) -> pd.DataFrame:
    mu = portfolio_data.mu_vec
    sigma = portfolio_data.sigma_vec
    corr = portfolio_data.corr_array
    cov = np.outer(sigma, sigma) * corr
    return generate_efficient_frontier(mu, cov, RISK_FREE_RATE)
