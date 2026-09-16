from fastapi.testclient import TestClient
from app import app, API_KEY, API_KEY_NAME

# Wrap the FastAPI application into a lightweight mock testing client
client = TestClient(app)

def test_authorized_telemetry_stream():
    """1. Test that valid telemetry packets with the correct API key pass cleanly."""
    payload = {
        "timestamp": "2026-09-16T17:00:00Z",
        "patient_id": "PT-TEST-01",
        "spo2": 98,
        "heart_rate": 80
    }
    headers = {API_KEY_NAME: API_KEY}
    response = client.post("/api/v1/telemetry/pulseox", json=payload, headers=headers)
    assert response.status_code == 201
    assert response.json()["status"] == "SUCCESS"

def test_unauthorized_missing_token_block():
    """2. Test that requests missing the X-API-KEY header are securely blocked."""
    payload = {
        "timestamp": "2026-09-16T17:00:00Z",
        "patient_id": "PT-TEST-02",
        "spo2": 95,
        "heart_rate": 75
    }
    response = client.post("/api/v1/telemetry/pulseox", json=payload)
    assert response.status_code == 403
    assert "Access Denied" in response.json()["detail"]

def test_pydantic_schema_validation_failure():
    """3. Test that corrupted data formats are blocked at the network gate."""
    payload = {
        "timestamp": "2026-09-16T17:00:00Z",
        "patient_id": "PT",  # Fails min_length rule
        "spo2": 500         # Fails maximum boundary logic rule (le=100)
    }
    headers = {API_KEY_NAME: API_KEY}
    response = client.post("/api/v1/telemetry/pulseox", json=payload, headers=headers)
    assert response.status_code == 422
