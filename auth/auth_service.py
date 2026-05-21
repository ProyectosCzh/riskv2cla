"""
SmartRisk - Authentication Service
"""
import re
from typing import Optional

from auth.password_utils import hash_password, verify_password
from database.repositories import (
    create_user,
    get_user_by_email,
    get_user_by_username,
)


class AuthError(Exception):
    pass


def register_user(
    username: str,
    email: str,
    password: str,
    full_name: str = "",
) -> dict:
    """Register a new user. Raises AuthError on validation failure."""
    username = username.strip()
    email = email.strip().lower()

    if len(username) < 3:
        raise AuthError("El nombre de usuario debe tener al menos 3 caracteres.")
    if get_user_by_username(username):
        raise AuthError("Ese nombre de usuario ya está en uso.")
    if get_user_by_email(email):
        raise AuthError("Ese correo electrónico ya está registrado.")
    if len(password) < 8:
        raise AuthError("La contraseña debe tener al menos 8 caracteres.")
    if not re.match(r"^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$", email):
        raise AuthError("Ingresa un correo electrónico válido.")

    hashed = hash_password(password)
    user = create_user(
        username=username,
        email=email,
        hashed_password=hashed,
        role="user",
        full_name=full_name.strip(),
    )
    return user


def authenticate_user(username_or_email: str, password: str) -> Optional[dict]:
    """Return user dict if credentials valid, else None."""
    val = username_or_email.strip()
    user = get_user_by_email(val) or get_user_by_username(val)
    if not user:
        return None
    if not user.get("is_active", True):
        return None
    if verify_password(password, user["password_hash"]):
        return user
    return None
