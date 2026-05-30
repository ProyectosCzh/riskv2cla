"""
SmartRisk - Sidebar Navigation Component
"""
import streamlit as st
from auth.session_manager import get_current_user, logout_session, is_admin
from config.settings import APP_NAME, APP_VERSION, ROLE_ADMIN
from ui.assets import get_logo_img_tag


NAV_ITEMS_USER = [
    ("🏠", "Dashboard",           "dashboard"),
    ("🎯", "Perfil de Riesgo",     "risk_quiz"),
    ("📊", "Mi Portafolio",        "portfolio"),
    ("🔬", "Simulador",            "simulator"),
    ("📈", "Resultados",           "results"),
    ("👤", "Mi Cuenta",            "profile"),
]

NAV_ITEMS_ADMIN = [
    ("🛠️", "Panel Admin",         "admin"),
]


def render_sidebar() -> None:
    """Render the main sidebar with navigation."""
    user = get_current_user()
    if not user:
        return

    with st.sidebar:
        # ── Logo ──────────────────────────────────────────────────────────
        st.markdown(
            f"""
            <div class="logo-container">
                <div class="logo-text">
                    {get_logo_img_tag(height="2rem")}SmartRisk
                </div>
                <div class="logo-sub">Robo-Advisor Académico</div>
            </div>
            <div class="logo-divider"></div>
            """,
            unsafe_allow_html=True,
        )

        # ── User info ──────────────────────────────────────────────────────
        display_name = user.get("full_name") or user.get("username", "Usuario")
        role_label = "Administrador" if user.get("role") == ROLE_ADMIN else "Inversor"
        st.markdown(
            f"""
            <div style="padding: 0 0.5rem 1rem; font-size: 0.8rem;">
                <div style="font-weight: 700; font-size: 0.92rem; color: white; margin-bottom: 2px;">
                    {display_name}
                </div>
                <div style="color: rgba(255,255,255,0.5); font-size: 0.75rem;">{role_label}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # ── Navigation ─────────────────────────────────────────────────────
        current = st.session_state.get("current_page", "dashboard")

        items = list(NAV_ITEMS_USER)
        if is_admin():
            items += NAV_ITEMS_ADMIN

        for icon, label, page_key in items:
            is_active = current == page_key
            btn_label = f"{icon}  {label}"
            if st.button(
                btn_label,
                key=f"nav_{page_key}",
                use_container_width=True,
                type="primary" if is_active else "secondary",
            ):
                st.session_state.current_page = page_key
                st.rerun()

        st.markdown("<div style='height: 2rem'></div>", unsafe_allow_html=True)

        # ── Divider + Logout ───────────────────────────────────────────────
        st.markdown("<div class='logo-divider'></div>", unsafe_allow_html=True)
        if st.button("⬡  Cerrar Sesión", key="nav_logout", use_container_width=True):
            logout_session()
            st.rerun()
