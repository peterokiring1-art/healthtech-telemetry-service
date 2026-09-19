import pytest
from fastapi.testclient import TestClient

# Import our active application server instance
from app import app

# Initialize the mock network transmission engine client
client = TestClient(app)

def test_successful_telemetry_ingestion():
    """
    GIVEN a valid patient telemetry payload
    WHEN a POST request is transmitted to the ingestion layer
    THEN it should accept the packet with a 200 OK status.
    """
    valid_payload = {
        "patient_id": "PT-TEST-001",
        "spo2": 98.0,
        "heart_rate": 72.0,
        "timestamp": 1789786600.0
    }
    
    response = client.post("/api/v1/telemetry", json=valid_payload)
    
    assert response.status_code == 200
    assert response.json()["status"] == "SUCCESS"
    assert "Persistent Storage" in response.json()["message"]


def test_clinical_abnormality_alert_triggering():
    """
    GIVEN a patient payload that breaks healthy clinical limits (SpO2 < 90)
    WHEN it hits the ingestion API
    THEN the server must accept it but flag an active clinical alert warning.
    """
    hypoxia_payload = {
        "patient_id": "PT-TEST-002",
        "spo2": 85.0,  # Critical boundary breach
        "heart_rate": 75.0,
        "timestamp": 1789786605.0
    }
    
    response = client.post("/api/v1/telemetry", json=hypoxia_payload)
    
    assert response.status_code == 200
    assert "alert" in response.json()
    assert "clinical abnormality threshold alert" in response.json()["alert"]


def test_malformed_pydantic_schema_validation_error():
    """
    GIVEN a payload with broken data structures (e.g., missing mandatory timestamp)
    WHEN it hits the API gateway
    THEN the Pydantic guard must reject it with a 422 Unprocessable Entity status.
    """
    broken_payload = {
        "patient_id": "PT-TEST-003",
        "spo2": 97.0,
        "heart_rate": 80.0,
        # Missing the required 'timestamp' key completely
    }
    
    response = client.post("/api/v1/telemetry", json=broken_payload)
    
    # 422 is FastAPI's standard structural validation exception status code
    assert response.status_code == 422


def test_analytics_endpoint_for_non_existent_patient():
    """
    GIVEN a completely fake patient tracking identifier
    WHEN a request hits the analytics engine
    THEN the system must safely return a clean 404 Not Found exception.
    """
    fake_patient_id = "PT-NOT-FOUND-999"
    
    response = client.get(f"/api/v1/telemetry/analytics/{fake_patient_id}")
    
    assert response.status_code == 404
    assert "No telemetry logs found" in response.json()["detail"]
