"""
SmartRisk - Responsive Navigation Component
Top navbar (desktop) + Bottom tab bar (mobile) — pure HTML, query-param driven.
"""
import streamlit as st
from auth.session_manager import get_current_user, is_admin

NAV_ORDER = [
    ("dashboard",  "🏠", "Dashboard"),
    ("risk_quiz",  "🎯", "Perfil de Riesgo"),
    ("portfolio",  "📊", "Construir Port."),
    ("simulator",  "🔬", "Simulador"),
    ("results",    "📈", "Resultados"),
]

NAV_EXTRA = [
    ("profile",    "👤", "Mi Cuenta"),
]

NAV_ADMIN = [
    ("admin",      "🛠️", "Panel Admin"),
]


def get_nav_items():
    items = list(NAV_ORDER) + list(NAV_EXTRA)
    if is_admin():
        items += NAV_ADMIN
    return items


def handle_nav_params() -> None:
    """Process ?page=... or ?logout=1 from HTML nav clicks."""
    params = st.query_params
    if "page" in params:
        st.session_state.current_page = params["page"]
        st.query_params.clear()
        st.rerun()
    if "logout" in params:
        from auth.session_manager import logout_session
        logout_session()
        st.query_params.clear()
        st.rerun()


def render_navbar() -> None:
    user = get_current_user()
    if not user:
        return

    current = st.session_state.get("current_page", "dashboard")
    items = get_nav_items()

    html = _build_navbar_html(items, current, user)
    st.markdown(html, unsafe_allow_html=True)


def _build_navbar_html(items: list, current: str, user: dict) -> str:
    display_name = user.get("full_name") or user.get("username", "")
    initial = display_name[:2].upper() if display_name else "U"

    # ── Desktop top navbar ────────────────────────────────────────────────
    desktop_items = ""
    for page_key, icon, label in items:
        active_cls = " nav-active" if current == page_key else ""
        desktop_items += (
            f'<a class="nav-item{active_cls}" href="?page={page_key}">'
            f"{icon} {label}</a>"
        )

    desktop = f"""
    <nav class="top-navbar">
      <span class="nav-logo">📉 SmartRisk</span>
      <div class="nav-items">{desktop_items}</div>
      <div class="nav-right">
        <span class="nav-user-avatar" title="{display_name}">{initial}</span>
        <a class="nav-logout-btn" href="?logout=1" title="Cerrar Sesión">⬡</a>
      </div>
    </nav>
    """

    # ── Mobile bottom tab bar ─────────────────────────────────────────────
    mobile_items = ""
    for page_key, icon, label in items:
        active_cls = " tab-active" if current == page_key else ""
        short = label.split()[0] if len(label) > 8 else label
        mobile_items += (
            f'<a class="tab-item{active_cls}" href="?page={page_key}">'
            f'<span class="tab-icon">{icon}</span>'
            f'<span class="tab-label">{short}</span></a>'
        )
    mobile_items += (
        '<a class="tab-item" href="?logout=1">'
        '<span class="tab-icon">🚪</span>'
        '<span class="tab-label">Salir</span></a>'
    )

    mobile = f"""<nav class="bottom-tab-bar">{mobile_items}</nav>"""

    return (
        f'<div class="nav-desktop-only">{desktop}</div>\n'
        f'<div class="nav-mobile-only">{mobile}</div>'
    )
