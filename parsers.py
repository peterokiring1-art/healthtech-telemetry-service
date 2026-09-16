import csv
import json
from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Optional
import psycopg2  # Dynamic database connector driver

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

# 🌍 Function to save your processed data array straight into your live database
def save_to_database(pulse_ox_data: List[PulseOximeterReading], ecg_data: List[EcgMonitorReading]):
    print("\n🌐 Connecting to Relational Database Stream for Data Storage...")
    try:
        connection = psycopg2.connect(
            host="localhost", database="postgres", user="postgres", password="postgres", port="5432"
        )
        cursor = connection.cursor()
        
        # 1. Insert Pulse Oximeter objects row by row using standard cursor logic
        pulse_ox_inserted = 0
        for reading in pulse_ox_data:
            try:
                cursor.execute(
                    "INSERT INTO pulse_ox_logs (timestamp, patient_id, spo2, heart_rate) VALUES (%s, %s, %s, %s)",
                    (reading.timestamp, reading.patient_id, reading.spo2, reading.heart_rate)
                )
                pulse_ox_inserted += 1
            except Exception as row_error:
                print(f"[DB RECORD SKIPPED] Error inserting individual PulseOx entry: {row_error}")
                connection.rollback()  # Safely clear the individual row transaction error block
                continue
        
        # 2. Insert ECG objects row by row
        ecg_inserted = 0
        for reading in ecg_data:
            try:
                cursor.execute(
                    "INSERT INTO ecg_logs (timestamp, patient_id, lead_ii_mv, status) VALUES (%s, %s, %s, %s)",
                    (reading.timestamp, reading.patient_id, reading.lead_ii_mv, reading.status)
                )
                ecg_inserted += 1
            except Exception as row_error:
                print(f"[DB RECORD SKIPPED] Error inserting individual ECG entry: {row_error}")
                connection.rollback()
                continue
                
        connection.commit()  # Lock down all successful database entries permanently
        print(f"[DATABASE SUCCESS] Streamed {pulse_ox_inserted} PulseOx records and {ecg_inserted} ECG logs directly to SQL tables.")
        
    except Exception as connection_error:
        print(f"[CRITICAL DATABASE ERROR] Pipeline connection failed: {connection_error}")
    finally:
        if 'connection' in locals() and connection:
            cursor.close()
            connection.close()

if __name__ == "__main__":
    print("=== Ingestion Engine Pipeline Active [Database Tier] ===")
    
    # Load dynamic configurations
    try:
        with open("config.json", "r") as config_file:
            config = json.load(config_file)
            spo2_limit = config.get("spo2_min_threshold", 90)
            hr_limit = config.get("heart_rate_max_threshold", 100)
    except FileNotFoundError:
        spo2_limit, hr_limit = 90, 100

    try:
        json_engine = JsonTelemetryParser()
        csv_engine = CsvTelemetryParser()
        
        print("\n--- Processing JSON Data ---")
        ox_data = json_engine.parse_file("pulse_oximeter.json")
        for record in ox_data: print(record)
            
        print("\n🚨 CRITICAL CLINICAL ALERTS DETECTED:")
        for record in ox_data:
            if record.has_clinical_alert(spo2_limit, hr_limit):
                print(f"[ALERT] Patient: {record.patient_id} | SpO2: {record.spo2}% | HR: {record.heart_rate} bpm")
            
        print("\n--- Processing CSV Data ---")
        ecg_data = csv_engine.parse_file("ecg_monitor.csv")
        for record in ecg_data: print(record)
        
        # 👇 Trigger the automated storage routine 
        save_to_database(ox_data, ecg_data)
            
    except FileNotFoundError as e:
        print(f"\n[!] Configuration Notice: {e.filename} not found yet. Run data generator first.")
