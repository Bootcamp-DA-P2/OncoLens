import uuid
from datetime import datetime
from time import perf_counter
from typing import Any, Dict, List

from postgrest.exceptions import APIError
from database.supabase_client import supabase


class CDSSDatabase:
    def __init__(self):
        self.last_timings: Dict[str, Any] = {}

    @staticmethod
    def _response_data(response: Any) -> Any:
        return getattr(response, "data", None) if response is not None else None

    @staticmethod
    def _first_row(data: Any) -> Dict[str, Any] | None:
        if isinstance(data, list):
            return data[0] if data else None
        if isinstance(data, dict):
            return data
        return None
    
    def _get_patient_db_id(self, clinical_patient_id: str) -> int:
        response = (
            supabase
            .table("patients")
            .select("id")
            .eq("clinical_patient_id", clinical_patient_id)
            .maybe_single()
            .execute()
        )

        row = self._first_row(self._response_data(response))
        if row is None:
            raise ValueError(
                f"No existe el paciente con clinical_patient_id='{clinical_patient_id}'"
            )

        return int(row["id"])


    def save_or_update_patient(self, patient: Dict[str, Any]) -> None:
        clinical_patient_id = str(patient.get("patient_id", "")).strip()
        data = {
            "clinical_patient_id": clinical_patient_id,
            "first_name": patient.get("first_name"),
            "last_name": patient.get("last_name"),
            "age": patient.get("age"),
            "sex": patient.get("sex"),
            "nationality": patient.get("nationality"),
            "weight_kg": patient.get("weight_kg"),
            "height_cm": patient.get("height_cm"),
            "bmi": patient.get("bmi"),
            "bmi_classification": patient.get("bmi_classification"),
            "smoker_status": patient.get("smoker_status"),
            "cohort": patient.get("cohort"),
            "notes": patient.get("clinical_notes"),
        }

        existing = (
            supabase
            .table("patients")
            .select("id")
            .eq("clinical_patient_id", clinical_patient_id)
            .limit(1)
            .execute()
        )

        if existing.data:
            (
                supabase
                .table("patients")
                .update(data)
                .eq("id", existing.data[0]["id"])
                .execute()
            )
        else:
            (
                supabase
                .table("patients")
                .insert(data)
                .execute()
            )

    def save_prediction(self, prediction: Dict[str, Any]) -> int:
        timings: Dict[str, float | str] = {}

        clinical_patient_id = str(prediction.get("patient_id") or "").strip()
        if not clinical_patient_id:
            raise ValueError("patient_id es obligatorio para guardar la prediccion.")

        t0 = perf_counter()
        patient = (
            supabase
            .table("patients")
            .select("id")
            .eq("clinical_patient_id", clinical_patient_id)
            .maybe_single()
            .execute()
        )
        timings["patient_lookup_ms"] = round((perf_counter() - t0) * 1000.0, 2)

        patient_data = self._first_row(self._response_data(patient))

        if not patient_data:
            t0 = perf_counter()
            created = (
                supabase
                .table("patients")
                .insert({"clinical_patient_id": clinical_patient_id})
                .execute()
            )
            timings["patient_create_ms"] = round((perf_counter() - t0) * 1000.0, 2)

            created_data = self._first_row(self._response_data(created))

            if not created_data:
                retry = (
                    supabase
                    .table("patients")
                    .select("id")
                    .eq("clinical_patient_id", clinical_patient_id)
                    .limit(1)
                    .execute()
                )
                created_data = self._first_row(self._response_data(retry))

            if not created_data:
                raise ValueError(
                    f"No fue posible crear el paciente con clinical_patient_id={clinical_patient_id}"
                )
            patient_id = created_data["id"]
        else:
            patient_id = patient_data["id"]

        sample_id = prediction.get("sample_id")
        if not sample_id:
            sample_id = str(prediction.get("sample_name") or f"sample_{uuid.uuid4().hex[:12]}")

        sample_row = {
            "sample_id": sample_id,
            "patient_id": patient_id,
            "source_patient_id": clinical_patient_id,
            "tipo": "tumor" if bool(prediction.get("is_tumor", False)) else "normal",
            "cohorte": (
                prediction.get("stage2_prediction")
                if bool(prediction.get("is_tumor", False))
                else prediction.get("cohort")
            ) or "BRCA",
            "fecha_carga": datetime.utcnow().isoformat(timespec="seconds"),
        }

        t0 = perf_counter()
        try:
            (
                supabase
                .table("samples")
                .upsert(sample_row, on_conflict="sample_id")
                .execute()
            )
        except APIError as exc:
            if "muestras_cohorte_check" not in str(exc):
                raise
            sample_row["cohorte"] = "BRCA"
            (
                supabase
                .table("samples")
                .upsert(sample_row, on_conflict="sample_id")
                .execute()
            )
        timings["sample_upsert_ms"] = round((perf_counter() - t0) * 1000.0, 2)

        data = {
            "patient_id": patient_id,
            "sample_id": sample_id,
            "sample_values_json": prediction.get("sample_values_json"),
            "validation_summary_json": prediction.get("validation_summary_json"),
            "stage1_prediction": prediction.get("stage1_prediction"),
            "stage1_probability": float(prediction.get("stage1_probability", 0.0)),
            "stage2_prediction": prediction.get("stage2_prediction"),
            "stage2_probability": prediction.get("stage2_probability"),
            "final_prediction": prediction.get("final_prediction"),
            "confidence_level": prediction.get("confidence_level"),
            "n_features": int(prediction.get("n_features", 0)),
            "user_notes": prediction.get("user_notes"),
            "validated": bool(prediction.get("validated", False)),
            "is_tumor": bool(prediction.get("is_tumor", False)),
            "processed": False,
            "model2_probabilities_json": prediction.get("model2_probabilities_json"),
            "case_status": "PENDIENTE_VALIDACION",
            "comparison_result": None,
            "retraining_eligible": False,
            "version_id": prediction.get("version_id"),
        }

        t0 = perf_counter()
        existing_prediction = (
            supabase
            .table("predictions")
            .select("id")
            .eq("sample_id", sample_id)
            .limit(1)
            .execute()
        )
        timings["prediction_lookup_ms"] = round((perf_counter() - t0) * 1000.0, 2)

        if existing_prediction.data:
            timings["prediction_write_mode"] = "reuse_existing"
            timings["prediction_write_ms"] = 0.0
            self.last_timings = timings
            return int(existing_prediction.data[0]["id"])

        t0 = perf_counter()
        response = (
            supabase
            .table("predictions")
            .insert(data)
            .execute()
        )
        timings["prediction_write_mode"] = "insert"
        timings["prediction_write_ms"] = round((perf_counter() - t0) * 1000.0, 2)
        self.last_timings = timings

        inserted = self._first_row(self._response_data(response))
        if inserted is None:
            retry = (
                supabase
                .table("predictions")
                .select("id")
                .eq("sample_id", sample_id)
                .limit(1)
                .execute()
            )
            inserted = self._first_row(self._response_data(retry))

        if inserted is None:
            raise ValueError(f"No fue posible recuperar la prediccion guardada para sample_id={sample_id}")

        return int(inserted["id"])


    def get_predictions(self, limit: int = 500) -> List[Dict[str, Any]]:

        response = (
            supabase
            .table("predictions")
            .select("""
                *,
                patients(
                    clinical_patient_id,
                    first_name,
                    last_name,
                    age,
                    sex,
                    nationality,
                    weight_kg,
                    height_cm,
                    bmi,
                    bmi_classification,
                    smoker_status,
                    cohort,
                    notes
                ),
                samples(
                    sample_id,
                    tipo,
                    cohorte,
                    fecha_carga
                ),
                clinical_feedback(
                    confirmed_diagnosis,
                    clinical_notes,
                    is_correct,
                    feedback_date
                )
            """)
            .order("timestamp", desc=True)
            .limit(limit)
            .execute()
        )

        rows = []
        for row in response.data or []:
            patient_info = row.get("patients") or {}
            sample_info = row.get("samples") or {}
            feedback_info = row.get("clinical_feedback") or []
            if isinstance(feedback_info, list):
                feedback = feedback_info[0] if feedback_info else {}
            else:
                feedback = feedback_info

            rows.append(
                {
                    **row,
                    "patient_id": patient_info.get("clinical_patient_id", row.get("patient_id")),
                    "first_name": patient_info.get("first_name"),
                    "last_name": patient_info.get("last_name"),
                    "age": patient_info.get("age"),
                    "sex": patient_info.get("sex"),
                    "nationality": patient_info.get("nationality"),
                    "weight_kg": patient_info.get("weight_kg"),
                    "height_cm": patient_info.get("height_cm"),
                    "bmi": patient_info.get("bmi"),
                    "bmi_classification": patient_info.get("bmi_classification"),
                    "smoker_status": patient_info.get("smoker_status"),
                    "cohort": patient_info.get("cohort"),
                    "clinical_notes": patient_info.get("notes"),
                    "sample_id": sample_info.get("sample_id", row.get("sample_id")),
                    "sample_tipo": sample_info.get("tipo"),
                    "sample_cohorte": sample_info.get("cohorte"),
                    "sample_fecha_carga": sample_info.get("fecha_carga"),
                    "confirmed_diagnosis": feedback.get("confirmed_diagnosis"),
                    "feedback_date": feedback.get("feedback_date"),
                    "is_correct": feedback.get("is_correct"),
                }
            )

        return rows







    def confirm_case_validation(
        self,
        prediction_id: int,
        confirmed_diagnosis: str,
        clinical_notes: str = "",
    ) -> Dict[str, Any]:

        confirmed_label = confirmed_diagnosis.strip().upper()

        response = (
            supabase
            .table("predictions")
            .select("*")
            .eq("id", prediction_id)
            .limit(1)
            .execute()
        )

        prediction = self._first_row(self._response_data(response))
        if prediction is None:
            return {
                "ok": False,
                "message": "Caso no encontrado."
            }

        predicted_label = prediction["final_prediction"].strip().upper()

        is_correct = predicted_label == confirmed_label

        comparison_result = (
            "CORRECTO"
            if is_correct
            else "INCORRECTO"
        )

        (
            supabase
            .table("predictions")
            .update({
                "case_status": "CONFIRMADO",
                "comparison_result": comparison_result,
                "retraining_eligible": True,
            })
            .eq("id", prediction_id)
            .execute()
        )

        feedback_row = {
            "prediction_id": prediction_id,
            "confirmed_diagnosis": confirmed_label,
            "clinical_notes": clinical_notes,
            "is_correct": is_correct,
        }
        feedback_existing = (
            supabase
            .table("clinical_feedback")
            .select("feedback_id")
            .eq("prediction_id", prediction_id)
            .limit(1)
            .execute()
        )
        feedback_existing_row = self._first_row(self._response_data(feedback_existing))
        if feedback_existing_row is not None:
            (
                supabase
                .table("clinical_feedback")
                .update(feedback_row)
                .eq("feedback_id", feedback_existing_row["feedback_id"])
                .execute()
            )
        else:
            (
                supabase
                .table("clinical_feedback")
                .insert({"feedback_id": str(uuid.uuid4()), **feedback_row})
                .execute()
            )

        if prediction.get("sample_values_json"):

            retraining_row = {
                "prediction_id": prediction_id,
                "patient_id": str(prediction["patient_id"]),
                "label_true": confirmed_label,
                "sample_id": prediction["sample_id"],
                "processed": False,
            }
            retraining_existing = (
                supabase
                .table("retraining_buffer")
                .select("buffer_id")
                .eq("prediction_id", prediction_id)
                .limit(1)
                .execute()
            )
            retraining_existing_row = self._first_row(self._response_data(retraining_existing))
            if retraining_existing_row is not None:
                (
                    supabase
                    .table("retraining_buffer")
                    .update(retraining_row)
                    .eq("buffer_id", retraining_existing_row["buffer_id"])
                    .execute()
                )
            else:
                (
                    supabase
                    .table("retraining_buffer")
                    .insert({"buffer_id": str(uuid.uuid4()), **retraining_row})
                    .execute()
                )

        return {
            "ok": True,
            "prediction": predicted_label,
            "confirmed": confirmed_label,
            "comparison_result": comparison_result,
            "is_correct": is_correct,
        }


    def get_confirmed_retraining_cases(self) -> List[Dict[str, Any]]:

        response = (
            supabase
            .table("predictions")
            .select("""
                id,
                patient_id,
                final_prediction,
                sample_values_json,
                case_status,
                retraining_eligible,
                clinical_feedback(
                    confirmed_diagnosis,
                    feedback_date
                )
            """)
            .eq("case_status", "CONFIRMADO")
            .eq("retraining_eligible", True)
            .not_.is_("sample_values_json", "null")
            .order("id")
            .execute()
        )

        rows = []
        for row in response.data or []:
            feedback_info = row.get("clinical_feedback") or []
            if isinstance(feedback_info, list):
                feedback = feedback_info[0] if feedback_info else {}
            else:
                feedback = feedback_info
            rows.append(
                {
                    "id": row.get("id"),
                    "patient_id": row.get("patient_id"),
                    "final_prediction": row.get("final_prediction"),
                    "sample_values_json": row.get("sample_values_json"),
                    "case_status": row.get("case_status"),
                    "retraining_eligible": row.get("retraining_eligible"),
                    "confirmed_diagnosis": feedback.get("confirmed_diagnosis"),
                    "feedback_date": feedback.get("feedback_date"),
                }
            )

        return rows


    def save_model_version(self, version: Dict[str, Any]) -> None:

        data = {
            "version_id": version.get("version_id"),
            "source_cases": int(version.get("source_cases", 0)),
            "model1_path": version.get("model1_path") or version.get("model_path"),
            "model2_path": version.get("model2_path"),
            "metrics_json": version.get("metrics_json"),
            "notes": version.get("notes"),
        }

        (
            supabase
            .table("model_versions")
            .insert(data)
            .execute()
        )


    def get_model_versions(self, limit: int = 20) -> List[Dict[str, Any]]:

        response = (
            supabase
            .table("model_versions")
            .select("""
                version_id,
                created_at,
                source_cases,
                model1_path,
                model2_path,
                metrics_json,
                notes
            """)
            .order("created_at", desc=True)
            .limit(limit)
            .execute()
        )

        return response.data or []


    def save_feedback(
        self,
        feedback_id: str,
        prediction_id: int,
        confirmed_diagnosis: str,
        clinical_notes: str,
        is_correct: bool | None,
    ) -> None:

        data = {
            "prediction_id": prediction_id,
            "confirmed_diagnosis": confirmed_diagnosis,
            "clinical_notes": clinical_notes,
            "is_correct": is_correct,
        }

        existing = (
            supabase
            .table("clinical_feedback")
            .select("feedback_id")
            .eq("prediction_id", prediction_id)
            .limit(1)
            .execute()
        )

        if existing.data:
            (
                supabase
                .table("clinical_feedback")
                .update(data)
                .eq("feedback_id", existing.data[0]["feedback_id"])
                .execute()
            )
        else:
            (
                supabase
                .table("clinical_feedback")
                .insert({"feedback_id": feedback_id, **data})
                .execute()
            )




    def get_statistics(self) -> Dict[str, Any]:

        total = (
            supabase
            .table("predictions")
            .select("id", count="exact")
            .execute()
        ).count

        tumors = (
            supabase
            .table("predictions")
            .select("id", count="exact")
            .eq("is_tumor", True)
            .execute()
        ).count

        confirmed = (
            supabase
            .table("predictions")
            .select("id", count="exact")
            .eq("case_status", "CONFIRMADO")
            .execute()
        ).count

        return {
            "total_predictions": total or 0,
            "tumor_predictions": tumors or 0,
            "normal_predictions": (total or 0) - (tumors or 0),
            "confirmed_cases": confirmed or 0,
            "pending_cases": (total or 0) - (confirmed or 0),
        }

