"""
SmartRisk - JSON Persistence Layer (Per-User Sharding)
Each user's data is stored in separate JSON files under /data/.
"""
import json
import os
import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional

from config.settings import (
    USERS_DIR,
    PORTFOLIOS_DIR,
    SIMULATIONS_DIR,
    RISK_RESULTS_DIR,
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
    os.replace(tmp, filepath)


def _now() -> str:
    return datetime.utcnow().isoformat()


def _new_id() -> str:
    return str(uuid.uuid4())


# ── Users ─────────────────────────────────────────────────────────────────────

def get_all_users() -> dict:
    """Read all per-user files and return merged dict."""
    users = {}
    for f in sorted(USERS_DIR.glob("*.json")):
        data = _read(f)
        if data.get("id"):
            users[data["id"]] = data
    return users


def _user_path(user_id: str) -> Path:
    return USERS_DIR / f"{user_id}.json"


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
    _write(_user_path(uid), user)
    return user


def update_user(user_id: str, updates: dict) -> Optional[dict]:
    path = _user_path(user_id)
    if not path.exists():
        return None
    user = _read(path)
    user.update(updates)
    user["updated_at"] = _now()
    _write(path, user)
    return user


def delete_user(user_id: str) -> bool:
    path = _user_path(user_id)
    if not path.exists():
        return False
    path.unlink()
    for p in [_portfolios_path(user_id), _simulations_path(user_id), _risk_results_path(user_id)]:
        if p.exists():
            p.unlink()
    return True


def ensure_admin_exists() -> None:
    """Create default admin account if no active admin exists."""
    from auth.password_utils import hash_password

    users = get_all_users()
    has_admin = any(u.get("role") == "admin" and u.get("is_active", True) for u in users.values())
    if not has_admin:
        create_user(
            username="admin",
            email="admin@smartrisk.com",
            hashed_password=hash_password("Admin1234!"),
            role="admin",
            full_name="Administrador",
        )


# ── Portfolios ─────────────────────────────────────────────────────────────────

def _portfolios_path(user_id: str) -> Path:
    return PORTFOLIOS_DIR / f"{user_id}.json"


def get_portfolios_for_user(user_id: str) -> list:
    return list(_read(_portfolios_path(user_id)).values())


def save_portfolio(user_id: str, name: str, assets: list, weights: list) -> dict:
    portfolios = _read(_portfolios_path(user_id))
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
    _write(_portfolios_path(user_id), portfolios)
    return record


def delete_portfolio(portfolio_id: str) -> bool:
    for f in PORTFOLIOS_DIR.glob("*.json"):
        portfolios = _read(f)
        if portfolio_id in portfolios:
            del portfolios[portfolio_id]
            _write(f, portfolios)
            return True
    return False


# ── Risk Results ───────────────────────────────────────────────────────────────

def _risk_results_path(user_id: str) -> Path:
    return RISK_RESULTS_DIR / f"{user_id}.json"


def get_risk_profile_for_user(user_id: str) -> Optional[dict]:
    data = _read(_risk_results_path(user_id))
    if not data.get("user_id"):
        return None
    score = data.get("score", 0)
    answers = data.get("answers", [])
    if score < 5 or score > 15 or len(answers) != 5:
        return None
    return data


def save_risk_profile(user_id: str, profile: str, score: int, answers: list) -> dict:
    record = {
        "user_id": user_id,
        "profile": profile,
        "score": score,
        "answers": answers,
        "created_at": _now(),
    }
    _write(_risk_results_path(user_id), record)
    return record


# ── Simulations ────────────────────────────────────────────────────────────────

def _simulations_path(user_id: str) -> Path:
    return SIMULATIONS_DIR / f"{user_id}.json"


def get_simulations_for_user(user_id: str) -> list:
    sims = _read(_simulations_path(user_id))
    user_sims = list(sims.values())
    return sorted(user_sims, key=lambda x: x.get("created_at", ""), reverse=True)


def save_simulation(user_id: str, config: dict, summary: dict) -> dict:
    sims = _read(_simulations_path(user_id))
    sid = _new_id()
    record = {
        "id": sid,
        "user_id": user_id,
        "config": config,
        "summary": summary,
        "created_at": _now(),
    }
    sims[sid] = record
    _write(_simulations_path(user_id), sims)
    return record


def delete_simulation(simulation_id: str) -> bool:
    for f in SIMULATIONS_DIR.glob("*.json"):
        sims = _read(f)
        if simulation_id in sims:
            del sims[simulation_id]
            _write(f, sims)
            return True
    return False
