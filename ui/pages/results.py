"""
SmartRisk - Results History Page
"""
import streamlit as st
import pandas as pd

from auth.session_manager import get_current_user
from database.repositories import get_simulations_for_user, delete_simulation
from ui.components.metrics_cards import (
    page_header, section_header, alert_box, spacer, metric_card
)


def render_results() -> None:
    user = get_current_user()
    if not user:
        return

    page_header("Historial de Simulaciones 📈", "Revisa y compara todos tus análisis anteriores.")

    simulations = get_simulations_for_user(user["id"])

    if not simulations:
        alert_box(
            "Aún no tienes simulaciones guardadas. Ve al <strong>Simulador</strong> para ejecutar tu primer análisis.",
            "info",
        )
        return

    # ── Summary table ──────────────────────────────────────────────────────
    section_header(f"Tienes {len(simulations)} simulación(es) guardada(s)")

    rows = []
    for sim in simulations:
        cfg = sim.get("config", {})
        metrics = sim.get("summary", {})
        rows.append({
            "Portafolio": ", ".join(cfg.get("tickers", [])),
            "Capital Inicial": f"${cfg.get('initial_capital', 0):,.0f}",
            "DCA Mensual": f"${cfg.get('monthly_dca', 0):,.0f}",
            "Horizonte": f"{cfg.get('projection_years', '?')} años",
            "Capital Mediano": f"${metrics.get('median_capital', 0):,.0f}",
            "VaR 95%": f"${metrics.get('var_95_value', 0):,.0f}",
            "Max Drawdown": f"{metrics.get('max_drawdown', 0):.2%}",
            "Prob. Pérdida": f"{metrics.get('prob_loss', 0):.1%}",
            "CAGR": f"{metrics.get('cagr_median', 0):.2%}",
            "Fecha": sim.get("created_at", "")[:10],
            "_id": sim["id"],
        })

    df = pd.DataFrame(rows)
    display_df = df.drop(columns=["_id"])
    st.dataframe(display_df, use_container_width=True, hide_index=True)

    spacer()

    # ── Comparison view ────────────────────────────────────────────────────
    if len(simulations) >= 2:
        section_header("Comparar Simulaciones")
        sim_labels = [f"{s['config'].get('tickers',[])} · {s.get('created_at','')[:10]}" for s in simulations]
        cols_compare = st.columns(2)
        with cols_compare[0]:
            sim_a_idx = st.selectbox("Simulación A", range(len(simulations)), format_func=lambda i: sim_labels[i], key="cmp_a")
        with cols_compare[1]:
            sim_b_idx = st.selectbox("Simulación B", range(len(simulations)), format_func=lambda i: sim_labels[i], key="cmp_b", index=min(1, len(simulations)-1))

        sim_a = simulations[sim_a_idx]
        sim_b = simulations[sim_b_idx]

        col1, col2 = st.columns(2)
        for col, sim, label in [(col1, sim_a, "Simulación A"), (col2, sim_b, "Simulación B")]:
            with col:
                cfg = sim.get("config", {})
                m = sim.get("summary", {})
                st.markdown(
                    f"""
                    <div style="background:white; border:1px solid #E2E8F0; border-radius:12px;
                                padding:1.25rem; box-shadow:0 1px 3px rgba(0,0,0,0.06);">
                        <div style="font-weight:700; color:#1B3A6B; margin-bottom:0.75rem;">{label}</div>
                        <div style="font-size:0.85rem; color:#4A5568; line-height:1.9;">
                            <div><strong>Activos:</strong> {', '.join(cfg.get('tickers',[]))}</div>
                            <div><strong>Capital inicial:</strong> ${cfg.get('initial_capital',0):,.0f}</div>
                            <div><strong>Horizonte:</strong> {cfg.get('projection_years','?')} años</div>
                            <hr style="border-color:#EDF2F7; margin:0.5rem 0;">
                            <div><strong>Capital mediano:</strong> ${m.get('median_capital',0):,.0f}</div>
                            <div><strong>VaR 95%:</strong> ${m.get('var_95_value',0):,.0f}</div>
                            <div><strong>Max Drawdown:</strong> {m.get('max_drawdown',0):.2%}</div>
                            <div><strong>CAGR:</strong> {m.get('cagr_median',0):.2%}</div>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

    spacer()

    # ── Delete simulations ─────────────────────────────────────────────────
    section_header("Gestionar Simulaciones")
    sim_to_delete = st.selectbox(
        "Selecciona una simulación para eliminar",
        range(len(simulations)),
        format_func=lambda i: sim_labels[i] if len(simulations) >= 2 else sim_labels[0] if simulations else "",
        key="del_sim_select",
    )
    if st.button("🗑️ Eliminar Simulación Seleccionada", key="del_sim_btn"):
        sim_id = simulations[sim_to_delete]["id"]
        delete_simulation(sim_id)
        st.success("Simulación eliminada.")
        st.rerun()

    # ── Export all ─────────────────────────────────────────────────────────
    import io
    csv_buf = io.StringIO()
    display_df.to_csv(csv_buf, index=False)
    st.download_button(
        "⬇️ Exportar todo el historial (CSV)",
        data=csv_buf.getvalue(),
        file_name="smartrisk_historial.csv",
        mime="text/csv",
    )
