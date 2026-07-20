# 📑 Master Data Explorer Pro

Plataforma BI (Business Intelligence) con asistente de IA, pensada para gente que se dedica al análisis de datos: extrae información desde 6 fuentes distintas, la limpia/transforma con un conjunto de herramientas profesionales, y la explora desde un dashboard interactivo.

Incluye registro/login de usuarios y un sistema de planes **Free / Premium** (demo funcional, sin procesador de pagos real conectado todavía).

## Características

- **6 motores de extracción** (simulados, con datos de ejemplo): Web Scraping, API Extraction, Login Scraping, Email Extraction, PDF Processing, Excel Processing.
- **Suite de transformación** por fuente: deduplicación, limpieza de texto (trim, mayúsculas/minúsculas, quitar tildes), reemplazo masivo, columnas calculadas con fórmulas.
- **Reglas de automatización**: guardá reglas de limpieza que se aplican solas en cada extracción futura, sin repetir el trabajo manual (plan Premium).
- **Exportación** a CSV y Excel.
- **API REST** (FastAPI) con un endpoint `POST /run-etl` para disparar el pipeline completo, pensado para integrarse con el scheduler automático (corre cada 12h).
- **Cuentas de usuario**: registro y login con contraseñas hasheadas (bcrypt).
- **Planes**:

  | | Free | Premium |
  |---|---|---|
  | Precio | $0/mes | $19/mes *(demo, no se cobra nada real)* |
  | Fuentes | Web, API, Email | Las 6 fuentes |
  | Límite por extracción | 50 registros | 10.000 registros |
  | Reglas de automatización | ❌ | ✅ |
  | Exportación a Excel | ✅ | ✅ |

  > 💡 El botón "Actualizar a Premium" es una maqueta: cambia el plan al instante en la base de datos, sin ningún cobro real. No hay ningún procesador de pagos (Stripe u otro) conectado todavía.

## Stack técnico

- **Frontend/Dashboard**: Streamlit (multi-página con `st.navigation`)
- **API**: FastAPI + Uvicorn
- **Datos**: pandas, SQLAlchemy sobre SQLite
- **Auth**: bcrypt
- **Scheduler**: APScheduler
- **Extracción de archivos**: openpyxl, pdfplumber, pypdf

## Estructura del proyecto

```
├── auth/              # Registro, login y planes de usuario
├── api/               # API FastAPI (POST /run-etl)
├── assistant/         # Enrutador de comandos del asistente del dashboard
├── core/              # Orquestador del pipeline, filtros, reglas guardadas, logging
├── dashboards/
│   ├── streamlit_app.py   # Punto de entrada (define la navegación)
│   └── views/              # Landing, Login, Registro, Dashboard, Planes
├── extract/           # Los 6 motores de extracción
├── transform/         # Limpieza, normalización, deduplicación
├── load/              # Persistencia (DatabaseManager) y exportación (Exporter)
├── jobs/              # Scheduler (corre el pipeline cada 12h vía la API)
├── config.py          # Rutas, configuración y esquema de base de datos
└── run_all.py         # Launcher: corre el pipeline inicial y levanta el dashboard
```

## Instalación

Requiere Python 3.10+.

```bash
git clone https://github.com/TakeshiDaiki/Extraccion-de-datos.git
cd Extraccion-de-datos
python -m venv .venv
.venv\Scripts\activate          # Windows
source .venv/bin/activate       # Linux/Mac
pip install -r requirements.txt
```

## Uso

### Dashboard (Streamlit)

```bash
streamlit run dashboards/streamlit_app.py
```

Abre `http://localhost:8501`. Desde ahí podés registrarte, iniciar sesión y usar el dashboard según tu plan.

### Todo junto (pipeline inicial + dashboard)

```bash
python run_all.py
```

### API

```bash
uvicorn api.main:app --reload
```

Expone `GET /health` y `POST /run-etl` (dispara el pipeline completo).

### Scheduler (opcional)

Corre el pipeline automáticamente cada 12 horas llamando a la API (necesita que la API esté corriendo):

```bash
python jobs/scheduler.py
```

## Notas

- Los motores de extracción usan **datos simulados** (no hacen scraping/llamadas reales) — están pensados como base para conectar fuentes reales más adelante.
- El sistema de planes es una maqueta funcional: la lógica de límites y features por plan es real, pero no hay dinero real de por medio todavía.
