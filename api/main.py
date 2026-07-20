from fastapi import FastAPI, HTTPException

from core.pipeline import run_pipeline

app = FastAPI(title="BI Platform ETL API")

ALL_SOURCES = ["web", "api", "email", "excel", "pdf", "login"]


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/run-etl")
def run_etl():
    """
    Dispara el pipeline ETL completo (los 6 motores de extracción).
    Este es el endpoint que jobs/scheduler.py invoca cada 12 horas.
    """
    try:
        return run_pipeline(sources=ALL_SOURCES, limit=100)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
