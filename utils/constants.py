"""Application constants shared across the project."""

APP_NAME = "OncoSeq Explorer"
APP_VERSION = "1.0.0"
APP_SUBTITLE = "Clinical Decision Support System based on RNA-Seq gene expression profiles."

NAV_ITEMS = ["Dashboard", "Modelos", "Nuevo Paciente", "Validación clínica", "Reentrenamiento de modelos"]

METHODOLOGY_BADGES = [
    "Validación agrupada por paciente",
    "Hold-out independiente",
    "Validación cruzada",
    "Optimización con RandomizedSearchCV",
    "Modelos interpretables",
    "Pipelines reproducibles",
]