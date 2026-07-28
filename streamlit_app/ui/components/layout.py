"""Layout and theme primitives for Streamlit pages."""

from __future__ import annotations

import streamlit as st

from streamlit_app.config import config


def apply_theme() -> None:
    colors = config.COLORS
    st.markdown(
        f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600&family=IBM+Plex+Sans:wght@300;400;500;600&family=JetBrains+Mono:wght@400;500&display=swap');

        .stApp {{
            background-color: {colors['background']};
            color: {colors['text']} !important;
            font-family: "IBM Plex Sans", "Segoe UI", sans-serif;
        }}
        .stMarkdown, p, span, label, .stCaption {{ color: #334155 !important; }}
        [data-testid="stAppViewContainer"] .main .block-container {{
            padding-left: clamp(2.2rem, 3.2vw, 3rem);
            padding-right: clamp(1.3rem, 2.4vw, 2.1rem);
            max-width: 1280px;
        }}
        h1, h2, h3, h4, h5, h6 {{
            color: {colors['text']} !important;
            font-family: "Space Grotesk", "IBM Plex Sans", sans-serif !important;
            font-weight: 600 !important;
        }}
        [data-testid="stSidebar"] {{
            background-color: {colors['sidebar']} !important;
            border-right: 1px solid #2C3F56;
        }}
        [data-testid="stSidebar"] * {{ color: #F1F5F9 !important; }}
        [data-testid="stSidebar"] [data-baseweb="radio"] label {{
            border-radius: 10px;
            padding: 0.45rem 0.6rem;
            transition: background-color 0.2s ease;
        }}
        [data-testid="stSidebar"] [data-baseweb="radio"] label:hover {{
            background: rgba(22, 82, 240, 0.2);
        }}
        [data-testid="stSidebar"] [data-testid="stExpander"] summary,
        [data-testid="stSidebar"] [data-testid="stExpander"] summary * {{
            color: #6E8093 !important;
            font-weight: 600 !important;
        }}
        [data-testid="stSidebar"] .ol-filter-group-title {{
            margin: 4px 0 6px 0;
            font-size: 12px;
            line-height: 1.25;
            color: #8EA2B7 !important;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.04em;
        }}
        [data-testid="stSidebar"] .ol-filter-group-divider {{
            height: 1px;
            margin: 14px 0 10px 0;
            background: linear-gradient(90deg, rgba(198, 212, 227, 0.28), rgba(198, 212, 227, 0.08));
        }}
        .oncoseq-section-card {{
            background: rgba(255,255,255,0.88);
            border: 1px solid {colors['border']};
            border-radius: 14px;
            box-shadow: 0 6px 20px rgba(148, 163, 184, 0.10);
            padding: 18px;
            margin-bottom: 16px;
            backdrop-filter: blur(4px);
        }}
        .oncoseq-section-title {{
            font-size: 18px;
            font-weight: 700;
            color: {colors['text']};
            margin-bottom: 8px;
            border-left: 4px solid {colors['primary']};
            padding-left: 12px;
        }}
        .ol-header-shell {{
            background: linear-gradient(180deg, #FFFFFF 0%, #F8FBFF 100%);
            border: 1px solid {colors['border']};
            border-radius: 16px;
            padding: 20px 22px;
            margin-bottom: 14px;
            box-shadow: 0 10px 26px rgba(12, 30, 48, 0.05);
        }}
        .ol-header-title {{
            margin: 0;
            font-size: clamp(30px, 3.2vw, 40px);
            line-height: 1.14;
            color: {colors['text']};
            font-family: "Space Grotesk", sans-serif;
            font-weight: 700;
        }}
        .ol-header-subtitle {{
            margin: 8px 0 0 0;
            font-size: 12px;
            line-height: 1.35;
            color: #6B7C8F;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.04em;
        }}
        [data-testid="stAppViewContainer"] .ol-header-shell p.ol-header-description {{
            margin: 7px 0 0 0;
            width: 100%;
            max-width: none;
            font-size: 11px !important;
            line-height: 1.56 !important;
            color: #90A1B3 !important;
            font-weight: 400 !important;
        }}
        @media (max-width: 900px) {{
            [data-testid="stAppViewContainer"] .main .block-container {{
                padding-left: 1rem;
                padding-right: 1rem;
            }}
        }}
        .stButton > button {{
            border-radius: 11px !important;
            border: 1px solid #D7E3F1 !important;
            box-shadow: 0 4px 14px rgba(12, 30, 48, 0.04) !important;
        }}
        [data-testid="stExpander"] {{
            border: 1px solid #DCE6F1;
            border-radius: 12px;
            background: #FFFFFF;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_page_header(
    title: str,
    subtitle: str,
    description: str | None = None,
    show_logo: bool = False,
) -> None:
    subtitle_text = subtitle.strip() if subtitle else ""
    normalized_subtitle = subtitle_text.lower()
    if "decision support" in normalized_subtitle and "platform" in normalized_subtitle:
        subtitle_text = ""

    if show_logo:
        logo_col, text_col = st.columns([1.1, 5])
        with logo_col:
            st.image(config.IMAGES_DIR / "onco_lens.png", width=150)
        with text_col:
            st.markdown(
                f"""
                <div class="ol-header-shell">
                    <h1 class="ol-header-title">{title}</h1>
                    {f'<div class="ol-header-subtitle">{subtitle_text}</div>' if subtitle_text else ''}
                    {f'<p class="ol-header-description">{description}</p>' if description else ''}
                </div>
                """,
                unsafe_allow_html=True,
            )
    else:
        st.markdown(
            f"""
            <div class="ol-header-shell">
                <h1 class="ol-header-title">{title}</h1>
                {f'<div class="ol-header-subtitle">{subtitle_text}</div>' if subtitle_text else ''}
                {f'<p class="ol-header-description">{description}</p>' if description else ''}
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.divider()