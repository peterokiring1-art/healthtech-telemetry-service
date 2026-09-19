import os
import json
import pika
from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel, Field
from typing import Optional

from security import get_current_authenticated_user

router = APIRouter(
    prefix="/api/v1",
    tags=["Telemetry Ingestion Gateway"]
)

class TelemetryPayload(BaseModel):
    patient_id: str = Field(..., examples=["PT-CONC-001"], description="Unique tracking alphanumeric code")
    spo2: Optional[float] = Field(None, description="Oxygen Saturation Percentage")
    heart_rate: Optional[float] = Field(None, description="Heart Rate in Beats Per Minute")
    timestamp: float = Field(..., description="Unix hardware timestamp")

@router.post(
    "/telemetry", 
    status_code=status.HTTP_202_ACCEPTED, # 202 Accepted is proper REST for async message queuing
    summary="Ingest Real-time Client Telemetry Stream",
    responses={
        202: {"description": "Telemetry event accepted and sent to RabbitMQ broker array."},
        401: {"description": "Token signature mismatch or unauthorized access query."},
        422: {"description": "Validation anomaly detected inside Pydantic structures."}
    }
)
async def ingest_patient_telemetry(
    payload: TelemetryPayload, 
    current_user: str = Depends(get_current_authenticated_user)
):
    """
    Ingests live patient vitals telemetry records, enforces security gates via JWT,
    checks for immediate boundary dangers, and broadcasts the event payload to RabbitMQ.
    """
    try:
        # Establish connection to RabbitMQ container service
        rabbitmq_host = os.getenv("RABBITMQ_HOST", "127.0.0.1")
        connection = pika.BlockingConnection(pika.ConnectionParameters(host=rabbitmq_host))
        channel = connection.channel()
        
        # Declare an exchange queue name
        channel.queue_declare(queue='telemetry_stream_queue', durable=True)
        
        # Broadcast the JSON data payload packet strings
        channel.basic_publish(
            exchange='',
            routing_key='telemetry_stream_queue',
            body=json.dumps(payload.model_dump()),
            properties=pika.BasicProperties(delivery_mode=2) # Makes message persistent on broker restart
        )
        connection.close()
        
        is_abnormal = False
        if payload.spo2 and payload.spo2 < 90:
            is_abnormal = True
        if payload.heart_rate and (payload.heart_rate < 50 or payload.heart_rate > 120):
            is_abnormal = True
            
        if is_abnormal:
            return {
                "status": "ACCEPTED",
                "message": "Transmission successfully published to RabbitMQ broker cluster.",
                "alert": "Server flagged an active clinical abnormality threshold alert!"
            }
        return {"status": "ACCEPTED", "message": "Transmission successfully published to RabbitMQ broker cluster."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Broker messaging transmission failure: {str(e)}")
