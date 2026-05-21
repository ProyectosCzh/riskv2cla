"""
SmartRisk - Portfolio Builder Page
"""
from __future__ import annotations

import json
from pathlib import Path

import streamlit as st

from auth.session_manager import get_current_user
from database.repositories import (
    get_portfolios_for_user,
    save_portfolio,
    delete_portfolio,
)
from ui.components.metrics_cards import (
    page_header, section_header, alert_box, tooltip_box, spacer
)
from config.settings import MAX_ASSETS


CONFIG_DIR = Path(__file__).resolve().parent.parent.parent / "config"


def _load_assets() -> dict:
    with open(CONFIG_DIR / "assets.json") as f:
        return json.load(f)


def _flat_asset_list(assets_data: dict) -> list[dict]:
    """Flatten categorized assets into a list."""
    flat = []
    for category, items in assets_data["categories"].items():
        for item in items:
            flat.append({**item, "category": category})
    return flat


def render_portfolio_builder() -> None:
    user = get_current_user()
    if not user:
        return

    page_header("Constructor de Portafolio 📊", "Selecciona hasta 5 activos y asigna los pesos de inversión.")

    assets_data = _load_assets()
    flat_assets = _flat_asset_list(assets_data)
    ticker_map = {a["ticker"]: a for a in flat_assets}
    all_tickers = [a["ticker"] for a in flat_assets]
    ticker_labels = {a["ticker"]: f"{a['ticker']} — {a['name']}" for a in flat_assets}

    # ── Asset selector ─────────────────────────────────────────────────────
    section_header("Selección de Activos", f"Elige entre {len(flat_assets)} instrumentos disponibles (máx. {MAX_ASSETS})")

    col_sel, col_info = st.columns([2, 1])
    with col_sel:
        # Category filter
        categories = ["Todas las categorías"] + list(assets_data["categories"].keys())
        selected_cat = st.selectbox("Filtrar por categoría", categories, key="pb_cat")

        if selected_cat == "Todas las categorías":
            available = all_tickers
        else:
            available = [a["ticker"] for a in flat_assets if a["category"] == selected_cat]

        display_options = [ticker_labels[t] for t in available]

        selected_labels = st.multiselect(
            "Activos seleccionados",
            options=display_options,
            max_selections=MAX_ASSETS,
            key="pb_selected",
            placeholder=f"Selecciona hasta {MAX_ASSETS} activos...",
            help=f"Puedes agregar hasta {MAX_ASSETS} activos a tu cartera.",
        )
        selected_tickers = []
        for label in selected_labels:
            ticker = label.split(" — ")[0]
            selected_tickers.append(ticker)

    with col_info:
        st.markdown("<div style='height: 2rem'></div>", unsafe_allow_html=True)
        st.markdown(
            f"""
            <div style="background:#EBF4FF; border:1px solid #BEE3F8; border-radius:10px; padding:1rem;">
                <div style="font-weight:700; color:#1B3A6B; margin-bottom:0.5rem;">
                    📋 Catálogo de Activos
                </div>
                <div style="font-size:0.82rem; color:#4A5568; line-height:1.7;">
                    • {len([a for a in flat_assets if a['type']=='stock'])} Acciones individuales<br>
                    • {len([a for a in flat_assets if a['type']=='etf'])} ETFs diversificados<br>
                    • {len([a for a in flat_assets if 'bond' in a['type']])} Fondos de Bonos<br>
                    • {len([a for a in flat_assets if a['type']=='commodity_etf'])} Commodities & Alternativos
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # ── Custom ticker ──────────────────────────────────────────────────────
    with st.expander("➕ Agregar ticker personalizado"):
        custom_ticker = st.text_input(
            "Ticker (ej. BRKB, COIN)",
            key="pb_custom",
            help="Ingresa cualquier ticker válido de Yahoo Finance.",
        ).upper().strip()
        if st.button("Agregar ticker", key="pb_add_custom"):
            if custom_ticker:
                if len(selected_tickers) >= MAX_ASSETS:
                    st.error(f"Ya tienes {MAX_ASSETS} activos seleccionados.")
                elif custom_ticker not in selected_tickers:
                    st.session_state["pb_custom_added"] = st.session_state.get("pb_custom_added", []) + [custom_ticker]
                    st.success(f"✅ {custom_ticker} agregado.")

    custom_added = st.session_state.get("pb_custom_added", [])
    selected_tickers = list(dict.fromkeys(selected_tickers + custom_added))[:MAX_ASSETS]

    spacer(0.5)

    # ── Weight assignment ──────────────────────────────────────────────────
    if not selected_tickers:
        alert_box("Selecciona al menos un activo para continuar.", "info")
        _render_saved_portfolios(user["id"])
        return

    section_header("Asignación de Pesos", "Desliza para asignar el porcentaje de inversión en cada activo.")
    tooltip_box("La suma de todos los pesos debe ser exactamente 100%. El sistema lo valida automáticamente.")

    weights = []
    remaining = 100

    for i, ticker in enumerate(selected_tickers):
        asset_info = ticker_map.get(ticker, {"name": "Ticker personalizado", "type": "custom"})
        is_last = (i == len(selected_tickers) - 1)

        col_label, col_slider, col_val = st.columns([1.5, 3, 0.7])
        with col_label:
            type_icons = {"stock": "📈", "etf": "📦", "bond_etf": "🛡️", "commodity_etf": "🏅", "reit": "🏢", "custom": "⭐"}
            icon = type_icons.get(asset_info.get("type", "custom"), "📈")
            st.markdown(
                f"""
                <div style="padding-top:0.55rem;">
                    <span style="font-weight:700; color:#1B3A6B;">{icon} {ticker}</span><br>
                    <span style="font-size:0.72rem; color:#A0AEC0;">{asset_info.get('name','')[:28]}</span>
                </div>
                """,
                unsafe_allow_html=True,
            )

        if is_last:
            # Last asset gets the remainder
            last_weight = max(0, 100 - sum(weights))
            with col_slider:
                st.slider(
                    f"Peso {ticker}", 0, 100, int(last_weight),
                    disabled=True, key=f"w_{ticker}_slider", label_visibility="collapsed"
                )
            with col_val:
                st.markdown(f"<div style='padding-top:0.5rem; font-weight:700; color:#1B3A6B;'>{last_weight:.0f}%</div>", unsafe_allow_html=True)
            weights.append(last_weight / 100)
        else:
            max_val = min(100, remaining)
            default_val = min(int(100 / len(selected_tickers)), max_val)
            w = st.slider(
                f"Peso {ticker}", 0, max_val, default_val,
                key=f"w_{ticker}_slider", label_visibility="collapsed"
            )
            with col_val:
                st.markdown(f"<div style='padding-top:0.5rem; font-weight:700; color:#1B3A6B;'>{w}%</div>", unsafe_allow_html=True)
            weights.append(w / 100)
            remaining -= w

    total_pct = sum(w * 100 for w in weights)
    is_valid = abs(total_pct - 100) < 0.5

    # Weight bar visualization
    _render_weight_bar(selected_tickers, weights)

    if is_valid:
        alert_box(f"✅ Suma total: {total_pct:.1f}% — Portafolio válido.", "success")
    else:
        alert_box(f"⚠️ Suma total: {total_pct:.1f}% — Debe ser 100%.", "warning")

    # ── Save portfolio ─────────────────────────────────────────────────────
    spacer(0.5)
    col_name, col_btn = st.columns([2, 1])
    with col_name:
        portfolio_name = st.text_input(
            "Nombre del portafolio",
            value=f"Mi Portafolio {', '.join(selected_tickers)}",
            key="pb_name",
        )
    with col_btn:
        st.markdown("<div style='height:1.9rem'></div>", unsafe_allow_html=True)
        if st.button("💾 Guardar Portafolio", type="primary", use_container_width=True, disabled=not is_valid):
            if is_valid:
                record = save_portfolio(user["id"], portfolio_name, selected_tickers, weights)
                # Also store as draft for simulator
                st.session_state.portfolio_draft = {
                    "id": record["id"],
                    "tickers": selected_tickers,
                    "weights": weights,
                    "name": portfolio_name,
                }
                st.success(f"✅ Portafolio «{portfolio_name}» guardado correctamente.")
                st.rerun()

    spacer()
    _render_saved_portfolios(user["id"])


def _render_weight_bar(tickers: list, weights: list) -> None:
    colors = ["#1B3A6B", "#2952A3", "#63B3ED", "#38A169", "#DD6B20"]
    bars = ""
    for i, (t, w) in enumerate(zip(tickers, weights)):
        pct = w * 100
        if pct > 0:
            color = colors[i % len(colors)]
            bars += f'<div style="background:{color}; width:{pct}%; height:100%; display:inline-block; position:relative;" title="{t}: {pct:.1f}%"></div>'

    st.markdown(
        f"""
        <div style="height:24px; border-radius:6px; overflow:hidden; background:#E2E8F0; margin:0.75rem 0; display:flex;">
            {bars}
        </div>
        <div style="display:flex; gap:1rem; flex-wrap:wrap; margin-bottom:0.5rem;">
        """ +
        "".join([
            f'<span style="font-size:0.75rem; color:#4A5568;">'
            f'<span style="display:inline-block; width:10px; height:10px; border-radius:2px; background:{colors[i%5]}; margin-right:4px;"></span>'
            f'{t} {w*100:.1f}%</span>'
            for i, (t, w) in enumerate(zip(tickers, weights))
        ]) +
        "</div>",
        unsafe_allow_html=True,
    )


def _render_saved_portfolios(user_id: str) -> None:
    portfolios = get_portfolios_for_user(user_id)
    if not portfolios:
        return

    section_header("Portafolios Guardados")
    for p in portfolios:
        col_info, col_actions = st.columns([3, 1])
        with col_info:
            weights_pct = [f"{w*100:.1f}%" for w in p["weights"]]
            allocation = " · ".join(f"{t} {w}" for t, w in zip(p["assets"], weights_pct))
            st.markdown(
                f"""
                <div style="background:white; border:1px solid #E2E8F0; border-radius:10px;
                            padding:0.875rem 1rem; box-shadow:0 1px 3px rgba(0,0,0,0.06);">
                    <div style="font-weight:600; color:#1B3A6B; margin-bottom:4px;">{p['name']}</div>
                    <div style="font-size:0.78rem; color:#A0AEC0;">{allocation}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with col_actions:
            st.markdown("<div style='height: 0.3rem'></div>", unsafe_allow_html=True)
            col_use, col_del = st.columns(2)
            with col_use:
                if st.button("Usar", key=f"use_{p['id']}", use_container_width=True):
                    st.session_state.portfolio_draft = {
                        "id": p["id"],
                        "tickers": p["assets"],
                        "weights": p["weights"],
                        "name": p["name"],
                    }
                    st.session_state.current_page = "simulator"
                    st.rerun()
            with col_del:
                if st.button("🗑️", key=f"del_{p['id']}", use_container_width=True):
                    delete_portfolio(p["id"])
                    st.rerun()
