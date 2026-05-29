"""
SmartRisk - Market Data Downloader with Local Cache
"""
import json
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd
import yfinance as yf

from config.settings import CACHE_DIR, CACHE_EXPIRY_HOURS, MAX_HISTORY_YEARS


def _cache_path(ticker: str, years: int) -> Path:
    return CACHE_DIR / f"{ticker}_{years}y.json"


def _is_cache_valid(path: Path) -> bool:
    if not path.exists():
        return False
    mtime = datetime.fromtimestamp(path.stat().st_mtime)
    return datetime.now() - mtime < timedelta(hours=CACHE_EXPIRY_HOURS)


def _load_cache(path: Path) -> Optional[pd.Series]:
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        series = pd.Series(data["prices"], dtype=float)
        series.index = pd.to_datetime(data["dates"])
        return series
    except Exception:
        return None


def _save_cache(path: Path, prices: pd.Series) -> None:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    payload = {
        "dates": prices.index.strftime("%Y-%m-%d").tolist(),
        "prices": prices.values.tolist(),
        "cached_at": datetime.now().isoformat(),
    }
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f)


def download_prices(ticker: str, years: int = 5) -> Optional[pd.Series]:
    """
    Download adjusted close prices for a ticker.
    Returns a pandas Series with datetime index or None on failure.
    Uses local JSON cache to avoid repeated downloads.
    """
    years = min(years, MAX_HISTORY_YEARS)
    cache_path = _cache_path(ticker, years)

    if _is_cache_valid(cache_path):
        cached = _load_cache(cache_path)
        if cached is not None and len(cached) > 20:
            return cached

    try:
        end = datetime.now()
        start = end - timedelta(days=int(years * 365.25))
        raw = yf.download(
            ticker,
            start=start.strftime("%Y-%m-%d"),
            end=end.strftime("%Y-%m-%d"),
            progress=False,
            auto_adjust=True,
        )
        if raw.empty:
            return None

        if "Close" in raw.columns:
            prices = raw["Close"].squeeze().dropna()
        else:
            return None

        if len(prices) < 20:
            return None

        _save_cache(cache_path, prices)
        return prices
    except Exception:
        return None


from core.ds.queue import DownloadQueue


def download_multiple(
    tickers: list[str],
    years: int = 5,
    progress_callback=None,
) -> dict[str, pd.Series]:
    """Download prices for multiple tickers using a FIFO queue.
    
    Args:
        tickers: List of ticker symbols to download.
        years: Years of history to download.
        progress_callback: Optional callable(processed, total, current_ticker).
    
    Returns:
        Dict mapping ticker -> price Series.
    """
    queue = DownloadQueue()
    for t in tickers:
        queue.enqueue(t)

    result = {}
    total = queue.size
    processed = 0

    while not queue.is_empty():
        ticker = queue.dequeue()
        series = download_prices(ticker, years)
        if series is not None:
            result[ticker] = series
        processed += 1
        if progress_callback:
            progress_callback(processed, total, ticker)
        time.sleep(0.05)

    return result


def compute_returns(prices: pd.Series) -> pd.Series:
    """Compute daily log returns."""
    return np.log(prices / prices.shift(1)).dropna()


def compute_stats(prices: pd.Series) -> dict:
    """
    Compute annualized mean return, volatility, and max drawdown
    from price series.
    """
    returns = compute_returns(prices)
    mu = float(returns.mean() * 252)
    sigma = float(returns.std() * np.sqrt(252))
    # Max drawdown
    cum = (1 + returns).cumprod()
    roll_max = cum.cummax()
    drawdown = (cum - roll_max) / roll_max
    max_dd = float(drawdown.min())
    return {"mu": mu, "sigma": sigma, "max_drawdown": max_dd}


def build_correlation_matrix(
    prices_dict: dict[str, pd.Series],
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Align price series and compute return correlation matrix.
    Returns (returns_df, corr_matrix).
    """
    aligned = pd.DataFrame(prices_dict).dropna()
    log_returns = np.log(aligned / aligned.shift(1)).dropna()
    corr = log_returns.corr()
    return log_returns, corr
