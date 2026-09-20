import streamlit as st
import device_rag_service as rag
import random
from datetime import datetime
from pypdf import PdfReader
from docx import Document
from fleet_data import hospital_fleet_catalog

# Production Page Configuration
st.set_page_config(layout="wide", page_title="Hass Scientific Hub")

# Custom UI Styles
st.markdown("""
<style>
    html, body, [data-testid="stMarkdownContainer"] p, label { font-size: 22px !important; line-height: 1.6 !important; }
    .stButton>button { background-color: #007bff !important; color: white !important; font-size: 24px !important; font-weight: bold !important; width: 100% !important; padding: 14px 28px !important; border-radius: 8px !important; }
    .card-box { background-color: white; padding: 30px; border-radius: 14px; border: 1px solid #e2e8f0; margin-bottom: 25px; }
</style>
""", unsafe_allow_html=True)

# Session State Initializer
if "biomedical_fleet" not in st.session_state:
    st.session_state["biomedical_fleet"] = hospital_fleet_catalog.copy()

if "voice_text_bridge" not in st.session_state:
    st.session_state["voice_text_bridge"] = ""

st.markdown('# Hass Scientific & Medical <span style="color:#007bff">Diagnostic Hub</span>', unsafe_allow_html=True)
st.markdown('### *Clinical AI Knowledge Gateway & Comprehensive Hospital Fleet Engineering Terminal*')
st.markdown("---")

st.sidebar.markdown("# System Navigation")
page_selection = st.sidebar.radio("Go To Portal Page Layout:", ["Field Service Maintenance Log", "Manufacturer Document Ingestion Console", "Add New Hospital Asset Line"])

# PAGE 1: DYNAMIC ASSET REGISTRY
if page_selection == "Add New Hospital Asset Line":
    st.markdown('<div class="card-box">', unsafe_allow_html=True)
    st.header("Dynamic Fleet Inventory Management")
    new_machine_name = st.text_input("Enter New Hospital Equipment Model Designation Name:", placeholder="e.g. Radiology - Fixed Mammography Unit")
    
    if st.button("Add New Instrument to Fleet Registry"):
        if new_machine_name:
            clean_name = new_machine_name.strip()
            if clean_name in st.session_state["biomedical_fleet"]:
                st.warning(f"The asset model line '{clean_name}' is already registered.")
            else:
                st.session_state["biomedical_fleet"].append(clean_name)
                st.session_state["biomedical_fleet"].sort()
                st.success(f"Registered '{clean_name}' into the local operational fleet database.")
        else:
            st.error("Please enter a device model designation string.")
    st.subheader("Current Active Hospital Facility Registry Fleet")
    st.write(", ".join(st.session_state["biomedical_fleet"]))
    st.markdown('</div>', unsafe_allow_html=True)

# PAGE 2: MAIN TECHNICIAN DIAGNOSTIC LOGS
elif page_selection == "Field Service Maintenance Log":
    st.markdown('<div class="card-box">', unsafe_allow_html=True)
    st.header("Active Instrument Diagnosis Panel")
    
    col1, col2 = st.columns(2)
    with col1:
        user_model = st.selectbox("Target Instrument Profile", st.session_state["biomedical_fleet"], key="user_model")
    with col2:
        serial_num = st.text_input("Machine Serial Number Matrix", value=f"SN-HASS-{random.randint(10000, 99999)}")
    st.markdown('</div>', unsafe_allow_html=True)
    
    c_left, c_right = st.columns(2)
    with c_left:
        st.markdown('<div class="card-box" style="height:100%;">', unsafe_allow_html=True)
        st.subheader("Voice Assistant Control")
        lang_choice = st.selectbox("Choose Dictation Language", ["English (en-US)", "Swahili / Kiswahili (sw-KE)"])
        selected_lang_code = "en-US" if "English" in lang_choice else "sw-KE"

        if "voice_capture" in st.query_params:
            st.session_state["voice_text_bridge"] = st.query_params["voice_capture"]
            st.query_params.clear()
        
        voice_lines = [
            '<div style="text-align: center; font-family: sans-serif; padding-top: 10px;">',
            '    <button id="mic_btn" style="background-color: #ff4b4b; color: white; border: none; padding: 14px 20px; font-size: 16px; font-weight: bold; border-radius: 6px; cursor: pointer; width: 100%;">Tap to Speak Anomaly</button>',
            '    <p id="mic_status" style="margin-top: 10px; font-size: 13px; color: #666; font-weight: 500;">Status: Idle</p>',
            '</div>',
            '<script>',
            '    const micBtn = document.getElementById("mic_btn");',
            '    const micStatus = document.getElementById("mic_status");',
            '    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;',
            '    if (SpeechRecognition) {',
            '        const recognition = new SpeechRecognition();',
            '        recognition.lang = "__LANG_PLACEHOLDER__";',
            '        micBtn.onclick = function() { recognition.start(); micStatus.innerText = "Recording Active..."; micStatus.style.color = "#ff4b4b"; };',
            '        recognition.onresult = function(event) {',
            '            const transcript = event.results.transcript;',
            '            const url = new URL(window.parent.location.href);',
            '            url.searchParams.set("voice_capture", transcript);',
            '            window.parent.location.href = url.toString();',
            '        };',
            '    } else { micStatus.innerText = "Microphone API Restricted"; }',
            '</script>'
        ]
        voice_component_code = "\n".join(voice_lines).replace("__LANG_PLACEHOLDER__", selected_lang_code)
        st.components.v1.html(voice_component_code, height=110)
        st.markdown('</div>', unsafe_allow_html=True)
        
    with c_right:
        st.markdown('<div class="card-box" style="height:100%;">', unsafe_allow_html=True)
        st.subheader("Interactive Collaborative Analysis")
        error_logged = st.text_input("Enter Active System Fault Code or Critical Symptom:", value=st.session_state["voice_text_bridge"])
        user_suggestion = st.text_area("Add Your Engineering Hypothesis / Observations (Let\'s analyze together):", height=72)
        st.markdown('</div>', unsafe_allow_html=True)
        
    if st.button("Run Collaborative AI Problem Analysis"):
        if error_logged:
            with st.spinner("AI Engine cross-examining compiled knowledge layers..."):
                ai_solution = rag.query_and_analyze_fault(user_model, error_logged, user_suggestion)
                if ai_solution:
                    with st.expander("View AI Diagnostic Analysis Report & Corrective Protocols", expanded=True):
                        st.markdown(ai_solution)
                    with st.expander("View Generated Live Technical Repair Schematic Blueprint", expanded=True):
                        model_upper = user_model.upper()
                        if "LABORATORY" in model_upper: st.success("System Identity Map: Laboratory Hydraulic Flow-Cell & Aperture Isolation Blueprint.")
                        elif "RADIOLOGY" in model_upper: st.success("System Identity Map: Radiology High-Voltage SMPS & Gantry Rotor Target Block Alignment Blueprint.")
                        elif "THEATRE" in model_upper: st.success("System Identity Map: Operating Room Anesthesia Gas Mixer & Diathermy RF Delivery Waveform Schematic.")
                        elif "ICU" in model_upper: st.success("System Identity Map: Critical Care Mechanical Ventilator Valve Loop & Infusion Stepper Motor Module Guide.")
                        elif "NICU" in model_upper: st.success("System Identity Map: Neonatal Forced-Convection Heat Servo Circuit & Active Humidity Module Schematic.")
                        elif "CSSD" in model_upper: st.success("System Identity Map: Autoclave Vacuum Extraction Pump Line & CSSD Steam Pressure Valve Blueprint.")
                        else: st.success("System Identity Map: Advanced Microfluidic Power System Board Reference Schematic Map.")
        else:
            st.error("Please specify an active error code before conducting analysis.")

    # EXPERIENCE LEARNING LOOP
    st.markdown('<div class="card-box" style="background-color: #edf2f7; border: 1px dashed #cbd5e0;">', unsafe_allow_html=True)
    with st.expander("Log Final Successful Fix & Train AI", expanded=False):
        st.subheader("Train the AI Memory Node")
        st.markdown("Record your successful field fix below so the AI remembers it next time!")
        solved_code = st.text_input("Confirm Remedied Error Code:")
        final_fix_text = st.text_area("What was the exact successful fix? (Be precise):")
        if st.button("Lock Fix into AI Memory"):
            if solved_code and final_fix_text:
                rag.save_successful_fix(user_model, solved_code, final_fix_text)
                st.success(f"Your successful field fix for {user_model} '{solved_code.upper()}' has been locked into permanent memory!")
            else: st.error("Incomplete Fields: Confirm parameters before logging.")
    st.markdown('</div>', unsafe_allow_html=True)

# PAGE 3: MANUFACTURER BATCH MANUAL INGESTION CONSOLE
else:
    st.markdown('<div class="card-box">', unsafe_allow_html=True)
    st.header("Service Manual Automated Batch Ingestion")
    st.markdown("Upload manufacturer service manuals (**PDF, DOCX**) to compile technical knowledge loops.")
    selected_model = st.selectbox("Target Device Profile", st.session_state["biomedical_fleet"], key="admin_model")
    uploaded_files = st.file_uploader(f"Select Service Manuals for {selected_model}", type=["pdf", "docx"], accept_multiple_files=True)
    
    if uploaded_files:
        st.info(f"Selected {len(uploaded_files)} file(s) for batch processing.")
        if st.button("Parse and Commit All Resources to System Memory"):
            progress_bar = st.progress(0)
            total_files = len(uploaded_files)
            total_chunks_saved = 0
