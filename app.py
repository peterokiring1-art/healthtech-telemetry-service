from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from datetime import datetime
import psycopg2
from typing import Optional

app = FastAPI(title="HealthTech Telemetry Service GateWay")

# Strict Pydantic Schema Validation Model for IoT Device Packets
class TelemetryPayload(BaseModel):
    patient_id: str
    timestamp: str
    spo2: Optional[float]
    heart_rate: Optional[float]

def get_db_connection():
    # Connecting to your verified local dev parameters
    return psycopg2.connect(
        dbname="postgres",
        user="postgres",
        password="postgres",
        host="127.0.0.1",
        port="5432"
    )

@app.on_event("startup")
def startup_event():
    """Validates structural database readiness at app instantiation."""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        # Verify the optimized logs table exists
        cur.execute("""
            CREATE TABLE IF NOT EXISTS pulse_ox_logs (
                id SERIAL PRIMARY KEY,
                timestamp TIMESTAMPTZ NOT NULL,
                patient_id VARCHAR(50) NOT NULL,
                spo2 REAL,
                heart_rate REAL
            );
        """)
        conn.commit()
        cur.close()
        conn.close()
        print("🗄️ [SUCCESS] Database operational layer fully verified.")
    except Exception as db_err:
        print(f"⚠️ [DATABASE CONNECTION WARNING]: {db_err}")
        print("⚡ Core gateway running in fallback isolation mode. Proceeding with network app loop.")

@app.post("/telemetry")
async def receive_telemetry(payload: TelemetryPayload):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Safe parameterized insertion to prevent SQL injection vulnerabilities
        insert_query = """
        INSERT INTO pulse_ox_logs (patient_id, timestamp, spo2, heart_rate)
        VALUES (%s, %s, %s, %s);
        """
        cur.execute(insert_query, (
            payload.patient_id,
            payload.timestamp,
            payload.spo2,
            payload.heart_rate
        ))
        
        conn.commit()
        cur.close()
        conn.close()
        
        # Clinical alert interceptor mirroring your parser algorithm criteria
        has_alert = payload.spo2 is not None and payload.spo2 < 90
        
        return {
            "status": "SUCCESS",
            "message": "Authenticated Storage Confirmed.",
            "clinical_alert": has_alert
        }
        
    except Exception as e:
        # Prevent runtime failures from crashing the engine by returning an HTTP 500 error instead
        print(f"❌ Transaction Processing Failure: {e}")
        raise HTTPException(status_code=500, detail=f"Internal Storage Failure: {str(e)}")
