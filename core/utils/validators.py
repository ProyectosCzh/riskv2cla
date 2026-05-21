"""
SmartRisk - Input Validators
"""
import re
from typing import Optional


def validate_email(email: str) -> bool:
    pattern = r"^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$"
    return bool(re.match(pattern, email.strip()))


def validate_username(username: str) -> Optional[str]:
    """Return error message or None if valid."""
    u = username.strip()
    if len(u) < 3:
        return "El nombre de usuario debe tener al menos 3 caracteres."
    if len(u) > 30:
        return "El nombre de usuario no puede exceder 30 caracteres."
    if not re.match(r"^[a-zA-Z0-9_\-]+$", u):
        return "Solo se permiten letras, números, guiones y guiones bajos."
    return None


def validate_password(password: str) -> Optional[str]:
    if len(password) < 8:
        return "La contraseña debe tener al menos 8 caracteres."
    return None


def validate_weights(weights: list[float], tolerance: float = 0.005) -> bool:
    """Check that weights are non-negative and sum to ~1."""
    if not weights:
        return False
    if any(w < 0 for w in weights):
        return False
    return abs(sum(weights) - 1.0) <= tolerance


def validate_ticker(ticker: str) -> Optional[str]:
    t = ticker.strip().upper()
    if not t:
        return "El ticker no puede estar vacío."
    if len(t) > 10:
        return "El ticker no puede exceder 10 caracteres."
    if not re.match(r"^[A-Z0-9.\-\^]+$", t):
        return "Ticker inválido. Solo letras, números, puntos y guiones."
    return None
