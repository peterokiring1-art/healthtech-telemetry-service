import streamlit as st
import psycopg2
import pandas as pd
import plotly.express as px
import time

# Configure layout properties
st.set_page_config(page_title="HealthTech Telemetry Core", layout="wide")

def get_db_connection():
    return psycopg2.connect(
        dbname="postgres",
        user="postgres",
        password="postgres",
        host="127.0.0.1",
        port="5432"
    )

st.title("🩺 HealthTech Real-Time Telemetry Dashboard")
st.markdown("---")

# --- AUTO REFRESH SETUP ---
if "run_count" not in st.session_state:
    st.session_state.run_count = 0
st.session_state.run_count += 1

st.sidebar.success(f"🔄 Connected to PostgreSQL Engine")
st.sidebar.info(f"📊 Auto-refreshing active. Poll cycle: {st.session_state.run_count}")

try:
    conn = get_db_connection()
    
    # Fetch data logs using direct DBAPI2 connections
    query_all = "SELECT patient_id, timestamp, spo2, heart_rate FROM pulse_ox_logs ORDER BY timestamp DESC;"
    df = pd.read_sql(query_all, conn)
    
    query_alerts = "SELECT patient_id, timestamp, spo2, heart_rate FROM pulse_ox_logs WHERE spo2 < 90 ORDER BY timestamp DESC;"
    df_alerts = pd.read_sql(query_alerts, conn)
    
    # --- SECTION 1: EMERGENCY CLINICAL ALERTS GRID ---
    st.subheader("🚨 Critical Clinical Anomalies (SpO2 < 90%)")
    if not df_alerts.empty:
        for idx, row in df_alerts.iterrows():
            st.error(
                f"⚠️ **CRITICAL DROP** | Patient: `{row['patient_id']}` | "
                f"SpO2: **{row['spo2']}%** | Heart Rate: **{row['heart_rate']} bpm** | "
                f"Time: {row['timestamp']}"
            )
    else:
        st.success("✅ Operational Normal: No active patient hypoxia anomalies flagged.")
        
    st.markdown("---")
    
    # --- SECTION 2: PATIENT HISTORICAL TREND TRACKING ---
    st.subheader("📊 Patient Metric Historical Analytics")
    
    if not df.empty:
        patient_list = df['patient_id'].unique()
        selected_patient = st.selectbox("Select Patient Profile to Inspect:", patient_list)
        
        df_patient = df[df['patient_id'] == selected_patient].sort_values('timestamp')
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(f"### Oxygen Saturation Trend (SpO2) for {selected_patient}")
            fig_spo2 = px.line(df_patient, x='timestamp', y='spo2', markers=True, title="SpO2 (%) over Time")
            fig_spo2.add_hline(y=90, line_dash="dash", line_color="red", annotation_text="Hypoxia Threshold")
            # 💡 Fix 1: Updated layout configuration parameter
            st.plotly_chart(fig_spo2, width="stretch")
            
        with col2:
            st.markdown(f"### Heart Rate Trend (HR) for {selected_patient}")
            fig_hr = px.line(df_patient, x='timestamp', y='heart_rate', markers=True, title="Heart Rate (bpm) over Time")
            # 💡 Fix 2: Updated layout configuration parameter
            st.plotly_chart(fig_hr, width="stretch")
            
        st.markdown("### 📋 Complete Log History")
        # 💡 Fix 3: Updated data table configuration parameter
        st.dataframe(df_patient, width="stretch")
        
    else:
        st.warning("No data logs located inside the database storage.")
        
    conn.close()

except Exception as e:
    st.error(f"❌ Failed to query database: {e}")

time.sleep(5)
st.rerun()
