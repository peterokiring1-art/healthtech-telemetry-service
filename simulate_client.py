import random
import time
import requests
import numpy as np
from concurrent.futures import ThreadPoolExecutor

SERVER_BASE_URL = "http://127.0.0.1:8585"
INGEST_ENDPOINT = f"{SERVER_BASE_URL}/v1/device/data"

def generate_patient_waveform(is_abnormal=False, seq_len=180):
    time_space = np.linspace(0, 1, seq_len)
    if not is_abnormal:
        pulse = np.sin(2 * np.pi * 2 * time_space) + 0.5 * np.sin(2 * np.pi * 5 * time_space)
    else:
        pulse = np.sin(2 * np.pi * 4 * time_space) + np.sin(2 * np.pi * 12 * time_space)
    noise = np.random.normal(0, 0.3, seq_len)
    final_signal = pulse + noise
    return final_signal.tolist()

def simulate_single_patient_device(patient_num: int):
    patient_id = f"PT-AI-{patient_num:03d}"
    print(f"📡 IoT Telemetry Module Activated for Patient: {patient_id}")
    
    should_fail = (patient_num % 2 == 0)
    mock_waveform = generate_patient_waveform(is_abnormal=should_fail, seq_len=180)
    
    payload = {
        "patient_id": patient_id,
        "signal_waveform": mock_waveform
    }
    
    headers = {
        "X-Auth-Role": "clinician_peter"
    }
    
    try:
        response = requests.post(INGEST_ENDPOINT, json=payload, headers=headers, timeout=5)
        
        if response.status_code == 200:
            resp_data = response.json()
            ai_meta = resp_data.get("ai_analysis", {})
            print(f"✅ [{patient_id}] Gateway Status: {resp_data.get('message')}")
            print(f"       ↳ AI Diagnosis: [Class {ai_meta.get('prediction_class_id')}] -> {ai_meta.get('diagnostic_label')}")
        else:
            print(f"❌ [{patient_id}] Request Refused. Code: {response.status_code} | Info: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"💥 [{patient_id}] Connection error: {e}")

def run_concurrent_pipeline():
    print("=== Launching Live Deep Learning Concurrent Simulation Pipeline ===")
    with ThreadPoolExecutor(max_workers=10) as executor:
        patient_numbers = list(range(1, 11))
        executor.map(simulate_single_patient_device, patient_numbers)
    print("🏁 All secure concurrent AI device transmissions complete.")

if __name__ == "__main__":
    run_concurrent_pipeline()
