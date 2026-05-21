"""
SmartRisk - User Service
High-level operations on user data.
"""
from typing import Optional
from database.repositories import (
    get_all_users,
    get_user_by_id,
    get_user_by_email,
    get_user_by_username,
    update_user,
    delete_user,
)


def list_users() -> list[dict]:
    """Return all users as a list, sorted by creation date."""
    users = get_all_users()
    return sorted(users.values(), key=lambda u: u.get("created_at", ""))


def get_user(user_id: str) -> Optional[dict]:
    return get_user_by_id(user_id)


def deactivate_user(user_id: str) -> bool:
    result = update_user(user_id, {"is_active": False})
    return result is not None


def activate_user(user_id: str) -> bool:
    result = update_user(user_id, {"is_active": True})
    return result is not None


def promote_to_admin(user_id: str) -> bool:
    result = update_user(user_id, {"role": "admin"})
    return result is not None


def demote_to_user(user_id: str) -> bool:
    result = update_user(user_id, {"role": "user"})
    return result is not None


def remove_user(user_id: str) -> bool:
    return delete_user(user_id)
