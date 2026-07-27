from __future__ import annotations

import os
from time import perf_counter

import pandas as pd
import streamlit as st

from database.cdss_database import CDSSDatabase
from managers.feedback_manager import FeedbackManager
from streamlit_app.components.cards import render_kpi_card, render_status_card
from streamlit_app.components.layout import render_page_header


VALID_DIAGNOSES = ["NORMAL", "BRCA", "COAD", "KIRC", "LUAD", "PRAD"]


def _is_dev_mode() -> bool:
    secret_flag = bool(st.secrets.get("DEV_MODE", False))
    env_flag = os.getenv("ONCOSEQ_DEV_MODE", "0").strip().lower() in {"1", "true", "yes", "on"}
    return secret_flag or env_flag


def _render_perf_metrics(perf: dict[str, float]) -> None:
    if not perf:
        return
    with st.expander("Metricas de rendimiento (dev)"):
        rows = [{"Etapa": key, "Tiempo (ms)": round(float(value), 2)} for key, value in perf.items()]
        st.dataframe(pd.DataFrame(rows), width="stretch", hide_index=True)


def _human_status(status: str) -> str:
    return "Confirmado" if status == "CONFIRMADO" else "Pendiente de validacion"


def _human_result(value: str | None) -> str:
    if value == "CORRECTO":
        return "Correcto"
    if value == "INCORRECTO":
        return "Incorrecto"
    return "-"


def _display_prediction(row: pd.Series) -> str:
    stage1 = str(row.get("stage1_prediction", "")).upper()
    stage2 = row.get("stage2_prediction")
    if stage2:
        return str(stage2).upper()
    if stage1 in {"1", "TUMOR"}:
        return "TUMOR"
    return "NORMAL"


def _prepare_table(dataframe: pd.DataFrame) -> pd.DataFrame:
    if dataframe.empty:
        return dataframe

    view = pd.DataFrame()
    view["ID del paciente"] = dataframe["patient_id"].fillna("N/D")
    view["Fecha del analisis"] = dataframe["timestamp"].fillna("")
    view["Prediccion"] = dataframe.apply(_display_prediction, axis=1)
    view["Diagnostico confirmado"] = dataframe["confirmed_diagnosis"].fillna("")
    view["Estado"] = dataframe["case_status"].fillna("PENDIENTE_VALIDACION").apply(_human_status)
    view["Resultado"] = dataframe["comparison_result"].apply(_human_result)
    return view


def _render_case_card(row: pd.Series) -> None:
    case_id = int(row["id"])
    patient_id = str(row.get("patient_id") or "N/D")
    prediction = _display_prediction(row)
    status = _human_status(str(row.get("case_status") or "PENDIENTE_VALIDACION"))
    timestamp = str(row.get("timestamp") or "")

    st.markdown(
        f"""
        <div style="background:#ffffff;border:1px solid #dbe7f3;border-radius:16px;padding:16px 18px;margin-bottom:12px;box-shadow:0 10px 26px rgba(15, 23, 42, 0.05);">
            <div style="display:flex;justify-content:space-between;gap:12px;align-items:flex-start;flex-wrap:wrap;">
                <div>
                    <div style="font-size:12px;color:#64748B;text-transform:uppercase;letter-spacing:0.6px;font-weight:700;">Caso pendiente</div>
                    <div style="font-size:18px;font-weight:700;color:#0F3759;margin-top:4px;">Paciente {patient_id}</div>
                    <div style="font-size:13px;color:#334155;margin-top:6px;">Prediccion registrada: <strong>{prediction}</strong></div>
                </div>
                <div style="text-align:right;min-width:180px;">
                    <div style="font-size:12px;color:#64748B;">Fecha</div>
                    <div style="font-size:13px;color:#0F172A;font-weight:600;">{timestamp}</div>
                    <div style="margin-top:8px;font-size:12px;color:#64748B;">Estado</div>
                    <div style="font-size:13px;color:#0F172A;font-weight:600;">{status}</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    selected_case_id = st.session_state.get("history_selected_case_id")
    is_open = selected_case_id == case_id
    button_text = "Cerrar formulario" if is_open else "Validar caso"
    if st.button(button_text, key=f"open_validation_{case_id}", width="stretch"):
        st.session_state.history_selected_case_id = None if is_open else case_id
        st.rerun()


def _render_pending_cases(dataframe: pd.DataFrame) -> None:
    pending = dataframe[dataframe["case_status"] != "CONFIRMADO"]
    st.markdown("### Validacion clinica")
    st.caption("Revise las predicciones pendientes y confirme el diagnostico clinico definitivo para incorporar resultados reales y favorecer la mejora continua de los modelos predictivos.")

    if pending.empty:
        st.info("No hay casos pendientes de validacion clinica.")
        return

    if "history_selected_case_id" not in st.session_state:
        st.session_state.history_selected_case_id = None

    selected_case_id = st.session_state.history_selected_case_id
    manager = FeedbackManager()
    for _, row in pending.iterrows():
        case_id = int(row["id"])
        _render_case_card(row)

        if selected_case_id != case_id:
            continue

        patient_id = str(row.get("patient_id") or "N/D")
        predicted = _display_prediction(row)
        with st.expander(f"Formulario de validacion | Caso #{case_id} | Paciente {patient_id}", expanded=True):
            st.write(f"Prediccion registrada por el modelo: **{predicted}**")
            diagnosis = st.selectbox(
                "Diagnostico definitivo",
                options=VALID_DIAGNOSES,
                key=f"diagnosis_{case_id}",
            )
            notes = st.text_area("Notas de validacion", key=f"notes_{case_id}")

            if st.button("Guardar validacion", key=f"save_validation_{case_id}", type="primary"):
                result = manager.submit_feedback(
                    prediction_id=case_id,
                    confirmed_diagnosis=diagnosis,
                    clinical_notes=notes,
                )
                if result.get("ok"):
                    readable = "Correcto" if result.get("is_correct") else "Incorrecto"
                    render_status_card(
                        "Validacion clinica registrada",
                        f"Prediccion del modelo: {result.get('prediction')} | Diagnostico confirmado: {result.get('confirmed')} | Resultado: {readable}",
                        "ok",
                    )
                    st.session_state.history_selected_case_id = None
                    st.rerun()
                else:
                    render_status_card("No se pudo guardar", result.get("message", "No se encontro el caso seleccionado."), "warning")


def render() -> None:
    render_page_header(
        "Validacion clinica",
        "Revision y confirmacion medica",
        "Revision de predicciones, confirmacion del diagnostico clinico y preparacion de casos para la mejora continua de los modelos predictivos.",
    )

    database = CDSSDatabase()
    perf: dict[str, float] = {}

    t0 = perf_counter()
    rows = database.get_predictions(limit=1000)
    perf["history_get_predictions_ms"] = (perf_counter() - t0) * 1000.0

    t0 = perf_counter()
    dataframe = pd.DataFrame(rows)
    perf["history_dataframe_build_ms"] = (perf_counter() - t0) * 1000.0

    if dataframe.empty:
        render_status_card("Sin casos", "Aun no hay casos analizados en el sistema.", "warning")
        return

    if "history_selected_case_id" not in st.session_state:
        st.session_state.history_selected_case_id = None

    total = len(dataframe)
    confirmed = int((dataframe["case_status"] == "CONFIRMADO").sum())
    pending = max(total - confirmed, 0)

    kpi_cols = st.columns(3)
    with kpi_cols[0]:
        render_kpi_card("Casos analizados", str(total), "Predicciones registradas")
    with kpi_cols[1]:
        render_kpi_card("Pendientes de validacion", str(pending), "Revision clinica")
    with kpi_cols[2]:
        render_kpi_card("Casos confirmados", str(confirmed), "Con diagnostico definitivo")

    st.markdown("### Casos registrados")
    st.caption("Listado resumido de todas las predicciones almacenadas. La tabla completa solo se muestra bajo demanda.")

    with st.expander("Ver listado completo de casos"):
        table_df = _prepare_table(dataframe)
        st.dataframe(
            table_df[["ID del paciente", "Fecha del analisis", "Prediccion", "Diagnostico confirmado", "Estado", "Resultado"]],
            width="stretch",
            hide_index=True,
        )

    _render_pending_cases(dataframe)

    if _is_dev_mode():
        _render_perf_metrics(perf)
