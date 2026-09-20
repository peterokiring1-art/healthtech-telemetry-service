import streamlit as st
import device_rag_service as rag
import random
from datetime import datetime
from pypdf import PdfReader

st.set_page_chart_config = {"layout": "wide"}
st.title("🔬 Hass Scientific & Medical Diagnostic Systems Hub")

# Shared comprehensive fleet array containing your complete product catalog matrix
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
# 🔒 PANEL 1: ADMINISTRATOR AUTOMATED MANUAL INGESTION
# =======================================================
if user_role == "🔒 Administrator PDF Manual Ingestion Console":
    st.subheader("📥 Service Manual Automated PDF Digest Ingestion")
    st.markdown("Select a device profile to parse manufacturer documentation directly into AI database memory.")
    
    selected_model = st.selectbox("Target Laboratory Device Profile", biomedical_fleet, key="admin_model")
    uploaded_pdf = st.file_uploader(f"Select Service Manual PDF for {selected_model}", type=["pdf"])
    
    if uploaded_pdf is not None:
        if st.button("📥 Parse and Commit PDF Document to System Memory"):
            with st.spinner("Extracting and compiling document text components..."):
                try:
                    reader = PdfReader(uploaded_pdf)
                    total_pages = len(reader.pages)
                    
                    chunks_saved = 0
                    for page_num in range(total_pages):
                        page_text = reader.pages[page_num].extract_text()
                        if page_text and page_text.strip():
                            section_label = f"Page {page_num + 1} of Manual Document"
                            clean_content = page_text.replace("\x00", "").strip()
                            rag.save_manual_chunk(selected_model, section_label, clean_content)
                            chunks_saved += 1
                    
                    if chunks_saved > 0:
                        st.success(f"📊 [INGESTION SUCCESS] Extracted and digested {chunks_saved} operational chunks for {selected_model} successfully!")
                    else:
                        st.error("⚠️ Extraction Failure: No readable text found. Verify the document is not an image-only scan.")
                except Exception as e:
                    st.error(f"❌ Structural extraction failure: {str(e)}")

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
