"""
SmartRisk - User Profile Page
"""
import streamlit as st

from auth.session_manager import get_current_user
from auth.password_utils import hash_password, verify_password
from core.utils.string_validator import StringValidator
from database.repositories import (
    update_user,
    get_portfolios_for_user,
    get_simulations_for_user,
    get_risk_profile_for_user,
)
from ui.components.metrics_cards import (
    page_header, section_header, alert_box, metric_card, spacer, tooltip_box
)


def render_profile() -> None:
    user = get_current_user()
    if not user:
        return

    page_header("Mi Cuenta 👤", "Administra tu perfil y preferencias personales.")

    tab_info, tab_pass, tab_stats = st.tabs(["📋 Información", "🔒 Seguridad", "📊 Mis Estadísticas"])

    # ── Personal Info ──────────────────────────────────────────────────────
    with tab_info:
        section_header("Datos Personales")

        col1, col2 = st.columns([1, 2])

        with col1:
            # Avatar placeholder
            initials = (user.get("full_name") or user.get("username", "U"))[:2].upper()
            st.markdown(
                f"""
                <div style="width:100px; height:100px; border-radius:50%;
                            background:#1B3A6B; display:flex; align-items:center;
                            justify-content:center; margin:0 auto 1rem;">
                    <span style="font-size:2rem; font-weight:800; color:white;">{initials}</span>
                </div>
                <div style="text-align:center; font-size:0.75rem; color:#A0AEC0; margin-bottom:0.5rem;">
                    {'🛠️ Administrador' if user.get('role')=='admin' else '👤 Inversor'}
                </div>
                <div style="text-align:center; font-size:0.72rem; color:#CBD5E0;">
                    Miembro desde {user.get('created_at','')[:10]}
                </div>
                """,
                unsafe_allow_html=True,
            )

        with col2:
            edit_full = st.text_input("Nombre completo", value=user.get("full_name", ""), key="prof_full")
            edit_email = st.text_input("Correo electrónico", value=user.get("email", ""), key="prof_email")
            st.text_input("Nombre de usuario", value=user.get("username", ""), disabled=True,
                          help="El nombre de usuario no puede cambiarse.")

            if st.button("Guardar Cambios", type="primary", key="prof_save"):
                if not edit_email or "@" not in edit_email:
                    st.error("Ingresa un correo electrónico válido.")
                else:
                    update_user(user["id"], {
                        "full_name": edit_full.strip(),
                        "email": edit_email.strip().lower(),
                    })
                    # Update session state
                    st.session_state.user["full_name"] = edit_full.strip()
                    st.session_state.user["email"] = edit_email.strip().lower()
                    st.success("✅ Perfil actualizado correctamente.")

    # ── Security ───────────────────────────────────────────────────────────
    with tab_pass:
        section_header("Cambiar Contraseña")
        tooltip_box("Usa una contraseña de al menos 8 caracteres con letras y números.")

        current_pass = st.text_input("Contraseña actual", type="password", key="sec_current")
        new_pass     = st.text_input("Nueva contraseña", type="password", key="sec_new")
        confirm_pass = st.text_input("Confirmar nueva contraseña", type="password", key="sec_confirm")

        if st.button("Actualizar Contraseña", type="primary", key="sec_save"):
            if not all([current_pass, new_pass, confirm_pass]):
                st.error("Completa todos los campos.")
            elif not verify_password(current_pass, user["password_hash"]):
                st.error("La contraseña actual es incorrecta.")
            elif new_pass != confirm_pass:
                st.error("Las contraseñas nuevas no coinciden.")
            else:
                is_valid, msg = StringValidator.validate_password(new_pass)
                if not is_valid:
                    st.error(msg)
                else:
                    new_hash = hash_password(new_pass)
                    update_user(user["id"], {"password_hash": new_hash})
                    st.session_state.user["password_hash"] = new_hash
                    st.success("✅ Contraseña actualizada exitosamente.")

    # ── Stats ──────────────────────────────────────────────────────────────
    with tab_stats:
        section_header("Resumen de Actividad")

        portfolios   = get_portfolios_for_user(user["id"])
        simulations  = get_simulations_for_user(user["id"])
        risk_result  = get_risk_profile_for_user(user["id"])

        col1, col2, col3 = st.columns(3)
        with col1:
            metric_card("Portafolios", str(len(portfolios)), "Carteras guardadas")
        with col2:
            metric_card("Simulaciones", str(len(simulations)), "Monte Carlo ejecutados")
        with col3:
            profile = risk_result["profile"].capitalize() if risk_result else "Sin definir"
            metric_card("Perfil de Riesgo", profile, "Clasificación actual")

        spacer()

        if simulations:
            section_header("Mejor Simulación (por capital mediano)")
            best = max(simulations, key=lambda s: s.get("summary", {}).get("median_capital", 0))
            cfg  = best.get("config", {})
            met  = best.get("summary", {})

            col_a, col_b, col_c = st.columns(3)
            with col_a:
                metric_card("Capital Mediano", f"${met.get('median_capital',0):,.0f}", ", ".join(cfg.get("tickers", [])))
            with col_b:
                metric_card("CAGR", f"{met.get('cagr_median',0):.2%}", f"{cfg.get('projection_years','?')} años")
            with col_c:
                metric_card("VaR 95%", f"${met.get('var_95_value',0):,.0f}", "Escenario pesimista probable")
