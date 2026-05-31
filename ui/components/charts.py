"""
SmartRisk - Plotly Chart Components
"""
import numpy as np
import pandas as pd
import plotly.graph_objects as go

# ── Color palette ──────────────────────────────────────────────────────────────
NAVY = "#1B3A6B"
BLUE = "#2952A3"
LIGHT_BLUE = "#63B3ED"
GREEN = "#38A169"
RED = "#E53E3E"
ORANGE = "#DD6B20"
GRAY = "#718096"
BG = "#F8FAFD"
GRID = "#E2E8F0"

PLOTLY_LAYOUT = dict(
    paper_bgcolor="white",
    plot_bgcolor="white",
    font=dict(family="DM Sans, sans-serif", color="#1A202C", size=12),
    xaxis=dict(gridcolor=GRID, showgrid=True, zeroline=False),
    yaxis=dict(gridcolor=GRID, showgrid=True, zeroline=False),
)


def _layout_kwargs(*, margin: dict[str, int] | None = None) -> dict:
    """Return a fresh Plotly layout dict with an optional chart-specific margin."""
    layout = dict(PLOTLY_LAYOUT)
    if margin is not None:
        layout["margin"] = margin
    return layout


def plot_monte_carlo_paths(
    paths: np.ndarray,
    projection_years: float,
    initial_capital: float,
) -> go.Figure:
    """
    Plot Monte Carlo paths showing median, 3 best and 3 worst scenarios.
    """
    n_steps = paths.shape[1]
    t = np.linspace(0, projection_years, n_steps)

    final_values = paths[:, -1]
    sorted_idx = np.argsort(final_values)
    worst_idx = sorted_idx[:3]
    best_idx = sorted_idx[-3:]
    median_idx = sorted_idx[len(sorted_idx) // 2]

    fig = go.Figure()

    # ── 3 worst paths (red shades) ─────────────────────────────────────────
    red_shades = ["#E53E3E", "#FC8181", "#FEB2B2"]
    for rank, i in enumerate(worst_idx):
        fig.add_trace(go.Scatter(
            x=t, y=paths[i],
            mode="lines",
            line=dict(color=red_shades[rank], width=1.2),
            name=f"Peor {'I' if rank == 0 else 'II' if rank == 1 else 'III'}",
            showlegend=True,
        ))

    # ── 3 best paths (green shades) ────────────────────────────────────────
    green_shades = ["#9AE6B4", "#48BB78", "#38A169"]
    for rank, i in enumerate(reversed(best_idx)):
        fig.add_trace(go.Scatter(
            x=t, y=paths[i],
            mode="lines",
            line=dict(color=green_shades[rank], width=1.2),
            name=f"Mejor {'I' if rank == 0 else 'II' if rank == 1 else 'III'}",
            showlegend=True,
        ))

    # ── Median path (black) ────────────────────────────────────────────────
    p50 = np.percentile(paths, 50, axis=0)
    fig.add_trace(go.Scatter(
        x=t, y=p50,
        mode="lines",
        line=dict(color="#000000", width=2.5),
        name="Mediana (P50)",
    ))

    # ── Initial capital reference ──────────────────────────────────────────
    fig.add_hline(
        y=initial_capital,
        line_dash="dot",
        line_color=GRAY,
        opacity=0.6,
        annotation_text=f"Capital inicial ${initial_capital:,.0f}",
        annotation_position="bottom right",
        annotation_font_size=10,
    )

    fig.update_layout(
        **_layout_kwargs(margin=dict(l=50, r=30, t=50, b=50)),
        title=dict(text="Proyección de Capital — Simulación Monte Carlo", font=dict(size=15, color=NAVY), x=0),
        xaxis_title="Años",
        yaxis_title="Valor del Portafolio (USD)",
        yaxis_tickprefix="$",
        yaxis_tickformat=",.0f",
        legend=dict(orientation="h", yanchor="bottom", y=-0.25, xanchor="left", x=0),
        height=460,
    )
    return fig


def plot_final_value_histogram(final_values: np.ndarray, initial_capital: float) -> go.Figure:
    """Plot distribution of final portfolio values."""
    fig = go.Figure()

    fig.add_trace(go.Histogram(
        x=final_values,
        nbinsx=60,
        marker_color=BLUE,
        opacity=0.8,
        name="Distribución de valores finales",
    ))

    median_val = float(np.median(final_values))
    p5_val = float(np.percentile(final_values, 5))

    for val, color, label in [
        (median_val,     NAVY,  f"Mediana ${median_val:,.0f}"),
        (p5_val,         RED,   f"VaR 95% ${p5_val:,.0f}"),
        (initial_capital, GRAY, f"Capital inicial ${initial_capital:,.0f}"),
    ]:
        fig.add_vline(x=val, line_dash="dash", line_color=color, line_width=2,
                      annotation_text=label, annotation_position="top",
                      annotation_font_size=10, annotation_font_color=color)

    fig.update_layout(
        **_layout_kwargs(margin=dict(l=50, r=30, t=50, b=50)),
        title=dict(text="Distribución del Capital Final", font=dict(size=15, color=NAVY), x=0),
        xaxis_title="Valor Final (USD)",
        xaxis_tickprefix="$",
        xaxis_tickformat=",.0f",
        yaxis_title="Frecuencia",
        showlegend=False,
        height=360,
    )
    return fig


def plot_portfolio_weights(tickers: list[str], weights: list[float]) -> go.Figure:
    """Donut chart for portfolio allocation."""
    colors = [NAVY, BLUE, LIGHT_BLUE, GREEN, ORANGE]
    fig = go.Figure(go.Pie(
        labels=tickers,
        values=[w * 100 for w in weights],
        hole=0.55,
        marker=dict(colors=colors[:len(tickers)], line=dict(color="white", width=2)),
        textinfo="label+percent",
        textfont=dict(size=12),
    ))
    fig.update_layout(
        **_layout_kwargs(margin=dict(l=20, r=20, t=50, b=20)),
        title=dict(text="Distribución del Portafolio", font=dict(size=15, color=NAVY), x=0),
        showlegend=False,
        height=320,
    )
    return fig


def plot_historical_performance(
    prices_dict: dict[str, pd.Series],
    weights: list[float],
    tickers: list[str],
) -> go.Figure:
    """Normalized historical performance chart."""
    fig = go.Figure()

    df = pd.DataFrame({t: prices_dict[t] for t in tickers if t in prices_dict}).dropna()
    normed = df / df.iloc[0] * 100

    colors_map = dict(zip(tickers, [NAVY, BLUE, LIGHT_BLUE, GREEN, ORANGE]))

    for ticker in tickers:
        if ticker in normed.columns:
            fig.add_trace(go.Scatter(
                x=normed.index,
                y=normed[ticker],
                mode="lines",
                name=ticker,
                line=dict(color=colors_map.get(ticker, GRAY), width=1.5),
            ))

    # Portfolio weighted
    if len(tickers) > 1:
        w_arr = np.array(weights)
        port = (normed[tickers] * w_arr).sum(axis=1)
        fig.add_trace(go.Scatter(
            x=port.index,
            y=port,
            mode="lines",
            name="Portafolio",
            line=dict(color=RED, width=2.5, dash="solid"),
        ))

    fig.update_layout(
        **_layout_kwargs(margin=dict(l=50, r=30, t=50, b=50)),
        title=dict(text="Rendimiento Histórico Normalizado (Base 100)", font=dict(size=15, color=NAVY), x=0),
        xaxis_title="Fecha",
        yaxis_title="Valor (Base 100)",
        legend=dict(orientation="h", yanchor="bottom", y=-0.3, xanchor="left", x=0),
        height=380,
    )
    return fig

