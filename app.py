import time
import logging
from threading import Thread
from fastapi import FastAPI

# Import our unified state and route components
from app_state import telemetry_queue
from routes import telemetry, analytics
from optimize_db import TunedSessionLocal
from init_db import PatientTelemetryModel

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("TelemetryServer")

app = FastAPI(
    title="HealthTech Telemetry Service Gateway",
    description="Enterprise-grade decoupled and router-modularized clinical microservice architecture",
    version="4.0.0"
)

# Mount our clean decoupled APIRouters onto the application framework
app.include_router(telemetry.router)
app.include_router(analytics.router)

def database_ingestion_worker():
    logger.info(" Worker Thread Connected and Listening via Centralized State Routing.")
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
                logger.error(f"SQL Router Write Error: {str(e)}")
            finally:
                db_session.close()
            telemetry_queue.task_done()
        except Exception as e:
            pass

@app.on_event("startup")
async def startup_event():
    worker_thread = Thread(target=database_ingestion_worker, daemon=True)
    worker_thread.start()
    logger.info(" Enterprise Pipeline Core Core Workers Bootstrapped Successfully.")
