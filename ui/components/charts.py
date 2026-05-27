"""
SmartRisk - Plotly Chart Components
"""
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

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
    n_display: int = 200,
) -> go.Figure:
    """
    Plot a fan chart of Monte Carlo simulation paths.
    Shows percentile bands + sample paths.
    """
    n_steps = paths.shape[1]
    t = np.linspace(0, projection_years, n_steps)

    p5  = np.percentile(paths, 5,  axis=0)
    p25 = np.percentile(paths, 25, axis=0)
    p50 = np.percentile(paths, 50, axis=0)
    p75 = np.percentile(paths, 75, axis=0)
    p95 = np.percentile(paths, 95, axis=0)

    fig = go.Figure()

    # ── Sample paths (thin, semi-transparent) ─────────────────────────────
    rng = np.random.default_rng(0)
    idx = rng.choice(paths.shape[0], size=min(n_display, paths.shape[0]), replace=False)
    for i in idx:
        fig.add_trace(go.Scatter(
            x=t, y=paths[i],
            mode="lines",
            line=dict(color="rgba(41, 82, 163, 0.07)", width=0.8),
            showlegend=False,
            hoverinfo="skip",
        ))

    # ── Confidence bands ───────────────────────────────────────────────────
    fig.add_trace(go.Scatter(
        x=np.concatenate([t, t[::-1]]),
        y=np.concatenate([p95, p5[::-1]]),
        fill="toself",
        fillcolor="rgba(99, 179, 237, 0.12)",
        line=dict(color="rgba(0,0,0,0)"),
        name="Rango 5%-95%",
        hoverinfo="skip",
    ))
    fig.add_trace(go.Scatter(
        x=np.concatenate([t, t[::-1]]),
        y=np.concatenate([p75, p25[::-1]]),
        fill="toself",
        fillcolor="rgba(99, 179, 237, 0.22)",
        line=dict(color="rgba(0,0,0,0)"),
        name="Rango 25%-75%",
        hoverinfo="skip",
    ))

    # ── Percentile lines ───────────────────────────────────────────────────
    for vals, color, name, dash in [
        (p95, GREEN,  "Escenario optimista (P95)",   "dash"),
        (p50, NAVY,   "Escenario mediano (P50)",      "solid"),
        (p5,  RED,    "Escenario pesimista (P5)",     "dash"),
    ]:
        fig.add_trace(go.Scatter(
            x=t, y=vals,
            mode="lines",
            line=dict(color=color, width=2, dash=dash),
            name=name,
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


def plot_efficient_frontier(
    frontier_df: pd.DataFrame,
    current_vol: float,
    current_ret: float,
    opt_vol: float | None = None,
    opt_ret: float | None = None,
) -> go.Figure:
    """Plot Markowitz efficient frontier."""
    fig = go.Figure()

    # Frontier curve colored by Sharpe
    fig.add_trace(go.Scatter(
        x=frontier_df["volatility"] * 100,
        y=frontier_df["return"] * 100,
        mode="lines+markers",
        marker=dict(
            size=5,
            color=frontier_df["sharpe"],
            colorscale="Blues",
            showscale=True,
            colorbar=dict(title="Sharpe", thickness=12, len=0.7),
        ),
        line=dict(color=BLUE, width=2),
        name="Frontera Eficiente",
    ))

    # Current portfolio
    fig.add_trace(go.Scatter(
        x=[current_vol * 100],
        y=[current_ret * 100],
        mode="markers",
        marker=dict(size=14, color=ORANGE, symbol="star", line=dict(color="white", width=1.5)),
        name="Portafolio Actual",
    ))

    # Optimized portfolio
    if opt_vol is not None and opt_ret is not None:
        fig.add_trace(go.Scatter(
            x=[opt_vol * 100],
            y=[opt_ret * 100],
            mode="markers",
            marker=dict(size=14, color=GREEN, symbol="diamond", line=dict(color="white", width=1.5)),
            name="Portafolio Optimizado",
        ))

    fig.update_layout(
        **_layout_kwargs(margin=dict(l=50, r=30, t=50, b=50)),
        title=dict(text="Frontera Eficiente de Markowitz", font=dict(size=15, color=NAVY), x=0),
        xaxis_title="Volatilidad Anual (%)",
        yaxis_title="Rendimiento Esperado Anual (%)",
        xaxis_ticksuffix="%",
        yaxis_ticksuffix="%",
        legend=dict(orientation="h", yanchor="bottom", y=-0.25, xanchor="left", x=0),
        height=420,
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


def plot_correlation_heatmap(corr_matrix: pd.DataFrame) -> go.Figure:
    """Correlation heatmap between assets."""
    tickers = list(corr_matrix.columns)
    z = corr_matrix.values

    fig = go.Figure(go.Heatmap(
        z=z,
        x=tickers,
        y=tickers,
        colorscale="RdBu_r",
        zmin=-1,
        zmax=1,
        text=np.round(z, 2),
        texttemplate="%{text}",
        textfont=dict(size=11),
        hoverongaps=False,
        colorbar=dict(title="ρ", thickness=12),
    ))

    fig.update_layout(
        **_layout_kwargs(margin=dict(l=60, r=30, t=50, b=60)),
        title=dict(text="Matriz de Correlación", font=dict(size=15, color=NAVY), x=0),
        height=350,
    )
    return fig
