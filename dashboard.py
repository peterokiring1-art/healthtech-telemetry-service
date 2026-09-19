import streamlit as pd_stream
import pandas as pd
import time
from optimize_db import TunedSessionLocal
from init_db import PatientTelemetryModel

# Set professional medical portal page layout
pd_stream.set_page_config(
    page_title="HealthTech Clinical Telemetry Center",
    page_icon="🏥",
    layout="wide"
)

pd_stream.title("🏥 Central Clinical Device Telemetry Monitoring Center")
pd_stream.markdown("Real-time time-series analytics and physiological anomaly tracking engine.")

# Setup background active query connection context
db_session = TunedSessionLocal()

try:
    # 1. Fetch distinct active patient IDs to populate our UI dropdown filter select box
    distinct_patients = db_session.query(PatientTelemetryModel.patient_id).distinct().all()
    patient_list = sorted([p[0] for p in distinct_patients])
    
    if not patient_list:
        pd_stream.warning("⚠️ No persistent records found inside telemetry_storage.db. Launch the simulator client!")
    else:
        # Sidebar control configuration
        pd_stream.sidebar.header("📋 Patient Controls")
        selected_patient = pd_stream.sidebar.selectbox("Select Active Monitored Node:", patient_list)
        
        # 2. Extract specific selected patient records directly from SQL storage into Pandas
        query_stmt = db_session.query(PatientTelemetryModel).filter(
            PatientTelemetryModel.patient_id == selected_patient
        ).statement
        df = pd.read_sql(query_stmt, db_session.bind)
        
        # Chronological chronological timeline alignment processing
        df = df.sort_values(by="raw_timestamp")
        df['spo2'] = df['spo2'].ffill().fillna(98.0)
        df['heart_rate'] = df['heart_rate'].ffill().fillna(75.0)
        
        # Create rolling smoothed metric variables for plotting
        df['spo2_smoothed'] = df['spo2'].rolling(window=3, min_periods=1).mean().round(1)
        df['hr_smoothed'] = df['heart_rate'].rolling(window=3, min_periods=1).mean().round(1)
        
        # 3. High-level clinical performance KPI metric displays
        avg_spo2 = df['spo2'].mean().round(1)
        avg_hr = df['heart_rate'].mean().round(1)
        total_packets = len(df)
        
        col1, col2, col3 = pd_stream.columns(3)
        col1.metric("Avg Oxygen Saturation (SpO2)", f"{avg_spo2}%", delta=None)
        col2.metric("Avg Heart Rate (HR)", f"{avg_hr} BPM", delta=None)
        col3.metric("Total Transmission Heartbeats Captured", f"{total_packets} logs", delta=None)
        
        # 4. Graphical Area Plottings using Streamlit's native charting engines
        pd_stream.subheader("📈 Physiological Metric Trends (Smoothed vs Raw)")
        
        # Chart A: Heart Rate Metrics
        hr_plot_data = df.set_index('id')[['heart_rate', 'hr_smoothed']]
        pd_stream.markdown("**Heart Rate Track (BPM):**")
        pd_stream.line_chart(hr_plot_data)
        
        # Chart B: SpO2 Metrics
        spo2_plot_data = df.set_index('id')[['spo2', 'spo2_smoothed']]
        pd_stream.markdown("**Oxygen Saturation Track (%):**")
        pd_stream.line_chart(spo2_plot_data)
        
        # 5. Raw Data Grid Overview
        pd_stream.subheader("🗄️ Active Session Transaction Audit Logs")
        pd_stream.dataframe(df[['id', 'patient_id', 'spo2', 'heart_rate', 'raw_timestamp']].tail(10), use_container_width=True)

finally:
    db_session.close()

# Add automatic auto-refresh trigger to mock web-socket updates
time.sleep(2)
pd_stream.rerun()
