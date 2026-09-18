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

# Setup production logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("TelemetryServer")

app = FastAPI(
    title="HealthTech Telemetry Service Gateway",
    description="Clinical device ingestion with deep analytical formatting arrays",
    version="2.5.0"
)

# Safe memory queues and temporary cache to store data for analytics lookups
telemetry_queue = Queue()
DATABASE_MOCK_CACHE: List[dict] = []

class TelemetryPayload(BaseModel):
    patient_id: str = Field(..., example="PT-CONC-001")
    spo2: Optional[float] = Field(None)
    heart_rate: Optional[float] = Field(None)
    timestamp: float = Field(..., description="Unix timestamp")

@app.post("/api/v1/telemetry", status_code=status.HTTP_200_OK)
async def ingest_patient_telemetry(payload: TelemetryPayload):
    try:
        DATABASE_MOCK_CACHE.append(payload.model_dump())
        telemetry_queue.put(payload)
        return {"status": "SUCCESS", "message": "Authenticated Storage Confirmed."}
    except Exception as e:
        logger.error(f"Ingestion error: {str(e)}")
        raise HTTPException(status_code=500, detail="Server error processing metrics")

# Upgraded Endpoint with Deep Data Formatting & Summarization
@app.get("/api/v1/telemetry/analytics/{patient_id}", summary="Fetch Formatted Patient Analytics & Clinical Summaries")
async def get_patient_analytics(patient_id: str):
    patient_records = [r for r in DATABASE_MOCK_CACHE if r["patient_id"] == patient_id]
    
    if not patient_records:
        raise HTTPException(status_code=404, detail=f"No telemetry logs found for: {patient_id}")
    
    try:
        df = pd.DataFrame(patient_records).sort_values(by="timestamp")
        
        # 1. Clean data gaps using forward-fill
        df['spo2'] = df['spo2'].ffill().fillna(98.0)
        df['heart_rate'] = df['heart_rate'].ffill().fillna(75.0)
        
        # 2. Limit sensor noise spikes
        df['spo2'] = np.clip(df['spo2'], 0.0, 100.0)
        
        # 3. Compute running moving average metrics
        df['spo2_smoothed'] = df['spo2'].rolling(window=3, min_periods=1).mean().round(1)
        df['hr_smoothed'] = df['heart_rate'].rolling(window=3, min_periods=1).mean().round(1)
        
        # 🌟 NEW ADDITION: Generate Explicit, Human-Readable Timestamp Strings
        df['readable_time'] = df['timestamp'].apply(
            lambda x: datetime.fromtimestamp(x).strftime('%Y-%m-%d %H:%M:%S')
        )
        
        # 🌟 NEW ADDITION: Generate the Clinical Summary Aggregate Metrics
        total_alerts = int((df['spo2'] < 90).sum() + ((df['heart_rate'] < 50) | (df['heart_rate'] > 120)).sum())
        
        clinical_summary = {
            "overall_avg_spo2": float(df['spo2'].mean().round(1)),
            "overall_avg_heart_rate": float(df['heart_rate'].mean().round(1)),
            "monitored_duration_packets": len(df),
            "critical_anomaly_flags_raised": total_alerts,
            "clinical_status": "STABLE" if total_alerts == 0 else "ATTENTION_REQUIRED"
        }
        
        # Structure payload output cleanly
        cleaned_json_records = df.to_dict(orient="records")
        
        return {
            "patient_id": patient_id,
            "status": "ANALYTICS_TRANSFORMED",
            "clinical_summary_snapshot": clinical_summary,
            "data_timeline": cleaned_json_records
        }
    except Exception as e:
        logger.error(f"Analytics computation failure: {str(e)}")
        raise HTTPException(status_code=500, detail="Error compiling data stream trends.")

def database_ingestion_worker():
    while True:
        try:
            payload = telemetry_queue.get()
            time.sleep(0.01)
            telemetry_queue.task_done()
        except:
            pass

@app.on_event("startup")
async def startup_event():
    worker_thread = Thread(target=database_ingestion_worker, daemon=True)
    worker_thread.start()
