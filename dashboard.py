import streamlit as st
import device_rag_service as rag
import random
from datetime import datetime
from pypdf import PdfReader

st.set_page_config(layout="wide")
st.title("🔬 Hass Scientific & Medical Diagnostic Systems Hub")

# Comprehensive machine fleet catalog matrix
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
    
    # 📑 Enhanced Multi-File Uploader widget anchor
    uploaded_pdfs = st.file_uploader(
        f"Select Service Manual PDFs for {selected_model}", 
        type=["pdf"], 
        accept_multiple_files=True  # 👈 Enabled batch document processing
    )
    
    if uploaded_pdfs:
        st.info(f"📂 Selected {len(uploaded_pdfs)} PDF document(s) for batch processing.")
        
        if st.button("📥 Parse and Commit All PDF Documents to System Memory"):
            progress_bar = st.progress(0)
            total_files = len(uploaded_pdfs)
            
            total_chunks_saved = 0
            
            # Loop through each uploaded document in the batch array
            for file_index, pdf_file in enumerate(uploaded_pdfs):
                st.markdown(f"⏳ Processing file {file_index + 1}/{total_files}: **{pdf_file.name}**")
                try:
                    reader = PdfReader(pdf_file)
                    file_chunks = 0
                    
                    for page_num in range(len(reader.pages)):
                        page_text = reader.pages[page_num].extract_text()
                        if page_text and page_text.strip():
                            # Track chunk title by document name and page reference
                            section_label = f"[{pdf_file.name}] Page {page_num + 1}"
                            clean_content = page_text.replace("\x00", "").strip()
                            
                            rag.save_manual_chunk(selected_model, section_label, clean_content)
                            file_chunks += 1
                            total_chunks_saved += 1
                            
                    st.caption(f"✔️ Finished parsing {file_chunks} text chunks from {pdf_file.name}")
                except Exception as e:
                    st.error(f"❌ Structural extraction failure on '{pdf_file.name}': {str(e)}")
                
                # Update progress bar tracker metrics dynamically
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
    st.markdown("Log a field instrument issue below to extract step-by-step manufacturer troubleshooting resolutions.")
    
    user_model = st.selectbox("Target Instrument Profile", biomedical_fleet, key="user_model")
    serial_num = st.text_input("Machine Serial Number Matrix", value=f"SN-HASS-{random.randint(10000, 99999)}")
    error_logged = st.text_input("Enter Active System Fault Code or Critical Symptom", placeholder="e.g., E-402, ISE-CAL-FAIL, Reagent Level Low")
    
    if st.button("🔍 Query Knowledge Base For Immediate Fix"):
        if error_logged:
            with st.spinner("Scanning compiled technical service manual sheets..."):
                solutions = rag.query_device_manual(user_model, error_logged)
                
                if solutions:
                    st.success(f"💡 Found {len(solutions)} verified resolution protocol(s) within manual context documents:")
                    for title, content in solutions:
                        with st.expander(f"📖 Document Reference: {title}", expanded=True):
                            st.markdown(f"**🔧 Engineering Corrective Actions:**\n{content}")
                else:
                    st.warning(f"🔍 No exact matching entries found for '{error_logged}' on {user_model}.")
                    st.markdown(f"""
                    **💡 Baseline Field Diagnostics Checklist for {user_model}:**
                    * Inspect primary switch-mode power inputs, board voltages, and ribbon harness loops.
                    * Initiate a standard prime sequence and flush the microfluidic path or optical apertures.
                    * Verify internal pump pressures, reagent volumes, and sensor calibration curves.
                    """)
        else:
            st.error("⚠️ Empty parameter check: Please enter a symptom profile before querying.")
