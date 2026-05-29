"""
SmartRisk - Simulator Page (Monte Carlo)
"""
import pandas as pd
import streamlit as st

from auth.session_manager import get_current_user
from core.ds.stack import SimulationStack
from database.repositories import (
    get_portfolios_for_user,
    get_risk_profile_for_user,
)
from services.portfolio_service import build_portfolio_data
from services.simulation_service import run_simulation, persist_simulation
from ui.components.metrics_cards import (
    page_header, section_header, alert_box, tooltip_box, spacer, metric_card
)
from ui.components.charts import (
    plot_monte_carlo_paths,
    plot_final_value_histogram,
    plot_portfolio_weights,
    plot_historical_performance,
    plot_correlation_heatmap,
)
from config.settings import (
    DEFAULT_INITIAL_CAPITAL,
    DEFAULT_MONTHLY_DCA,
    DEFAULT_PROJECTION_YEARS,
    DEFAULT_HISTORY_YEARS,
    MAX_SIMULATIONS,
)


def render_simulator() -> None:
    user = get_current_user()
    if not user:
        return

    page_header("Simulador Monte Carlo 🔬", "Proyecta el futuro de tu portafolio con miles de escenarios estocásticos.")

    # ── Portfolio selection ────────────────────────────────────────────────
    section_header("1. Selecciona tu Portafolio")
    portfolios = get_portfolios_for_user(user["id"])
    draft = st.session_state.get("portfolio_draft")

    if not portfolios and not draft:
        alert_box("No tienes portafolios guardados. Ve a <strong>Mi Portafolio</strong> y construye uno primero.", "warning")
        return

    # Build selection options
    options = {}
    if draft:
        options[f"[Borrador] {draft.get('name','Portafolio')}"] = draft
    for p in portfolios:
        options[p["name"]] = {"tickers": p["assets"], "weights": p["weights"], "name": p["name"]}

    selected_name = st.selectbox("Portafolio a simular", list(options.keys()), key="sim_portfolio")
    selected_portfolio = options[selected_name]

    tickers = selected_portfolio["tickers"]
    weights = selected_portfolio["weights"]

    # Quick summary
    cols = st.columns(len(tickers))
    colors = ["#1B3A6B", "#2952A3", "#63B3ED", "#38A169", "#DD6B20"]
    for i, (t, w) in enumerate(zip(tickers, weights)):
        with cols[i]:
            st.markdown(
                f"""
                <div style="background:{colors[i%5]}; border-radius:8px; padding:0.6rem; text-align:center; color:white;">
                    <div style="font-weight:700; font-size:1rem;">{t}</div>
                    <div style="font-size:0.82rem; opacity:0.85;">{w*100:.1f}%</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    spacer()

    # ── Simulation parameters ──────────────────────────────────────────────
    section_header("2. Parámetros de Simulación")

    col1, col2 = st.columns(2)
    with col1:
        initial_capital = st.number_input(
            "Capital inicial (USD)",
            min_value=100,
            max_value=10_000_000,
            value=DEFAULT_INITIAL_CAPITAL,
            step=1000,
            key="sim_capital",
            help="Monto inicial de inversión en dólares.",
        )
        monthly_dca = st.number_input(
            "Aportación mensual DCA (USD)",
            min_value=0,
            max_value=100_000,
            value=DEFAULT_MONTHLY_DCA,
            step=100,
            key="sim_dca",
            help="Aportación mensual adicional (Dollar Cost Averaging). Ingresa 0 si no deseas aportar mensualmente.",
        )

    with col2:
        history_years = st.select_slider(
            "Ventana histórica de análisis",
            options=[1, 3, 5, 7, 10],
            value=DEFAULT_HISTORY_YEARS,
            key="sim_history",
            help="Años de datos históricos para calibrar los parámetros del modelo.",
        )
        projection_years = st.slider(
            "Horizonte de proyección (años)",
            min_value=1,
            max_value=20,
            value=DEFAULT_PROJECTION_YEARS,
            key="sim_projection",
            help="Período de tiempo futuro que deseas simular.",
        )

    col3, col4 = st.columns(2)
    with col3:
        sim_options = [1_000, 3_000, 5_000, 10_000]
        if MAX_SIMULATIONS not in sim_options:
            sim_options.append(MAX_SIMULATIONS)
        sim_options = sorted(sim_options)
        n_sims = st.select_slider(
            "Número de simulaciones",
            options=sim_options,
            value=min(5_000, MAX_SIMULATIONS),
            key="sim_n",
            help="Mayor número = mayor precisión, pero más tiempo de cómputo.",
        )
    with col4:
        st.markdown("<div style='height:0.3rem'></div>", unsafe_allow_html=True)
        tooltip_box(
            f"Ventana {'larga' if history_years >= 7 else 'corta'}: "
            f"{'Mayor significancia estadística, captura ciclos económicos completos.' if history_years >= 7 else 'Más sensible al contexto macroeconómico reciente (inflación, tasas).'}"
        )

    spacer()

    # ── Run simulation ─────────────────────────────────────────────────────
    run_btn = st.button("🚀 Ejecutar Simulación Monte Carlo", type="primary", use_container_width=True)

    if run_btn:
        progress_bar = st.progress(0.0, text="Preparando descarga...")

        def _on_download_progress(processed: int, total: int, ticker: str):
            progress_bar.progress(
                processed / total,
                text=f"⬇️ Descargando {ticker}... ({processed}/{total})",
            )

        st.caption("📌 Usando DownloadQueue (cola FIFO con lista enlazada simple) — los tickers se encolan y procesan en orden de llegada")
        portfolio_data = build_portfolio_data(
            tickers, weights, history_years,
            progress_callback=_on_download_progress,
        )
        progress_bar.empty()

        if portfolio_data is None:
            alert_box("❌ No se pudieron descargar los datos de mercado. Verifica los tickers e intenta nuevamente.", "danger")
            return

        # Risk profile audit
        risk_result = get_risk_profile_for_user(user["id"])
        if risk_result:
            audit = portfolio_data.risk_profile_check(risk_result["profile"])
            if not audit["ok"]:
                st.markdown(
                    f'<div class="alert-warning" style="margin-bottom:1rem;">🚨 <strong>Alerta de Perfil:</strong> {audit["message"]}</div>',
                    unsafe_allow_html=True,
                )

        with st.spinner(f"🔬 Simulando {n_sims:,} escenarios..."):
            result = run_simulation(
                portfolio_data,
                initial_capital=float(initial_capital),
                monthly_dca=float(monthly_dca),
                projection_years=float(projection_years),
                n_simulations=n_sims,
            )

        # Persist
        persist_simulation(user["id"], portfolio_data, result)

        # Push to simulation stack (LIFO)
        stack = st.session_state.get("sim_stack", SimulationStack())
        stack.push((result, portfolio_data, tickers, weights))
        st.session_state.sim_stack = stack
        st.session_state.sim_redo = SimulationStack()

        st.success("✅ Simulación completada. Resultados guardados.")
        st.rerun()

    # ── Display from stack (LIFO - top is most recent) ────────────────────
    stack = st.session_state.get("sim_stack")
    redo = st.session_state.get("sim_redo", SimulationStack())

    if stack and not stack.is_empty():
        result, portfolio_data, tickers, weights = stack.peek()
        _render_stack_navigation(stack, redo)
        _render_results(result, portfolio_data, tickers, weights)


def _render_stack_navigation(stack, redo) -> None:
    """Render LIFO stack navigation for simulation history."""
    if stack.size <= 1 and redo.is_empty():
        return
    st.markdown("---")
    cols = st.columns([1, 2, 1, 2])
    with cols[0]:
        if stack.size > 1 and st.button("⏪ Descartar última", use_container_width=True):
            redo.push(stack.pop())
            st.rerun()
    with cols[1]:
        total = stack.size + redo.size
        st.markdown(
            f"<div style='text-align:center; padding:0.3rem; color:#4A5568;'>"
            f"📚 <strong>Pila de simulación</strong> — {stack.size} de {total} en sesión"
            f"</div>",
            unsafe_allow_html=True,
        )
        st.caption("📌 SimulationStack (pila LIFO con lista doblemente enlazada) — push() apila, pop() desapila, peek() muestra el tope")
    with cols[2]:
        if not redo.is_empty() and st.button("Recuperar ⏩", use_container_width=True):
            stack.push(redo.pop())
            st.rerun()
    with cols[3]:
        if stack.size > 0 and st.button("🗑️ Vaciar historial", use_container_width=True):
            stack.clear()
            redo.clear()
            st.rerun()


def _render_results(result, portfolio_data, tickers: list, weights: list) -> None:
    spacer()
    section_header("📊 Resultados de la Simulación")

    metrics = result.metrics
    cfg = result.config

    # ── Key metrics row ────────────────────────────────────────────────────
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        metric_card(
            "Capital Final Esperado",
            f"${metrics['median_capital']:,.0f}",
            f"CAGR mediano: {metrics['cagr_median']:.2%}",
            color="#38A169",
        )
    with col2:
        metric_card(
            "VaR 95% (Peor caso probable)",
            f"${metrics['var_95_value']:,.0f}",
            f"Pérdida potencial: ${metrics['var_95_loss']:,.0f}",
            color="#E53E3E",
        )
    with col3:
        metric_card(
            "Max Drawdown (Mediana)",
            f"{metrics['max_drawdown']:.2%}",
            "Peor caída proyectada",
            color="#DD6B20",
        )
    with col4:
        metric_card(
            "Probabilidad de Pérdida",
            f"{metrics['prob_loss']:.1%}",
            f"sobre ${metrics['total_invested']:,.0f} invertidos",
            color="#E53E3E" if metrics["prob_loss"] > 0.3 else "#38A169",
        )

    spacer(0.5)

    col5, col6, col7, col8 = st.columns(4)
    with col5:
        metric_card("Sharpe Ratio", f"{portfolio_data.portfolio_sharpe:.2f}", "Eficiencia riesgo/retorno")
    with col6:
        metric_card("Volatilidad Anual", f"{portfolio_data.portfolio_sigma:.2%}", "Desviación estándar del portafolio")
    with col7:
        metric_card("Retorno Esperado", f"{portfolio_data.portfolio_mu:.2%}", "Media histórica anualizada")
    with col8:
        metric_card("CVaR 95%", f"${metrics['cvar_95']:,.0f}", "Pérdida esperada más allá del VaR")

    spacer()

    # ── Tooltips ───────────────────────────────────────────────────────────
    with st.expander("📚 ¿Qué significa cada métrica?"):
        col_a, col_b = st.columns(2)
        with col_a:
            tooltip_box("<strong>VaR 95%</strong>: En el 95% de los escenarios simulados, tu capital final será mayor a este valor. Es tu piso de protección en condiciones normales de mercado.")
            spacer(0.3)
            tooltip_box("<strong>Max Drawdown</strong>: La mayor caída desde un pico hasta un valle en la trayectoria mediana. Mide el peor dolor temporal que podrías experimentar.")
        with col_b:
            tooltip_box("<strong>Sharpe Ratio</strong>: Rendimiento extra (sobre la tasa libre de riesgo) por unidad de riesgo asumido. Valores > 1 son considerados buenos.")
            spacer(0.3)
            tooltip_box("<strong>CVaR (Expected Shortfall)</strong>: El promedio de pérdidas en el peor 5% de escenarios. Más conservador que el VaR.")

    spacer()

    # ── Charts ─────────────────────────────────────────────────────────────
    tab1, tab2, tab3, tab4 = st.tabs([
        "📈 Proyección", "📊 Distribución",
        "📉 Histórico", "🔗 Correlaciones"
    ])

    with tab1:
        fig = plot_monte_carlo_paths(result.paths, cfg.projection_years, cfg.initial_capital)
        st.plotly_chart(fig, use_container_width=True)
        alert_box(
            f"Basado en <strong>{cfg.n_simulations:,} escenarios</strong> usando GBM con datos de mercado reales. "
            f"Se muestran la mediana (negra), los 3 mejores escenarios (verde) y los 3 peores (rojo).",
            "info",
        )

    with tab2:
        col_hist, col_pie = st.columns([2, 1])
        with col_hist:
            fig2 = plot_final_value_histogram(result.final_values, cfg.initial_capital)
            st.plotly_chart(fig2, use_container_width=True)
        with col_pie:
            fig_pie = plot_portfolio_weights(tickers, weights)
            st.plotly_chart(fig_pie, use_container_width=True)

    with tab3:
        fig4 = plot_historical_performance(portfolio_data.prices, weights, tickers)
        st.plotly_chart(fig4, use_container_width=True)

        # Historical stats per asset
        section_header("Estadísticas Históricas por Activo")
        hist_rows = []
        for t in tickers:
            s = portfolio_data.stats.get(t, {})
            hist_rows.append({
                "Activo": t,
                "Retorno Anual": f"{s.get('mu', 0):.2%}",
                "Volatilidad Anual": f"{s.get('sigma', 0):.2%}",
                "Max Drawdown (histórico)": f"{s.get('max_drawdown', 0):.2%}",
            })
        st.dataframe(pd.DataFrame(hist_rows), use_container_width=True, hide_index=True)

    with tab4:
        fig5 = plot_correlation_heatmap(portfolio_data.corr_matrix)
        st.plotly_chart(fig5, use_container_width=True)
        tooltip_box(
            "La correlación mide cómo se mueven juntos dos activos. "
            "Valores cercanos a -1 indican movimientos opuestos (ideal para diversificación). "
            "Valores cercanos a 1 indican que suben y bajan al mismo tiempo."
        )


