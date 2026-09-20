from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from datetime import datetime
import psycopg2
from typing import Optional
import queue
import threading
import time

app = FastAPI(title="Hass Scientific - Enterprise Instrumentation Ingestion Gateway")

# High-speed thread-safe buffer queue for machine logs
telemetry_queue = queue.Queue(maxsize=10000)

class MachineTelemetryPayload(BaseModel):
    machine_model: str             
    serial_number: str             
    timestamp: str
    status_flag: str               
    fault_code: Optional[str] = None  
    operational_metric: Optional[float] = None 

def get_db_connection():
    return psycopg2.connect(
        dbname="postgres",
        user="postgres",
        password="postgres",
        host="127.0.0.1",
        port="5432"
    )

def db_worker_processor():
    """Continuous background worker draining telemetry queues into PostgreSQL."""
    print("🚀 Worker Thread Activated: Monitoring Hass Scientific Machine Streams.")
    while True:
        try:
            payload = telemetry_queue.get()
            conn = get_db_connection()
            cur = conn.cursor()
            
            # Writing into a proper enterprise clinical database schema
            insert_query = """
            INSERT INTO machine_telemetry_logs (machine_model, serial_number, timestamp, status_flag, fault_code, operational_metric)
            VALUES (%s, %s, %s, %s, %s, %s);
            """
            
            cur.execute(insert_query, (
                payload.machine_model,
                payload.serial_number,
                payload.timestamp,
                payload.status_flag,
                payload.fault_code,
                payload.operational_metric
            ))
            
            conn.commit()
            cur.close()
            conn.close()
            
            print(f"💾 [ASYNC LOG SUCCESS] Processed telemetry packet for: {payload.machine_model}")
            telemetry_queue.task_done()
            
        except Exception as e:
            print(f"❌ Background DB insertion halt: {e}")
            time.sleep(2)

@app.on_event("startup")
def startup_event():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        # Initialize an explicit database table for your clinical fleet logs
        cur.execute("""
            CREATE TABLE IF NOT EXISTS machine_telemetry_logs (
                id SERIAL PRIMARY KEY,
                machine_model VARCHAR(100) NOT NULL,
                serial_number VARCHAR(50) NOT NULL,
                timestamp TIMESTAMPTZ NOT NULL,
                status_flag VARCHAR(20) NOT NULL,
                fault_code VARCHAR(50),
                operational_metric REAL
            );
        """)
        conn.commit()
        cur.close()
        conn.close()
        
        # Launch background consumer task worker thread
        worker_thread = threading.Thread(target=db_worker_processor, daemon=True)
        worker_thread.start()
        print("🚀 Asynchronous clinical instrumentation background daemon fully attached.")
    except Exception as e:
        print(f"⚠️ Service initialization checkpoint error: {e}")

@app.post("/telemetry")
async def receive_telemetry(payload: MachineTelemetryPayload):
    try:
        telemetry_queue.put_nowait(payload)
        is_critical = payload.status_flag == "CRITICAL"
        return {
            "status": "QUEUED",
            "message": f"Telemetry for {payload.machine_model} successfully pushed to buffer pool.",
            "requires_immediate_field_service": is_critical
        }
    except queue.Full:
        raise HTTPException(status_code=503, detail="Gateway ingestion pipeline buffer saturated.")
