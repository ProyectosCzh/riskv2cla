"""
Tests for StringValidator class.
"""
import pytest
from core.utils.string_validator import StringValidator


class TestEmailValidation:
    def test_valid_email(self):
        is_valid, result = StringValidator.validate_email("user@example.com")
        assert is_valid is True
        assert result == "user@example.com"

    def test_valid_email_with_plus(self):
        is_valid, _ = StringValidator.validate_email("user+tag@example.com")
        assert is_valid is True

    def test_invalid_email_no_at(self):
        is_valid, msg = StringValidator.validate_email("notanemail")
        assert is_valid is False
        assert "válido" in msg

    def test_invalid_email_empty(self):
        is_valid, msg = StringValidator.validate_email("")
        assert is_valid is False

    def test_invalid_email_whitespace(self):
        is_valid, msg = StringValidator.validate_email("   ")
        assert is_valid is False

    def test_email_case_insensitive(self):
        is_valid, result = StringValidator.validate_email("USER@EXAMPLE.COM")
        assert is_valid is True
        assert result == "user@example.com"


class TestPasswordValidation:
    def test_valid_password(self):
        is_valid, result = StringValidator.validate_password("MyP@ss123")
        assert is_valid is True
        assert result == "MyP@ss123"

    def test_short_password(self):
        is_valid, msg = StringValidator.validate_password("Ab1")
        assert is_valid is False
        assert "8 caracteres" in msg

    def test_empty_password(self):
        is_valid, msg = StringValidator.validate_password("")
        assert is_valid is False
        assert "vacía" in msg

    def test_long_password(self):
        long_pwd = "A1" * 65
        is_valid, msg = StringValidator.validate_password(long_pwd)
        assert is_valid is False
        assert "128" in msg


class TestUsernameValidation:
    def test_valid_username(self):
        is_valid, result = StringValidator.validate_username("juanperez")
        assert is_valid is True
        assert result == "juanperez"

    def test_short_username(self):
        is_valid, msg = StringValidator.validate_username("ab")
        assert is_valid is False
        assert "3 caracteres" in msg

    def test_username_with_underscore(self):
        is_valid, _ = StringValidator.validate_username("juan_perez")
        assert is_valid is True

    def test_username_with_special_chars(self):
        is_valid, msg = StringValidator.validate_username("juan perez!")
        assert is_valid is False
        assert "letras, números" in msg

    def test_empty_username(self):
        is_valid, msg = StringValidator.validate_username("")
        assert is_valid is False

    def test_long_username(self):
        is_valid, msg = StringValidator.validate_username("a" * 31)
        assert is_valid is False
        assert "30" in msg


class TestTickerValidation:
    def test_valid_ticker(self):
        is_valid, result = StringValidator.validate_ticker("AAPL")
        assert is_valid is True
        assert result == "AAPL"

    def test_ticker_lowercase(self):
        is_valid, result = StringValidator.validate_ticker("aapl")
        assert is_valid is True
        assert result == "AAPL"

    def test_sanitize_ticker(self):
        assert StringValidator.sanitize_ticker(" msft ") == "MSFT"
        assert StringValidator.sanitize_ticker("") == ""

    def test_invalid_ticker(self):
        is_valid, _ = StringValidator.validate_ticker("TOOLONG")
        assert is_valid is False

    def test_ticker_with_numbers(self):
        is_valid, _ = StringValidator.validate_ticker("BRK.A")
        assert is_valid is False

