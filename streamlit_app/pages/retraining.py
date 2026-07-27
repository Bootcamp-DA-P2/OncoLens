from __future__ import annotations

from time import perf_counter

import pandas as pd
import streamlit as st

from database.cdss_database import CDSSDatabase
from services.retraining import RetrainingService
from streamlit_app.components.cards import render_kpi_card, render_status_card
from streamlit_app.components.layout import render_page_header


def render() -> None:
    render_page_header(
        "Reentrenamiento de modelos",
        "Mejora continua supervisada",
        "Los casos confirmados por el profesional sanitario pueden incorporarse al proceso de reentrenamiento para mejorar el rendimiento de los modelos predictivos y aportar nuevo conocimiento al sistema.",
    )

    database = CDSSDatabase()
    service = RetrainingService()

    t0 = perf_counter()
    eligible_cases = database.get_confirmed_retraining_cases()
    load_ms = (perf_counter() - t0) * 1000.0

    st.session_state.setdefault("retraining_perf", {})
    st.session_state.retraining_perf = {"load_ms": load_ms}

    missing_cases = max(3 - len(eligible_cases), 0)

    kpi_cols = st.columns(3)
    with kpi_cols[0]:
        render_kpi_card("Casos preparados", str(len(eligible_cases)), "Confirmados con muestra disponible")
    with kpi_cols[1]:
        render_kpi_card("Minimo recomendado", "3", "Casos requeridos")
    with kpi_cols[2]:
        render_kpi_card("Casos faltantes", str(missing_cases), "Para completar el umbral")

    if st.button("Ejecutar reentrenamiento manual", type="primary", width="stretch"):
        result = service.run_manual_retraining()
        if result.get("ok"):
            render_status_card(
                "Reentrenamiento completado",
                f"Se genero una nueva version con {result.get('source_cases')} casos confirmados.",
                "ok",
            )
            st.rerun()
        else:
            render_status_card("Reentrenamiento no ejecutado", result.get("message", "No fue posible ejecutar el proceso."), "warning")

    with st.expander("Ver casos preparados para reentrenamiento"):
        if eligible_cases:
            preview = pd.DataFrame(eligible_cases)[["id", "patient_id", "final_prediction", "confirmed_diagnosis", "feedback_date"]]
            st.dataframe(preview, width="stretch", hide_index=True)
        else:
            st.info("Todavía no hay casos confirmados suficientes para alimentar el buffer de reentrenamiento.")
