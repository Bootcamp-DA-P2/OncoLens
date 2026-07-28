"""Sidebar navigation rendering."""

from __future__ import annotations

import streamlit as st

from streamlit_app.config import config
from utils.constants import NAV_ITEMS


def render_sidebar() -> str:
    left, center, right = st.sidebar.columns([0.2, 12, 0.2])
    with center:
        st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)
        st.image(config.IMAGES_DIR / "onco_lens.png", width="stretch")
        st.markdown(
            "<div style='text-align:center;font-family:\"Space Grotesk\",sans-serif;font-size:28px;font-weight:700;color:#F8FAFC;letter-spacing:-0.02em;margin-top:10px;'>OncoLens</div>",
            unsafe_allow_html=True,
        )
        st.markdown(
            "<div style='text-align:center;color:#CBD5E1;font-size:12px;line-height:1.45;max-width:255px;margin:8px auto 0 auto;'>Plataforma de apoyo a la decision clinica desarrollada con fines de investigacion.</div>",
            unsafe_allow_html=True,
        )
        st.markdown("<div style='height:12px;'></div>", unsafe_allow_html=True)

    st.sidebar.divider()
    st.sidebar.markdown(
        "<div style='font-size:11px;color:#B6C3D4;text-transform:uppercase;letter-spacing:0.08em;font-weight:600;margin:2px 0 6px 0;'>Navegacion</div>",
        unsafe_allow_html=True,
    )
    return st.sidebar.radio("Secciones", NAV_ITEMS, index=0, label_visibility="collapsed")