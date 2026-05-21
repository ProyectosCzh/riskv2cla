"""
SmartRisk - Session Management via Streamlit Session State
"""
import streamlit as st
from config.settings import ROLE_ADMIN


def init_session() -> None:
    """Initialize session state keys if not present."""
    defaults = {
        "authenticated": False,
        "user": None,
        "current_page": "dashboard",
        "portfolio_draft": None,
        "simulation_result": None,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def login_session(user: dict) -> None:
    """Persist user in session after successful authentication."""
    st.session_state.authenticated = True
    st.session_state.user = user
    st.session_state.current_page = "dashboard"


def logout_session() -> None:
    """Clear authentication from session."""
    for key in ["authenticated", "user", "portfolio_draft", "simulation_result", "sim_portfolio_data"]:
        if key in st.session_state:
            st.session_state[key] = None if key != "authenticated" else False
    st.session_state.current_page = "dashboard"


def get_current_user() -> dict | None:
    return st.session_state.get("user")


def is_authenticated() -> bool:
    return bool(st.session_state.get("authenticated"))


def is_admin() -> bool:
    user = get_current_user()
    return bool(user and user.get("role") == ROLE_ADMIN)
