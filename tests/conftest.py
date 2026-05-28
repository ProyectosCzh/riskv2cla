"""
Shared test fixtures and configuration for SmartRisk tests.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import pytest
import numpy as np
import pandas as pd


@pytest.fixture
def data_dir(tmp_path):
    """Create a temporary data directory for test isolation."""
    return tmp_path / "data"


@pytest.fixture
def patch_repos_settings(data_dir, monkeypatch):
    """Redirect all repositories data dirs to a temp directory.

    This prevents tests from polluting the real data/ directory
    and ensures each test starts with a clean state.
    """
    import database.repositories as repos
    for sub in ["users", "portfolios", "simulations", "risk_results"]:
        (data_dir / sub).mkdir(parents=True)
        monkeypatch.setattr(repos, sub.upper() + "_DIR", data_dir / sub)
    return data_dir


@pytest.fixture
def mock_market_data(monkeypatch):
    """Mock download_multiple to return fake price data (no yfinance needed)."""
    def fake_download(tickers, years):
        dates = pd.bdate_range("2020-01-01", "2024-12-31")
        n = len(dates)
        prices = {}
        for t in tickers:
            seed = abs(hash(t)) % (2**31)
            rng = np.random.default_rng(seed)
            rets = rng.normal(0.0004, 0.012, n)
            prices[t] = pd.Series(100 * np.exp(np.cumsum(rets)), index=dates, name=t)
        return prices

    import services.portfolio_service as ps
    monkeypatch.setattr(ps, "download_multiple", fake_download)

    from core.market import downloader
    monkeypatch.setattr(downloader, "download_multiple", fake_download)
