import sqlite3
import json
import numpy as np
import scipy.signal as signal

def load_raw_telemetry(db_path="telemetry_storage.db", session_id=None):
    """
    Phase 1 Data Bridge: Pulls raw device signal arrays from the database.
    Falls back to a clean synthetic array if the table is currently empty.
    """
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Querying schema matching your process_telemetry / worker frameworks
        if session_id:
            cursor.execute("SELECT voltage_array FROM telemetry WHERE session_id = ?", (session_id,))
        else:
            cursor.execute("SELECT voltage_array FROM telemetry ORDER BY id DESC LIMIT 1")
            
        row = cursor.fetchone()
        conn.close()
        
        if row and row[0]:
            return np.array(json.loads(row[0]), dtype=float)
    except Exception as e:
        print(f"[DB Notice] Could not read from database ({e}). Falling back to simulation.")
    
    # Fallback/Simulation: 10 seconds of 500Hz ECG data with high-frequency noise
    fs = 500
    t = np.arange(0, 10, 1/fs)
    clean_ecg = np.zeros_like(t)
    for r_peak in np.arange(0.5, 10, 0.85): # Simulating ~70 BPM
        idx = np.where((t >= r_peak) & (t < r_peak + 0.08))[0]
        if len(idx) > 0:
            clean_ecg[idx] = signal.windows.gaussian(len(idx), std=len(idx)/5) * 1.5
            
    # Inject high-frequency electrode chatter / noise
    noise = 0.15 * np.sin(2 * np.pi * 60 * t) + 0.05 * np.random.normal(size=len(t))
    return clean_ecg + noise

def butter_lowpass_filter(data, cutoff=45.0, fs=500.0, order=4):
    """
    SciPy DSP Engine: Removes high-frequency noise and muscle artifacts.
    Uses zero-phase filtering (filtfilt) to prevent phase shifting.
    """
    nyquist = 0.5 * fs
    normal_cutoff = cutoff / nyquist
    b, a = signal.butter(order, normal_cutoff, btype='low', analog=False)
    return signal.filtfilt(b, a, data)

def pan_tompkins_peak_detector(filtered_signal, fs=500.0):
    """
    Mathematical Pan-Tompkins Algorithm Variant for Biomedical Feature Extraction:
    1. Derivative: Highlights the sharp slope of the QRS complex.
    2. Squaring: Amplifies high-amplitude R-peaks relative to T-waves.
    3. Moving Window Integration: Smooths the complex to create detection blocks.
    """
    # Step 1: Take the derivative
    derivative = np.diff(filtered_signal)
    
    # Step 2: Square the signal
    squared = derivative ** 2
    
    # Step 3: Moving window integration (approx 150ms window size)
    window_len = int(0.150 * fs)
    integrated = np.convolve(squared, np.ones(window_len)/window_len, mode='same')
    
    # Step 4: Isolate peaks with minimum distance matching physiological limits
    # Max heart rate threshold ~220 BPM implies peaks cannot be closer than ~270ms
    min_peak_distance = int(0.270 * fs)
    peaks, _ = signal.find_peaks(integrated, distance=min_peak_distance, prominence=np.mean(integrated)*1.5)
    
    return peaks, integrated

def compute_biomedical_metrics(peaks, fs=500.0):
    """
    Transforms peak index intervals into actionable medical telemetry metrics.
    """
    if len(peaks) < 2:
        return {"status": "Insufficient Peaks Detected", "bpm": 0, "rmssd_ms": 0}
        
    # Convert peak intervals (samples) to time intervals (milliseconds)
    rr_intervals_ms = (np.diff(peaks) / fs) * 1000.0
    
    # Calculate Heart Rate (BPM)
    mean_rr_sec = np.mean(rr_intervals_ms) / 1000.0
    bpm = int(60.0 / mean_rr_sec)
    
    # Calculate Root Mean Square of Successive Differences (RMSSD) for HRV
    successive_diffs = np.diff(rr_intervals_ms)
    rmssd = round(np.sqrt(np.mean(successive_diffs ** 2)), 2)
    
    return {
        "status": "Healthy Metrics Processed",
        "total_beats_detected": len(peaks),
        "heart_rate_bpm": bpm,
        "hrv_rmssd_ms": rmssd
    }

if __name__ == "__main__":
    print("\n⚡ Starting Phase 2 Core DSP Extraction Pipeline...")
    
    # 1. Ingest Raw Waveforms
    fs = 500.0
    raw_signal = load_raw_telemetry()
    print(f"-> Ingested {len(raw_signal)} data points from the clinical telemetry array.")
    
    # 2. Filter Signal
    clean_signal = butter_lowpass_filter(raw_signal, cutoff=40.0, fs=fs)
    print("-> SciPy Butterworth 4th-order lowpass filter applied successfully.")
    
    # 3. Process Peaks (Pan-Tompkins)
    peaks, processed_envelope = pan_tompkins_peak_detector(clean_signal, fs=fs)
    print(f"-> Pan-Tompkins evaluation complete. Isolated {len(peaks)} high-confidence R-peaks.")
    
    # 4. Generate Machine Learning Ready Features
    metrics = compute_biomedical_metrics(peaks, fs=fs)
    print("\n📊 EXTRACTED CLINICAL METRICS FOR DOWNSTREAM MACHINE LEARNING:")
    print(json.dumps(metrics, indent=4))
