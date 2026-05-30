"""
SmartRisk - UI Assets (logos, icons, etc.)
"""
import base64
import streamlit as st
from pathlib import Path

ASSETS_DIR = Path(__file__).parent
LOGORISK_PATH = ASSETS_DIR / "logorisk.jpg"


@st.cache_data
def _load_logo_b64() -> str:
    with open(LOGORISK_PATH, "rb") as f:
        return base64.b64encode(f.read()).decode()


def get_logo_img_tag(height: str = "1.6rem") -> str:
    b64 = _load_logo_b64()
    return (
        f'<img src="data:image/jpeg;base64,{b64}" '
        f'style="height:{height}; vertical-align:middle; '
        f'margin-right:0.35rem; display:inline-block;">'
    )
