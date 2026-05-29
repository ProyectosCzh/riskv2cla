"""
SmartRisk - Simulation Service
Orchestrates Monte Carlo runs and persists results.
"""
from typing import Optional

from core.finance.monte_carlo import SimulationConfig, SimulationResult, run_monte_carlo
from services.portfolio_service import PortfolioData
from database.repositories import save_simulation
from config.settings import DEFAULT_SIMULATIONS


def run_simulation(
    portfolio_data: PortfolioData,
    initial_capital: float = 10_000.0,
    monthly_dca: float = 0.0,
    projection_years: float = 5.0,
    n_simulations: int = DEFAULT_SIMULATIONS,
    seed: Optional[int] = 42,
) -> SimulationResult:
    """
    Run a full Monte Carlo simulation for a portfolio.
    """
    cfg = SimulationConfig(
        tickers=portfolio_data.tickers,
        weights=portfolio_data.weights.tolist(),
        mu_vec=portfolio_data.mu_vec,
        sigma_vec=portfolio_data.sigma_vec,
        corr_matrix=portfolio_data.corr_array,
        initial_capital=initial_capital,
        monthly_dca=monthly_dca,
        projection_years=projection_years,
        n_simulations=n_simulations,
        seed=seed,
    )
    return run_monte_carlo(cfg)


def persist_simulation(
    user_id: str,
    portfolio_data: PortfolioData,
    result: SimulationResult,
) -> dict:
    """Save simulation summary to JSON store."""
    config_payload = {
        "tickers": portfolio_data.tickers,
        "weights": portfolio_data.weights.tolist(),
        "initial_capital": result.config.initial_capital,
        "monthly_dca": result.config.monthly_dca,
        "projection_years": result.config.projection_years,
        "n_simulations": result.config.n_simulations,
    }
    return save_simulation(user_id, config_payload, result.metrics)
