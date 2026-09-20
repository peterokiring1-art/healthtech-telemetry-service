import streamlit as st
import device_rag_service as rag
import random
from datetime import datetime
from pypdf import PdfReader
from docx import Document

st.set_page_config(layout="wide", page_title="Hass Scientific Diagnostic Hub")
st.title("🔬 Hass Scientific & Medical Diagnostic Systems Hub")

# Complete machine fleet catalog matrix matching your exact inventory
biomedical_fleet = [
    "bioMérieux VITEK 2 COMPACT", "bioMérieux MINI VIDAS", "bioMérieux VIDAS KUBE",
    "Erba XL-100", "Erba XL-180", "Erba XL-200", "Erba XL-300", "Erba XL-600", "Erba XL-640", "Erba XL-1000",
    "Erba CHEM-5", "Erba CHEM-7", "Erba CHEM-Touch", "Erba Hb-Vario", "ErbaScan",
    "Erba Elite 3", "Erba Elite 5", "Erba Elite 580", "Erba H360", "Erba H560", "Erba H7100",
    "Erba ECL 760", "Erba ECL 105", "Erba ECL 412",
    "Erba Laura Smart", "Erba Laura V2 (Laura)", "Erba Laura XL",
    "Erba EC 90", "Erba Erba Lyte", "Erba EC 90 VET"
]

if "voice_text_bridge" not in st.session_state:
    st.session_state["voice_text_bridge"] = ""

user_role = st.radio(
    "🔄 Select Active System Interface Panel", 
    ["🧑‍⚕️ User / Field Technician Service Desk", "🔒 Administrator Resource Ingestion Console"],
    horizontal=True
)

# =======================================================
# 🔒 PANEL 1: ADMINISTRATOR MULTI-FORMAT INGESTION
# =======================================================
if user_role == "🔒 Administrator Resource Ingestion Console":
    st.subheader("📥 Service Manual & Asset Multi-Format Ingestion")
    st.markdown("Upload manufacturer service manuals (**PDF, DOCX**) directly into the AI database.")
    
    selected_model = st.selectbox("Target Laboratory Device Profile", biomedical_fleet, key="admin_model")
    uploaded_files = st.file_uploader(f"Select Service Manuals for {selected_model}", type=["pdf", "docx"], accept_multiple_files=True)
    
    if uploaded_files:
        if st.button("📥 Parse and Commit All Resources to System Memory"):
            progress_bar = st.progress(0)
            total_files = len(uploaded_files)
            total_chunks_saved = 0
            for file_index, file_obj in enumerate(uploaded_files):
                file_ext = file_obj.name.split(".")[-1].lower()
                try:
                    if file_ext == "pdf":
                        reader = PdfReader(file_obj)
                        for page_num in range(len(reader.pages)):
                            page_text = reader.pages[page_num].extract_text()
                            if page_text and page_text.strip():
                                label = f"[{file_obj.name}] Page {page_num + 1}"
                                rag.save_manual_chunk(selected_model, label, page_text.strip())
                                total_chunks_saved += 1
                    elif file_ext == "docx":
                        doc = Document(file_obj)
                        full_text = [para.text.strip() for para in doc.paragraphs if para.text.strip()]
                        if full_text:
                            label = f"[{file_obj.name}] Word Document Contents"
                            rag.save_manual_chunk(selected_model, label, "\n".join(full_text))
                            total_chunks_saved += 1
                except Exception as e:
                    st.error(f"❌ Failed to parse '{file_obj.name}': {str(e)}")
                progress_bar.progress((file_index + 1) / total_files)
            if total_chunks_saved > 0:
                st.success(f"📊 [SUCCESS] Processed {total_chunks_saved} chapters into knowledge tables!")

# =======================================================
# 🧑‍⚕️ PANEL 2: USER / FIELD SERVICE DIAGNOSTIC LOGS
# =======================================================
else:
    st.subheader("🛠️ Active Field Service Maintenance Log")
    st.markdown("Record a fault below via **Voice Dictation Microphone** or text query to extract an intelligent solution protocol.")
    
    col1, col2 = st.columns(2)
    with col1:
        user_model = st.selectbox("Target Instrument Profile", biomedical_fleet, key="user_model")
    with col2:
        serial_num = st.text_input("Machine Serial Number Matrix", value=f"SN-HASS-{random.randint(10000, 99999)}")
    
    lang_choice = st.selectbox("🌐 Select Your Voice Assistance Language", ["English (en-US)", "Swahili / Kiswahili (sw-KE)"])
    selected_lang_code = "en-US" if "English" in lang_choice else "sw-KE"

    st.markdown("### 🎙️ Voice Input Control Panel")
    if "voice_capture" in st.query_params:
        st.session_state["voice_text_bridge"] = st.query_params["voice_capture"]
        st.query_params.clear()
    
    st.components.v1.html(f"""
    <div style="background-color: #f0f2f6; padding: 12px; border-radius: 8px; border: 1px solid #dcdcdc; text-align: center; font-family: sans-serif;">
        <button id="mic_btn" style="background-color: #ff4b4b; color: white; border: none; padding: 10px 20px; font-size: 15px; font-weight: bold; border-radius: 5px; cursor: pointer;">
            🎤 Tap to Speak Symptom / Error
        </button>
        <p id="mic_status" style="margin-top: 8px; font-size: 13px; color: #555;">Microphone status: Idle</p>
    </div>
    <script>
        const micBtn = document.getElementById('mic_btn');
        const micStatus = document.getElementById('mic_status');
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        if (SpeechRecognition) {{
            const recognition = new SpeechRecognition();
            recognition.lang = "{selected_lang_code}";
            micBtn.onclick = function() {{ recognition.start(); micStatus.innerText = "🔊 Recording Active..."; }};
            recognition.onresult = function(event) {{
                const transcript = event.results[0][0].transcript;
                const url = new URL(window.parent.location.href);
                url.searchParams.set('voice_capture', transcript);
                window.parent.location.href = url.toString();
            }};
        }}
    </script>
    """, height=110)
    
    error_logged = st.text_input("Enter Active System Fault Code or Critical Symptom:", value=st.session_state["voice_text_bridge"])
    
    st.markdown("### 🤝 Interactive Collaborative Analysis")
    user_suggestion = st.text_area("Add Your Engineering Hypothesis / Observations (Let's analyze together):")
    
    if st.button("🔍 Run Collaborative AI Problem Analysis"):
        if error_logged:
            with st.spinner("🤖 AI Engine cross-examining databases..."):
                ai_solution = rag.query_and_analyze_fault(user_model, error_logged, user_suggestion)
                if ai_solution:
                    st.subheader("🛠️ Joint Diagnostic Engineering Report")
                    st.markdown(ai_solution)
                    
                    st.write("---")
                    st.subheader("🖼️ Generated Live Technical Repair Schematic Diagram")
                    model_upper = user_model.upper()
                    if any(x in model_upper for x in ["H5", "ELITE", "H3", "H7"]):
                        st.info("💡 Displaying Hematology Hydraulic Aperture & Fluidic Path Isolation Layout Map.")
                    elif any(x in model_upper for x in ["XL", "CHEM"]):
                        st.info("💡 Displaying Automated Chemistry Photometer Lamp Light-Path Alignment Blueprint.")
                    else:
                        st.info("💡 Displaying Advanced Microfluidic Power System Board Reference Schematic Map.")
        else:
            st.error("⚠️ Please specify an active error code before conducting analysis.")

    # =======================================================
    # 📝 THE SUCCESS LEARNING LAYER LOG INJECTION INTERFACE
    # =======================================================
    st.write("---")
    st.subheader("💾 [EXPERIENCE LOOP] Log Final Successful Fix & Train AI")
    st.markdown("Did you successfully repair this machine in the field? Record your exact solution below so the AI remembers it next time!")
    
    solved_code = st.text_input("Confirm Remedied Error Code (e.g., W-102, E-201):", key="solved_code")
    final_fix_text = st.text_area("What was the exact successful fix? (Be precise):", placeholder="e.g., Replaced the broken 12V suction solenoid valve and flushed the line with enzyme solution...")
    
    if st.button("💾 Lock Fix into AI Memory"):
        if solved_code and final_fix_text:
            rag.save_successful_fix(user_model, solved_code, final_fix_text)
            st.success(f"🎉 [AI TRAINED] Your successful field fix for {user_model} '{solved_code.upper()}' has been locked into permanent memory!")
        else:
            st.error("⚠️ Incomplete Fields: Confirm the error code and write out your successful fix text before locking.")
