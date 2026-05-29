"""
Tests for auth module.
Run with: pytest tests/test_auth.py -v
"""
import pytest
from auth.auth_service import register_user, authenticate_user
from core.exceptions import AuthError, ValidationError
from auth.password_utils import hash_password, verify_password


class TestPasswordUtils:
    def test_hash_and_verify(self):
        h = hash_password("MyP@ss123")
        assert h != "MyP@ss123"
        assert verify_password("MyP@ss123", h) is True

    def test_wrong_password_fails(self):
        h = hash_password("Correct1")
        assert verify_password("Wrong1", h) is False

    def test_empty_password_fails(self):
        h = hash_password("SomeP@ss1")
        assert verify_password("", h) is False

    def test_different_hashes_for_same_password(self):
        h1 = hash_password("SameP@ss1")
        h2 = hash_password("SameP@ss1")
        assert h1 != h2


class TestRegisterUser:
    def test_register_success(self, patch_repos_settings):
        user = register_user("newuser", "new@test.com", "StrongP@ss1")
        assert user["username"] == "newuser"
        assert user["role"] == "user"
        assert user["is_active"] is True

    def test_register_with_full_name(self, patch_repos_settings):
        user = register_user("nameduser", "named@test.com", "StrongP@ss1",
                             full_name="Full Name")
        assert user["full_name"] == "Full Name"

    def test_duplicate_username(self, patch_repos_settings):
        register_user("dupuser", "first@test.com", "StrongP@ss1")
        with pytest.raises(AuthError, match="ya está en uso"):
            register_user("dupuser", "other@test.com", "StrongP@ss1")

    def test_duplicate_email(self, patch_repos_settings):
        register_user("user1", "same@test.com", "StrongP@ss1")
        with pytest.raises(AuthError, match="ya está registrado"):
            register_user("user2", "same@test.com", "StrongP@ss1")

    def test_short_username(self, patch_repos_settings):
        with pytest.raises(ValidationError, match="3 caracteres"):
            register_user("ab", "ab@test.com", "StrongP@ss1")

    def test_short_password(self, patch_repos_settings):
        with pytest.raises(ValidationError, match="8 caracteres"):
            register_user("validuser", "valid@test.com", "Short1")

    def test_invalid_email(self, patch_repos_settings):
        with pytest.raises(ValidationError, match="correo"):
            register_user("validuser", "notanemail", "StrongP@ss1")


class TestAuthenticateUser:
    def test_login_with_username(self, patch_repos_settings):
        register_user("logintest", "login@test.com", "MyP@ss1234")
        user = authenticate_user("logintest", "MyP@ss1234")
        assert user is not None
        assert user["username"] == "logintest"

    def test_login_with_email(self, patch_repos_settings):
        register_user("login2", "login2@test.com", "MyP@ss1234")
        user = authenticate_user("login2@test.com", "MyP@ss1234")
        assert user is not None

    def test_wrong_password(self, patch_repos_settings):
        register_user("login3", "login3@test.com", "MyP@ss1234")
        user = authenticate_user("login3", "WrongP@ss1")
        assert user is None

    def test_nonexistent_user(self, patch_repos_settings):
        user = authenticate_user("noone", "AnyP@ss1")
        assert user is None

    def test_username_whitespace_trimmed(self, patch_repos_settings):
        register_user("whitespace", "ws@test.com", "MyP@ss1234")
        user = authenticate_user("  whitespace  ", "MyP@ss1234")
        assert user is not None
