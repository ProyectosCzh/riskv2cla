"""
SmartRisk - Metrics Cards UI Components
"""
import streamlit as st


def metric_card(label: str, value: str, delta: str = "", color: str = "#1B3A6B") -> None:
    """Render a single metric card via HTML."""
    delta_html = f'<div class="metric-delta">{delta}</div>' if delta else ""
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">{label}</div>
            <div class="metric-value" style="color:{color};">{value}</div>
            {delta_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def alert_box(message: str, alert_type: str = "info") -> None:
    """
    Render an alert box.
    alert_type: 'info' | 'warning' | 'danger' | 'success'
    """
    st.markdown(
        f'<div class="alert-{alert_type}">{message}</div>',
        unsafe_allow_html=True,
    )


def tooltip_box(text: str) -> None:
    """Render an educational tooltip box."""
    st.markdown(
        f'<div class="tooltip-box">💡 {text}</div>',
        unsafe_allow_html=True,
    )


def section_header(title: str, subtitle: str = "") -> None:
    """Render a section header with optional subtitle."""
    st.markdown(f'<div class="section-header">{title}</div>', unsafe_allow_html=True)
    if subtitle:
        st.markdown(f'<div class="section-subheader">{subtitle}</div>', unsafe_allow_html=True)


def page_header(title: str, subtitle: str = "") -> None:
    """Render a page title block."""
    st.markdown(f'<div class="page-title">{title}</div>', unsafe_allow_html=True)
    if subtitle:
        st.markdown(f'<div class="page-subtitle">{subtitle}</div>', unsafe_allow_html=True)


def spacer(height: int = 1) -> None:
    st.markdown(f'<div style="height:{height}rem"></div>', unsafe_allow_html=True)
