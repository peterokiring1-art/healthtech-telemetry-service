import time
import logging
from threading import Thread
from contextlib import asynccontextmanager
from fastapi import FastAPI

# Import unified centralized state components
from app_state import telemetry_queue
from routes import telemetry, analytics
from optimize_db import TunedSessionLocal
from init_db import PatientTelemetryModel

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("TelemetryServer")

def database_ingestion_worker():
    logger.info("👷 Tuned SQL Background Ingestion Worker Active.")
    while True:
        try:
            payload_data = telemetry_queue.get()
            db_session = TunedSessionLocal()
            try:
                db_record = PatientTelemetryModel(
                    patient_id=payload_data["patient_id"],
                    spo2=payload_data["spo2"],
                    heart_rate=payload_data["heart_rate"],
                    raw_timestamp=payload_data["timestamp"]
                )
                db_session.add(db_record)
                db_session.commit()
            except Exception as e:
                db_session.rollback()
                logger.error(f"SQL Async Router Write Error: {str(e)}")
            finally:
                db_session.close()
            telemetry_queue.task_done()
        except Exception:
            pass

# 🌟 MODERNISED LIFESPAN CONTEXT MANAGER AS RECOMENDED BY FASTAPI
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize the detached daemon processing thread
    worker_thread = Thread(target=database_ingestion_worker, daemon=True)
    worker_thread.start()
    logger.info("🚀 Enterprise Pipeline Core Lifespan Workers Bootstrapped.")
    yield
    # Shutdown logic goes here if needed when server stops
    logger.info("🛑 Shutting down enterprise lifespan gateway workers.")

app = FastAPI(
    title="HealthTech Telemetry Service Gateway",
    description="Enterprise decoupled and router-modularized clinical microservice architecture",
    version="5.0.0",
    lifespan=lifespan
)

# Mount separate sub-route domains
app.include_router(telemetry.router)
app.include_router(analytics.router)
