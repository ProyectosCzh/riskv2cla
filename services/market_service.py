"""
SmartRisk - Market Service
Thin wrapper around downloader for UI-layer convenience.
"""
import json
from pathlib import Path
from typing import Optional

import pandas as pd

from core.market.downloader import download_prices, compute_stats, compute_returns


CONFIG_DIR = Path(__file__).resolve().parent.parent / "config"


def get_asset_catalog() -> dict:
    with open(CONFIG_DIR / "assets.json", encoding="utf-8") as f:
        return json.load(f)


def get_asset_info(ticker: str) -> Optional[dict]:
    catalog = get_asset_catalog()
    for items in catalog["categories"].values():
        for asset in items:
            if asset["ticker"] == ticker:
                return asset
    return None


def fetch_asset_stats(ticker: str, years: int = 5) -> Optional[dict]:
    """Download price data and return annualized statistics."""
    prices = download_prices(ticker, years)
    if prices is None:
        return None
    stats = compute_stats(prices)
    returns = compute_returns(prices)
    stats["n_observations"] = int(len(prices))
    stats["start_date"] = str(prices.index.min().date())
    stats["end_date"]   = str(prices.index.max().date())
    stats["last_price"] = float(prices.iloc[-1])
    return stats


def get_quick_stats_table(tickers: list[str], years: int = 5) -> pd.DataFrame:
    """Return a DataFrame with stats for multiple tickers."""
    rows = []
    for t in tickers:
        s = fetch_asset_stats(t, years)
        if s:
            rows.append({
                "Ticker": t,
                "Último Precio": f"${s['last_price']:.2f}",
                "Retorno Anual": f"{s['mu']:.2%}",
                "Volatilidad": f"{s['sigma']:.2%}",
                "Max Drawdown": f"{s['max_drawdown']:.2%}",
                "Observaciones": s["n_observations"],
                "Inicio": s["start_date"],
            })
    return pd.DataFrame(rows)


def get_risk_profiles() -> dict:
    """Loads risk profiles from JSON file."""
    path = CONFIG_DIR / "risk_profiles.json"
    with open(path, encoding="utf-8") as f:
        return json.load(f)
