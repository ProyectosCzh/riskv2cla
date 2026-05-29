"""
SmartRisk - Results History Page
"""
import streamlit as st
import pandas as pd

from auth.session_manager import get_current_user
from core.ds.sorting import SimulationSorter
from database.repositories import get_simulations_for_user, delete_simulation
from ui.components.metrics_cards import (
    page_header, section_header, alert_box, spacer, metric_card
)

SORT_OPTIONS = {
    "Más recientes": ("created_at", True),
    "Mejor capital final": ("summary.median_capital", True),
    "Peor capital final": ("summary.median_capital", False),
    "Mejor VaR 95%": ("summary.var_95_value", True),
    "Mejor CAGR": ("summary.cagr_median", True),
    "Peor CAGR": ("summary.cagr_median", False),
}


def _extract_value(sim: dict, dotted_key: str):
    """Extract a value from a nested dict using dot notation."""
    val = sim
    for part in dotted_key.split("."):
        if isinstance(val, dict):
            val = val.get(part, 0)
        else:
            return 0
    return val if isinstance(val, (int, float)) else 0


def render_results() -> None:
    user = get_current_user()
    if not user:
        return

    page_header("Historial de Simulaciones 📈", "Revisa y compara todos tus análisis anteriores.")

    simulations = get_simulations_for_user(user["id"])
    sim_labels = [f"{s['config'].get('tickers',[])} · {s.get('created_at','')[:10]}" for s in simulations]

    if not simulations:
        alert_box(
            "Aún no tienes simulaciones guardadas. Ve al <strong>Simulador</strong> para ejecutar tu primer análisis.",
            "info",
        )
        return

    # ── Sort controls ──────────────────────────────────────────────────────
    section_header(f"Tienes {len(simulations)} simulación(es) guardada(s)")
    col_sort, col_algo = st.columns([2, 1])
    with col_sort:
        selected_sort = st.selectbox(
            "Ordenar por",
            options=list(SORT_OPTIONS.keys()),
            index=0,
            key="sort_select",
        )
    sort_key, sort_reverse = SORT_OPTIONS[selected_sort]
    with col_algo:
        if sort_key == "created_at":
            sims_sorted = simulations
            algo_name = "—"
        else:
            def _sort_key_fn(s):
                return _extract_value(s, sort_key)
            sims_sorted = SimulationSorter.sort(simulations, key=_sort_key_fn, reverse=sort_reverse)
            algo_name = SimulationSorter.ALGORITHM
        st.markdown(
            f"<div style='padding-top:1.7rem; text-align:right; color:#718096; font-size:0.82rem;'>"
            f"Algoritmo: <strong>{algo_name}</strong> · {len(sims_sorted)} elementos</div>",
            unsafe_allow_html=True,
        )
        if sort_key != "created_at":
            st.caption(f"📌 SimulationSorter.sort() — {'QuickSort (O(n log n)) si > 10 elementos' if len(sims_sorted) > 10 else 'MergeSort (O(n log n)) si ≤ 10 elementos'}")

    rows = []
    for sim in sims_sorted:
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

    # ── Best / Worst highlight ─────────────────────────────────────────────
    if sort_key != "created_at" and len(display_df) >= 2:
        spacer(0.3)
        cols_best = st.columns(2)
        with cols_best[0]:
            best = display_df.iloc[0]
            st.markdown(
                f"<div style='background:#F0FFF4; border:1px solid #C6F6D5; border-radius:10px; "
                f"padding:0.7rem 1rem;'>"
                f"🏆 <strong>Mejor:</strong> {best['Portafolio']} — {best['Capital Mediano']}</div>",
                unsafe_allow_html=True,
            )
        with cols_best[1]:
            worst = display_df.iloc[-1]
            st.markdown(
                f"<div style='background:#FFF5F5; border:1px solid #FED7D7; border-radius:10px; "
                f"padding:0.7rem 1rem;'>"
                f"⚠️ <strong>Peor:</strong> {worst['Portafolio']} — {worst['Capital Mediano']}</div>",
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


