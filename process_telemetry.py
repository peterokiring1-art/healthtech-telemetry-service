import numpy as np
import pandas as pd
import time

def run_clinical_data_pipeline(raw_patient_data: list):
    print("=== Phase 1: Ingesting Raw Time-Series Sensor Stream ===")
    
    # 1. Convert raw dictionaries into a structured Pandas DataFrame
    df = pd.DataFrame(raw_patient_data)
    print("\nInitial Ingested Structure:")
    print(df)
    
    print("\n=== Phase 2: Cleaning Anomalies & Missing Signals (Data Cleansing) ===")
    
    # 2. Check for missing values (represented as None or NaN)
    print(f"Detected Missing SpO2 points: {df['spo2'].isnull().sum()}")
    print(f"Detected Missing Heart Rate points: {df['heart_rate'].isnull().sum()}")
    
    # 3. Clean Missing Data using Forward-Fill (ffill) 
    # This carries the last known stable physiological reading forward if a sensor drops out briefly.
    df['spo2'] = df['spo2'].ffill()
    df['heart_rate'] = df['heart_rate'].ffill()
    
    # If any remaining NaNs exist at the very start, fill them with baseline clinical constants
    df['spo2'] = df['spo2'].fillna(98)
    df['heart_rate'] = df['heart_rate'].fillna(75)
    
    print("\nCleaned Dataset (Gaps Remedied):")
    print(df)
    
    print("\n=== Phase 3: Clinical Analytics & Signal Processing ===")
    
    # 4. Use NumPy to clip extreme sensor noise anomalies 
    # (e.g., an impossible SpO2 reading of 120% gets clipped to max 100%)
    df['spo2'] = np.clip(df['spo2'], 0, 100)
    
    # 5. Calculate a 3-period Rolling Moving Average using Pandas rolling()
    # This smooths out micro-spikes to provide clinicians with a steady trend line.
    df['spo2_smoothed'] = df['spo2'].rolling(window=3, min_periods=1).mean().round(1)
    df['hr_smoothed'] = df['heart_rate'].rolling(window=3, min_periods=1).mean().round(1)
    
    print("\nFinal Transformed Telemetry Dataset (With Moving Averages):")
    print(df[['patient_id', 'spo2', 'spo2_smoothed', 'heart_rate', 'hr_smoothed']])
    
    return df

if __name__ == "__main__":
    # Mocking a noisy time-series dataset received from a patient device 
    # Notice the 'None' gaps (missing packets) and extreme noise (115% SpO2)
    noisy_simulated_stream = [
        {"patient_id": "PT-CONC-001", "timestamp": time.time(), "spo2": 97, "heart_rate": 72},
        {"patient_id": "PT-CONC-001", "timestamp": time.time() + 1, "spo2": None, "heart_rate": 74},  # Sensor drop
        {"patient_id": "PT-CONC-001", "timestamp": time.time() + 2, "spo2": 96, "heart_rate": None},  # Sensor drop
        {"patient_id": "PT-CONC-001", "timestamp": time.time() + 3, "spo2": 115, "heart_rate": 108}, # Noise spike
        {"patient_id": "PT-CONC-001", "timestamp": time.time() + 4, "spo2": 85, "heart_rate": 112},  # Genuine distress drop
        {"patient_id": "PT-CONC-001", "timestamp": time.time() + 5, "spo2": 86, "heart_rate": 110},
    ]
    
    run_clinical_data_pipeline(noisy_simulated_stream)
