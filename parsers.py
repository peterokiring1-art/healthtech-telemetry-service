import csv
import json
from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Optional

class CorruptedDataError(Exception):
    pass

class TelemetryReading:
    def __init__(self, timestamp: str, patient_id: str):
        self.timestamp: datetime = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
        self.patient_id: str = patient_id

class PulseOximeterReading(TelemetryReading):
    def __init__(self, timestamp: str, patient_id: str, spo2: Optional[int], heart_rate: Optional[int]):
        super().__init__(timestamp, patient_id)
        self.spo2: Optional[int] = spo2
        self.heart_rate: Optional[int] = heart_rate

    def __repr__(self):
        return f"<PulseOx {self.patient_id} | SpO2: {self.spo2}% | HR: {self.heart_rate} bpm>"

    def has_clinical_alert(self, spo2_min: int = 90, hr_max: int = 100) -> bool:
        """Returns True if SpO2 drops below configuration or Heart Rate exceeds maximum limits"""
        if self.spo2 is not None and self.spo2 < spo2_min:
            return True
        if self.heart_rate is not None and self.heart_rate > hr_max:
            return True
        return False

class EcgMonitorReading(TelemetryReading):
    def __init__(self, timestamp: str, patient_id: str, lead_ii_mv: Optional[float], status: str):
        super().__init__(timestamp, patient_id)
        self.lead_ii_mv: Optional[float] = lead_ii_mv
        self.status: str = status

    def __repr__(self):
        voltage = f"{self.lead_ii_mv} mV" if self.lead_ii_mv is not None else "N/A"
        return f"<ECG {self.patient_id} | Signal: {voltage} | Status: {self.status}>"

class BaseDeviceParser(ABC):
    @abstractmethod
    def parse_file(self, file_path: str) -> List[TelemetryReading]:
        pass

class JsonTelemetryParser(BaseDeviceParser):
    def parse_file(self, file_path: str) -> List[PulseOximeterReading]:
        readings = []
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            for record in data:
                try:
                    if "timestamp" not in record or "patient_id" not in record:
                        raise CorruptedDataError("Missing foundational identity flags.")
                    spo2_raw = record.get("spo2")
                    spo2 = int(spo2_raw) if isinstance(spo2_raw, int) or (isinstance(spo2_raw, str) and spo2_raw.isdigit()) else None
                    hr_raw = record.get("heart_rate")
                    hr = int(hr_raw) if isinstance(hr_raw, int) or (isinstance(hr_raw, str) and hr_raw.isdigit()) else None
                    readings.append(PulseOximeterReading(record["timestamp"], record["patient_id"], spo2, hr))
                except Exception as e:
                    print(f"[LOG WARNING] Skipping corrupted JSON record due to: {e}")
                    continue
        return readings

class CsvTelemetryParser(BaseDeviceParser):
    def parse_file(self, file_path: str) -> List[EcgMonitorReading]:
        readings = []
        with open(file_path, mode='r', encoding='utf-8', newline='') as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    cleaned_row = {k.strip(): v.strip() for k, v in row.items() if k is not None}
                    if "timestamp" not in cleaned_row or "patient_id" not in cleaned_row:
                        raise CorruptedDataError("CSV row lacks foundational headers.")
                    raw_mv = cleaned_row.get("lead_ii_mv")
                    lead_ii_mv = float(raw_mv) if raw_mv else None
                    readings.append(EcgMonitorReading(
                        timestamp=cleaned_row["timestamp"],
                        patient_id=cleaned_row["patient_id"],
                        lead_ii_mv=lead_ii_mv,
                        status=cleaned_row.get("status", "UNKNOWN")
                    ))
                except Exception as e:
                    print(f"[LOG WARNING] Skipping corrupted CSV row due to error: {e}")
                    continue
        return readings

if __name__ == "__main__":
    print("=== Ingestion Engine Pipeline Active [Feature Branch] ===")
    
    # Dynamic Configuration Loading Layer
    try:
        with open("config.json", "r") as config_file:
            config = json.load(config_file)
            spo2_limit = config.get("spo2_min_threshold", 90)
            hr_limit = config.get("heart_rate_max_threshold", 100)
            print(f"[CONFIG LOADED] Thresholds set -> Min SpO2: {spo2_limit}% | Max HR: {hr_limit} bpm")
    except FileNotFoundError:
        print("[CONFIG WARNING] config.json missing. Falling back to internal engineering defaults.")
        spo2_limit, hr_limit = 90, 100

    try:
        json_engine = JsonTelemetryParser()
        csv_engine = CsvTelemetryParser()
        
        print("\n--- Testing JSON Data Pipeline ---")
        ox_data = json_engine.parse_file("pulse_oximeter.json")
        for record in ox_data: 
            print(record)
            
        print("\n🚨 CRITICAL CLINICAL ALERTS DETECTED:")
        alert_count = 0
        for record in ox_data:
            # Threshold parameters are loaded dynamically from file config bounds
            if record.has_clinical_alert(spo2_limit, hr_limit):
                alert_count += 1
                print(f"[ALERT #{alert_count}] Patient: {record.patient_id} | SpO2: {record.spo2}% | HR: {record.heart_rate} bpm")
        if alert_count == 0:
            print("No medical anomalies flagged in this telemetry stream.")
            
        print("\n--- Testing CSV Data Pipeline ---")
        ecg_data = csv_engine.parse_file("ecg_monitor.csv")
        for record in ecg_data: 
            print(record)
            
    except FileNotFoundError as e:
        print(f"\n[!] Configuration Notice: {e.filename} not found yet. Run data generator first.")
