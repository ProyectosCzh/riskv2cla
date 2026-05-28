"""
Integration tests - full user workflow.
Run with: pytest tests/test_integration.py -v
"""
import pytest
import numpy as np

from database.repositories import (
    ensure_admin_exists, get_all_users, create_user, delete_user,
    get_user_by_username, get_user_by_email,
    save_portfolio, get_portfolios_for_user, delete_portfolio,
    save_simulation, get_simulations_for_user, delete_simulation,
    save_risk_profile, get_risk_profile_for_user,
)
from auth.auth_service import register_user, authenticate_user
from services.portfolio_service import build_portfolio_data, run_markowitz_optimization
from services.simulation_service import run_simulation, persist_simulation


class TestFullUserWorkflow:
    """Complete user journey from registration to simulation cleanup."""

    def test_complete_flow(self, patch_repos_settings, mock_market_data):
        # 1. Bootstrap admin
        ensure_admin_exists()
        admins = [u for u in get_all_users().values() if u["role"] == "admin"]
        assert len(admins) >= 1

        # 2. Register new user
        user = register_user("integration_user", "int@test.com", "TestP@ss123")
        assert user["is_active"] is True
        uid = user["id"]

        # 3. Authenticate with username
        auth = authenticate_user("integration_user", "TestP@ss123")
        assert auth is not None
        assert auth["id"] == uid

        # 4. Authenticate with email
        auth2 = authenticate_user("int@test.com", "TestP@ss123")
        assert auth2 is not None
        assert auth2["id"] == uid

        # 5. Wrong password fails
        assert authenticate_user("integration_user", "wrong") is None

        # 6. Create portfolio
        pf = save_portfolio(uid, "Integration PF", ["AAPL", "MSFT"], [0.6, 0.4])
        assert pf["name"] == "Integration PF"
        ports = get_portfolios_for_user(uid)
        assert len(ports) == 1

        # 7. Save risk profile
        rp = save_risk_profile(uid, "agresivo", 85, [5, 5, 4, 5, 3])
        assert rp["profile"] == "agresivo"
        loaded = get_risk_profile_for_user(uid)
        assert loaded["profile"] == "agresivo"

        # 8. Build portfolio data (uses mock_market_data, no yfinance)
        data = build_portfolio_data(["AAPL", "MSFT"], [0.6, 0.4], history_years=3)
        assert data is not None
        assert data.portfolio_mu != 0
        assert data.portfolio_sigma > 0

        # 9. Risk profile check
        audit = data.risk_profile_check("agresivo")
        assert audit["ok"] is True

        # 10. Markowitz optimization
        opt = run_markowitz_optimization(data, "max_sharpe")
        assert abs(sum(opt.weights) - 1.0) < 1e-5
        assert opt.sharpe_ratio > 0

        # 11. Run Monte Carlo simulation
        result = run_simulation(
            data, initial_capital=10000, projection_years=5, n_simulations=200,
        )
        assert result is not None
        assert result.metrics["median_capital"] > 0
        assert result.metrics["cagr_median"] is not None

        # 12. Persist simulation
        persist_simulation(uid, data, result)
        sims = get_simulations_for_user(uid)
        assert len(sims) == 1
        assert sims[0]["summary"]["median_capital"] > 0

        # 13. Admin sees all users
        all_users = get_all_users()
        usernames = [u["username"] for u in all_users.values()]
        assert "integration_user" in usernames
        assert "admin" in usernames

        # 14. Cleanup in reverse order
        delete_simulation(sims[0]["id"])
        assert len(get_simulations_for_user(uid)) == 0

        delete_portfolio(pf["id"])
        assert len(get_portfolios_for_user(uid)) == 0

        delete_user(uid)
        assert get_user_by_username("integration_user") is None
        assert get_user_by_email("int@test.com") is None


class TestAdminWorkflow:
    """Admin-specific operations."""

    def test_admin_can_list_all_users(self, patch_repos_settings):
        ensure_admin_exists()
        create_user(**dict(
            username="alice", email="alice@test.com",
            hashed_password="h", role="user", full_name="Alice",
        ))
        create_user(**dict(
            username="bob", email="bob@test.com",
            hashed_password="h", role="user", full_name="Bob",
        ))
        all_users = get_all_users()
        assert len(all_users) == 3  # admin + alice + bob

    def test_register_authenticate_simulation_cycle(self, patch_repos_settings, mock_market_data):
        """Minimal cycle: register → auth → simulate → verify."""
        user = register_user("cycle", "cycle@test.com", "CycleP@ss1")
        uid = user["id"]

        auth = authenticate_user("cycle", "CycleP@ss1")
        assert auth is not None

        pf = save_portfolio(uid, "Cycle PF", ["AAPL", "MSFT"], [0.5, 0.5])
        data = build_portfolio_data(["AAPL", "MSFT"], [0.5, 0.5], history_years=3)
        assert data is not None

        result = run_simulation(data, initial_capital=5000, projection_years=3, n_simulations=200)
        persist_simulation(uid, data, result)

        sims = get_simulations_for_user(uid)
        assert len(sims) == 1
        assert sims[0]["summary"]["median_capital"] > 0
