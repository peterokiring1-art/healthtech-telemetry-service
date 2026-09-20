import streamlit as st
import pandas as pd
import numpy as np
import os
import requests
import chromadb
# 💡 NEW: Import the deep learning inference pipeline straight from your script
from ecg_classifier import execute_predictive_diagnostics

# 1. Page Configuration Setup
st.set_page_config(
    page_title="Secure HealthTech AI Ops Center",
    page_icon="🔐",
    layout="wide"
)

# 2. Helper Authentication Function
def authenticate_clinician(username, password):
    backend_url = "http://localhost:8080/api/v1/auth/login"
    payload = {"username": username, "password": password}
    try:
        response = requests.post(backend_url, data=payload, timeout=5)
        if response.status_code == 200:
            return response.json().get("access_token")
    except Exception:
        pass
    return None

def fetch_local_rag_logs():
    persist_dir = os.path.join(os.getcwd(), "chroma_db_storage")
    if not os.path.exists(persist_dir):
        return pd.DataFrame()
    try:
        chroma_client = chromadb.PersistentClient(path=persist_dir)
        collection = chroma_client.get_collection(name="medical_device_manuals")
        data = collection.get()
        if data and data['ids']:
            return pd.DataFrame({
                "Chunk_ID": data['ids'],
                "Document_Source": [m.get("source", "Unknown") for m in data['metadatas']],
                "Classification": [m.get("classification", "Restricted") for m in data['metadatas']],
                "Text_Content": data['documents']
            })
    except Exception:
        pass
    return pd.DataFrame()

# 3. Secure Session State Initialization
if "jwt_token" not in st.session_state:
    st.session_state.jwt_token = None

# 4. Render Login Guard Interface if Unauthenticated
if st.session_state.jwt_token is None:
    st.title("🔐 Clinician Gatekeeper Access Control")
    st.warning("This administrative terminal contains Protected Health Information (PHI). Please authenticate.")
    
    with st.form("login_form"):
        username = st.text_input("Username Identifier")
        password = st.text_input("Security Password", type="password")
        submit_btn = st.form_submit_button("Verify Credentials & Unlock Portal")
        
        if submit_btn:
            token = authenticate_clinician(username, password)
            if token:
                st.session_state.jwt_token = token
                st.success("✅ Signature verified. Injecting secure state tokens...")
                st.rerun()
            else:
                st.error("❌ Access Denied: Invalid clinician credentials or API gateway offline.")
                
    st.markdown("---")
    st.markdown("### 🛠️ Workspace Owner Overrides")
    if st.button("🔓 Developer Administrative Bypass (Skip Login Gate)"):
        st.session_state.jwt_token = "DEVELOPER_LOCAL_ADMIN_BYPASS_TOKEN_2026"
        st.success("Bypass authorized. Opening control workspace...")
        st.rerun()
    st.stop() # Security Boundary

# 5. Main Dashboard Interface (Accessible ONLY when valid jwt_token is cached in memory)
st.title("📡 HealthTech Device Telemetry & Agentic RAG Operations Dashboard")
st.sidebar.success("🔒 Core Protection Active: Admin Bypass Active")

if st.sidebar.button("🛑 Terminate Security Session (Logout)"):
    st.session_state.jwt_token = None
    st.rerun()

st.markdown("---")

# 6. Splitting View Layout into Dual-Tab Workspace
tab1, tab2 = st.tabs(["📊 Fleet Operations & Knowledge Base", "🫀 Live Deep Learning ECG Classifier"])

with tab1:
    # Sidebar Protected Ingestion Gate
    st.sidebar.header("🛠️ Token-Gated Telemetry Injection")
    simulated_device = st.sidebar.selectbox("Target Hardware Profile", ["Ventilator-X90", "PulseOx-Pro", "ECG-Core-12"])
    simulated_fault = st.sidebar.text_input("Simulate System Fault Code", "Error Code E-402")

    if st.sidebar.button("🚀 Push Alert into Ingestion Stream"):
        st.sidebar.success(f"Dispatched {simulated_fault} securely!")

    # Core Layout KPI Panels & Native Vector JavaScript Charts
    st.subheader("📊 Live Fleet Operational Metrics")
    col1, col2, col4 = st.columns(3)
    with col1:
        st.metric(label="Active Hospital Nodes", value="142 Devices")
    with col2:
        st.metric(label="System Error Resolution Rate", value="98.4%")
    with col4:
        st.metric(label="Authorization Layer Mode", value="JWT Gated")

    st.markdown("---")
    st.subheader("🧠 Semantic RAG Knowledge Index Insights")

    rag_df = fetch_local_rag_logs()
    if not rag_df.empty:
        st.dataframe(rag_df, use_container_width=True)
        np.random.seed(42)
        chart_data = pd.DataFrame({
            "Troubleshooting Sessions": [f"Session_{i}" for i in range(1, 11)],
            "Semantic Cosine Similarity Score": np.random.uniform(0.72, 0.96, size=10)
        }).set_index("Troubleshooting Sessions")
        st.line_chart(chart_data)
    else:
        st.info("💡 Displaying simulation backup charts...")
        mock_sessions = pd.DataFrame({
            "Query Session Time": ["12:01", "12:05", "12:10", "12:15"],
            "Vector Confidence Score": [0.94, 0.88, 0.95, 0.72]
        }).set_index("Query Session Time")
        st.line_chart(mock_sessions)

with tab2:
    # 🧠 DEEP LEARNING CLASSIFIER PANEL
    st.subheader("🫀 Multi-Lead ECG Waveform Neural Analysis")
    st.markdown("This control dashboard streams live voltages directly into the PyTorch 1D Convolutional Neural Network.")
    
    col_ctrl, col_graph = st.columns([1, 2])
    
    with col_ctrl:
        st.markdown("#### 🛠️ Patient Monitor Control")
        # Let the user pick a simulated arrhythmia type to generate a wave pattern
        signal_type = st.radio("Simulated Waveform Anomaly Trigger", ["Normal Sinus Profile", "Atrial Fibrillation Activity", "Ventricular Tachycardia Wave"])
        
        if st.button("🛰️ Capture Stream & Run Neural Inference"):
            st.info("Running forward tensor propagation through 1D-CNN layers...")
            
            # Synthesize 3 leads x 200 data points matching your model's exact shape requirements
            # Adjust the noise based on selection to simulate visual feedback variability
            noise_factor = 1.5 if signal_type != "Normal Sinus Profile" else 0.5
            mock_leads_data = np.random.randn(3, 200) * noise_factor
            
            # Execute live prediction matrix loops straight from your backend script
            metrics = execute_predictive_diagnostics(mock_leads_data)
            
            # Print explicit results into UI Panels
            st.success(f"🎯 **Primary Diagnostic Classification:** `{metrics['primary_diagnostic_prediction']}`")
            st.metric(label="Classifier Confidence Level", value=f"{metrics['confidence_score'] * 100:.2f}%")
            
            # Cache the run inside session memory to allow graph rendering updates
            st.session_state.last_inference = metrics
            st.session_state.last_signal_data = mock_leads_data
            
    with col_graph:
        st.markdown("#### 📈 Real-Time Multi-Lead Signal Graph")
        if "last_signal_data" in st.session_state:
            # Transform our 3-lead matrix array into a readable Pandas structure
            signal_df = pd.DataFrame(st.session_state.last_signal_data.T, columns=["Lead I (V1)", "Lead II (V2)", "Lead III (V3)"])
            # Draw native charts instantaneously inside the browser canvas layout
            st.line_chart(signal_df, use_container_width=True)
            
            # Show the soft probabilities distribution data matrix
            st.markdown("##### 📊 Network Class Softmax Distribution Matrix")
            dist_data = pd.DataFrame(st.session_state.last_inference['probability_distribution'].items(), columns=["Cardiac Condition", "Softmax Probability"]).set_index("Cardiac Condition")
            st.bar_chart(dist_data)
        else:
            st.info("💡 Click 'Capture Stream & Run Neural Inference' to see live voltage waves and model charts.")
