import pytest
import io
from fastapi.testclient import TestClient
from app import app

client = TestClient(app)

@pytest.fixture(scope="module")
def auth_token_header():
    login_credentials = {"username": "clinician_peter", "password": "secure_password_2026"}
    response = client.post("/api/v1/auth/login", data=login_credentials)
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

def test_equipment_rag_troubleshooting_resolution(auth_token_header):
    """Verifies that the LangChain knowledge dictionary returns a matching engineering response."""
    payload = {"equipment_model": "PulseOx-Pro-2000", "fault_code": "OPTICAL_FOULING_ERR4"}
    response = client.post("/api/v1/clinical-rag/troubleshoot-alert", json=payload, headers=auth_token_header)
    assert response.status_code == 200
    assert response.json()["status"] == "ENGINEER_NOTIFIED"
    assert "ROOT CAUSE IDENTIFIED" in response.json()["dispatched_action_plan"]

def test_medical_imaging_cv_dicom_processing(auth_token_header):
    """Verifies that the computer vision image array router captures file uploads successfully."""
    mock_file_data = b"MOCK_DICOM_BINARY_ARRAY_DATA_STRING"
    file_payload = {"file": ("test_scan.dcm", io.BytesIO(mock_file_data), "application/dicom")}
    
    response = client.post("/api/v1/vision/analyze-dicom", files=file_payload, headers=auth_token_header)
    assert response.status_code == 200
    assert response.json()["status"] == "IMAGE_PROCESSED"
    assert "computer_vision_metrics" in response.json()
