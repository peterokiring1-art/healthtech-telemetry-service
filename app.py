import json
from datetime import datetime
from typing import Optional
from fastapi import FastAPI, HTTPException, status, Security, Depends
from fastapi.security.api_key import APIKeyHeader
from pydantic import BaseModel, Field
import psycopg2

# 🔐 Establish your secret network token key
API_KEY = "healthtech-secure-token-2026"
API_KEY_NAME = "X-API-KEY"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

app = FastAPI(
    title="Clinical Telemetry Network Service",
    description="Live Secure HTTP API backend receiving authenticated medical device streams.",
    version="1.1.0"
)

class PulseOxNetworkPayload(BaseModel):
    timestamp: str
    patient_id: str = Field(..., min_length=3, max_length=50)
    spo2: Optional[int] = Field(None, ge=0, le=100)
    heart_rate: Optional[int] = Field(None, ge=0, le=300)

    def check_clinical_alert(self) -> bool:
        try:
            with open("config.json", "r") as file:
                config = json.load(file)
                spo2_min = config.get("spo2_min_threshold", 90)
                hr_max = config.get("heart_rate_max_threshold", 100)
        except FileNotFoundError:
            spo2_min, hr_max = 90, 100
        if (self.spo2 is not None and self.spo2 < spo2_min) or (self.heart_rate is not None and self.heart_rate > hr_max):
            return True
        return False

# 🔒 Security dependency injection layer
def verify_api_key(header_value: str = Depends(api_key_header)):
    if header_value == API_KEY:
        return header_value
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Access Denied: Invalid or missing X-API-KEY network authentication token."
    )

@app.get("/", status_code=status.HTTP_200_OK)
def system_diagnostic_root():
    return {"status": "ONLINE", "service": "Secure Gateway Active"}

# 📡 Updated Endpoint: Protected by the security dependency
@app.post("/api/v1/telemetry/pulseox", status_code=status.HTTP_201_CREATED)
def stream_pulseox_record(payload: PulseOxNetworkPayload, auth: str = Depends(verify_api_key)):
    print(f"\n⚡ Secure Network Stream Verified from Patient: {payload.patient_id}")
    
    if payload.check_clinical_alert():
        print(f"🚨 [NETWORK ALERT] Critical vitals for {payload.patient_id}!")

    try:
        connection = psycopg2.connect(
            host="localhost", database="postgres", user="postgres", password="postgres", port="5432"
        )
        cursor = connection.cursor()
        cursor.execute(
            "INSERT INTO pulse_ox_logs (timestamp, patient_id, spo2, heart_rate) VALUES (%s, %s, %s, %s);",
            (payload.timestamp, payload.patient_id, payload.spo2, payload.heart_rate)
        )
        connection.commit()
        return {"status": "SUCCESS", "message": "Authenticated packet archived safely.", "alert_triggered": payload.check_clinical_alert()}
    except Exception as db_err:
        print(f"[DB ERROR] Insertion failed: {db_err}")
        raise HTTPException(status_code=500, detail="Database insertion error.")
    finally:
        if 'connection' in locals() and connection:
            cursor.close()
            connection.close()
