import streamlit as st
import pandas as pd
import time
from optimize_db import TunedSessionLocal
from init_db import PatientTelemetryModel

st.set_page_config(
    page_title="HealthTech Clinical Monitoring Center",
    page_icon="🏥",
    layout="wide"
)

st.title("🏥 Central Clinical Device Telemetry Monitoring Center")
st.markdown("Real-time time-series analytics and physiological anomaly tracking engine.")

db_session = TunedSessionLocal()

try:
    distinct_patients = db_session.query(PatientTelemetryModel.patient_id).distinct().all()
    # 🌟 FIXED: Unpack raw string values out of the SQLAlchemy Row tuple objects safely
    patient_list = sorted([p[0] for p in distinct_patients if p[0]])
    
    if not patient_list:
        st.warning("⚠️ No persistent records found inside telemetry_storage.db.")
    else:
        st.sidebar.header("📋 Patient Controls")
        selected_patient = st.sidebar.selectbox("Select Active Monitored Node:", patient_list)
        
        # Load raw relational logs into a Pandas dataframe wrapper
        query_stmt = db_session.query(PatientTelemetryModel).filter(
            PatientTelemetryModel.patient_id == selected_patient
        ).statement
        df = pd.read_sql(query_stmt, db_session.bind).sort_values(by="raw_timestamp")
        
        # In-line data cleansing vectors
        df['spo2'] = df['spo2'].ffill().fillna(98.0)
        df['heart_rate'] = df['heart_rate'].ffill().fillna(75.0)
        
        df['spo2_smoothed'] = df['spo2'].rolling(window=3, min_periods=1).mean().round(1)
        df['hr_smoothed'] = df['heart_rate'].rolling(window=3, min_periods=1).mean().round(1)
        
        # Calculate critical boundary conditions metrics
        avg_spo2 = df['spo2'].mean().round(1)
        avg_hr = df['heart_rate'].mean().round(1)
        total_packets = len(df)
        
        # Count total historical alerts anomalies
        total_anomalies = int((df['spo2'] < 90).sum() + ((df['heart_rate'] < 50) | (df['heart_rate'] > 120)).sum())
        
        # Real-time conditional status indicators
        if total_anomalies > 0:
            st.error(f"🚨 ALERT REQUIRED: Patient {selected_patient} has triggered {total_anomalies} active clinical threshold warnings during this monitoring period!")
        else:
            st.success(f"✅ PATIENT STABLE: Node {selected_patient} is showing healthy normal boundary physiological metrics.")

        # High level summary status layout cards
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Avg Oxygen Saturation (SpO2)", f"{avg_spo2}%")
        col2.metric("Avg Heart Rate (HR)", f"{avg_hr} BPM")
        col3.metric("Captured Vital Packets", f"{total_packets} logs")
        col4.metric("Clinical Anomalies Detected", f"{total_anomalies} flags", delta="- Critical" if total_anomalies > 0 else "Normal")
        
        st.subheader("📈 Physiological Metric Trends (Smoothed vs Raw)")
        st.markdown("**Heart Rate Track (BPM):**")
        st.line_chart(df.set_index('id')[['heart_rate', 'hr_smoothed']])
        
        st.markdown("**Oxygen Saturation Track (%):**")
        st.line_chart(df.set_index('id')[['spo2', 'spo2_smoothed']])
        
        st.subheader("🗄️ Active Session Transaction Audit Logs")
        st.dataframe(df[['id', 'patient_id', 'spo2', 'heart_rate', 'raw_timestamp']].tail(10), use_container_width=True)

finally:
    db_session.close()

time.sleep(2)
st.rerun()
