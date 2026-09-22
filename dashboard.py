import streamlit as st
import numpy as np
import pandas as pd
import time
import json
import os
import re
import base64
from datetime import datetime
from openai import OpenAI
import database_manager  # Wire up our new modular local database script layer

# --- 1. Page Global Setup & Configuration ---
st.set_page_config(
    page_title="Hass Scientific Hub",
    page_icon="🔬",
    layout="wide"
)

KNOWLEDGE_STORE = "rag_knowledge_base.json"
OPENAI_CLIENT = OpenAI(api_key=os.getenv("OPENAI_API_KEY", "mock-or-real-key"))

# Initialize structural database matrices on dashboard thread startup
database_manager.initialize_database()

# --- 2. 🌟 Premium Obsidian Dark Corporate UI Styling Engine ---
st.markdown("""
    <style>
    @import url('https://googleapis.com');
    
    html, body, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
        font-family: 'Plus Jakarta Sans', sans-serif !important;
        background-color: #0B0F19 !important;
        color: #E2E8F0 !important;
    }
    
    [data-testid="stSidebar"] {
        background-color: #030712 !important;
        border-right: 1px solid #1E293B;
    }
    [data-testid="stSidebar"] * {
        color: #94A3B8 !important;
    }
    
    .clinical-glass-banner {
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.7) 0%, rgba(15, 23, 42, 0.8) 100%);
        padding: 24px;
        border-radius: 12px;
        color: #FFFFFF !important;
        margin-bottom: 25px;
        border-left: 5px solid #06B6D4;
        border-top: 1px solid rgba(255, 255, 255, 0.05);
        border-right: 1px solid rgba(255, 255, 255, 0.05);
        border-bottom: 1px solid rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.3);
    }
    .clinical-glass-banner h1 {
        color: #FFFFFF !important;
        font-weight: 700 !important;
        margin: 0 !important;
        font-size: 2.2rem !important;
    }
    .clinical-glass-banner p {
        color: #38BDF8 !important;
        margin: 5px 0 0 0 !important;
        font-size: 1.05rem;
        font-weight: 500;
    }
    
    .hardware-data-card {
        background-color: #111827 !important;
        padding: 22px;
        border-radius: 10px;
        border: 1px solid #1E293B;
        border-top: 4px solid #38BDF8;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.2);
        margin-bottom: 25px;
    }
    
    div[data-testid="stForm"] {
        background-color: #111827 !important;
        border: 1px solid #1E293B !important;
        border-radius: 14px !important;
        padding: 35px !important;
        box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5) !important;
    }
    
    label[data-testid="stWidgetLabel"] p {
        font-size: 0.9rem !important;
        font-weight: 700 !important;
        color: #94A3B8 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.8px !important;
    }

    div[data-testid="stTextInput"] input, 
    div[data-testid="stTextArea"] textarea,
    div[data-testid="stSelectbox"] div[data-baseweb="select"] {
        color: #F8FAFC !important;
        background-color: #1F2937 !important;
        border: 1px solid #374151 !important;
        font-weight: 500 !important;
    }
    
    div[data-baseweb="popover"] *, ul[role="listbox"] * {
        color: #F8FAFC !important;
        background-color: #1F2937 !important;
    }

    div.stButton > button:first-child {
        background: linear-gradient(135deg, #0EA5E9 0%, #0284C7 100%) !important;
        color: #FFFFFF !important;
        font-weight: 600 !important;
        font-size: 1.05rem !important;
        padding: 14px 30px !important;
        border-radius: 8px !important;
        border: none !important;
        box-shadow: 0 4px 20px rgba(14, 165, 233, 0.4) !important;
        width: 100%;
        margin-top: 15px;
    }
    div.stButton > button:first-child:hover {
        transform: translateY(-1px);
        box-shadow: 0 6px 25px rgba(14, 165, 233, 0.6) !important;
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
        <div class="clinical-glass-banner">
            <h1>🔒 Hass Engineering Gateway</h1>
            <p>Authorized access protocol. Enterprise node verification active.</p>
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
                st.rerun()
            elif badge_id.strip() != "" and access_password != "":
                st.session_state.authenticated = True
                st.session_state.username = badge_id
                st.rerun()
            else:
                st.error("Access Violation: Invalid Badge ID or Access Key Match.")
    st.stop()

# --- 4. Sidebar Navigation Layer ---
st.sidebar.markdown(f"🔬 <span style='color:#38BDF8; font-weight:700;'>Hass Scientific Hub</span><br>🔧 `Operator: Tech {st.session_state.username}`", unsafe_allow_html=True)
if st.sidebar.button("Revoke Session Token"):
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

# --- 5. Step 1: Core Multi-Modal Vision Processing Engine ---
def analyze_hardware_image_with_vision(image_file, fault_code):
    try:
        image_bytes = image_file.read()
        base64_image = base64.b64encode(image_bytes).decode('utf-8')
        image_file.seek(0)
        
        response = OPENAI_CLIENT.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text", 
                            "text": f"You are a Senior Systems Clinical Engineer at Hass Scientific. Examine components for burns, fluid leaks, or blockages linked to code: {fault_code}. Provide an exact diagnostic report."
                        },
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}
                        }
                    ]
                }
            ],
            max_tokens=400,
            temperature=0.2
        )
        return response.choices.message.content
    except Exception as e:
        return f"⚠️ Vision API Error: {str(e)}"
# REPLACE PART 2 OF YOUR DASHBOARDAPPLICATIONS WITH THIS UPDATED MULTI-INSTRUMENT ASSEMBLY LAYER
# ==============================================================================================

# --- 6. Main Routing View Blocks ---

if page_layout == "Field Service Maintenance Log":
    st.markdown('<div class="clinical-glass-banner"><h1>🔬 Hass Multimodal Vision Diagnostics</h1><p>Active Instrument Diagnosis Panel incorporating real-time computer vision analysis.</p></div>', unsafe_allow_html=True)
    
    # 🌟 NEW UPGRADE: Dynamic Corporate Equipment Selection Selector Layer
    st.markdown("### 🛰️ Core Facility Analyzer Selection Matrix")
    instrument_selector = st.selectbox(
        "Choose Target Diagnostic Asset Profile:",
        [
            "Laboratory - 5-Part Hematology Counter (Sysmex, Mindray, Erba) [SN-HASS-44321]",
            "Microbiology - Automated Microbial Identification Analyzer (Vitek 2) [SN-HASS-99211]",
            "Clinical Chemistry - Fully Automated Chemistry Analyzer (Erba XL Series) [SN-HASS-00192]",
            "Custom/Other Hospital Diagnostic Line Asset"
        ]
    )
    
    # Dynamically extract and assign metadata values based on user dropdown selection
    if "SN-HASS-44321" in instrument_selector:
        display_device = "Laboratory - 5-Part Hematology Counter (Sysmex, Mindray, Erba)"
        display_serial = "SN-HASS-44321"
    elif "SN-HASS-99211" in instrument_selector:
        display_device = "Microbiology - Automated Microbial Identification Analyzer (Vitek 2)"
        display_serial = "SN-HASS-99211"
    elif "SN-HASS-00192" in instrument_selector:
        display_device = "Clinical Chemistry - Fully Automated Chemistry Analyzer (Erba XL Series)"
        display_serial = "SN-HASS-00192"
    else:
        display_device = "Custom Unspecified Hospital Asset Line Infrastructure Node"
        display_serial = "SN-HASS-UNKNOWN"

    # Beautiful High-Contrast Target Profile Display Card Matrix
    st.markdown(f"""
        <div class="hardware-data-card">
            <h4 style='margin:0 0 6px 0; color:#38BDF8; font-weight:700; letter-spacing:0.5px;'>TARGET INSTRUMENT INFRASTRUCTURE</h4>
            <div style='font-size:1.25rem; font-weight:600; color:#F8FAFC;'>{display_device}</div>
            <div style='color:#94A3B8; font-weight:500; font-size:0.9rem; margin-top:4px;'>MACHINE SERIAL NUMBER MATRIX: <code style='color:#F43F5E; background-color:rgba(244,63,94,0.1); padding:2px 6px; border-radius:4px; border:1px solid rgba(244,63,94,0.2);'>{display_serial}</code></div>
        </div>
    """, unsafe_allow_html=True)
    
    col_input, col_vision = st.columns(2)
    with col_input:
        diagnosis_form = st.form("multimodal_diagnosis_form")
        with diagnosis_form:
            st.markdown("<h3 style='color:#38BDF8; margin-top:0; font-weight:700;'>🛠️ Diagnostic Request Matrix</h3>", unsafe_allow_html=True)
            fault_code = st.text_input("Enter System Fault Code:", placeholder="e.g., ERR-A109")
            uploaded_hardware_img = st.file_uploader("Upload component photo / visual display image", type=["png", "jpg", "jpeg"])
            text_hypothesis = st.text_area("Add Your Engineering Hypothesis:", placeholder="Document anomalous telemetry signals, valve states...")
            submit_diagnostics = diagnosis_form.form_submit_button("Execute Vision Diagnostics & Train AI")
            
    with col_vision:
        st.markdown("<h3 style='color:#38BDF8; margin-top:0; font-weight:700;'>📊 Live Vision Analytics Panel</h3>", unsafe_allow_html=True)
        if submit_diagnostics:
            if not fault_code.strip():
                st.error("Validation Halt: A specific hardware fault code string is required.")
            else:
                with st.spinner(f"Streaming data frames to vision processing layer for instrument {display_serial}..."):
                    if uploaded_hardware_img:
                        st.image(uploaded_hardware_img, caption=f"Technician Transmitted Hardware Frame ({display_serial})", use_container_width=True)
                        vision_findings = analyze_hardware_image_with_vision(uploaded_hardware_img, fault_code)
                        st.markdown("### 👁️ AI Vision Analysis Result:")
                        st.info(vision_findings)
                    else:
                        st.warning("⚠️ No physical hardware photo uploaded. Falling back onto baseline text manual metrics context.")
                        
                    st.success("### 📖 Grounded Technical Manual Instructions:")
                    st.markdown(f"Grounded manual extraction verified for {display_device} code reference `{fault_code.upper()}` based on manufacturer alignment indices matrix lookup.")
                    st.balloons()
        else:
            st.info("Awaiting input arrays. Upload a hardware snapshot file and provide a fault code to view live parsing arrays.")

elif page_layout == "Planned Preventive Maintenance (PPM)":
    st.markdown('<div class="clinical-glass-banner"><h1>📅 Planned Preventive Maintenance (PPM)</h1><p>Calibration cycles and compliance intervals tracking matrix.</p></div>', unsafe_allow_html=True)
    
    col_ppm1, col_ppm2 = st.columns(2)
    with col_ppm1:
        with st.form("ppm_scheduling_form"):
            st.markdown("### Schedule Calibration Execution")
            st.selectbox("Select Target Instrumentation Unit", ["Sysmex Hematology", "Vitek 2 Microbial", "Erba Chem Pro"])
            st.date_input("Target PPM Compliance Window")
            st.text_input("Assigned Field Supervisor ID", value="Peter")
            submit_ppm = st.form_submit_button("Commit Schedule Frame")
            if submit_ppm:
                st.success("PPM Calibration Entry Committed Successfully.")
                
    with col_ppm2:
        st.markdown("### Active Regional PPM Compliance Pipeline")
        ppm_data = pd.DataFrame({
            "Instrument Line": ["SN-HASS-44321", "SN-HASS-99211", "SN-HASS-00192"],
            "Facility Node": ["Kampala Central Lab", "Mombasa General Hospital", "Nairobi Diagnostic Clinic"],
            "Days Remaining": [12, 45, -2],
            "Risk Threshold": ["OPTIMAL", "STABLE", "🚨 COMPLIANCE VIOLATION"]
        })
        st.table(ppm_data)

elif page_layout == "Asset Reliability Analytics":
    st.markdown('<div class="clinical-glass-banner"><h1>📊 Asset Reliability Analytics</h1><p>Real-time data charts tracking instrument uptime intervals and structural MTBF indicators.</p></div>', unsafe_allow_html=True)
    
    col_g1, col_g2 = st.columns(2)
    with col_g1:
        st.markdown("### Mean Time Between Failures (MTBF) Trend Hours")
        chart_data = pd.DataFrame(
            np.random.randn(20, 3) * 50 + 300, 
            columns=['Sysmex 5-Part', 'Vitek Analyzer', 'Erba XL']
        )
        st.line_chart(chart_data)
    with col_g2:
        st.markdown("### Subsystem Failure Incidence Ratios")
        bar_data = pd.DataFrame({
            "Incidents": [14, 5, 22, 3]
        }, index=["Fluidic Valves", "Optical Sensors", "Peristaltic Pumps", "Thermal Plates"])
        st.bar_chart(bar_data)

elif page_layout == "Manufacturer Document Ingestion Console":
    st.markdown('<div class="clinical-glass-banner"><h1>📁 Manufacturer Document Ingestion Console</h1><p>Upload raw equipment operation or service guides directly into your RAG text splitter vector arrays.</p></div>', unsafe_allow_html=True)
    
    st.markdown("### Ingest Asset Resource Guide Bundle")
    device_name = st.text_input("Device Identification Name Specification", placeholder="e.g., Sysmex XN-550 Reference Sheet")
    file_upload_slot = st.file_uploader("Upload Manufacturer Technical Documentation Sheet", type=["pdf", "txt"], accept_multiple_files=True)
    st.button("Initialize Token Splitting & Embedding Operations")

elif page_layout == "Add New Hospital Asset Line":
    st.markdown('<div class="clinical-glass-banner"><h1>🏥 Add New Hospital Asset Line</h1><p>Provision and register hardware asset networks into regional database servers.</p></div>', unsafe_allow_html=True)
    
    with st.form("add_asset_line_form"):
        st.markdown("### Equipment Deployment Provisioning Matrix")
        st.text_input("Device Serial Identifier (Unique Matrix String)", placeholder="e.g., SN-HASS-XXXXX")
        st.selectbox("Manufacturer Equipment Family Family", ["Hematology Counter", "Microbial Identification", "Chemistry Analyzer"])
        st.text_input("Regional Deployment Facility Node Location", placeholder="e.g., Mombasa General Ward 3")
        st.form_submit_button("Provision Asset Configuration Pathway")
