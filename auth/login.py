"""
SmartRisk - Login Page
"""
import streamlit as st
from auth.auth_service import authenticate_user, register_user
from core.exceptions import AuthError, ValidationError
from auth.session_manager import login_session


def render_login() -> None:
    """Render the login form. Called when user is not authenticated."""
    # Center column layout
    col1, col2, col3 = st.columns([1, 1.6, 1])
    with col2:
        st.markdown(
            """
            <div style="text-align:center; padding: 2.5rem 0 1.5rem;">
                <div style="font-size: 2.5rem; font-weight: 900; color: #1B3A6B;
                            letter-spacing: -0.03em; margin-bottom: 0.25rem;">
                    📉 SmartRisk
                </div>
                <div style="font-size: 0.85rem; color: #718096; letter-spacing: 0.08em;
                            text-transform: uppercase; margin-bottom: 2rem;">
                    Robo-Advisor Académico · SI210M1
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        tab_login, tab_register = st.tabs(["Iniciar Sesión", "Crear Cuenta"])

        # ── Login Tab ──────────────────────────────────────────────────────
        with tab_login:
            st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)
            username = st.text_input(
                "Usuario o correo electrónico",
                placeholder="Ingresa tu usuario o email",
                key="login_username",
            )
            password = st.text_input(
                "Contraseña",
                type="password",
                placeholder="••••••••",
                key="login_password",
            )

            st.markdown("<div style='height:0.25rem'></div>", unsafe_allow_html=True)

            if st.button("Iniciar Sesión", type="primary", use_container_width=True):
                if not username or not password:
                    st.error("Por favor completa todos los campos.")
                else:
                    user = authenticate_user(username, password)
                    if user:
                        login_session(user)
                        st.success(f"Bienvenido, {user.get('full_name') or user['username']}!")
                        st.rerun()
                    else:
                        st.error("Credenciales incorrectas. Verifica tu usuario y contraseña.")

            st.markdown(
                """
                <div style="text-align:center; margin-top:1rem; font-size: 0.8rem; color: #A0AEC0;">
                    Cuenta de demo: <strong>admin</strong> / <strong>Admin1234!</strong>
                </div>
                """,
                unsafe_allow_html=True,
            )

        # ── Register Tab ───────────────────────────────────────────────────
        with tab_register:
            st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)
            _render_register_form()

        st.markdown(
            """
            <div style="text-align:center; margin-top:2rem; font-size:0.72rem; color:#CBD5E0;">
                © 2026 SmartRisk · Diego Rodas · Julianne Arriharan · Josue Mercado<br>
                Universidad · Estructura de Datos SI210M1
            </div>
            """,
            unsafe_allow_html=True,
        )


def _render_register_form() -> None:
    full_name = st.text_input("Nombre completo", placeholder="Juan Pérez", key="reg_name")
    username  = st.text_input("Nombre de usuario", placeholder="juanperez", key="reg_username")
    email     = st.text_input("Correo electrónico", placeholder="juan@email.com", key="reg_email")
    password  = st.text_input("Contraseña", type="password", placeholder="Mín. 8 caracteres", key="reg_pass")
    password2 = st.text_input("Confirmar contraseña", type="password", placeholder="••••••••", key="reg_pass2")

    if st.button("Crear Cuenta", type="primary", use_container_width=True):
        if not all([full_name, username, email, password, password2]):
            st.error("Por favor completa todos los campos.")
        elif password != password2:
            st.error("Las contraseñas no coinciden.")
        else:
            try:
                user = register_user(username, email, password, full_name)
                st.success("✅ Cuenta creada exitosamente. Ahora puedes iniciar sesión.")
            except (AuthError, ValidationError) as e:
                st.error(str(e))
                st.caption(f"📌 Jerarquía SmartRiskError: {type(e).__name__} capturada — herencia de excepciones personalizadas")
