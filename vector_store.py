import os
import chromadb
from langchain_text_splitters import RecursiveCharacterTextSplitter

def initialize_persistent_vector_store():
    print("📁 Initializing Production-Grade Persistent ChromaDB Architecture...")
    
    # 1. Establish a dedicated local workspace folder for persistent disk synchronization
    # This prevents the database from wiping clean when the app cycle reloads.
    persist_dir = os.path.join(os.getcwd(), "chroma_db_storage")
    chroma_client = chromadb.PersistentClient(path=persist_dir)
    
    # 2. Allocate or establish a distinct text collection vector table
    # Chroma utilizes an internal default sentence-transformer embedding model (all-MiniLM-L6-v2)
    collection = chroma_client.get_or_create_collection(name="medical_device_manuals")
    
    # 3. Pull technical manual payload context matching your rag_preprocessor layout
    manual_document = (
        "HEALTH-TECH MEDICAL SYSTEMS: VENTILATOR MODEL X90 - TECHNICAL MANUAL\n"
        "[CRITICAL ALERT]: If the ventilator sensor array flags Error Code E-402, it indicates "
        "a critical pressure differential imbalance within the primary oxygen delivery manifold. "
        "Technicians must immediately check the backup regulator valves to prevent delivery failure.\n\n"
        "Step 2.1: Power down the diagnostic auxiliary node entirely before detaching the patient line. "
        "Step 2.2: Attach a calibrated reference flow analyzer gauge directly to the primary output port. "
        "Step 2.3: Boot the device into engineering maintenance mode by holding down the auxiliary button."
    )
    
    # 4. Apply optimized character segmenting logic
    splitter = RecursiveCharacterTextSplitter(chunk_size=350, chunk_overlap=50)
    document_chunks = splitter.split_text(manual_document)
    
    # 5. Populate the vector index with explicit structural tracking boundaries
    print(f" -> Mapping and indexing {len(document_chunks)} text segments into persistent storage...")
    
    # Format list collections matching input matrices requirements
    chunk_ids = [f"doc_chunk_x90_{idx}" for idx in range(len(document_chunks))]
    chunk_metadata = [{"source": "ventilator_x90_manual.txt", "classification": "restricted_technical"} for _ in document_chunks]
    
    collection.add(
        documents=document_chunks,
        ids=chunk_ids,
        metadatas=chunk_metadata
    )
    print(" ✅ Persistent database storage tracking array successfully synced.")

    # 6. Execute a cross-reference semantic similarity matrix test query
    # We query using completely different vocabulary terms to prove coordinate overlap mapping works.
    target_query = "What is the troubleshooting step for gas delivery failures?"
    print(f"\n🔍 PROCESSING SEMANTIC RETRIEVAL MATRIX QUERY: '{target_query}'")
    
    query_response = collection.query(
        query_texts=[target_query],
        n_results=1  # Pull down only the single closest cosine-proximity text matches
    )
    
    # Extract structural return bounds
    extracted_text_block = query_response['documents'][0]
    extracted_id_marker = query_response['ids'][0]
    
    print("=" * 85)
    print(f"🎯 HIGHEST SEMANTIC CORESIDENCE ISOLATED ({extracted_id_marker}):")
    print(extracted_text_block)
    print("=" * 85)

if __name__ == "__main__":
    initialize_persistent_vector_store()
