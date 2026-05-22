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
    with open(CONFIG_DIR / "assets.json", encoding="utf-8") as f:
        return json.load(f)


def _flat_asset_list(assets_data: dict) -> list[dict]:
    """Flatten categorized assets into a list."""
    flat = []
    for category, items in assets_data["categories"].items():
        for item in items:
            flat.append({**item, "category": category})
    return flat


def _normalize_weight_values(weight_map: dict[str, float]) -> dict[str, float]:
    """Scale current weights so they sum to 100.

    If all current values are zero, return an equal allocation.
    """
    total = sum(weight_map.values())
    if total <= 0:
        equal_weight = 100.0 / len(weight_map)
        return {ticker: equal_weight for ticker in weight_map}
    return {ticker: (value / total) * 100.0 for ticker, value in weight_map.items()}


def _request_normalization() -> None:
    """Request a weight normalization on the next render pass."""
    st.session_state["pb_normalize_requested"] = True


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
        # Show full asset list (no category filter). Do NOT provide a "select all" option.
        display_options = [ticker_labels[t] for t in all_tickers]

        selected_labels = st.multiselect(
            "Activos seleccionados",
            options=display_options,
            max_selections=MAX_ASSETS,
            key="pb_selected",
            placeholder=f"Selecciona hasta {MAX_ASSETS} activos...",
            help=f"Puedes agregar hasta {MAX_ASSETS} activos a tu cartera.",
        )
        selected_tickers = [label.split(" — ")[0] for label in selected_labels]

    selected_tickers = list(dict.fromkeys(selected_tickers))[:MAX_ASSETS]

    spacer(0.5)

    # ── Weight assignment ──────────────────────────────────────────────────
    if not selected_tickers:
        alert_box("Selecciona al menos un activo para continuar.", "info")
        _render_saved_portfolios(user["id"])
        return

    section_header("Asignación de Pesos", "Ingresa el porcentaje de inversión en cada activo.")
    tooltip_box("La suma de todos los pesos debe ser exactamente 100%. El sistema lo valida automáticamente.")

    default_pct = int(100 / len(selected_tickers)) if selected_tickers else 0

    if st.session_state.pop("pb_normalize_requested", False):
        current_weights = {
            ticker: float(st.session_state.get(f"w_{ticker}_input", default_pct))
            for ticker in selected_tickers
        }
        normalized_weights = _normalize_weight_values(current_weights)
        for ticker, value in normalized_weights.items():
            st.session_state[f"w_{ticker}_input"] = round(value, 2)

    # Initialize only the active selection keys once so every asset remains editable.
    for ticker in selected_tickers:
        key = f"w_{ticker}_input"
        if key not in st.session_state:
            st.session_state[key] = float(default_pct)

    weights_inputs: dict[str, float] = {
        ticker: float(st.session_state.get(f"w_{ticker}_input", default_pct))
        for ticker in selected_tickers
    }

    for i, ticker in enumerate(selected_tickers):
        asset_info = ticker_map[ticker]
        col_label, col_input, col_val = st.columns([1.5, 2.5, 0.7])
        with col_label:
            type_icons = {"stock": "📈", "etf": "📦", "bond_etf": "🛡️", "commodity_etf": "🏅", "reit": "🏢"}
            icon = type_icons.get(asset_info.get("type", "stock"), "📈")
            st.markdown(
                f"""
                <div style="padding-top:0.55rem;">
                    <span style="font-weight:700; color:#1B3A6B;">{icon} {ticker}</span><br>
                    <span style="font-size:0.72rem; color:#A0AEC0;">{asset_info.get('name','')[:28]}</span>
                </div>
                """,
                unsafe_allow_html=True,
            )

        key = f"w_{ticker}_input"
        with col_input:
            st.number_input(
                f"Peso {ticker} (%)",
                min_value=0.0,
                max_value=100.0,
                step=0.1,
                key=key,
                label_visibility="collapsed",
            )
        weights_inputs[ticker] = float(st.session_state.get(key, default_pct))
        with col_val:
            st.markdown(
                f"<div style='padding-top:0.5rem; font-weight:700; color:#1B3A6B;'>{weights_inputs[ticker]:.1f}%</div>",
                unsafe_allow_html=True,
            )

    # Normalize button: scale current percentages to sum to 100
    col_norm, col_spacer = st.columns([1, 3])
    with col_norm:
        st.button("🔁 Normalizar a 100%", on_click=_request_normalization)

    # Build final weights list (fractions) and validation
    weights_inputs = {
        ticker: float(st.session_state.get(f"w_{ticker}_input", default_pct))
        for ticker in selected_tickers
    }
    total_pct = sum(weights_inputs.values())
    weights = [weights_inputs[t] / 100.0 for t in selected_tickers]

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
