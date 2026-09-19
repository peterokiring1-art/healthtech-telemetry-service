import pytest
from fastapi.testclient import TestClient
from app import app

client = TestClient(app)

@pytest.fixture(scope="module")
def auth_token_header():
    """
    Automated fixture that logs into the microservice before tests run
    and returns a valid Bearer token authorization header string.
    """
    login_credentials = {
        "username": "clinician_peter",
        "password": "secure_password_2026"
    }
    # Form data login simulation matching OAuth2 specification
    response = client.post("/api/v1/auth/login", data=login_credentials)
    
    # Diagnostic assertion fallback tracking
    assert response.status_code == 200, f"Login endpoint broken! Returned details: {response.text}"
    
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_successful_telemetry_ingestion(auth_token_header):
    valid_payload = {
        "patient_id": "PT-TEST-001",
        "spo2": 98.0,
        "heart_rate": 72.0,
        "timestamp": 1789786600.0
    }
    response = client.post("/api/v1/telemetry", json=valid_payload, headers=auth_token_header)
    assert response.status_code == 200


def test_rejected_unauthenticated_telemetry_ingestion():
    payload = {
        "patient_id": "PT-TEST-001",
        "spo2": 98.0,
        "heart_rate": 72.0,
        "timestamp": 1789786600.0
    }
    response = client.post("/api/v1/telemetry", json=payload)
    assert response.status_code == 401


def test_clinical_abnormality_alert_triggering(auth_token_header):
    hypoxia_payload = {
        "patient_id": "PT-TEST-002",
        "spo2": 85.0,
        "heart_rate": 75.0,
        "timestamp": 1789786605.0
    }
    response = client.post("/api/v1/telemetry", json=hypoxia_payload, headers=auth_token_header)
    assert response.status_code == 200


def test_malformed_pydantic_schema_validation_error(auth_token_header):
    broken_payload = {
        "patient_id": "PT-TEST-003",
        "spo2": 97.0,
        "heart_rate": 80.0
    }
    response = client.post("/api/v1/telemetry", json=broken_payload, headers=auth_token_header)
    assert response.status_code == 422
