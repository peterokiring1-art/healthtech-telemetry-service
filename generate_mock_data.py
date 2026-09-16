import json
import csv

def build_mock_assets():
    print("=== Generating Messy Biomedical Datasets ===")
    
    # 1. Output a corrupted pulse oximeter JSON payload to test data stripping and type conversion
    pulse_ox_payload = [
        {"timestamp": "2026-09-16T09:15:00Z", "patient_id": "PT-091", "spo2": 98, "heart_rate": 72},
        {"timestamp": "2026-09-16T09:15:01Z", "patient_id": "PT-091", "spo2": "ERROR", "heart_rate": 74}, # Strips string anomaly safely
        {"timestamp": "2026-09-16T09:15:02Z", "patient_id": "PT-091", "heart_rate": 75},                # Handles missing SpO2 field
        {"patient_id": "MALFORMED_ROW_NO_TIME", "spo2": 95}                                              # Missing timestamp (Triggers warning)
    ]
    with open("pulse_oximeter.json", "w", encoding="utf-8") as j_file:
        json.dump(pulse_ox_payload, j_file, indent=2)
    print("[SUCCESS] pulse_oximeter.json successfully created in your workspace.")

    # 2. Output an erratic ECG CSV table to test column whitespace handling and float conversion
    ecg_headers = ["timestamp", "patient_id", "lead_ii_mv", "status"]
    ecg_payload = [
        ["2026-09-16T09:15:00Z", "PT-091", "0.15", "VALID"],
        ["2026-09-16T09:15:01Z", "PT-091", "", "DEVICE_MALFUNCTION"],   # Safe None field for blank telemetry signals
        ["2026-09-16T09:15:02Z", "PT-091", " -0.05 ", "VALID"],         # Contains trailing whitespace spacing error
        ["2026-09-16T09:15:03Z", "PT-092", "invalid_float", "VALID"]    # Malformed text voltage measurement (Triggers warning)
    ]
    with open("ecg_monitor.csv", "w", newline="", encoding="utf-8") as c_file:
        writer = csv.writer(c_file)
        writer.writerow(ecg_headers)
        writer.writerows(ecg_payload)
    print("[SUCCESS] ecg_monitor.csv successfully created in your workspace.")

if __name__ == "__main__":
    build_mock_assets()
