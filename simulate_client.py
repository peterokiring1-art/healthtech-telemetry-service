import time
import random
import requests

API_URL = "http://127.0.0"

def authenticate_client():
    login_data = {"username": "clinician_peter", "password": "secure_password_2026"}
    try:
        res = requests.post(f"{API_URL}/auth/login", data=login_data)
        return {"Authorization": f"Bearer {res.json()['access_token']}"}
    except Exception:
        print("❌ Auth failure. Ensure app server gateway is running on port 8080!")
        return None

def run_hardware_fault_simulation():
    headers = authenticate_client()
    if not headers: return
    
    print("\n🚀 Starting Live Biomedical Fault & Telemetry Ingestion Simulator...")
    
    # 1. Simulate Standard Functional Patient Stream Flow
    stable_payload = {"patient_id": "PT-CONC-001", "spo2": 98.0, "heart_rate": 72.0, "timestamp": time.time()}
    requests.post(f"{API_URL}/telemetry", json=stable_payload, headers=headers)
    print("✅ Broadcasted Frame 1: Patient Metrics Stable.")
    
    # 2. Simulate Active Hardware Fault Telemetry Event Break
    print("\n🚨 WARNING: Simulating sudden sensor displacement on Node PT-CONC-001...")
    fault_payload = {"equipment_model": "PulseOx-Pro-2000", "fault_code": "OPTICAL_FOULING_ERR4"}
    
    # Hit the automated RAG Troubleshooting Notification Router Channel directly
    rag_res = requests.post(f"{API_URL}/clinical-rag/troubleshoot-alert", json=fault_payload, headers=headers)
    
    print("\n📥 [AI ENGINEERING NOTIFICATION DISPATCHED OVER WORKSPACE]:")
    print(rag_res.json()["dispatched_action_plan"])

if __name__ == "__main__":
    run_hardware_fault_simulation()
