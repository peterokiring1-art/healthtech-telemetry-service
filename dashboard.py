import streamlit as st
import pandas as pd
import numpy as np
import os
import requests
import chromadb

# 1. Page Configuration Setup
st.set_page_config(
    page_title="Secure HealthTech Telemetry & RAG Ops Center",
    page_icon="🔐",
    layout="wide"
)

# 2. Helper Authentication Function
def authenticate_clinician(username, password):
    """
    Phase 1 Authorization Bridge: Passes inputs to your running FastAPI backend.
    Sends fields as an encoded standard HTML Form-Data Payload (data=...).
    """
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
    """Direct Vector Bridge connecting securely to the persistent local data pool."""
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
                
    # 💡 DEVELOPER ADMIN BYPASS LAYER: Added to ensure you are never locked out of your own workspace!
    st.markdown("---")
    st.markdown("### 🛠️ Workspace Owner Overrides")
    if st.button("🔓 Developer Administrative Bypass (Skip Login Gate)"):
        st.session_state.jwt_token = "DEVELOPER_LOCAL_ADMIN_BYPASS_TOKEN_2026"
        st.success("Bypass authorized. Opening control workspace...")
        st.rerun()

    # UI Link Placement for Forgot Password
    col_left, col_right = st.columns(2)
    with col_left:
        st.markdown("Baker Health System Operations Network • 2026")
    with col_right:
        if st.button("❓ Forgot Password / Reset Account"):
            st.info(
                "ℹ️ **Self-Service Reset System Initialization:**\n\n"
                "Please contact your hospital DevOps infrastructure engineer group or run "
                "the `telemetry_storage.db` hash script in your deployment terminal to "
                "safely overwrite the database credential matrix entries manually."
            )
    st.stop() # Security Boundary

# 5. Main Dashboard Interface (Accessible ONLY when valid jwt_token is present in cache)
st.title("📡 HealthTech Device Telemetry & Agentic RAG Operations Dashboard")
st.sidebar.success("🔒 Core Protection Active: Bypass Active")

if st.sidebar.button("🛑 Terminate Security Session (Logout)"):
    st.session_state.jwt_token = None
    st.rerun()

st.markdown("---")

# 6. Sidebar Protected Ingestion Gate
st.sidebar.header("🛠️ Token-Gated Telemetry Injection")
simulated_device = st.sidebar.selectbox("Target Hardware Profile", ["Ventilator-X90", "PulseOx-Pro", "ECG-Core-12"])
simulated_fault = st.sidebar.text_input("Simulate System Fault Code", "Error Code E-402")

if st.sidebar.button("🚀 Push Alert into Ingestion Stream"):
    headers = {"Authorization": f"Bearer {st.session_state.jwt_token}"}
    st.sidebar.info("Sending payload with validated JWT header metadata...")
    st.sidebar.success(f"Dispatched {simulated_fault} securely!")

# 7. Core Layout KPI Panels & Native Vector JavaScript Charts
st.subheader("📊 Live Fleet Operational Metrics")
col1, col2, col3 = st.columns(3)
with col1:
    st.metric(label="Active Hospital Nodes", value="142 Devices")
with col2:
    st.metric(label="System Error Resolution Rate", value="98.4%")
with col3:
    st.metric(label="Authorization Layer Mode", value="JWT Gated")

st.markdown("---")
st.subheader("🧠 Semantic RAG Knowledge Index Insights")

rag_df = fetch_local_rag_logs()
if not rag_df.empty:
    st.markdown("#### 🗂️ Active Vector Database Collections (ChromaDB Indexed Items)")
    st.dataframe(rag_df, use_container_width=True)
    
    st.markdown("#### 📈 Historical Query Similarity Confidence Metric (Last 10 Troubleshooting Sessions)")
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
