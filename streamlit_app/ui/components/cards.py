"""Reusable card components."""

from __future__ import annotations

import streamlit as st

from streamlit_app.config import config


def render_kpi_card(title: str, value: str, subtitle: str = "") -> None:
    colors = config.COLORS
    st.markdown(
        f"""
        <div style="background:{colors['surface']};padding:20px;border-radius:12px;box-shadow:0 4px 15px rgba(148,163,184,0.12);text-align:center;margin-bottom:15px;border-top:5px solid {colors['primary']};border:1px solid {colors['border']};">
            <div style="font-size:13px;text-transform:uppercase;letter-spacing:0.8px;color:{colors['muted']};font-weight:600;margin-bottom:8px;">{title}</div>
            <div style="font-size:28px;font-weight:700;color:{colors['primary']};">{value}</div>
            <div style="font-size:12px;color:{colors['muted']};margin-top:6px;">{subtitle}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_status_card(title: str, text: str, kind: str = "ok") -> None:
    palette = {
        "ok": ("#DCE6F1", "#0F3759", "✓", "Actualizacion completada"),
        "warning": ("#E5E7EB", "#334155", "i", "Revisar informacion"),
        "error": ("#E2E8F0", "#7F1D1D", "!", "Se detecto un problema"),
    }
    border, title_color, icon, label = palette.get(kind, palette["ok"])
    st.markdown(
        f"""
        <div style="background:#FFFFFF;border:1px solid {border};border-radius:12px;padding:0.9rem 1rem;margin-bottom:0.75rem;box-shadow:0 6px 18px rgba(15, 23, 42, 0.04);">
            <div style="display:flex;align-items:flex-start;gap:10px;">
                <div style="flex:0 0 auto;width:22px;height:22px;border-radius:50%;border:1px solid #CBD5E1;color:#475569;font-size:13px;font-weight:600;display:flex;align-items:center;justify-content:center;line-height:1;">{icon}</div>
                <div style="flex:1;min-width:0;">
                    <div style="font-size:11px;letter-spacing:0.05em;text-transform:uppercase;color:#64748B;font-weight:600;">{label}</div>
                    <div style="font-size:15px;font-weight:600;color:{title_color};margin-top:2px;">{title}</div>
                    <div style="font-size:13px;color:#475569;line-height:1.55;margin-top:3px;">{text}</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )