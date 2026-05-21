"""
SmartRisk - Custom CSS Injection
Professional fintech aesthetic: navy, slate, white. Clean and corporate.
"""

CUSTOM_CSS = """
<style>
/* ── Import fonts ─────────────────────────────────────────────────────────── */
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600;700&family=DM+Mono:wght@400;500&display=swap');

/* ── Root variables ──────────────────────────────────────────────────────── */
:root {
    --navy: #1B3A6B;
    --navy-light: #2952A3;
    --slate: #4A5568;
    --slate-light: #718096;
    --sky: #EBF4FF;
    --white: #FFFFFF;
    --bg: #F8FAFD;
    --border: #E2E8F0;
    --success: #38A169;
    --warning: #D69E2E;
    --danger: #E53E3E;
    --text: #1A202C;
    --text-muted: #718096;
    --card-shadow: 0 1px 3px rgba(0,0,0,0.08), 0 1px 2px rgba(0,0,0,0.05);
    --card-shadow-hover: 0 4px 12px rgba(27,58,107,0.12);
}

/* ── Global ──────────────────────────────────────────────────────────────── */
html, body, [class*="css"] {
    font-family: 'DM Sans', -apple-system, BlinkMacSystemFont, sans-serif !important;
    color: var(--text);
}

.main .block-container {
    padding-top: 1.5rem;
    padding-left: 2rem;
    padding-right: 2rem;
    max-width: 1280px;
}

/* ── Sidebar ─────────────────────────────────────────────────────────────── */
[data-testid="stSidebar"] {
    background: var(--navy) !important;
    border-right: none;
}

[data-testid="stSidebar"] * {
    color: rgba(255,255,255,0.9) !important;
}

[data-testid="stSidebar"] .stButton button {
    background: rgba(255,255,255,0.08) !important;
    border: 1px solid rgba(255,255,255,0.15) !important;
    color: white !important;
    width: 100%;
    text-align: left;
    border-radius: 8px;
    padding: 0.5rem 0.85rem;
    font-size: 0.875rem;
    font-weight: 500;
    transition: all 0.15s ease;
    margin-bottom: 2px;
}

[data-testid="stSidebar"] .stButton button:hover {
    background: rgba(255,255,255,0.18) !important;
    border-color: rgba(255,255,255,0.3) !important;
}

/* ── Metric Cards ────────────────────────────────────────────────────────── */
.metric-card {
    background: var(--white);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 1.25rem 1.5rem;
    box-shadow: var(--card-shadow);
    transition: box-shadow 0.2s ease;
}
.metric-card:hover {
    box-shadow: var(--card-shadow-hover);
}
.metric-card .metric-label {
    font-size: 0.75rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    color: var(--slate-light);
    margin-bottom: 0.35rem;
}
.metric-card .metric-value {
    font-size: 1.75rem;
    font-weight: 700;
    color: var(--navy);
    line-height: 1.2;
}
.metric-card .metric-delta {
    font-size: 0.8rem;
    color: var(--slate-light);
    margin-top: 0.25rem;
}

/* ── Section Headers ─────────────────────────────────────────────────────── */
.section-header {
    font-size: 1.25rem;
    font-weight: 700;
    color: var(--navy);
    margin-bottom: 0.25rem;
    padding-bottom: 0.6rem;
    border-bottom: 2px solid var(--sky);
}
.section-subheader {
    font-size: 0.875rem;
    color: var(--slate-light);
    margin-bottom: 1.25rem;
}

/* ── Alert Boxes ─────────────────────────────────────────────────────────── */
.alert-warning {
    background: #FFFBEB;
    border: 1px solid #F6E05E;
    border-left: 4px solid var(--warning);
    border-radius: 8px;
    padding: 0.875rem 1rem;
    color: #744210;
    font-size: 0.875rem;
}
.alert-danger {
    background: #FFF5F5;
    border: 1px solid #FEB2B2;
    border-left: 4px solid var(--danger);
    border-radius: 8px;
    padding: 0.875rem 1rem;
    color: #742A2A;
    font-size: 0.875rem;
}
.alert-success {
    background: #F0FFF4;
    border: 1px solid #9AE6B4;
    border-left: 4px solid var(--success);
    border-radius: 8px;
    padding: 0.875rem 1rem;
    color: #22543D;
    font-size: 0.875rem;
}
.alert-info {
    background: var(--sky);
    border: 1px solid #BEE3F8;
    border-left: 4px solid var(--navy-light);
    border-radius: 8px;
    padding: 0.875rem 1rem;
    color: #2A4365;
    font-size: 0.875rem;
}

/* ── Profile Badge ───────────────────────────────────────────────────────── */
.profile-badge {
    display: inline-block;
    padding: 0.3rem 0.85rem;
    border-radius: 20px;
    font-size: 0.8rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}
.badge-conservador { background: #C6F6D5; color: #22543D; }
.badge-moderado    { background: #BEE3F8; color: #2A4365; }
.badge-agresivo    { background: #FED7D7; color: #742A2A; }

/* ── Logo ────────────────────────────────────────────────────────────────── */
.logo-container {
    padding: 1.5rem 1rem 0.5rem;
    text-align: center;
}
.logo-text {
    font-size: 1.5rem;
    font-weight: 800;
    color: white !important;
    letter-spacing: -0.02em;
}
.logo-sub {
    font-size: 0.7rem;
    color: rgba(255,255,255,0.55) !important;
    letter-spacing: 0.1em;
    text-transform: uppercase;
}
.logo-divider {
    height: 1px;
    background: rgba(255,255,255,0.12);
    margin: 1rem 0.5rem;
}

/* ── Page Title ──────────────────────────────────────────────────────────── */
.page-title {
    font-size: 1.6rem;
    font-weight: 800;
    color: var(--navy);
    letter-spacing: -0.02em;
    margin-bottom: 0.2rem;
}
.page-subtitle {
    font-size: 0.9rem;
    color: var(--slate-light);
    margin-bottom: 1.5rem;
}

/* ── Tables ──────────────────────────────────────────────────────────────── */
[data-testid="stDataFrame"] {
    border: 1px solid var(--border) !important;
    border-radius: 10px !important;
    overflow: hidden;
}

/* ── Buttons (primary) ───────────────────────────────────────────────────── */
.stButton > button[kind="primary"] {
    background: var(--navy) !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    padding: 0.55rem 1.25rem !important;
}
.stButton > button[kind="primary"]:hover {
    background: var(--navy-light) !important;
}

/* ── Streamlit native overrides ──────────────────────────────────────────── */
[data-testid="metric-container"] {
    background: var(--white);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 0.875rem 1rem;
    box-shadow: var(--card-shadow);
}

/* ── Tooltips ────────────────────────────────────────────────────────────── */
.tooltip-box {
    background: #EFF6FF;
    border: 1px solid #BFDBFE;
    border-radius: 8px;
    padding: 0.75rem;
    font-size: 0.82rem;
    color: #1E40AF;
    margin-top: 0.5rem;
}

/* ── Scrollbar ───────────────────────────────────────────────────────────── */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: #F1F5F9; }
::-webkit-scrollbar-thumb { background: #CBD5E0; border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: #A0AEC0; }

/* ── Hide Streamlit branding ─────────────────────────────────────────────── */
#MainMenu { visibility: hidden; }
footer { visibility: hidden; }
header { visibility: hidden; }
</style>
"""


def inject_css() -> None:
    """Inject custom CSS into Streamlit app."""
    import streamlit as st
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)
