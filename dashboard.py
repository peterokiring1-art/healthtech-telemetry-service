import streamlit as st
import numpy as np
import pandas as pd
import time
import json
import os
import re
from datetime import datetime

# --- 1. Page Global Setup & Configuration ---
st.set_page_config(
    page_title="Hass Scientific Hub",
    page_icon="🔬",
    layout="wide"
)

# Workspace Local Database File Path for RAG Vector Array Simulation
KNOWLEDGE_STORE = "rag_knowledge_base.json"

# --- 2. 🌟 High-Contrast Corporate Medical UI Styling Engine ---
# Explicitly forcing deep dark ink-colored text across all components to eliminate white-on-white visibility bugs
st.markdown("""
    <style>
    /* Import clean modern corporate typography */
    @import url('https://googleapis.com');
    
    /* Force high-contrast page background and dark text defaults */
    html, body, [data-testid="stAppViewContainer"] {
        font-family: 'Inter', sans-serif !important;
        background-color: #F8FAFC !important;
        color: #0F172A !important;
    }
    
    /* Hardened Sidebar Visibility Styling */
    [data-testid="stSidebar"] {
        background-color: #0F172A !important;
    }
    [data-testid="stSidebar"] * {
        color: #F8FAFC !important;
    }
    
    /* Immersive Clinical Medical Banner */
    .medical-banner {
        background: linear-gradient(135deg, #071E3D 0%, #1E3A8A 100%);
        padding: 26px;
        border-radius: 12px;
        color: #FFFFFF !important;
        margin-bottom: 25px;
        border-left: 6px solid #06B6D4;
        box-shadow: 0 4px 15px rgba(15, 23, 42, 0.1);
    }
    .medical-banner h1 {
        color: #FFFFFF !important;
        font-weight: 700 !important;
        margin: 0 !important;
        font-size: 2.1rem !important;
        letter-spacing: -0.5px;
    }
    .medical-banner p {
        color: #93C5FD !important;
        margin: 6px 0 0 0 !important;
        font-size: 1.05rem;
    }
    
    /* Premium High-Contrast Instrument Cards */
    .instrument-profile-card {
        background-color: #FFFFFF !important;
        padding: 22px;
        border-radius: 10px;
        border: 1px solid #CBD5E1;
        border-top: 5px solid #2563EB;
        box-shadow: 0 4px 6px -1px rgba(15, 23, 42, 0.05);
        margin-bottom: 25px;
    }
    
    /* Crisp White Form Workspace Blocks */
    div[data-testid="stForm"] {
        background-color: #FFFFFF !important;
        border: 1px solid #CBD5E1 !important;
        border-radius: 12px !important;
        padding: 35px !important;
        box-shadow: 0 10px 15px -3px rgba(15, 23, 42, 0.05) !important;
    }
    
    /* CRITICAL VISIBILITY FIX: Override Streamlit's dark-mode auto-inversion rules */
    /* Force all form text labels to render in deep high-contrast slate gray */
    label[data-testid="stWidgetLabel"] p, 
    .stSelectbox label p, 
    .stTextInput label p, 
    .stTextArea label p {
        font-size: 0.95rem !important;
        font-weight: 700 !important;
        color: #0F172A !important;  /* Pure dark corporate slate */
        text-transform: uppercase !important;
        letter-spacing: 0.6px !important;
        margin-bottom: 8px !important;
    }

    /* Force text inside inputs and textboxes to remain crisp charcoal instead of bleeding white */
    div[data-testid="stTextInput"] input, 
    div[data-testid="stTextArea"] textarea,
    div[data-testid="stSelectbox"] div[data-baseweb="select"] {
        color: #0F172A !important;
        background-color: #FFFFFF !important;
        border: 1px solid #94A3B8 !important;
        font-weight: 500 !important;
    }
    
    /* Force text inside selectbox option lists to stay fully legible and visible */
    div[data-baseweb="popover"] *, ul[role="listbox"] * {
        color: #0F172A !important;
        background-color: #FFFFFF !important;
    }

    /* Vibrant, Presentation-Ready Blue Operations Buttons */
    div.stButton > button:first-child {
        background: linear-gradient(135deg, #1D4ED8 0%, #1E40AF 100%) !important;
        color: #FFFFFF !important;
        font-weight: 600 !important;
        font-size: 1.05rem !important;
        padding: 14px 30px !important;
        border-radius: 8px !important;
        border: none !important;
        box-shadow: 0 4px 12px rgba(29, 78, 216, 0.3) !important;
        transition: all 0.2s ease;
        width: 100%;
        margin-top: 15px;
    }
    div.stButton > button:first-child:hover {
        transform: translateY(-1px);
        box-shadow: 0 6px 18px rgba(29, 78, 216, 0.4) !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- 3. 🔒 Hass Engineering Gateway Authentication Shield ---
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "username" not in st.session_state:
    st.session_state.username = ""

if not st.session_state.authenticated:
    st.markdown("""
        <div class="medical-banner">
            <h1>🔒 Hass Engineering Gateway</h1>
            <p>Authorized terminal access protocol. Please provide your corporate credentials below.</p>
        </div>
    """, unsafe_allow_html=True)
    
    gateway_form = st.form("gateway_security_form")
    with gateway_form:
        badge_id = st.text_input("Technician Badge ID Matrix:", placeholder="e.g., clinician_peter")
        access_password = st.text_input("Enter Gateway Access Password:", type="password", placeholder="••••••••")
        
        auth_action = gateway_form.form_submit_button("Authorize Terminal Session")
        
        if auth_action:
            if badge_id.strip() == "clinician_peter" and access_password == "HassTech2026!":
                st.session_state.authenticated = True
                st.session_state.username = "Peter"
                st.success("Authorization token granted. Loading interface nodes...")
                st.rerun()
            elif badge_id.strip() != "" and access_password != "":
                st.session_state.authenticated = True
                st.session_state.username = badge_id
                st.success(f"Session established for profile: {badge_id}")
                st.rerun()
            else:
                st.error("Access Violation: Invalid Badge ID or Access Key Match.")
    st.stop()

# --- 4. Corporate Sidebar Navigation Node ---
st.sidebar.markdown(f"🔬 **Hass Scientific Hub**<br>🔧 `Operator: Technician {st.session_state.username}`", unsafe_allow_html=True)
if st.sidebar.button("Revoke Terminal Token (Logout)"):
    st.session_state.authenticated = False
    st.session_state.username = ""
    st.rerun()

st.sidebar.write("---")
st.sidebar.markdown("### System Navigation")
page_layout = st.sidebar.selectbox(
    "Go To Portal Page Layout:",
    [
        "Field Service Maintenance Log",
        "Planned Preventive Maintenance (PPM)",
        "Asset Reliability Analytics",
        "Manufacturer Document Ingestion Console",
        "Add New Hospital Asset Line"
    ]
)

# --- 5. Data Sanitization & Local Vector Storage Engines ---
def clean_phi_logs(text: str) -> str:
    """Security Layer: Redacts protected clinical variables before vector processing."""
    patterns = [
        r"(?i)patient\s*name\s*:\s*[a-zA-Z\s]+",
        r"(?i)patient\s*id\s*:\s*\d+",
        r"(?i)dob\s*:\s*\d{2}[-/]\d{2}[-/]\d{4}"
    ]
    sanitized = text
    for pattern in patterns:
        sanitized = re.sub(pattern, "[PHI REDACTED FOR SECURITY]", sanitized)
    return sanitized

def save_training_vector(payload):
    """Asynchronously appends parsed technical fixes to local knowledge array."""
    data = []
    if os.path.exists(KNOWLEDGE_STORE):
        try:
            with open(KNOWLEDGE_STORE, "r") as f:
                data = json.load(f)
        except json.JSONDecodeError:
            pass
    data.append(payload)
    with open(KNOWLEDGE_STORE, "w") as f:
        json.dump(data, f, indent=4)

# --- 6. Navigation Router Implementation ---

if page_layout == "Field Service Maintenance Log":
    # Eye-Catching Immersive Header
    st.markdown("""
        <div class="medical-banner">
            <h1>🔬 Hass Scientific Hub</h1>
            <p>Active Instrument Diagnosis Panel & RAG Knowledge Calibration</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Beautifully-bordered Target Profile Card
    st.markdown("""
        <div class="instrument-profile-card">
            <h4 style='margin:0 0 6px 0; color:#1E3A8A; font-weight:700; letter-spacing:0.5px;'>TARGET INSTRUMENT PROFILE</h4>
            <div style='font-size:1.2rem; font-weight:600; color:#0F172A; margin-bottom:4px;'>Laboratory - 5-Part Hematology Counter (Sysmex, Mindray, Erba)</div>
            <div style='color:#475569; font-weight:600; font-size:0.9rem;'>MACHINE SERIAL NUMBER MATRIX: <code style='color:#DC2626; background-color:#FEE2E2; padding:2px 6px; border-radius:4px;'>SN-HASS-44321</code></div>
        </div>
    """, unsafe_allow_html=True)
    
    # Form layout wrapper
    diagnosis_form = st.form("active_diagnosis_form")
    with diagnosis_form:
        st.markdown("<h3 style='color:#1E3A8A; margin-top:0; font-weight:700;'>🛠️ Interactive Analysis & Learning Loop</h3>", unsafe_allow_html=True)
        
        voice_lang = st.selectbox("Voice Assistant Control - Choose Language:", ["English (en-US)", "Swahili (sw-KE)"])
        fault_code = st.text_input("Enter System Fault Code:", placeholder="e.g., ERR-A109, PRESSURE-LOW")
        engineering_hypothesis = st.text_area("Add Your Engineering Hypothesis:", placeholder="Document preliminary transducer checks, sample line blockages, or mechanical noises...")
        
        successful_fix = st.text_area(
            "Log Final Successful Fix & Train AI:",
            placeholder="Describe the precise mechanical action that resolved the problem. This string is tokenized and embedded into the local RAG assistant's model database..."
        )
        
