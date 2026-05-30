"""
Tests for database/repositories.py (per-user sharding).
Run with: pytest tests/test_repositories.py -v
"""
import pytest
from database.repositories import (
    create_user, get_all_users, get_user_by_email, get_user_by_username,
    update_user, delete_user, ensure_admin_exists,
    save_portfolio, get_portfolios_for_user, delete_portfolio,
    save_simulation, get_simulations_for_user, delete_simulation,
    save_risk_profile, get_risk_profile_for_user,
)

SAMPLE_USER = dict(
    username="testuser", email="test@test.com",
    hashed_password="hash123", role="user", full_name="Test User",
)


class TestUserCRUD:
    def test_create_and_get(self, patch_repos_settings):
        u = create_user(**SAMPLE_USER)
        assert u["id"]
        assert u["username"] == "testuser"
        assert u["is_active"] is True

    def test_get_by_email(self, patch_repos_settings):
        create_user(**SAMPLE_USER)
        found = get_user_by_email("test@test.com")
        assert found is not None
        assert found["username"] == "testuser"

    def test_get_by_email_case_insensitive(self, patch_repos_settings):
        create_user(**SAMPLE_USER)
        found = get_user_by_email("TEST@TEST.COM")
        assert found is not None

    def test_get_by_username(self, patch_repos_settings):
        create_user(**SAMPLE_USER)
        found = get_user_by_username("testuser")
        assert found is not None
        assert found["email"] == "test@test.com"

    def test_update_user(self, patch_repos_settings):
        u = create_user(**SAMPLE_USER)
        updated = update_user(u["id"], {"full_name": "Updated"})
        assert updated["full_name"] == "Updated"
        assert updated["updated_at"] != u["created_at"]

    def test_update_nonexistent(self, patch_repos_settings):
        assert update_user("nonexistent", {"x": 1}) is None

    def test_delete_user(self, patch_repos_settings):
        u = create_user(**SAMPLE_USER)
        assert delete_user(u["id"]) is True
        assert get_user_by_email("test@test.com") is None

    def test_delete_nonexistent(self, patch_repos_settings):
        assert delete_user("nonexistent") is False

    def test_get_all_users(self, patch_repos_settings):
        create_user(**SAMPLE_USER)
        create_user(**dict(SAMPLE_USER, username="user2", email="u2@test.com"))
        all_users = get_all_users()
        assert len(all_users) == 2

    def test_get_all_users_empty(self, patch_repos_settings):
        assert get_all_users() == {}

    def test_ensure_admin_creates_admin(self, patch_repos_settings):
        ensure_admin_exists()
        users = get_all_users()
        admins = [u for u in users.values() if u["role"] == "admin"]
        assert len(admins) >= 1

    def test_ensure_admin_idempotent(self, patch_repos_settings):
        ensure_admin_exists()
        count1 = len(get_all_users())
        ensure_admin_exists()
        count2 = len(get_all_users())
        assert count1 == count2


class TestShardingIsolation:
    def test_users_isolated(self, patch_repos_settings):
        u1 = create_user(**SAMPLE_USER)
        u2 = create_user(**dict(SAMPLE_USER, username="user2", email="u2@test.com"))
        all_users = get_all_users()
        assert all_users[u1["id"]]["username"] == "testuser"
        assert all_users[u2["id"]]["username"] == "user2"
        assert u1["id"] != u2["id"]

    def test_portfolios_scoped(self, patch_repos_settings):
        u1 = create_user(**SAMPLE_USER)
        u2 = create_user(**dict(SAMPLE_USER, username="user2", email="u2@test.com"))
        p1 = save_portfolio(u1["id"], "P1", ["AAPL"], [1.0])
        p2 = save_portfolio(u2["id"], "P2", ["MSFT"], [1.0])
        assert len(get_portfolios_for_user(u1["id"])) == 1
        assert get_portfolios_for_user(u1["id"])[0]["name"] == "P1"
        assert get_portfolios_for_user(u2["id"])[0]["name"] == "P2"
        assert p1["id"] != p2["id"]

    def test_simulations_scoped(self, patch_repos_settings):
        u1 = create_user(**SAMPLE_USER)
        u2 = create_user(**dict(SAMPLE_USER, username="user2", email="u2@test.com"))
        s1 = save_simulation(u1["id"], {"tickers": ["A"]}, {"m": 1})
        s2 = save_simulation(u2["id"], {"tickers": ["B"]}, {"m": 2})
        assert len(get_simulations_for_user(u1["id"])) == 1
        assert get_simulations_for_user(u2["id"])[0]["config"]["tickers"] == ["B"]
        assert s1["id"] != s2["id"]


class TestPortfolioCRUD:
    def test_save_and_list(self, patch_repos_settings):
        u = create_user(**SAMPLE_USER)
        p = save_portfolio(u["id"], "Test", ["AAPL", "MSFT"], [0.6, 0.4])
        assert p["id"]
        assert p["name"] == "Test"
        assert p["assets"] == ["AAPL", "MSFT"]
        ports = get_portfolios_for_user(u["id"])
        assert len(ports) == 1

    def test_multiple_portfolios(self, patch_repos_settings):
        u = create_user(**SAMPLE_USER)
        save_portfolio(u["id"], "P1", ["SPY"], [1.0])
        save_portfolio(u["id"], "P2", ["BND"], [1.0])
        assert len(get_portfolios_for_user(u["id"])) == 2

    def test_empty_portfolios(self, patch_repos_settings):
        u = create_user(**SAMPLE_USER)
        assert get_portfolios_for_user(u["id"]) == []

    def test_delete_portfolio(self, patch_repos_settings):
        u = create_user(**SAMPLE_USER)
        p = save_portfolio(u["id"], "ToDelete", ["SPY"], [1.0])
        assert delete_portfolio(p["id"]) is True
        assert len(get_portfolios_for_user(u["id"])) == 0

    def test_delete_nonexistent_portfolio(self, patch_repos_settings):
        assert delete_portfolio("nonexistent") is False


class TestSimulationCRUD:
    def test_save_and_list(self, patch_repos_settings):
        u = create_user(**SAMPLE_USER)
        s = save_simulation(u["id"], {"tickers": ["SPY"]}, {"median": 50000})
        assert s["id"]
        sims = get_simulations_for_user(u["id"])
        assert len(sims) == 1
        assert sims[0]["summary"]["median"] == 50000

    def test_multiple_simulations(self, patch_repos_settings):
        u = create_user(**SAMPLE_USER)
        save_simulation(u["id"], {"t": 1}, {"m": 1})
        save_simulation(u["id"], {"t": 2}, {"m": 2})
        assert len(get_simulations_for_user(u["id"])) == 2

    def test_empty_simulations(self, patch_repos_settings):
        u = create_user(**SAMPLE_USER)
        assert get_simulations_for_user(u["id"]) == []

    def test_delete_simulation(self, patch_repos_settings):
        u = create_user(**SAMPLE_USER)
        s = save_simulation(u["id"], {"t": 1}, {"m": 1})
        assert delete_simulation(s["id"]) is True
        assert len(get_simulations_for_user(u["id"])) == 0

    def test_delete_nonexistent_simulation(self, patch_repos_settings):
        assert delete_simulation("nonexistent") is False


class TestRiskProfileCRUD:
    def test_save_and_get(self, patch_repos_settings):
        u = create_user(**SAMPLE_USER)
        rp = save_risk_profile(u["id"], "moderado", 10, [1, 2, 3, 4, 5])
        assert rp["profile"] == "moderado"
        assert rp["score"] == 10
        loaded = get_risk_profile_for_user(u["id"])
        assert loaded is not None
        assert loaded["score"] == 10

    def test_update_risk_profile(self, patch_repos_settings):
        u = create_user(**SAMPLE_USER)
        save_risk_profile(u["id"], "conservador", 6, [1, 1, 1, 1, 1])
        save_risk_profile(u["id"], "agresivo", 14, [5, 5, 5, 5, 5])
        loaded = get_risk_profile_for_user(u["id"])
        assert loaded is not None
        assert loaded["profile"] == "agresivo"

    def test_get_nonexistent(self, patch_repos_settings):
        assert get_risk_profile_for_user("noone") is None
