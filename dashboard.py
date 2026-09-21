import streamlit as st
import device_rag_service as ragnor
import random
import pandas as pd
from datetime import datetime
from fleet_data import hospital_fleet_catalog

st.set_page_config(layout="wide", page_title="Hass System Hub Portal")

# Enterprise CSS Styling Injector
st.markdown("""
<style>
    html, body, [data-testid="stMarkdownContainer"] p, label { font-size: 20px !important; line-height: 1.6 !important; }
    .stButton>button { background-color: #007bff !important; color: white !important; font-size: 22px !important; font-weight: bold !important; width: 100% !important; padding: 12px 24px !important; border-radius: 8px !important; }
    .card-box { background-color: white; padding: 25px; border-radius: 12px; border: 1px solid #e2e8f0; margin-bottom: 20px; }
    .auth-container { max-width: 500px; margin: 100px auto; padding: 40px; background-color: white; border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.05); border: 1px solid #e2e8f0; }
</style>
""", unsafe_allow_html=True)

# -------------------------------------------------------
# DIRECTION 1: SECURITY GATE & GATEWAY LOGINS
# -------------------------------------------------------
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if not st.session_state["authenticated"]:
    st.markdown('<div class="auth-container">', unsafe_allow_html=True)
    st.markdown('## 🔒 Hass Engineering Gateway')
    st.markdown('Please provide corporate access credentials to authorize this terminal.')
    user_id = st.text_input("Technician Badge ID Matrix:")
    password = st.text_input("Enter Gateway Access Password:", type="password")
    
    if st.button("Authorize Session Connection"):
        # Custom authorization evaluation metrics matching your name
        if user_id.strip().upper() == "PETER" and password == "biomed2026":
            st.session_state["authenticated"] = True
            st.session_state["tech_name"] = user_id.strip().capitalize()
            st.rerun()
        else:
            st.error("Authentication Denied: Invalid parameters or badge registration signature.")
    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# Post-Authentication Initialization Checks
if "biomedical_fleet" not in st.session_state:
    st.session_state["biomedical_fleet"] = hospital_fleet_catalog.copy()

if "voice_text_bridge" not in st.session_state:
    st.session_state["voice_text_bridge"] = ""

# Master Hero Header Canvas Frame
st.markdown(f'# 🔬 Hass Scientific Hub | <span style="color:#007bff">Technician: {st.session_state["tech_name"]}</span>', unsafe_allow_html=True)
st.markdown("---")

# Main Portal Navigation Panel
st.sidebar.markdown("# System Navigation")
page_selection = st.sidebar.radio("Go To Portal Page Layout:", [
    "Field Service Maintenance Log", 
    "Planned Preventive Maintenance (PPM)", 
    "Asset Reliability Analytics",
    "Manufacturer Document Ingestion Console", 
    "Add New Hospital Asset Line"
])

# =======================================================
# PAGE 1: DYNAMIC INVENTORY REGISTER LINE MANAGER
# =======================================================
if page_selection == "Add New Hospital Asset Line":
    st.markdown('<div class="card-box">', unsafe_allow_html=True)
    st.header("Dynamic Fleet Inventory Management")
    new_machine_name = st.text_input("Enter New Hospital Equipment Model Designation Name:")
    if st.button("Add New Instrument to Fleet Registry"):
        if new_machine_name:
            clean_name = new_machine_name.strip()
            if clean_name not in st.session_state["biomedical_fleet"]:
                st.session_state["biomedical_fleet"].append(clean_name)
                st.session_state["biomedical_fleet"].sort()
                st.success(f"Registered '{clean_name}' successfully.")
    st.write(", ".join(st.session_state["biomedical_fleet"]))
    st.markdown('</div>', unsafe_allow_html=True)

# =======================================================
# PAGE 2: MAIN FIELD SERVICE TROUBLESHOOTING LOGS
# =======================================================
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
        st.markdown('<div class="card-box">', unsafe_allow_html=True)
        st.subheader("Voice Assistant Control")
        lang_choice = st.selectbox("Choose Language", ["English (en-US)", "Swahili / Kiswahili (sw-KE)"])
        selected_lang_code = "en-US" if "English" in lang_choice else "sw-KE"

        if "voice_capture" in st.query_params:
            st.session_state["voice_text_bridge"] = st.query_params["voice_capture"]
            st.query_params.clear()
        
        voice_lines = [
            '<div style="text-align: center; font-family: sans-serif;">',
            '    <button id="mic_btn" style="background-color: #ff4b4b; color: white; border: none; padding: 14px 20px; font-size: 16px; font-weight: bold; border-radius: 6px; cursor: pointer; width: 100%;">Tap to Speak Anomaly</button>',
            '    <p id="mic_status" style="margin-top: 10px; font-size: 13px; color: #666;">Status: Idle</p>',
            '</div>',
            '<script>',
            '    const micBtn = document.getElementById("mic_btn");',
            '    const micStatus = document.getElementById("mic_status");',
            '    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;',
            '    if (SpeechRecognition) {',
            '        const recognition = new SpeechRecognition();',
            '        recognition.lang = "__LANG_PLACEHOLDER__";',
            '        micBtn.onclick = function() { recognition.start(); micStatus.innerText = "Recording..."; };',
            '        recognition.onresult = function(event) {',
            '            const transcript = event.results[0][0].transcript;',
            '            const url = new URL(window.parent.location.href);',
            '            url.searchParams.set("voice_capture", transcript);',
            '            window.parent.location.href = url.toString();',
            '        };',
            '    } else { micStatus.innerText = "Microphone Blocked"; }',
            '</script>'
        ]
        voice_component_code = "\n".join(voice_lines).replace("__LANG_PLACEHOLDER__", selected_lang_code)
        st.components.v1.html(voice_component_code, height=110)
        st.markdown('</div>', unsafe_allow_html=True)
        
    with c_right:
        st.markdown('<div class="card-box">', unsafe_allow_html=True)
        st.subheader("Interactive Analysis")
        error_logged = st.text_input("Enter System Fault Code:", value=st.session_state["voice_text_bridge"])
        user_suggestion = st.text_area("Add Your Engineering Hypothesis:", height=72)
        st.markdown('</div>', unsafe_allow_html=True)
        
    if st.button("Run Collaborative AI Problem Analysis"):
        if error_logged:
            with st.spinner("AI Engine running diagnostics..."):
                ai_solution = ragnor.query_and_analyze_fault(user_model, error_logged, user_suggestion)
                if ai_solution:
                    st.info(ai_solution)
        else:
            st.error("Please enter a fault code before running analysis.")

    st.markdown('<div class="card-box" style="background-color: #edf2f7;">', unsafe_allow_html=True)
    with st.expander("Log Final Successful Fix & Train AI", expanded=False):
        solved_code = st.text_input("Confirm Error Code:")
        final_fix_text = st.text_area("What was the successful fix?:")
        if st.button("Lock Fix into AI Memory"):
            if solved_code and final_fix_text:
                ragnor.save_successful_fix(user_model, solved_code, final_fix_text)
                st.success("Your field fix has been locked into permanent memory!")
    st.markdown('</div>', unsafe_allow_html=True)

# =======================================================
# DIRECTION 2: PLANNED PREVENTIVE MAINTENANCE (PPM) LOGS
# =======================================================
elif page_selection == "Planned Preventive Maintenance (PPM)":
    st.markdown('<div class="card-box">', unsafe_allow_html=True)
    st.header("🗓️ Planned Preventive Maintenance Scheduling Board")
    st.markdown("Register upcoming inspection protocols, verification dates, and validation cycles.")
    
    col_p1, col_p2 = st.columns(2)
    with col_p1:
        ppm_model = st.selectbox("Select Asset to Calibrate:", st.session_state["biomedical_fleet"])
        ppm_serial = st.text_input("Asset Serial Number Matrix:", placeholder="e.g. SN-RAD-CT-4001")
    with col_p2:
        ppm_date = st.date_input("Target Calibration Milestone Date:", datetime.now())
        ppm_status = st.selectbox("Operational Calibration Status:", ["Scheduled", "Completed", "Overdue"])
        
    if st.button("🗓️ Commit Maintenance Window to Schedule Matrix"):
        if ppm_serial:
            ragnor.save_ppm_schedule(ppm_model, ppm_serial, str(ppm_date), st.session_state["tech_name"], ppm_status)
            st.success(f"PPM interval successfully mapped for {ppm_model} [{ppm_serial.upper()}]!")
        else:
            st.error("Missing Parameter Check: Provide asset serial code designation.")
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="card-box">', unsafe_allow_html=True)
    st.subheader("📋 Active Hospital Facility PPM Calibration Matrix")
    raw_schedules = ragnor.get_all_ppm_schedules()
