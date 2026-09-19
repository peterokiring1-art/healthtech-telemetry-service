import time
import logging
from threading import Thread
from queue import Queue
from typing import Optional, List
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field
import pandas as pd
import numpy as np
from datetime import datetime

# Import our tuned database engine components
from optimize_db import TunedSessionLocal, profile_query_performance
from init_db import PatientTelemetryModel

# Setup production logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("TelemetryServer")

app = FastAPI(
    title="HealthTech Telemetry Service Gateway",
    description="Production-grade clinical device ingestion with persistent database storage mapping",
    version="3.0.0"
)

# Shared safe memory queue for background worker processing
telemetry_queue = Queue()

class TelemetryPayload(BaseModel):
    patient_id: str = Field(..., example="PT-CONC-001")
    spo2: Optional[float] = Field(None)
    heart_rate: Optional[float] = Field(None)
    timestamp: float = Field(..., description="Unix timestamp")

# 1. Asynchronous Ingestion Gateway Endpoint (POST)
@app.post("/api/v1/telemetry", status_code=status.HTTP_200_OK)
async def ingest_patient_telemetry(payload: TelemetryPayload):
    try:
        # Instantly hand off payload to the thread-safe background insertion queue
        telemetry_queue.put(payload.model_dump())
        
        # Clinical Rule Check for Threshold Alerts
        is_abnormal = False
        if payload.spo2 and payload.spo2 < 90:
            is_abnormal = True
        if payload.heart_rate and (payload.heart_rate < 50 or payload.heart_rate > 120):
            is_abnormal = True
            
        if is_abnormal:
            return {
                "status": "SUCCESS",
                "message": "Transmission Queued for Persistent Storage.",
                "alert": "Server flagged an active clinical abnormality threshold alert!"
            }
        return {"status": "SUCCESS", "message": "Transmission Queued for Persistent Storage."}
    except Exception as e:
        logger.error(f"Ingestion error: {str(e)}")
        raise HTTPException(status_code=500, detail="Server error processing metric pipelines")

# 2. Time-Series Analytics Endpoint connected to SQL Backend (GET)
@app.get("/api/v1/telemetry/analytics/{patient_id}")
@profile_query_performance
def get_patient_analytics(patient_id: str):
    db_session = TunedSessionLocal()
    try:
        # Fetch raw patient records directly from our optimized database table
        records = db_session.query(PatientTelemetryModel).filter(
            PatientTelemetryModel.patient_id == patient_id
        ).all()
        
        if not records:
            raise HTTPException(status_code=404, detail=f"No telemetry logs found for patient: {patient_id}")
        
        # Convert SQLAlchemy objects into a list of dictionaries for Pandas ingestion
        raw_data = [
            {
                "patient_id": r.patient_id,
                "spo2": r.spo2,
                "heart_rate": r.heart_rate,
                "timestamp": r.raw_timestamp
            } for r in records
        ]
        
        # Process analytics via vectorized Pandas operations
        df = pd.DataFrame(raw_data).sort_values(by="timestamp")
        df['spo2'] = df['spo2'].ffill().fillna(98.0)
        df['heart_rate'] = df['heart_rate'].ffill().fillna(75.0)
        df['spo2'] = np.clip(df['spo2'], 0.0, 100.0)
        
        # Calculate moving averages
        df['spo2_smoothed'] = df['spo2'].rolling(window=3, min_periods=1).mean().round(1)
        df['hr_smoothed'] = df['heart_rate'].rolling(window=3, min_periods=1).mean().round(1)
        
        # Create human-readable timestamps
        df['readable_time'] = df['timestamp'].apply(
            lambda x: datetime.fromtimestamp(x).strftime('%Y-%m-%d %H:%M:%S')
        )
        
        # Calculate Aggregates
        total_alerts = int((df['spo2'] < 90).sum() + ((df['heart_rate'] < 50) | (df['heart_rate'] > 120)).sum())
        clinical_summary = {
            "overall_avg_spo2": float(df['spo2'].mean().round(1)),
            "overall_avg_heart_rate": float(df['heart_rate'].mean().round(1)),
            "monitored_duration_packets": len(df),
            "critical_anomaly_flags_raised": total_alerts,
            "clinical_status": "STABLE" if total_alerts == 0 else "ATTENTION_REQUIRED"
        }
        
        return {
            "patient_id": patient_id,
            "status": "ANALYTICS_TRANSFORMED",
            "clinical_summary_snapshot": clinical_summary,
            "data_timeline": df.to_dict(orient="records")
        }
    finally:
        db_session.close()

# 3. Decoupled Ingestion Thread Worker writing directly to SQL Tables
def database_ingestion_worker():
    logger.info("👷 Tuned SQL Background Ingestion Worker Thread Activated.")
    while True:
        try:
            # Block until an entry arrives from the ingestion gateway queue
            payload_data = telemetry_queue.get()
            
            # Spin up an optimized session context transaction block
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
                logger.error(f"SQL Batch Insertion Rollback Error: {str(e)}")
            finally:
                db_session.close()
                
            telemetry_queue.task_done()
        except Exception as e:
            logger.error(f"Queue Worker Fatal Crash Prevented: {str(e)}")

@app.on_event("startup")
async def startup_event():
    logger.info("🗄️ Relational database engine validation running...")
    worker_thread = Thread(target=database_ingestion_worker, daemon=True)
    worker_thread.start()
    logger.info("🚀 Persistent storage task worker pool successfully attached.")
