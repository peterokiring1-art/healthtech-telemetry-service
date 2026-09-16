import json
import csv

def build_mock_assets():
    print("=== Generating Messy Biomedical Datasets ===")
    
    # Updated JSON payload including a critical, high-risk patient record
    pulse_ox_payload = [
        {"timestamp": "2026-09-16T09:15:00Z", "patient_id": "PT-091", "spo2": 98, "heart_rate": 72},
        {"timestamp": "2026-09-16T09:15:01Z", "patient_id": "PT-091", "spo2": "ERROR", "heart_rate": 74},
        {"timestamp": "2026-09-16T09:15:02Z", "patient_id": "PT-091", "heart_rate": 75},
        {"patient_id": "MALFORMED_ROW_NO_TIME", "spo2": 95},
        # High-risk patient flag entry for clinical validation practice
        {"timestamp": "2026-09-16T09:15:03Z", "patient_id": "PT-091", "spo2": 85, "heart_rate": 110}
    ]
    with open("pulse_oximeter.json", "w", encoding="utf-8") as j_file:
        json.dump(pulse_ox_payload, j_file, indent=2)
    print("[SUCCESS] pulse_oximeter.json successfully updated with high-risk metrics.")

    # Erratic ECG CSV payload
    ecg_headers = ["timestamp", "patient_id", "lead_ii_mv", "status"]
    ecg_payload = [
        ["2026-09-16T09:15:00Z", "PT-091", "0.15", "VALID"],
        ["2026-09-16T09:15:01Z", "PT-091", "", "DEVICE_MALFUNCTION"],
        ["2026-09-16T09:15:02Z", "PT-091", " -0.05 ", "VALID"],
        ["2026-09-16T09:15:03Z", "PT-092", "invalid_float", "VALID"]
    ]
    with open("ecg_monitor.csv", "w", newline="", encoding="utf-8") as c_file:
        writer = csv.writer(c_file)
        writer.writerow(ecg_headers)
        writer.writerows(ecg_payload)
    print("[SUCCESS] ecg_monitor.csv successfully created.")

if __name__ == "__main__":
    build_mock_assets()
