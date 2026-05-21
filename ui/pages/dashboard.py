"""
SmartRisk - Dashboard Page
"""
import streamlit as st
from auth.session_manager import get_current_user
from database.repositories import (
    get_portfolios_for_user,
    get_simulations_for_user,
    get_risk_profile_for_user,
)
from services.market_service import get_risk_profiles
from ui.components.metrics_cards import (
    page_header, section_header, metric_card, alert_box, spacer
)


def render_dashboard() -> None:
    user = get_current_user()
    if not user:
        return

    name = user.get("full_name") or user.get("username", "Inversor")
    page_header(f"Bienvenido, {name} 👋", "Tu centro de comando financiero personal.")

    # ── Quick Stats ────────────────────────────────────────────────────────
    portfolios = get_portfolios_for_user(user["id"])
    simulations = get_simulations_for_user(user["id"])
    risk_result = get_risk_profile_for_user(user["id"])

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        metric_card("Portafolios Guardados", str(len(portfolios)), "Carteras configuradas")
    with col2:
        metric_card("Simulaciones", str(len(simulations)), "Monte Carlo ejecutados")
    with col3:
        profile_label = risk_result["profile"].capitalize() if risk_result else "—"
        metric_card("Perfil de Riesgo", profile_label, "Resultado del quiz")
    with col4:
        last_sim = simulations[0] if simulations else None
        if last_sim:
            capital = last_sim.get("summary", {}).get("median_capital", 0)
            metric_card("Última Simulación", f"${capital:,.0f}", "Capital mediano proyectado")
        else:
            metric_card("Última Simulación", "—", "Aún no ejecutada")

    spacer()

    # ── Status / Onboarding ────────────────────────────────────────────────
    section_header("Estado de tu Plan de Inversión")

    steps = [
        (bool(risk_result),       "1", "Completa el Perfil de Riesgo",   "Responde el quiz para clasificar tu tolerancia al riesgo."),
        (bool(portfolios),        "2", "Construye tu Portafolio",         "Selecciona hasta 5 activos y asigna los pesos de inversión."),
        (bool(simulations),       "3", "Ejecuta la Simulación",           "Proyecta el futuro de tu portafolio con Monte Carlo."),
        (len(simulations) > 0,    "4", "Analiza los Resultados",          "Interpreta VaR, Sharpe, Drawdown y toma decisiones."),
    ]

    for done, num, title, desc in steps:
        icon = "✅" if done else "⬜"
        color = "#38A169" if done else "#A0AEC0"
        st.markdown(
            f"""
            <div style="display:flex; align-items:flex-start; gap:1rem; padding:0.75rem 0;
                        border-bottom: 1px solid #EDF2F7;">
                <div style="font-size:1.1rem; min-width:1.5rem;">{icon}</div>
                <div>
                    <div style="font-weight:600; color:{'#1A202C' if done else '#718096'}; margin-bottom:2px;">
                        Paso {num} — {title}
                    </div>
                    <div style="font-size:0.82rem; color:#A0AEC0;">{desc}</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    spacer()

    # ── Risk profile summary ───────────────────────────────────────────────
    if risk_result:
        section_header("Tu Perfil de Riesgo")
        profiles = get_risk_profiles()

        profile_key = risk_result.get("profile", "moderado")
        profile_data = profiles.get(profile_key, {})

        col_a, col_b = st.columns([1, 2])
        with col_a:
            st.markdown(
                f"""
                <div style="background: white; border: 1px solid #E2E8F0; border-radius: 12px;
                            padding: 1.5rem; text-align: center; box-shadow: 0 1px 3px rgba(0,0,0,0.08);">
                    <div style="font-size: 2.5rem; margin-bottom: 0.5rem;">{profile_data.get('icon','⚖️')}</div>
                    <div style="font-size: 1.1rem; font-weight: 700; color: #1B3A6B; margin-bottom: 0.5rem;">
                        {profile_data.get('label','—')}
                    </div>
                    <div style="font-size: 0.78rem; color: #718096;">
                        Score: {risk_result.get('score', '—')} pts
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with col_b:
            st.markdown(
                f"""
                <div style="background: white; border: 1px solid #E2E8F0; border-radius: 12px;
                            padding: 1.5rem; box-shadow: 0 1px 3px rgba(0,0,0,0.08);">
                    <div style="font-size: 0.85rem; color: #4A5568; line-height: 1.7;">
                        {profile_data.get('description','—')}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    spacer()

    # ── Recent simulations ─────────────────────────────────────────────────
    if simulations:
        section_header("Simulaciones Recientes")
        for sim in simulations[:3]:
            cfg = sim.get("config", {})
            metrics = sim.get("summary", {})
            tickers = cfg.get("tickers", [])
            st.markdown(
                f"""
                <div style="background: white; border: 1px solid #E2E8F0; border-radius: 10px;
                            padding: 1rem 1.25rem; margin-bottom: 0.6rem;
                            box-shadow: 0 1px 3px rgba(0,0,0,0.06);">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <div>
                            <div style="font-weight:600; color:#1B3A6B; font-size:0.92rem;">
                                {', '.join(tickers)} · ${cfg.get('initial_capital',0):,.0f} inicial
                            </div>
                            <div style="font-size:0.78rem; color:#A0AEC0; margin-top:2px;">
                                {cfg.get('projection_years','?')} años · {cfg.get('n_simulations','?'):,} escenarios
                            </div>
                        </div>
                        <div style="text-align:right;">
                            <div style="font-weight:700; color:#38A169; font-size:1.05rem;">
                                ${metrics.get('median_capital', 0):,.0f}
                            </div>
                            <div style="font-size:0.75rem; color:#A0AEC0;">Capital mediano</div>
                        </div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
    else:
        alert_box(
            "Aún no tienes simulaciones. Construye un portafolio y ejecuta tu primera simulación Monte Carlo.",
            "info",
        )
