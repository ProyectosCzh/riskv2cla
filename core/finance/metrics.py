"""
SmartRisk - Financial Metrics Library
"""
import numpy as np
import pandas as pd


def annualized_return(returns: np.ndarray, periods_per_year: int = 252) -> float:
    """Geometric annualized return from period returns."""
    if len(returns) == 0:
        return 0.0
    compound = np.prod(1 + returns)
    n = len(returns)
    return float(compound ** (periods_per_year / n) - 1)


def annualized_volatility(returns: np.ndarray, periods_per_year: int = 252) -> float:
    """Annualized standard deviation from period returns."""
    return float(np.std(returns, ddof=1) * np.sqrt(periods_per_year))


def sharpe_ratio(returns: np.ndarray, rf: float = 0.035, periods_per_year: int = 252) -> float:
    """Annualized Sharpe ratio."""
    mu = annualized_return(returns, periods_per_year)
    sigma = annualized_volatility(returns, periods_per_year)
    if sigma <= 0:
        return 0.0
    return (mu - rf) / sigma


def sortino_ratio(returns: np.ndarray, rf: float = 0.035, periods_per_year: int = 252) -> float:
    """Sortino ratio using downside deviation."""
    mu = annualized_return(returns, periods_per_year)
    daily_rf = (1 + rf) ** (1 / periods_per_year) - 1
    downside = returns[returns < daily_rf]
    if len(downside) == 0:
        return float("inf")
    downside_std = float(np.std(downside, ddof=1) * np.sqrt(periods_per_year))
    if downside_std <= 0:
        return 0.0
    return (mu - rf) / downside_std


def max_drawdown(prices: pd.Series | np.ndarray) -> float:
    """Maximum drawdown from peak to trough."""
    arr = np.asarray(prices, dtype=float)
    peak = np.maximum.accumulate(arr)
    dd = (arr - peak) / (peak + 1e-10)
    return float(dd.min())


def value_at_risk(returns: np.ndarray, confidence: float = 0.95) -> float:
    """
    Historical VaR at given confidence level.
    Returns positive number representing loss.
    """
    return float(-np.percentile(returns, (1 - confidence) * 100))


def conditional_var(returns: np.ndarray, confidence: float = 0.95) -> float:
    """
    Expected Shortfall (CVaR) — mean loss beyond VaR.
    Returns positive number.
    """
    var = value_at_risk(returns, confidence)
    tail = returns[returns <= -var]
    if len(tail) == 0:
        return var
    return float(-tail.mean())


def calmar_ratio(returns: np.ndarray, prices: pd.Series) -> float:
    """Calmar ratio: annualized return / absolute max drawdown."""
    mu = annualized_return(returns)
    mdd = abs(max_drawdown(prices))
    if mdd <= 0:
        return 0.0
    return mu / mdd


def compute_all_metrics(
    returns: np.ndarray,
    prices: pd.Series,
    rf: float = 0.035,
) -> dict:
    """Compute a full set of metrics from return series and price series."""
    return {
        "annualized_return": annualized_return(returns),
        "annualized_volatility": annualized_volatility(returns),
        "sharpe_ratio": sharpe_ratio(returns, rf),
        "sortino_ratio": sortino_ratio(returns, rf),
        "max_drawdown": max_drawdown(prices),
        "var_95": value_at_risk(returns, 0.95),
        "cvar_95": conditional_var(returns, 0.95),
        "calmar_ratio": calmar_ratio(returns, prices),
    }
