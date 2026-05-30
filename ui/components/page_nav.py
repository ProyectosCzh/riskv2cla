"""
SmartRisk - Page-to-page navigation buttons (Previous / Next)
"""
import streamlit as st
from ui.components.navbar import NAV_ORDER, NAV_EXTRA, NAV_ADMIN
from auth.session_manager import is_admin


def get_flat_page_order() -> list[tuple]:
    order = list(NAV_ORDER) + list(NAV_EXTRA)
    if is_admin():
        order += NAV_ADMIN
    return order


def get_prev_next(current: str) -> tuple[str | None, str | None]:
    order = get_flat_page_order()
    pages = [p[0] for p in order]
    try:
        idx = pages.index(current)
    except ValueError:
        return None, None
    prev = pages[idx - 1] if idx > 0 else None
    next = pages[idx + 1] if idx < len(pages) - 1 else None
    return prev, next


def _go_to_page(page: str) -> None:
    st.session_state.current_page = page
    st.rerun()


def render_page_navigation(current_page: str) -> None:
    prev, next = get_prev_next(current_page)
    if prev is None and next is None:
        return

    st.markdown('<div class="page-nav-container">', unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col1:
        if prev is not None:
            st.button(
                "←  Anterior",
                key=f"pp_prev_{current_page}",
                use_container_width=True,
                on_click=_go_to_page,
                args=(prev,),
            )
    with col3:
        if next is not None:
            st.button(
                "Siguiente  →",
                key=f"pp_next_{current_page}",
                use_container_width=True,
                on_click=_go_to_page,
                args=(next,),
            )
    st.markdown('</div>', unsafe_allow_html=True)
