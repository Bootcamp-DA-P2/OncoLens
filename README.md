# OncoLens: Plataforma de Clasificacion de Cancer con RNA-Seq (MLOps + Produccion)

[![CI/CD GitHub Actions](https://img.shields.io/badge/CI%2FCD-GitHub%20Actions-2088FF?style=for-the-badge&logo=github-actions&logoColor=white)](https://github.com)
[![Docker Hub](https://img.shields.io/badge/Registry-Docker%20Hub-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://hub.docker.com)
[![Deploy Render](https://img.shields.io/badge/Deploy-Render-46E3B7?style=for-the-badge&logo=render&logoColor=1A1A1A)](https://onco-seq-explorer-app.onrender.com/)
[![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-App-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io)
[![Supabase](https://img.shields.io/badge/Database-Supabase-3ECF8E?style=for-the-badge&logo=supabase&logoColor=white)](https://supabase.com)

Solucion de apoyo a decision clinica para clasificacion de muestras transcriptomicas en dos etapas: deteccion TUMOR vs NORMAL y tipificacion tumoral.

## Demo y web

- Demo en Render: https://onco-seq-explorer-app.onrender.com/
- Web del proyecto: https://bootcamp-da-p2.github.io/OncoLens/

---

## 1. Vision general del proyecto

OncoLens implementa un flujo completo de ciencia de datos y despliegue productivo:

- Analisis y preparacion de datos RNA-Seq.
- Prediccion jerarquica con modelos entrenados.
- Interfaz Streamlit para uso clinico supervisado.
- Registro de resultados y feedback clinico.
- Reentrenamiento manual con casos confirmados.
- Contenerizacion Docker.
- Pipeline CI/CD con GitHub Actions, Docker Hub y Render.

---

## 2. Caracteristicas funcionales

### Prediccion clinica en 2 etapas

1. Modelo 1: clasifica TUMOR vs NORMAL.
2. Modelo 2: si la muestra es tumoral, clasifica subtipo (BRCA, COAD, KIRC, LUAD, PRAD).

### Dashboard de analisis

- KPIs de muestras, cohortes y participantes.
- Distribuciones de cohortes y tipo de muestra.
- Proyecciones PCA (global y tumoral).
- Previsualizacion del espacio transcriptomico en HTML.

### Operacion y mejora continua

- Historial de casos y validacion clinica.
- Buffer de casos para reentrenamiento.
- Versionado de modelos en base de datos.

---

## 3. Herramientas y stack tecnologico

### Machine Learning y analisis

![scikit-learn](https://img.shields.io/badge/scikit--learn-Modelado-F7931E?style=flat-square&logo=scikitlearn&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-Datos-150458?style=flat-square&logo=pandas&logoColor=white)
![NumPy](https://img.shields.io/badge/NumPy-Calculo-013243?style=flat-square&logo=numpy&logoColor=white)
![Plotly](https://img.shields.io/badge/Plotly-Visualizacion-3F4F75?style=flat-square&logo=plotly&logoColor=white)

- Python
- scikit-learn
- pandas
- numpy
- plotly

### Aplicacion y backend

![Streamlit](https://img.shields.io/badge/Streamlit-Frontend-FF4B4B?style=flat-square&logo=streamlit&logoColor=white)
![Supabase](https://img.shields.io/badge/Supabase-Postgres-3ECF8E?style=flat-square&logo=supabase&logoColor=white)

- Streamlit
- Supabase (Postgres + API)

### MLOps e infraestructura

![Docker](https://img.shields.io/badge/Docker-Container-2496ED?style=flat-square&logo=docker&logoColor=white)
![Docker Compose](https://img.shields.io/badge/Docker%20Compose-Orquestacion-1D63ED?style=flat-square&logo=docker&logoColor=white)
![GitHub Actions](https://img.shields.io/badge/GitHub%20Actions-CI%2FCD-2088FF?style=flat-square&logo=github-actions&logoColor=white)
![Render](https://img.shields.io/badge/Render-Deploy-46E3B7?style=flat-square&logo=render&logoColor=1A1A1A)

- Docker y Docker Compose
- GitHub Actions
- Docker Hub
- Render

---

## 4. Estructura del repositorio

```text
Onco_Seq_Explorer/
|- .github/
|  |- workflows/
|     |- docker-publish.yml
|- .streamlit/
|- assets/
|- data/
|  |- raw/
|  |- processed/
|  |- retraining/
|  |- uploads/
|- database/
|- docs/
|- managers/
|- models/
|- notebooks/
|- reports/
|  |- metrics/
|  |- interpretability/
|- scripts/
|- services/
|- streamlit_app/
|  |- ui/
|  |  |- components/
|  |- pages/
|  |- pca/
|  |- config.py
|  |- main.py
|- utils/
|- app.py
|- Dockerfile
|- docker-compose.yml
|- .dockerignore
|- .gitignore
|- requirements.txt
|- README.md
```

---

## 5. Docker: estructura y uso

### Archivos de contenedorizacion

- Dockerfile: imagen de la aplicacion.
- docker-compose.yml: ejecucion local con variables y volumen de data.
- .dockerignore: controla contexto de build para incluir solo artefactos necesarios.

### Build de imagen

```bash
docker build -t onco-seq-explorer:latest .
```

### Ejecucion local

```bash
docker run -p 8501:8501 -v ${PWD}/data:/app/data onco-seq-explorer:latest
```

### Ejecucion con Compose

```bash
docker compose up --build
```

### Buenas practicas ya aplicadas

- Dependencias instaladas desde requirements.txt.
- Exposicion del puerto 8501.
- Arranque por streamlit run app.py.
- Reglas de inclusion/exclusion para artefactos runtime en .dockerignore.

---

## 6. CI/CD automatizado

El pipeline actual publica imagen Docker y dispara despliegue:

1. Push a ramas configuradas en workflow.
2. GitHub Actions ejecuta build de imagen Docker.
3. Push automatico a Docker Hub.
4. Llamada al deploy hook de Render.

### Secrets requeridos en GitHub

- DOCKERHUB_USERNAME
- DOCKERHUB_TOKEN
- RENDER_DEPLOY_HOOK

### Flujo de despliegue

```text
GitHub Push
   |
   v
GitHub Actions
   |
   v
Docker Build + Push (Docker Hub)
   |
   v
Render Deploy Hook
   |
   v
Aplicacion en Produccion
```

---

## 7. Configuracion local

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS/Linux
source .venv/bin/activate

pip install -r requirements.txt
streamlit run app.py
```

---

## 8. Persistencia y seguridad

La persistencia operativa se realiza con Supabase.

Tablas principales:

- patients
- samples
- predictions
- clinical_feedback
- retraining_buffer
- model_versions

El archivo scripts/supabase_rls_min_policies.sql incluye una base para permisos y politicas minimas del rol anon.

Aviso:

- Herramienta de apoyo para investigacion y soporte clinico.
- No sustituye el juicio medico profesional.

---

## 9. Verificacion y calidad

Comando recomendado de chequeo:

```bash
python scripts/oncocheck.py .
```

---

## 10. Equipo

| Integrante | Responsabilidad |
|---|---|
| Alejandra Duque Garcia | Diseno y creacion de base de datos |
| Noelia Sanchez Facila | Desarrollo de la app en Streamlit |
| Yasira Blanco Moreno | Desarrollo web y app en Streamlit |
| Romina Navea Rodriguez | Desarrollo web y verificación técnica |

Trabajo compartido del equipo:

- EDA
- modelado
- evaluacion
- contenerizacion

---

## Licencia

MIT License

---
##  Descargo Legal

Esta herramienta es **SOLO para fines educativos y de investigación**.

**NO debe usarse para:**
- Diagnóstico clínico
- Tratamiento médico
- Decisiones médicas sin validación profesional

Siempre consulta con personal médico certificado.

---

## 📞 Contacto

Para preguntas, sugerencias o colaboraciones, contactar al equipo de desarrollo.

**Estado:** ✓ Producción | v1.0.0 | 2026
