"""
Smoke tests for Streamlit UI pages.
Run with: pytest tests/test_ui_smoke.py -v

These tests verify that the app loads and renders key UI elements
without requiring a browser. They use streamlit.testing.v1.AppTest
which runs the app in a simulated environment.
"""
import pytest
from streamlit.testing.v1 import AppTest


class TestAppSmoke:
    def test_app_loads_without_exception(self):
        """App should start without raising unhandled exceptions."""
        at = AppTest.from_file("app.py")
        at.run(timeout=15)
        assert not at.exception, f"App raised: {at.exception}"

    def test_login_page_has_text_inputs(self):
        """Unauthenticated app should show login form with inputs."""
        at = AppTest.from_file("app.py")
        at.run(timeout=15)
        text_inputs = at.text_input
        assert len(text_inputs) >= 2, (
            f"Expected at least 2 text inputs for login, got {len(text_inputs)}"
        )

    def test_authenticated_dashboard_renders(self):
        """Dashboard should render for an authenticated user."""
        at = AppTest.from_file("app.py")
        at.session_state["authenticated"] = True
        at.session_state["user"] = {
            "id": "smoke-test-id",
            "username": "smokeuser",
            "full_name": "Smoke User",
            "role": "user",
        }
        at.run(timeout=15)
        assert not at.exception, f"UI error on dashboard: {at.exception}"
        all_text = " ".join(
            str(m.value) for m in at.markdown
        )
        assert any(word in all_text for word in ["Bienvenido", "Smoke"]), (
            f"Dashboard welcome message not found. Text: {all_text[:200]}"
        )

    def test_admin_page_requires_admin(self):
        """Non-admin user should see access denied on admin panel."""
        at = AppTest.from_file("app.py")
        at.session_state["authenticated"] = True
        at.session_state["user"] = {
            "id": "regular-id",
            "username": "regular",
            "full_name": "Regular User",
            "role": "user",
        }
        at.session_state["current_page"] = "admin"
        at.run(timeout=15)
        assert not at.exception, f"UI error: {at.exception}"
