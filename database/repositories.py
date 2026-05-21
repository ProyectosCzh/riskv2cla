"""
SmartRisk - JSON Persistence Layer
All data is stored in JSON files under /data/.
"""
import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

from config.settings import (
    USERS_FILE,
    PORTFOLIOS_FILE,
    SIMULATIONS_FILE,
    RISK_RESULTS_FILE,
)


# ── Generic helpers ────────────────────────────────────────────────────────────

def _read(filepath: Path) -> dict:
    """Read a JSON file; return empty dict if missing or corrupt."""
    try:
        if filepath.exists():
            with open(filepath, "r", encoding="utf-8") as f:
                return json.load(f)
    except (json.JSONDecodeError, OSError):
        pass
    return {}


def _write(filepath: Path, data: dict) -> None:
    """Write data to a JSON file atomically."""
    filepath.parent.mkdir(parents=True, exist_ok=True)
    tmp = filepath.with_suffix(".tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2, default=str)
    tmp.replace(filepath)


def _now() -> str:
    return datetime.utcnow().isoformat()


def _new_id() -> str:
    return str(uuid.uuid4())


# ── Users ─────────────────────────────────────────────────────────────────────

def get_all_users() -> dict:
    return _read(USERS_FILE)


def get_user_by_id(user_id: str) -> Optional[dict]:
    return get_all_users().get(user_id)


def get_user_by_email(email: str) -> Optional[dict]:
    for user in get_all_users().values():
        if user.get("email", "").lower() == email.lower():
            return user
    return None


def get_user_by_username(username: str) -> Optional[dict]:
    for user in get_all_users().values():
        if user.get("username", "").lower() == username.lower():
            return user
    return None


def create_user(
    username: str,
    email: str,
    hashed_password: str,
    role: str = "user",
    full_name: str = "",
) -> dict:
    users = get_all_users()
    uid = _new_id()
    user = {
        "id": uid,
        "username": username,
        "email": email,
        "password_hash": hashed_password,
        "role": role,
        "full_name": full_name,
        "created_at": _now(),
        "updated_at": _now(),
        "is_active": True,
    }
    users[uid] = user
    _write(USERS_FILE, users)
    return user


def update_user(user_id: str, updates: dict) -> Optional[dict]:
    users = get_all_users()
    if user_id not in users:
        return None
    users[user_id].update(updates)
    users[user_id]["updated_at"] = _now()
    _write(USERS_FILE, users)
    return users[user_id]


def delete_user(user_id: str) -> bool:
    users = get_all_users()
    if user_id not in users:
        return False
    del users[user_id]
    _write(USERS_FILE, users)
    return True


def ensure_admin_exists() -> None:
    """Create default admin account if no admin user exists."""
    from auth.password_utils import hash_password

    users = get_all_users()
    has_admin = any(u.get("role") == "admin" for u in users.values())
    if not has_admin:
        create_user(
            username="admin",
            email="admin@smartrisk.com",
            hashed_password=hash_password("Admin1234!"),
            role="admin",
            full_name="Administrador",
        )


# ── Portfolios ─────────────────────────────────────────────────────────────────

def _all_portfolios() -> dict:
    return _read(PORTFOLIOS_FILE)


def get_portfolios_for_user(user_id: str) -> list:
    return [p for p in _all_portfolios().values() if p.get("user_id") == user_id]


def get_portfolio_by_id(portfolio_id: str) -> Optional[dict]:
    return _all_portfolios().get(portfolio_id)


def save_portfolio(user_id: str, name: str, assets: list, weights: list) -> dict:
    """assets: list of tickers; weights: list of floats summing to 1."""
    portfolios = _all_portfolios()
    pid = _new_id()
    record = {
        "id": pid,
        "user_id": user_id,
        "name": name,
        "assets": assets,
        "weights": weights,
        "created_at": _now(),
        "updated_at": _now(),
    }
    portfolios[pid] = record
    _write(PORTFOLIOS_FILE, portfolios)
    return record


def delete_portfolio(portfolio_id: str) -> bool:
    portfolios = _all_portfolios()
    if portfolio_id not in portfolios:
        return False
    del portfolios[portfolio_id]
    _write(PORTFOLIOS_FILE, portfolios)
    return True


# ── Risk Results ───────────────────────────────────────────────────────────────

def _all_risk_results() -> dict:
    return _read(RISK_RESULTS_FILE)


def get_risk_profile_for_user(user_id: str) -> Optional[dict]:
    return _all_risk_results().get(user_id)


def save_risk_profile(user_id: str, profile: str, score: int, answers: list) -> dict:
    results = _all_risk_results()
    record = {
        "user_id": user_id,
        "profile": profile,
        "score": score,
        "answers": answers,
        "created_at": _now(),
    }
    results[user_id] = record
    _write(RISK_RESULTS_FILE, results)
    return record


# ── Simulations ────────────────────────────────────────────────────────────────

def _all_simulations() -> dict:
    return _read(SIMULATIONS_FILE)


def get_simulations_for_user(user_id: str) -> list:
    sims = _all_simulations()
    user_sims = [s for s in sims.values() if s.get("user_id") == user_id]
    return sorted(user_sims, key=lambda x: x.get("created_at", ""), reverse=True)


def save_simulation(user_id: str, config: dict, summary: dict) -> dict:
    sims = _all_simulations()
    sid = _new_id()
    record = {
        "id": sid,
        "user_id": user_id,
        "config": config,
        "summary": summary,
        "created_at": _now(),
    }
    sims[sid] = record
    _write(SIMULATIONS_FILE, sims)
    return record


def delete_simulation(simulation_id: str) -> bool:
    sims = _all_simulations()
    if simulation_id not in sims:
        return False
    del sims[simulation_id]
    _write(SIMULATIONS_FILE, sims)
    return True
