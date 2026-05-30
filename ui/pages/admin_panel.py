"""
SmartRisk - Admin Panel Page
"""
import streamlit as st
import pandas as pd

from auth.session_manager import get_current_user, is_admin
from auth.auth_service import register_user
from core.exceptions import AuthError, ValidationError
from core.utils.string_validator import StringValidator
from auth.password_utils import hash_password
from database.repositories import (
    get_all_users,
    update_user,
    delete_user,
    get_simulations_for_user,
    get_portfolios_for_user,
)
from ui.components.metrics_cards import (
    page_header, section_header, alert_box, spacer, metric_card
)
from ui.components.page_nav import render_page_navigation


def render_admin_panel() -> None:
    if not is_admin():
        alert_box("Acceso denegado. Se requieren permisos de administrador.", "danger")
        return

    page_header("Panel de Administración 🛠️", "Gestión de usuarios y plataforma SmartRisk.")

    users = get_all_users()
    total_sims = sum(len(get_simulations_for_user(uid)) for uid in users)
    total_ports = sum(len(get_portfolios_for_user(uid)) for uid in users)

    # ── Platform stats ─────────────────────────────────────────────────────
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        metric_card("Total Usuarios", str(len(users)), "Registrados en la plataforma")
    with col2:
        admins = sum(1 for u in users.values() if u.get("role") == "admin")
        metric_card("Administradores", str(admins), "Con acceso admin")
    with col3:
        metric_card("Simulaciones Totales", str(total_sims), "En toda la plataforma")
    with col4:
        metric_card("Portafolios Totales", str(total_ports), "En toda la plataforma")

    spacer()

    tab_list, tab_create, tab_edit = st.tabs(["👥 Lista de Usuarios", "➕ Crear Usuario", "✏️ Editar / Eliminar"])

    # ── User list ──────────────────────────────────────────────────────────
    with tab_list:
        section_header("Usuarios Registrados")
        if not users:
            alert_box("No hay usuarios registrados.", "info")
        else:
            rows = []
            for uid, u in users.items():
                rows.append({
                    "ID": uid[:8] + "...",
                    "Usuario": u.get("username", ""),
                    "Nombre": u.get("full_name", ""),
                    "Email": u.get("email", ""),
                    "Rol": u.get("role", "user"),
                    "Activo": "✅" if u.get("is_active", True) else "❌",
                    "Registrado": u.get("created_at", "")[:10],
                    "Simulaciones": len(get_simulations_for_user(uid)),
                    "Portafolios": len(get_portfolios_for_user(uid)),
                })
            df = pd.DataFrame(rows)
            st.dataframe(df, use_container_width=True, hide_index=True)

    # ── Create user ────────────────────────────────────────────────────────
    with tab_create:
        section_header("Crear Nuevo Usuario")
        col_a, col_b = st.columns(2)
        with col_a:
            new_full = st.text_input("Nombre completo", key="adm_create_full")
            new_user = st.text_input("Nombre de usuario", key="adm_create_user")
            new_email = st.text_input("Correo electrónico", key="adm_create_email")
        with col_b:
            new_pass = st.text_input("Contraseña", type="password", key="adm_create_pass")
            new_role = st.selectbox("Rol", ["user", "admin"], key="adm_create_role")

        if st.button("Crear Usuario", type="primary", key="adm_create_btn"):
            if not all([new_full, new_user, new_email, new_pass]):
                st.error("Completa todos los campos.")
            else:
                try:
                    user_obj = register_user(new_user, new_email, new_pass, new_full)
                    if new_role == "admin":
                        update_user(user_obj["id"], {"role": "admin"})
                    st.success(f"✅ Usuario '{new_user}' creado exitosamente.")
                    st.rerun()
                except (AuthError, ValidationError) as e:
                    st.error(str(e))

    # ── Edit / Delete ──────────────────────────────────────────────────────
    with tab_edit:
        section_header("Editar o Eliminar Usuario")
        if not users:
            alert_box("No hay usuarios para gestionar.", "info")
        else:
            current_user = get_current_user()
            user_options = {
                f"{u.get('username')} ({u.get('email')})": uid
                for uid, u in users.items()
                if uid != current_user["id"]  # can't edit yourself here
            }

            if not user_options:
                alert_box("No hay otros usuarios para gestionar.", "info")
            else:
                selected_label = st.selectbox("Seleccionar usuario", list(user_options.keys()), key="adm_edit_select")
                selected_uid = user_options[selected_label]
                selected_user_data = users[selected_uid]

                col_e1, col_e2 = st.columns(2)
                with col_e1:
                    edit_full = st.text_input("Nombre completo", value=selected_user_data.get("full_name", ""), key="adm_edit_full")
                    edit_email = st.text_input("Email", value=selected_user_data.get("email", ""), key="adm_edit_email")
                with col_e2:
                    edit_role = st.selectbox(
                        "Rol",
                        ["user", "admin"],
                        index=0 if selected_user_data.get("role") == "user" else 1,
                        key="adm_edit_role",
                    )
                    edit_active = st.checkbox(
                        "Usuario activo",
                        value=selected_user_data.get("is_active", True),
                        key="adm_edit_active",
                    )

                edit_new_pass = st.text_input("Nueva contraseña (dejar vacío = sin cambio)", type="password", key="adm_edit_pass")

                col_save, col_del = st.columns(2)
                with col_save:
                    if st.button("💾 Guardar Cambios", type="primary", key="adm_save_btn", use_container_width=True):
                        updates: dict = {
                            "full_name": edit_full,
                            "email": edit_email,
                            "role": edit_role,
                            "is_active": edit_active,
                        }
                        if edit_new_pass:
                            is_valid, msg = StringValidator.validate_password(edit_new_pass)
                            if not is_valid:
                                st.error(msg)
                            else:
                                updates["password_hash"] = hash_password(edit_new_pass)
                        update_user(selected_uid, updates)
                        st.success("✅ Usuario actualizado.")
                        st.rerun()

                with col_del:
                    if st.button("🗑️ Eliminar Usuario", key="adm_del_btn", use_container_width=True):
                        delete_user(selected_uid)
                        st.success("Usuario eliminado.")
                        st.rerun()

    render_page_navigation("admin")
