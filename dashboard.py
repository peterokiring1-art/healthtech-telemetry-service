import streamlit as st
import pandas as pd
import numpy as np
import os
import chromadb

# 1. Page Configuration Setup
st.set_page_config(
    page_title="HealthTech Telemetry & RAG Ops Center",
    page_icon="📡",
    layout="wide"
)

st.title("📡 HealthTech Device Telemetry & Agentic RAG Operations Dashboard")
st.markdown("---")

# 2. Database & Vector Database Connectors
def fetch_local_rag_logs():
    """
    Direct Vector Bridge: Connects to your persistent chroma_db_storage
    and pulls down all indexed entries to map engineering search data.
    """
    persist_dir = os.path.join(os.getcwd(), "chroma_db_storage")
    if not os.path.exists(persist_dir):
        return pd.DataFrame() # Return empty if database isn't built yet
        
    try:
        chroma_client = chromadb.PersistentClient(path=persist_dir)
        collection = chroma_client.get_collection(name="medical_device_manuals")
        data = collection.get()
        
        # Transform ChromaDB dictionary arrays into a Pandas DataFrame
        if data and data['ids']:
            df = pd.DataFrame({
                "Chunk_ID": data['ids'],
                "Document_Source": [m.get("source", "Unknown") for m in data['metadatas']],
                "Classification": [m.get("classification", "Restricted") for m in data['metadatas']],
                "Text_Content": data['documents']
            })
            return df
    except Exception as e:
        st.sidebar.error(f"Vector connection error: {e}")
    return pd.DataFrame()

# 3. Sidebar Simulation Controllers
st.sidebar.header("🛠️ Simulated Telemetry Injection")
simulated_device = st.sidebar.selectbox("Target Hardware Profile", ["Ventilator-X90", "PulseOx-Pro", "ECG-Core-12"])
simulated_fault = st.sidebar.text_input("Simulate System Fault Code", "Error Code E-402")

if st.sidebar.button("🚀 Push Alert into Ingestion Stream"):
    st.sidebar.success(f"Dispatched {simulated_fault} to FastAPI queue!")

# 4. Core Layout KPI Panels
st.subheader("📊 Live Fleet Operational Metrics")
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(label="Active Hospital Nodes", value="142 Devices", delta="+3 current session")
with col2:
    st.metric(label="Ingestion Buffer Telemetry Rate", value="500 Hz", delta="Stable Normal")
with col3:
    st.metric(label="Vector Database Storage Capacity", value="2 Collection Tables")
with col4:
    st.metric(label="System Error Resolution Rate", value="98.4%", delta="+0.6% this week")

st.markdown("---")

# 5. Visualizing RAG Logs & Vector Matching Metrics
st.subheader("🧠 Semantic RAG Knowledge Index Insights")

rag_df = fetch_local_rag_logs()

if not rag_df.empty:
    st.markdown("#### 🗂️ Active Vector Database Collections (ChromaDB Indexed Items)")
    st.dataframe(rag_df, use_container_width=True)
    
    st.markdown("#### 📈 Historical Query Similarity Confidence Metric (Last 10 Troubleshooting Sessions)")
    
    # Generate mock semantic distances based on recent queries
    np.random.seed(42)
    session_logs = [f"Session_{i}" for i in range(1, 11)]
    similarity_scores = np.random.uniform(0.72, 0.96, size=10)
    
    chart_data = pd.DataFrame({
        "Troubleshooting Sessions": session_logs,
        "Semantic Cosine Similarity Score": similarity_scores
    }).set_index("Troubleshooting Sessions")
    
    # Streamlit Native Line Chart (No dependencies required)
    st.line_chart(chart_data)
    
    # Highlight critical alert classifications using native chart components
    st.markdown("#### 🚨 Technical Document Density Matrix")
    source_counts = rag_df['Document_Source'].value_counts().to_frame()
    
    # Streamlit Native Bar Chart (Bypasses Matplotlib completely!)
    st.bar_chart(source_counts)

else:
    st.info("💡 No active data vectors detected inside 'chroma_db_storage'. Launching simulation backup layout...")
    
    # Display mock analytics visualization using purely native charts
    mock_sessions = pd.DataFrame({
        "Query Session Time": ["12:01", "12:05", "12:10", "12:15"],
        "Vector Confidence Score": [0.94, 0.88, 0.95, 0.72]
    }).set_index("Query Session Time")
    
    st.line_chart(mock_sessions)
