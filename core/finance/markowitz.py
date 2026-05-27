"""
SmartRisk - Markowitz Portfolio Optimization
Efficient Frontier via SciPy SLSQP.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from scipy.optimize import minimize
from dataclasses import dataclass
from typing import Optional


@dataclass
class OptimizationResult:
    weights: np.ndarray
    expected_return: float
    volatility: float
    sharpe_ratio: float
    tickers: list[str]
    method: str  # "max_sharpe" or "min_variance"


def _portfolio_stats(
    weights: np.ndarray,
    mu: np.ndarray,
    cov: np.ndarray,
    rf: float = 0.045,
) -> tuple[float, float, float]:
    """Return (expected_return, volatility, sharpe_ratio)."""
    ret = float(weights @ mu)
    vol = float(np.sqrt(weights @ cov @ weights))
    sharpe = (ret - rf) / vol if vol > 1e-10 else 0.0
    return ret, vol, sharpe


def optimize_max_sharpe(
    mu: np.ndarray,
    cov: np.ndarray,
    rf: float = 0.045,
    tickers: Optional[list[str]] = None,
) -> OptimizationResult:
    """
    Find portfolio weights that maximize the Sharpe ratio.
    Constraints: weights >= 0, sum(weights) = 1.
    """
    n = len(mu)
    x0 = np.ones(n) / n

    def neg_sharpe(w):
        r, v, s = _portfolio_stats(w, mu, cov, rf)
        return -s

    constraints = [{"type": "eq", "fun": lambda w: np.sum(w) - 1}]
    bounds = [(0.05, 1.0)] * n #minimo 5% cada activo

    result = minimize(
        neg_sharpe,
        x0,
        method="SLSQP",
        bounds=bounds,
        constraints=constraints,
        options={"maxiter": 1000, "ftol": 1e-9},
    )

    weights = result.x
    weights = np.clip(weights, 0, 1)
    weights /= weights.sum()

    ret, vol, sharpe = _portfolio_stats(weights, mu, cov, rf)
    return OptimizationResult(
        weights=weights,
        expected_return=ret,
        volatility=vol,
        sharpe_ratio=sharpe,
        tickers=tickers or [str(i) for i in range(n)],
        method="max_sharpe",
    )


def optimize_min_variance(
    mu: np.ndarray,
    cov: np.ndarray,
    rf: float = 0.045,
    tickers: Optional[list[str]] = None,
) -> OptimizationResult:
    """
    Find portfolio weights that minimize total variance.
    Constraints: weights >= 0, sum(weights) = 1.
    """
    n = len(mu)
    x0 = np.ones(n) / n

    def portfolio_variance(w):
        return float(w @ cov @ w)

    constraints = [{"type": "eq", "fun": lambda w: np.sum(w) - 1}]
    bounds = [(0.05, 1.0)] * n

    result = minimize(
        portfolio_variance,
        x0,
        method="SLSQP",
        bounds=bounds,
        constraints=constraints,
        options={"maxiter": 1000, "ftol": 1e-9},
    )

    weights = result.x
    weights = np.clip(weights, 0, 1)
    weights /= weights.sum()

    ret, vol, sharpe = _portfolio_stats(weights, mu, cov, rf)
    return OptimizationResult(
        weights=weights,
        expected_return=ret,
        volatility=vol,
        sharpe_ratio=sharpe,
        tickers=tickers or [str(i) for i in range(n)],
        method="min_variance",
    )


def generate_efficient_frontier(
    mu: np.ndarray,
    cov: np.ndarray,
    rf: float = 0.045,
    n_points: int = 60,
) -> pd.DataFrame:
    """
    Generate (volatility, return, sharpe) points on the efficient frontier
    by sweeping target returns.
    """
    n = len(mu)
    min_ret = float(mu.min())
    max_ret = float(mu.max())
    target_returns = np.linspace(min_ret, max_ret, n_points)

    frontier = []
    x0 = np.ones(n) / n
    bounds = [(0.0, 1.0)] * n

    for target in target_returns:
        constraints = [
            {"type": "eq", "fun": lambda w: np.sum(w) - 1},
            {"type": "eq", "fun": lambda w, t=target: w @ mu - t},
        ]
        res = minimize(
            lambda w: float(w @ cov @ w),
            x0,
            method="SLSQP",
            bounds=bounds,
            constraints=constraints,
            options={"maxiter": 500, "ftol": 1e-9},
        )
        if res.success:
            w = np.clip(res.x, 0, 1)
            w /= w.sum()
            vol = float(np.sqrt(w @ cov @ w))
            ret = float(w @ mu)
            sharpe = (ret - rf) / vol if vol > 1e-10 else 0.0
            frontier.append({"volatility": vol, "return": ret, "sharpe": sharpe})

    return pd.DataFrame(frontier)
