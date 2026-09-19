from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
from typing import Optional
from queue import Queue

# We hook into the global queue object initialized at the application core layer
from app_state import telemetry_queue 

router = APIRouter(
    prefix="/api/v1",
    tags=["Ingestion Gateway"]
)

class TelemetryPayload(BaseModel):
    patient_id: str = Field(..., examples=["PT-CONC-001"], description="Unique tracking identifier")
    spo2: Optional[float] = Field(None)
    heart_rate: Optional[float] = Field(None)
    timestamp: float = Field(..., description="Unix hardware timestamp")

@router.post("/telemetry", status_code=status.HTTP_200_OK, summary="Ingest Real-time Client Telemetry Stream")
async def ingest_patient_telemetry(payload: TelemetryPayload):
    try:
        telemetry_queue.put(payload.model_dump())
        
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
        raise HTTPException(status_code=500, detail="Server error processing metric pipelines")
