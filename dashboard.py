import streamlit as st
import device_rag_service as rag
import random
from datetime import datetime
from pypdf import PdfReader
from docx import Document

# 🎨 Production Configuration: Force High-Visibility Wide Layout Scale
st.set_page_config(
    layout="wide", 
    page_title="Hass Scientific Hub",
    page_icon="🔬"
)

# Custom High-Contrast CSS Theme Injector
st.markdown("""
<style>
    /* Force high-visibility global font sizing scales across the UI */
    html, body, [data-testid="stMarkdownContainer"] p, label {
        font-size: 22px !important;
        line-height: 1.6 !important;
        color: #1e293b !important;
    }
    .stButton>button {
        background-color: #007bff !important;
        color: white !important;
        border-radius: 8px !important;
        padding: 14px 28px !important;
        font-size: 24px !important;
        font-weight: bold !important;
        border: none !important;
        width: 100% !important;
        box-shadow: 0 4px 6px rgba(0,0,0,0.08);
        transition: background-color 0.2s ease;
    }
    .stButton>button:hover { background-color: #0056b3 !important; }
    .card-box {
        background-color: white;
        padding: 30px;
        border-radius: 14px;
        border: 1px solid #e2e8f0;
        box-shadow: 0 4px 12px rgba(0,0,0,0.03);
        margin-bottom: 25px;
    }
    .stTextArea textarea, .stTextInput input, .stSelectbox div {
        font-size: 20px !important;
    }
    h1 { font-size: 46px !important; font-weight: 800 !important; color: #0f172a !important; }
    h2 { font-size: 34px !important; font-weight: 700 !important; color: #1e293b !important; }
    h3 { font-size: 28px !important; font-weight: 600 !important; color: #334155 !important; }
</style>
""", unsafe_allow_html=True)

# Shared comprehensive machine fleet catalog matrix
biomedical_fleet = [
    "Erba XL-100", "Erba XL-180", "Erba XL-200", "Erba XL-300", "Erba XL-600", "Erba XL-640", "Erba XL-1000",
    "Erba CHEM-5", "Erba CHEM-7", "Erba CHEM-Touch", "Erba Hb-Vario", "ErbaScan",
    "Erba Elite 3", "Erba Elite 5", "Erba Elite 580", "Erba H360", "Erba H560", "Erba H7100",
    "Erba ECL 760", "Erba ECL 105", "Erba ECL 412",
    "Erba Laura Smart", "Erba Laura V2 (Laura)", "Erba Laura XL",
    "Erba EC 90", "Erba Erba Lyte", "Erba EC 90 VET",
    "bioMérieux VITEK 2 COMPACT", "bioMérieux MINI VIDAS", "bioMérieux VIDAS KUBE"
]

if "voice_text_bridge" not in st.session_state:
    st.session_state["voice_text_bridge"] = ""

# 🏛️ Master Brand Header
st.markdown('# 🔬 Hass Scientific & Medical <span style="color:#007bff">Diagnostic Hub</span>', unsafe_allow_html=True)
st.markdown('### *Clinical AI Knowledge Gateway & Field Service Engineering Terminal*')
st.markdown("---")

# 🎛️ Multipage Architecture: Isolated Sidebar Navigation System
st.sidebar.markdown("# 🧭 System Navigation")
page_selection = st.sidebar.radio(
    "Go To Portal Page Layout:",
    ["🧑‍⚕️ Field Service Maintenance Log", "🔒 Manufacturer Document Ingestion Console"]
)

# =======================================================
# PAGE 1: USER / FIELD SERVICE DIAGNOSTIC LOGS
# =======================================================
if page_selection == "🧑‍⚕️ Field Service Maintenance Log":
    st.markdown('<div class="card-box">', unsafe_allow_html=True)
    st.header("🛠️ Active Instrument Diagnosis Panel")
    st.markdown("Record a fault below via **Voice Dictation Microphone** or text query to extract a prioritized fix.")
    
    col1, col2 = st.columns(2)
    with col1:
        user_model = st.selectbox("Target Instrument Profile", biomedical_fleet, key="user_model")
    with col2:
        serial_num = st.text_input("Machine Serial Number Matrix", value=f"SN-HASS-{random.randint(10000, 99999)}")
    st.markdown('</div>', unsafe_allow_html=True)
    
    c_left, c_right = st.columns(2)
    with c_left:
        st.markdown('<div class="card-box" style="height:100%;">', unsafe_allow_html=True)
        st.subheader("🎙️ Voice Assistant Control")
        lang_choice = st.selectbox("Choose Dictation Language", ["English (en-US)", "Swahili / Kiswahili (sw-KE)"])
        selected_lang_code = "en-US" if "English" in lang_choice else "sw-KE"

        if "voice_capture" in st.query_params:
            st.session_state["voice_text_bridge"] = st.query_params["voice_capture"]
            st.query_params.clear()
        
        voice_lines = [
            '<div style="text-align: center; font-family: sans-serif; padding-top: 5px;">',
            '    <button id="mic_btn" style="background-color: #ff4b4b; color: white; border: none; padding: 14px 20px; font-size: 16px; font-weight: bold; border-radius: 6px; cursor: pointer; width: 100%;">',
            '        🎤 Tap to Speak Anomaly',
            '    </button>',
            '    <p id="mic_status" style="margin-top: 10px; font-size: 13px; color: #666; font-weight:500;">Status: Idle</p>',
            '</div>',
            '<script>',
            '    const micBtn = document.getElementById("mic_btn");',
            '    const micStatus = document.getElementById("mic_status");',
            '    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;',
            '    if (SpeechRecognition) {',
            '        const recognition = new SpeechRecognition();',
            '        recognition.lang = "__LANG_PLACEHOLDER__";',
            '        micBtn.onclick = function() { recognition.start(); micStatus.innerText = "Recording Active... Speak Clearly."; micStatus.style.color = "#ff4b4b"; };',
            '        recognition.onresult = function(event) {',
            '            const transcript = event.results[0][0].transcript;',
            '            const url = new URL(window.parent.location.href);',
            '            url.searchParams.set("voice_capture", transcript);',
            '            window.parent.location.href = url.toString();',
            '        };',
            '    } else {',
            '        micStatus.innerText = "❌ Microphone API Restricted";',
            '    }',
            '</script>'
        ]
        voice_component_code = "\n".join(voice_lines).replace("__LANG_PLACEHOLDER__", selected_lang_code)
        st.components.v1.html(voice_component_code, height=110)
        st.markdown('</div>', unsafe_allow_html=True)
        
    with c_right:
        st.markdown('<div class="card-box" style="height:100%;">', unsafe_allow_html=True)
        st.subheader("🤝 Interactive Collaborative Analysis")
        error_logged = st.text_input("Enter Active System Fault Code or Critical Symptom:", value=st.session_state["voice_text_bridge"])
        user_suggestion = st.text_area("Add Your Engineering Hypothesis / Observations:", height=72)
        st.markdown('</div>', unsafe_allow_html=True)
        
    st.markdown('<div style="margin: 25px 0px;">', unsafe_allow_html=True)
    run_analysis = st.button("🔍 Run Collaborative AI Problem Analysis")
    st.markdown('</div>', unsafe_allow_html=True)

    if run_analysis:
        if error_logged:
            with st.spinner("🤖 AI Engine cross-examining compiled knowledge layers..."):
                ai_solution = rag.query_and_analyze_fault(user_model, error_logged, user_suggestion)
                if ai_solution:
                    # 💡 HIDDEN DETAILS STRATEGY: Placed inside expandable layouts for a cleaner presentation view
                    with st.expander("📊 View AI Diagnostic Analysis Report & Corrective Protocols", expanded=True):
                        st.markdown(ai_solution)
                    
                    with st.expander("🖼️ View Generated Live Technical Repair Schematic Blueprint", expanded=True):
                        model_upper = user_model.upper()
                        if any(x in model_upper for x in ["H360", "H560", "H7100", "ELITE"]):
                            st.success("💡 System Identity: Hematology Hydraulic Aperture & Fluidic Path Isolation Layout Map.")
                        elif any(x in model_upper for x in ["XL", "CHEM"]):
                            st.success("💡 System Identity: Automated Chemistry Photometer Lamp Light-Path Alignment Blueprint.")
                        elif any(x in model_upper for x in ["EC", "LYTE"]):
                            st.success("💡 System Identity: Automated Electrolyte Analyzer ISE Reference Voltage Board Blueprint Mapping.")
                        else:
                            st.success("💡 System Identity: Advanced Microfluidic Power System Board Reference Schematic Map.")
        else:
            st.error("Please specify an active error code before conducting analysis.")

    # =======================================================
    # EXPERIENCE LEARNING LOOP (COLLAPSED EXPANDER)
    # =======================================================
    st.markdown('<div class="card-box" style="background-color: #edf2f7; border: 1px dashed #cbd5e0;">', unsafe_allow_html=True)
    with st.expander("💾 [EXPERIENCE LOOP] Log Final Successful Fix & Train AI", expanded=False):
        st.subheader("Train the AI Memory Node")
        st.markdown("Record your successful field fix below so the AI remembers it next time!")
        
        col_s1, col_s2 = st.columns(2)
        with col_s1:
            solved_code = st.text_input("Confirm Remedied Error Code:", key="solved_code")
        with col_s2:
            final_fix_text = st.text_area("What was the exact successful fix? (Be precise):")
        
        if st.button("💾 Lock Fix into AI Memory"):
            if solved_code and final_fix_text:
                rag.save_successful_fix(user_model, solved_code, final_fix_text)
                st.success(f"🎉 [AI TRAINED] Your successful field fix for {user_model} '{solved_code.upper()}' has been locked into permanent memory!")
            else:
                st.error("⚠️ Incomplete Fields: Confirm parameters before logging.")
