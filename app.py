"""
SmartRisk - Main Application Entry Point
Robo-Advisor Académico · SI210M1 · 2026

Run with:
    streamlit run app.py
"""
import sys
from pathlib import Path

# ── Ensure project root is on path ─────────────────────────────────────────────
ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import streamlit as st

# ── Page config (must be first Streamlit call) ─────────────────────────────────
st.set_page_config(
    page_title="SmartRisk — Robo-Advisor",
    page_icon="📉",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Imports after page config ──────────────────────────────────────────────────
from auth.session_manager import init_session, is_authenticated
from auth.login import render_login
from database.repositories import ensure_admin_exists
from ui.styles.custom_css import inject_css
from ui.components.sidebar import render_sidebar

# Page renderers
from ui.pages.dashboard        import render_dashboard
from ui.pages.risk_quiz        import render_risk_quiz
from ui.pages.portfolio_builder import render_portfolio_builder
from ui.pages.simulator        import render_simulator
from ui.pages.results          import render_results
from ui.pages.admin_panel      import render_admin_panel
from ui.pages.profile          import render_profile


PAGE_MAP = {
    "dashboard":  render_dashboard,
    "risk_quiz":  render_risk_quiz,
    "portfolio":  render_portfolio_builder,
    "simulator":  render_simulator,
    "results":    render_results,
    "admin":      render_admin_panel,
    "profile":    render_profile,
}


def main() -> None:
    # ── Bootstrap ──────────────────────────────────────────────────────────
    inject_css()
    init_session()
    ensure_admin_exists()
    ensure_directories()

    # ── Auth gate ──────────────────────────────────────────────────────────
    if not is_authenticated():
        render_login()
        return

    # ── Authenticated layout ───────────────────────────────────────────────
    render_sidebar()

    current_page = st.session_state.get("current_page", "dashboard")
    renderer = PAGE_MAP.get(current_page, render_dashboard)
    
    try:
        renderer()
    except Exception as e:
        st.error(f"Ocurrió un error inesperado en la página: {e}")
        # Optionally show more detail for admins
        from auth.session_manager import is_admin
        if is_admin():
            st.exception(e)


def ensure_directories() -> None:
    """Create necessary data directories if they don't exist."""
    from config.settings import DATA_DIR, CACHE_DIR, EXPORTS_DIR
    for d in [DATA_DIR, CACHE_DIR, EXPORTS_DIR]:
        d.mkdir(parents=True, exist_ok=True)


if __name__ == "__main__":
    main()
