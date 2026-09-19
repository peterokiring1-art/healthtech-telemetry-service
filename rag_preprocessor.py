import os
import json
from langchain_text_splitters import RecursiveCharacterTextSplitter

def generate_mock_device_manual(filename="device_service_manual.txt"):
    """
    Synthesizes a technical medical equipment document containing
    structured maintenance procedures and strict FDA safety compliance markers.
    """
    manual_content = (
        "HEALTH-TECH MEDICAL SYSTEMS: VENTILATOR MODEL X90 - TECHNICAL MANUAL\n"
        "SECTION 1: SYSTEM ERROR CODES AND CRITICAL FAULT INITIALIZATION\n\n"
        "[CRITICAL ALERT]: If the ventilator sensor array flags Error Code E-402, it indicates "
        "a critical pressure differential imbalance within the primary oxygen delivery manifold. "
        "Technicians must immediately check the backup regulator valves to prevent delivery failure.\n\n"
        "SECTION 2: STEP-BY-STEP CALIBRATION ALTERNATIVES AND PROTOCOLS\n"
        "Step 2.1: Power down the diagnostic auxiliary node entirely before detaching the patient line. "
        "Step 2.2: Attach a calibrated reference flow analyzer gauge directly to the primary output port. "
        "Step 2.3: Boot the device into engineering maintenance mode by holding down the auxiliary button. "
        "Confirm that the pressure sensors register exactly 0.00 kPa (+/- 0.02) baseline value.\n\n"
        "SECTION 3: HIPAA COMPLIANCE AND PATIENT LOG RECORDING GATEWAY\n"
        "All telemetry streams generated during maintenance calibration cycles must be fully de-identified "
        "before transmission to the centralized database storage infrastructure. Explicit identifiers like "
        "patient names, matching registration IDs, and localized timestamps must be cleared to maintain absolute compliance."
    )
    
    with open(filename, "w", encoding="utf-8") as f:
        f.write(manual_content)
    print(f"📦 Successfully synthesized technical clinical guide: '{filename}'")

def execute_semantic_chunking(input_filename):
    """
    Loads raw medical manual documentation and intelligently segments it
    using adaptive character chunk borders to maintain semantic consistency.
    """
    if not os.path.exists(input_filename):
        raise FileNotFoundError(f"Missing manual target file: {input_filename}")
        
    with open(input_filename, "r", encoding="utf-8") as f:
        raw_text = f.read()

    # Define the smart chunking parameters
    # chunk_size: Max length of individual text blocks
    # chunk_overlap: Shared character window to preserve sentence context across cuts
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=300,
        chunk_overlap=50,
        separators=["\n\n", "\n", ". ", " ", ""]
    )

    # Perform the semantic text splits
    document_chunks = splitter.split_text(raw_text)
    
    print("\n📊 RAG INGESTION SEGMENTATION REPORT:")
    print(f" -> Total Characters in Original Document: {len(raw_text)}")
    print(f" -> Isolated Semantic Text Chunks Formatted: {len(document_chunks)}")
    print("=" * 70)

    # Evaluate the structural integrity of each chunk
    for idx, chunk in enumerate(document_chunks, 1):
        print(f"🧩 CHUNK #{idx} (Length: {len(chunk)} characters):")
        # Indent content visually for terminal review
        indented_text = "\n".join(f"   | {line}" for line in chunk.splitlines())
        print(indented_text)
        print("-" * 70)

if __name__ == "__main__":
    target_manual = "device_service_manual.txt"
    
    # Run the pipeline
    generate_mock_device_manual(target_manual)
    execute_semantic_chunking(target_manual)
    
    # Clean up local scratch workspace file
    if os.path.exists(target_manual):
        os.remove(target_manual)
