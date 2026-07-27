# CDSS Redesign Notes

# Rediseño del flujo clínico del CDSS

## Flujo actual de base de datos (Supabase)

### Esquema operativo

- `patients`: datos clínicos del paciente y contexto base.
- `samples`: metadatos de muestra (sample_id, tipo, cohorte, fecha).
- `predictions`: salida del flujo de inferencia y estado del caso.
- `clinical_feedback`: diagnóstico confirmado y notas clínicas.
- `retraining_buffer`: casos confirmados listos para reentrenamiento.
- `model_versions`: histórico de versiones y métricas del modelo reentrenado.

### Flujo 1: Nuevo Paciente (inferencia + persistencia)

1. `new_patient.py` valida muestra y prepara el contexto clínico.
2. `CDSSDatabase.save_or_update_patient(...)` crea/actualiza `patients`.
3. `PredictionManager.run_prediction(...)` ejecuta Modelo 1 y, si aplica, Modelo 2.
4. `CDSSDatabase.save_prediction(...)`:
  - asegura existencia de paciente en `patients`;
  - crea/actualiza `samples` (upsert por `sample_id`);
  - inserta en `predictions` con `case_status=PENDIENTE_VALIDACION`;
  - aplica guardas de idempotencia por `sample_id`.

### Flujo 2: Validación clínica

1. `history.py` consulta casos con `CDSSDatabase.get_predictions(...)`.
2. `FeedbackManager.submit_feedback(...)` delega en `CDSSDatabase.confirm_case_validation(...)`.
3. `confirm_case_validation(...)`:
  - actualiza `predictions` a `CONFIRMADO` y define `comparison_result`;
  - inserta/actualiza `clinical_feedback`;
  - inserta/actualiza `retraining_buffer` cuando hay muestra válida.

### Flujo 3: Reentrenamiento manual

1. `retraining.py` lista candidatos con `CDSSDatabase.get_confirmed_retraining_cases(...)`.
2. `RetrainingService.run_manual_retraining()` consume `retraining_buffer`.
3. Se registra la nueva versión con `CDSSDatabase.save_model_version(...)` en `model_versions`.

## Aspectos principales del modelo de datos

La tabla `predictions` almacena:

- Información del paciente y del contexto clínico en el momento del análisis.
- Resultados y probabilidades del Modelo 1 y del Modelo 2.
- Resumen del proceso de validación.
- Campos asociados al ciclo de validación clínica:
  - `confirmed_diagnosis`
  - `case_status` (`PENDIENTE_VALIDACION` o `CONFIRMADO`)
  - `comparison_result` (`CORRECTO` o `INCORRECTO`)
  - `is_correct`
  - `retraining_eligible`

## Principio de seguridad

Todos los informes y elementos de la interfaz presentan los resultados como **predicciones generadas por modelos de aprendizaje automático para apoyar la toma de decisiones clínicas**, y **nunca como un diagnóstico médico definitivo**.