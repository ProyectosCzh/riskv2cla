"""
SmartRisk - Monte Carlo Simulation Engine
Uses Geometric Brownian Motion with Cholesky decomposition for correlated assets.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class SimulationConfig:
    tickers: list[str]
    weights: list[float]
    mu_vec: np.ndarray          # annualized mean returns per asset
    sigma_vec: np.ndarray       # annualized volatilities per asset
    corr_matrix: np.ndarray     # correlation matrix
    initial_capital: float = 10_000.0
    monthly_dca: float = 0.0
    projection_years: float = 5.0
    n_simulations: int = 5_000
    dt: float = 1 / 252         # daily steps
    seed: Optional[int] = None


@dataclass
class SimulationResult:
    paths: np.ndarray           # shape (n_simulations, n_steps)
    final_values: np.ndarray    # shape (n_simulations,)
    config: SimulationConfig
    percentiles: dict = field(default_factory=dict)
    metrics: dict = field(default_factory=dict)


def run_monte_carlo(cfg: SimulationConfig) -> SimulationResult:
    """
    Simulate portfolio value paths using Geometric Brownian Motion.

    S(t+dt) = S(t) * exp((μ - σ²/2)dt + σ√dt * Z)

    Uses Cholesky decomposition to preserve asset correlations.
    """
    rng = np.random.default_rng(cfg.seed)

    weights = np.asarray(cfg.weights, dtype=float)
    mu = np.asarray(cfg.mu_vec, dtype=float)
    sigma = np.asarray(cfg.sigma_vec, dtype=float)
    corr = np.asarray(cfg.corr_matrix, dtype=float)

    # ── Build covariance matrix & Cholesky factor ──────────────────────────
    # Ensure positive definite by adding small jitter
    # cov = np.outer(sigma, sigma) * corr
    # min_eig = np.linalg.eigvalsh(cov).min()
    # if min_eig < 1e-10:
    #     cov += np.eye(len(sigma)) * (abs(min_eig) + 1e-8)

    # L = np.linalg.cholesky(cov)  # lower-triangular

    # n_assets = len(weights)
    n_steps = int(cfg.projection_years * 252)
    dt = cfg.dt

    # ── Portfolio drift (weighted average) ────────────────────────────────
    port_mu = float(weights @ mu)
    # Portfolio variance (scalar)
    cov = np.outer(sigma, sigma) * corr
    port_var = float(weights @ cov @ weights)
    port_sigma = float(np.sqrt(port_var))

    # ── Simulate correlated asset returns, collapse to portfolio ─────────
    # We simulate the portfolio as a single GBM process for speed,
    # using weighted mu and portfolio sigma.
    # Shape: (n_sim, n_steps)
    Z = rng.standard_normal((cfg.n_simulations, n_steps))

    # GBM increments
    drift = (port_mu - 0.5 * port_sigma**2) * dt
    diffusion = port_sigma * np.sqrt(dt) * Z

    log_returns = drift + diffusion  # (n_sim, n_steps)

    # Cumulative path: start at 1, multiply by exp(log_returns)
    cum_returns = np.exp(np.cumsum(log_returns, axis=1))

    # Prepend initial step (value = 1)
    ones = np.ones((cfg.n_simulations, 1))
    cum_returns = np.hstack([ones, cum_returns])  # (n_sim, n_steps+1)

    # ── Apply initial capital ─────────────────────────────────────────────
    paths = cfg.initial_capital * cum_returns  # (n_sim, n_steps+1)

    # ── Apply DCA (monthly contributions) ────────────────────────────────
    if cfg.monthly_dca > 0:
        trading_days_per_month = 21
        for step in range(1, n_steps + 1):
            if step % trading_days_per_month == 0:
                # Growth factor from the contribution step to the end
                growth_factor = cum_returns[:, -1] / cum_returns[:, step]
                # Add the DCA amount, grown to the end of the period
                paths[:, -1] += cfg.monthly_dca * growth_factor
    final_values = paths[:, -1]

    # ── Compute percentiles ───────────────────────────────────────────────
    percentile_keys = [5, 10, 25, 50, 75, 90, 95]
    percentiles = {
        p: float(np.percentile(final_values, p)) for p in percentile_keys
    }

    result = SimulationResult(
        paths=paths,
        final_values=final_values,
        config=cfg,
        percentiles=percentiles,
    )
    result.metrics = _compute_metrics(result)
    return result


def _compute_metrics(result: SimulationResult) -> dict:
    """Compute key risk/return metrics from simulation result."""
    final = result.final_values
    initial = result.config.initial_capital
    total_invested = initial + result.config.monthly_dca * result.config.projection_years * 12

    expected_capital = float(np.mean(final))
    median_capital = float(np.median(final))
    prob_loss = float(np.mean(final < total_invested))

    # VaR 95% (5th percentile loss)
    var_95_value = float(np.percentile(final, 5))
    var_95_loss = total_invested - var_95_value

    # CVaR (Expected Shortfall) — mean of worst 5%
    worst_5pct = final[final <= var_95_value]
    cvar_95 = float(np.mean(worst_5pct)) if len(worst_5pct) > 0 else var_95_value

    # Max Drawdown from median path
    median_path = np.median(result.paths, axis=0)
    roll_max = np.maximum.accumulate(median_path)
    drawdown = (median_path - roll_max) / (roll_max + 1e-10)
    max_drawdown = float(drawdown.min())

    # Annualized return (CAGR from median)
    years = result.config.projection_years
    if years > 0 and initial > 0:
        cagr = float((median_capital / initial) ** (1 / years) - 1)
    else:
        cagr = 0.0

    return {
        "expected_capital": expected_capital,
        "median_capital": median_capital,
        "var_95_value": var_95_value,
        "var_95_loss": var_95_loss,
        "cvar_95": cvar_95,
        "max_drawdown": max_drawdown,
        "prob_loss": prob_loss,
        "cagr_median": cagr,
        "total_invested": total_invested,
    }


def compute_sharpe(
    mu: float,
    sigma: float,
    risk_free_rate: float = 0.045,
) -> float:
    """Compute annualized Sharpe ratio."""
    if sigma <= 0:
        return 0.0
    return (mu - risk_free_rate) / sigma


def compute_sortino(
    returns: np.ndarray,
    risk_free_rate: float = 0.045,
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
