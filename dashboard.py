import streamlit as st
import device_rag_service as rag
import random
from datetime import datetime
from pypdf import PdfReader

st.set_page_config(layout="wide", page_title="Hass Scientific Diagnostic Hub")
st.title("🔬 Hass Scientific & Medical Diagnostic Systems Hub")

# Clean, fully closed string list array containing your exact inventory
biomedical_fleet = [
    "bioMérieux VITEK 2 COMPACT", "bioMérieux MINI VIDAS", "bioMérieux VIDAS KUBE",
    "Erba XL-100", "Erba XL-180", "Erba XL-200", "Erba XL-300", "Erba XL-600", "Erba XL-640", "Erba XL-1000",
    "Erba CHEM-5", "Erba CHEM-7", "Erba CHEM-Touch", "Erba Hb-Vario", "ErbaScan",
    "Erba Elite 3", "Erba Elite 5", "Erba Elite 580", "Erba H360", "Erba H560", "Erba H7100",
    "Erba ECL 760", "Erba ECL 105", "Erba ECL 412",
    "Erba Laura Smart", "Erba Laura V2 (Laura)", "Erba Laura XL",
    "Erba EC 90", "Erba Erba Lyte", "Erba EC 90 VET"
]

user_role = st.radio(
    "🔄 Select Active System Interface Panel", 
    ["🧑‍⚕️ User / Field Technician Service Desk", "🔒 Administrator PDF Manual Ingestion Console"],
    horizontal=True
)

# =======================================================
# 🔒 PANEL 1: ADMINISTRATOR BATCH MANUAL INGESTION
# =======================================================
if user_role == "🔒 Administrator PDF Manual Ingestion Console":
    st.subheader("📥 Service Manual Automated Batch PDF Digest Ingestion")
    st.markdown("Select a device profile to parse multiple manufacturer documents directly into AI database memory at once.")
    
    selected_model = st.selectbox("Target Laboratory Device Profile", biomedical_fleet, key="admin_model")
    
    uploaded_pdfs = st.file_uploader(
        f"Select Service Manual PDFs for {selected_model}", 
        type=["pdf"], 
        accept_multiple_files=True
    )
    
    if uploaded_pdfs:
        st.info(f"📂 Selected {len(uploaded_pdfs)} PDF document(s) for batch processing.")
        
        if st.button("📥 Parse and Commit All PDF Documents to System Memory"):
            progress_bar = st.progress(0)
            total_files = len(uploaded_pdfs)
            total_chunks_saved = 0
            
            for file_index, pdf_file in enumerate(uploaded_pdfs):
                st.markdown(f"⏳ Processing file {file_index + 1}/{total_files}: **{pdf_file.name}**")
                try:
                    reader = PdfReader(pdf_file)
                    file_chunks = 0
                    
                    for page_num in range(len(reader.pages)):
                        page_text = reader.pages[page_num].extract_text()
                        if page_text and page_text.strip():
                            # Fixed variable name mapping to pdf_file.name
                            section_label = f"[{pdf_file.name}] Page {page_num + 1}"
                            clean_content = page_text.replace("\x00", "").strip()
                            
                            rag.save_manual_chunk(selected_model, section_label, clean_content)
                            file_chunks += 1
                            total_chunks_saved += 1
                            
                    st.caption(f"✔️ Finished parsing {file_chunks} text chunks from {pdf_file.name}")
                except Exception as e:
                    st.error(f"❌ Structural extraction failure on '{pdf_file.name}': {str(e)}")
                
                progress_bar.progress((file_index + 1) / total_files)
            
            if total_chunks_saved > 0:
                st.success(f"📊 [BATCH INGESTION SUCCESS] Successfully extracted and indexed {total_chunks_saved} total pages across your documents into the local RAG matrix!")
            else:
                st.error("⚠️ Incomplete Processing: No readable text blocks could be extracted from the uploaded files.")

# =======================================================
# 🧑‍⚕️ PANEL 2: USER / FIELD SERVICE DIAGNOSTIC LOGS
# =======================================================
else:
    st.subheader("🛠️ Active Field Service Maintenance Log")
    st.markdown("Log a field instrument issue below to trigger an AI-synthesized corrective action solution protocol.")
    
    user_model = st.selectbox("Target Instrument Profile", biomedical_fleet, key="user_model")
    serial_num = st.text_input("Machine Serial Number Matrix", value=f"SN-HASS-{random.randint(10000, 99999)}")
    error_logged = st.text_input("Enter Active System Fault Code or Critical Symptom", placeholder="e.g., E-402, W-102, ISE-CAL-FAIL, Reagent Level Low")
    
    if st.button("🔍 Analyze Problem and Generate Field Solution"):
        if error_logged:
            with st.spinner("🤖 AI Engine cross-examining service manuals and synthesizing diagnostic solution..."):
                
                ai_solution = rag.query_and_analyze_fault(user_model, error_logged)
                
                if ai_solution:
                    st.subheader("🛠️ AI Diagnostic Analysis & Action Protocol")
                    st.markdown(ai_solution)
                else:
                    st.error("⚠️ System Error: Unable to compute diagnostic solution vectors.")
        else:
            st.error("⚠️ Empty parameter check: Please enter a symptom profile before querying.")
