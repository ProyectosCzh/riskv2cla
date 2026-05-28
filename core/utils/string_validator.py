import re


class StringValidator:
    TICKER_PATTERN = re.compile(r"^[A-Z]{1,5}$")
    EMAIL_PATTERN = re.compile(r"^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$")

    @classmethod
    def validate_email(cls, email: str) -> tuple:
        if not email or not email.strip():
            return False, "El correo no puede estar vacío."
        email = email.strip().lower()
        if not cls.EMAIL_PATTERN.match(email):
            return False, "Ingresa un correo electrónico válido (ej: usuario@dominio.com)."
        if len(email) > 254:
            return False, "El correo es demasiado largo."
        return True, email

    @classmethod
    def validate_password(cls, password: str) -> tuple:
        if not password:
            return False, "La contraseña no puede estar vacía."
        if len(password) < 8:
            return False, "La contraseña debe tener al menos 8 caracteres."
        if len(password) > 128:
            return False, "La contraseña no puede tener más de 128 caracteres."
        return True, password

    @classmethod
    def validate_username(cls, username: str) -> tuple:
        if not username or not username.strip():
            return False, "El nombre de usuario no puede estar vacío."
        username = username.strip()
        if len(username) < 3:
            return False, "El nombre de usuario debe tener al menos 3 caracteres."
        if len(username) > 30:
            return False, "El nombre de usuario no puede tener más de 30 caracteres."
        if not re.match(r"^[a-zA-Z0-9_]+$", username):
            return False, "El nombre de usuario solo puede contener letras, números y guiones bajos."
        return True, username

    @classmethod
    def sanitize_ticker(cls, ticker: str) -> str:
        if not ticker or not ticker.strip():
            return ""
        cleaned = ticker.strip().upper()
        if cls.TICKER_PATTERN.match(cleaned):
            return cleaned
        return ""

    @classmethod
    def validate_ticker(cls, ticker: str) -> tuple:
        cleaned = cls.sanitize_ticker(ticker)
        if not cleaned:
            return False, f"'{ticker}' no es un ticker válido (1-5 letras mayúsculas)."
        return True, cleaned


