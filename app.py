import json
from datetime import datetime
from typing import Optional
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field
import psycopg2

# Initialize the main Web Server application engine
app = FastAPI(
    title="Clinical Telemetry Network Service",
    description="Live HTTP API backend receiving authenticated medical device streams.",
    version="1.0.0"
)

# 📋 Pydantic Validation Schema for Pulse Oximetry Data Streams
class PulseOxNetworkPayload(BaseModel):
    timestamp: str = Field(..., description="ISO 8601 clinical record timestamp.")
    patient_id: str = Field(..., min_length=3, max_length=50, description="Unique target alphanumeric patient flag.")
    spo2: Optional[int] = Field(None, ge=0, le=100, description="Oxygen Saturation level percentage parameter.")
    heart_rate: Optional[int] = Field(None, ge=0, le=300, description="Patient heart rate beats per minute.")

    # Custom model validator layer to process dynamic thresholds
    def check_clinical_alert(self) -> bool:
        try:
            with open("config.json", "r") as file:
                config = json.load(file)
                spo2_min = config.get("spo2_min_threshold", 90)
                hr_max = config.get("heart_rate_max_threshold", 100)
        except FileNotFoundError:
            spo2_min, hr_max = 90, 100
            
        if self.spo2 is not None and self.spo2 < spo2_min:
            return True
        if self.heart_rate is not None and self.heart_rate > hr_max:
            return True
        return False


# 📡 Endpoint 1: Health Diagnostic Check Root Route
@app.get("/", status_code=status.HTTP_200_OK)
def system_diagnostic_root():
    return {
        "status": "ONLINE",
        "service": "Clinical Telemetry Network API Gateway",
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }


# 📡 Endpoint 2: Stream Ingestion Gateway for Pulse Oximeter Devices over HTTP POST
@app.post("/api/v1/telemetry/pulseox", status_code=status.HTTP_201_CREATED)
def stream_pulseox_record(payload: PulseOxNetworkPayload):
    print(f"\n⚡ Inbound Network Stream Received from Patient: {payload.patient_id}")
    
    # 1. Run live check for vital abnormalities
    if payload.check_clinical_alert():
        print(f"🚨 [NETWORK ALERT FLAGGED] Critical vitals detected for {payload.patient_id}!")

    # 2. Insert validated web data stream straight into PostgreSQL
    try:
        connection = psycopg2.connect(
            host="localhost", database="postgres", user="postgres", password="postgres", port="5432"
        )
        cursor = connection.cursor()
        
        # Safe parameterized execution string converting payload data securely
        cursor.execute(
            "INSERT INTO pulse_ox_logs (timestamp, patient_id, spo2, heart_rate) VALUES (%s, %s, %s, %s);",
            (payload.timestamp, payload.patient_id, payload.spo2, payload.heart_rate)
        )
        connection.commit()
        
        return {
            "status": "SUCCESS",
            "message": "Telemetry packet received, validated, and stored permanently in relational memory.",
            "alert_triggered": payload.check_clinical_alert()
        }
        
    except Exception as db_err:
        print(f"[CRITICAL DB DROPOUT] Server dropped transaction entry: {db_err}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Relational Engine instance drop out."
        )
    finally:
        if 'connection' in locals() and connection:
            cursor.close()
            connection.close()
