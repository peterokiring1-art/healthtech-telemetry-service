import threading
import requests
import random
import time
from datetime import datetime

# GUARANTEED HIGH-SPEED GATEWAY ROUTE
TARGET_URL = "http://127.0.0.1:8080"

def simulate_device(patient_id: str, cycles: int):
    print(f"?? IoT Sensor Initialized for Patient: {patient_id}")
    for i in range(cycles):
        spo2_val = random.randint(84, 99)
        hr_val = random.randint(65, 120)
        payload = {
            "patient_id": patient_id,
            "timestamp": datetime.now().isoformat(),
            "spo2": spo2_val,
            "heart_rate": hr_val
        }
        try:
            response = requests.post(TARGET_URL, json=payload, timeout=5)
            if response.status_code == 200:
                alert_flag = "?? [WARNING] Hypoxia Detected!" if spo2_val < 90 else "?? Normal"
                print(f"[{patient_id}] Sent Packet {i+1}/{cycles} | SpO2: {spo2_val}% | HR: {hr_val} bpm | Status: {alert_flag}")
            else:
                print(f"? [{patient_id}] Failed with Status Code: {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"?? [{patient_id}] Connection error: {e}")
        time.sleep(random.uniform(0.5, 1.5))
    print(f"?? Telemetry Stream Finalized for Patient: {patient_id}")

def run_concurrent_simulation():
    patients = [f"PT-CONC-{i:03d}" for i in range(1, 11)]
    threads = []
    print("=== Launching Multi-Patient Concurrent Simulation Pipeline ===\n")
    for p_id in patients:
        t = threading.Thread(target=simulate_device, args=(p_id, 3))
        threads.append(t)
        t.start()
    for t in threads:
        t.join()
    print("\n? All concurrent clinical device transmissions complete.")

if __name__ == "__main__":
    run_concurrent_simulation()
