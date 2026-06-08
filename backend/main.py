import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes.routes import router
from app.core.config import settings
from app.services.vibration import vibration
from app.log.logger import log
from app.ia.predictive import predictive_model
from app.services.simulation import simulation_loop
from app.ia.ia import ia

@asynccontextmanager
async def lifespan(app: FastAPI):
    log.info("🚀 Iniciando Sentrya API v3 (modo simulação)...")
    vibration.train_ia_from_sqlite()
    asyncio.create_task(simulation_loop(vibration.process_reading))
    log.info("✅ Simulação iniciada — 6 máquinas ativas")
    yield

app = FastAPI(
    title=settings.app_name,
    description="Sentrya API — Monitoramento IoT ESP32 com Isolation Forest",
    version="3.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "sensores_ativos": len(vibration.sensores),
        "ia_treinada": ia.is_trained,
    }

@app.get("/api/predictions/{sensor_id}")
async def get_prediction(sensor_id: str, minutes: int = 60):
    prediction = predictive_model.predict_future(sensor_id, minutes_ahead=minutes)
    if not prediction:
        return {"error": "Dados insuficientes para predição"}
    return {
        "sensor_id": sensor_id,
        "current_status": {
            "vibracao": prediction["current_vib"],
            "temperatura": prediction["current_temp"]
        },
        "prediction": {
            "horizonte_minutos": minutes,
            "vibracao_futura": prediction["predictions"]["vibracao"],
            "temperatura_futura": prediction["predictions"]["temperatura"]
        },
        "risk": {
            "trend": prediction["tendencia"],
            "time_to_failure_minutes": prediction["time_to_failure_minutes"],
            "recommendation": prediction["recommendation"]
        }
    }