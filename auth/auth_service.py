"""
SmartRisk - Authentication Service
"""
from typing import Optional

from auth.password_utils import hash_password, verify_password
from core.exceptions import AuthError, ValidationError
from core.utils.string_validator import StringValidator
from database.repositories import (
    create_user,
    get_user_by_email,
    get_user_by_username,
)


def register_user(
    username: str,
    email: str,
    password: str,
    full_name: str = "",
) -> dict:
    """Register a new user. Raises AuthError on validation failure."""
    username = username.strip()
    email = email.strip().lower()

    is_valid, msg = StringValidator.validate_username(username)  # 📌 StringValidator — validación de cadenas (Unidad IV)
    if not is_valid:
        raise ValidationError(msg)

    if get_user_by_username(username):
        raise AuthError("Ese nombre de usuario ya está en uso.")

    is_valid, msg = StringValidator.validate_email(email)
    if not is_valid:
        raise ValidationError(msg)

    if get_user_by_email(email):
        raise AuthError("Ese correo electrónico ya está registrado.")

    is_valid, msg = StringValidator.validate_password(password)
    if not is_valid:
        raise ValidationError(msg)

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
