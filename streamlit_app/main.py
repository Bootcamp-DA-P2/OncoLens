"""Main Streamlit entrypoint for UI package."""

from pathlib import Path
import sys

import streamlit as st

# Ensure repository root is importable when running `streamlit run streamlit_app/main.py`.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from streamlit_app.config import config
from streamlit_app.ui.components.layout import apply_theme
from streamlit_app.ui.components.sidebar import render_sidebar
from streamlit_app.pages import dashboard, history, models, new_patient, retraining


def run() -> None:
    st.set_page_config(**config.PAGE_CONFIG)
    apply_theme()

    section = render_sidebar()

    if section == "Dashboard":
        dashboard.render()
    elif section == "Modelos":
        models.render()
    elif section == "Nuevo Paciente":
        new_patient.render()
    elif section == "Validación clínica":
        history.render()
    elif section == "Reentrenamiento de modelos":
        retraining.render()
