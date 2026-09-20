import streamlit as st
import device_rag_service as rag
import random
from fleet_data import hospital_fleet_catalog

st.set_page_config(layout="wide", page_title="Hass Scientific Hub")

st.markdown("""
<style>
    html, body, [data-testid="stMarkdownContainer"] p, label { font-size: 22px !important; line-height: 1.6 !important; }
    .stButton>button { background-color: #007bff !important; color: white !important; font-size: 24px !important; font-weight: bold !important; width: 100% !important; padding: 14px 28px !important; border-radius: 8px !important; }
    .card-box { background-color: white; padding: 30px; border-radius: 14px; border: 1px solid #e2e8f0; margin-bottom: 25px; }
</style>
""", unsafe_allow_html=True)

if "biomedical_fleet" not in st.session_state:
    st.session_state["biomedical_fleet"] = hospital_fleet_catalog.copy()

if "voice_text_bridge" not in st.session_state:
    st.session_state["voice_text_bridge"] = ""

st.markdown('# Hass Scientific & Medical <span style="color:#007bff">Diagnostic Hub</span>', unsafe_allow_html=True)
st.markdown("---")

st.sidebar.markdown("# System Navigation")
page_selection = st.sidebar.radio("Go To Portal Page Layout:", ["Field Service Maintenance Log", "Manufacturer Document Ingestion Console", "Add New Hospital Asset Line"])

if page_selection == "Add New Hospital Asset Line":
    st.markdown('<div class="card-box">', unsafe_allow_html=True)
    st.header("Dynamic Fleet Inventory Management")
    new_machine_name = st.text_input("Enter New Hospital Equipment Designation Name:")
    if st.button("Add New Instrument to Fleet Registry"):
        if new_machine_name:
            clean_name = new_machine_name.strip()
            if clean_name not in st.session_state["biomedical_fleet"]:
                st.session_state["biomedical_fleet"].append(clean_name)
                st.session_state["biomedical_fleet"].sort()
                st.success(f"Registered '{clean_name}' successfully.")
    st.write(", ".join(st.session_state["biomedical_fleet"]))
    st.markdown('</div>', unsafe_allow_html=True)

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
                ai_solution = rag.query_and_analyze_fault(user_model, error_logged, user_suggestion)
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
                rag.save_successful_fix(user_model, solved_code, final_fix_text)
                st.success("Your field fix has been locked into permanent memory!")
    st.markdown('</div>', unsafe_allow_html=True)

else:
    st.markdown('<div class="card-box">', unsafe_allow_html=True)
    st.header("Service Manual Automated Ingestion Console")
    selected_model = st.selectbox("Target Device", st.session_state["biomedical_fleet"], key="admin_model")
    uploaded_files = st.file_uploader("Select Service Manuals", type=["pdf", "docx"], accept_multiple_files=True)
    
    if uploaded_files:
        if st.button("Parse and Ingest All Manuals to Memory"):
            progress_bar = st.progress(0)
            total_files = len(uploaded_files)
            total_chunks_saved = 0
            for file_index, file_obj in enumerate(uploaded_files):
                st.markdown(f"Ingesting: **{file_obj.name}**")
                # 🧠 CALL THE SAFE BACKEND EXTRACTION PARSER
                saved_chunks = rag.process_uploaded_file(selected_model, file_obj)
                total_chunks_saved += saved_chunks
                progress_bar.progress((file_index + 1) / total_files)
            if total_chunks_saved > 0:
                st.success(f"Processed {total_chunks_saved} data modules successfully!")
    st.markdown('</div>', unsafe_allow_html=True)
