import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import find_peaks, butter, filtfilt

def apply_bandpass_filter(data, lowcut, highcut, fs, order=4):
    """Applies a zero-phase Butterworth filter to isolate QRS complexes."""
    nyquist = 0.5 * fs
    low = lowcut / nyquist
    high = highcut / nyquist
    b, a = butter(order, [low, high], btype='band')
    return filtfilt(b, a, data)

def generate_mock_ecg(fs, duration, heart_rate_bpm):
    """Locally models a raw time-series ECG stream with injected noise."""
    total_samples = fs * duration
    time = np.arange(total_samples) / fs
    
    # Base heart rhythm spacing
    beat_period = 60.0 / heart_rate_bpm
    
    # Synthesize clean cardiac QRS complex spikes using a narrow Gaussian formula
    clean_signal = np.zeros(total_samples)
    for beat_time in np.arange(0.2, duration, beat_period):
        # Inject an intentional baseline timing shift to mimic an arrhythmia anomaly
        if beat_time > (duration / 2) and beat_time < (duration / 2 + 1):
            beat_time -= 0.15  # Premature cardiac contraction anomaly
            
        center_sample = int(beat_time * fs)
        if center_sample < total_samples:
            # Construct a high-amplitude R-wave spike
            qrs_width = int(0.04 * fs)
            window = np.arange(max(0, center_sample - qrs_width), min(total_samples, center_sample + qrs_width))
            clean_signal[window] += 1.5 * np.exp(-((window - center_sample) / (0.01 * fs))**2)

    # Inject high-frequency electronic sensor scatter noise (White Noise)
    sensor_noise = np.random.normal(0, 0.25, total_samples)
    
    # Inject low-frequency patient breathing baseline wander (0.3 Hz Sine wave)
    breathing_wander = 0.4 * np.sin(2 * np.pi * 0.3 * time)
    
    raw_noisy_signal = clean_signal + sensor_noise + breathing_wander
    return time, raw_noisy_signal

def extract_ecg_diagnostics():
    print("📈 Initializing Offline SciPy Time-Series Waveform Processor...")
    
    # 1. Setup Signal Properties (10 seconds sampled at 360 Hz)
    fs = 360  
    duration_seconds = 10
    simulated_hr = 75.0
    
    # Generate the dirty signal locally—completely bypassing the internet/pooch requirement
    time_axis, ecg_segment = generate_mock_ecg(fs, duration_seconds, simulated_hr)
    
    # 2. Clean the signal using a 5-15 Hz bandpass filter to remove breathing drift and sensor fuzz
    cleaned_signal = apply_bandpass_filter(ecg_segment, lowcut=5.0, highcut=15.0, fs=fs)
    
    # 3. Detect R-Peaks using spatial constraints
    # Prominence identifies high peak-to-trough isolation differentials
    r_peaks, _ = find_peaks(cleaned_signal, distance=150, prominence=0.4)
    
    # 4. Compute Diagnostic Clinical Metrics
    rr_intervals = np.diff(r_peaks) / fs  # Calculate R-R intervals in seconds
    heart_rate_bpm = 60.0 / np.mean(rr_intervals) if len(rr_intervals) > 0 else 0
    
    print(f"📊 Extraction Summary:")
    print(f"   - Total Beats Detected: {len(r_peaks)}")
    print(f"   - Computed Heart Rate: {heart_rate_bpm:.1f} BPM")
    print(f"   - Minimum R-R Split: {np.min(rr_intervals):.3f} seconds (Anomaly Tracker)")
    
    # 5. Render Processing Plot Validation Layout
    plt.figure(figsize=(12, 6))
    plt.plot(time_axis, ecg_segment, label="Raw Unfiltered ECG (With Sensor Noise & Breathing Wander)", color="gray", alpha=0.5)
    plt.plot(time_axis, cleaned_signal, label="Filtered Signal (5-15Hz Bandpass Isolated)", color="blue", linewidth=1.5)
    plt.scatter(r_peaks / fs, cleaned_signal[r_peaks], color="red", label="Detected R-Peaks (Heartbeats)", zorder=5, s=50)
    
    plt.title("Phase 2 Testing: 1D Clinical Waveform Feature Extraction Pipeline (Offline Edition)")
    plt.xlabel("Time (seconds)")
    plt.ylabel("Voltage Amplitude (mV)")
    plt.legend(loc="upper right")
    plt.grid(True, linestyle="--", alpha=0.5)
    
    output_filename = "ecg_extraction_output.png"
    plt.savefig(output_filename)
    print(f"💾 Visual extraction verification matrix saved as: '{output_filename}'")
    plt.close()

if __name__ == "__main__":
    extract_ecg_diagnostics()
