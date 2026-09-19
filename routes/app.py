import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
import chromadb
from routes import telemetry, analytics, auth, vision_ml, clinical_rag

# 1. Define the Lifespan Context Manager to cache connections in app.state
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("\n[LIFESPAN] 🚀 Bootstrapping Enterprise Gateway Workers...")
    
    # Initialize the local persistent ChromaDB engine on server startup
    persist_dir = os.path.join(os.getcwd(), "chroma_db_storage")
    chroma_client = chromadb.PersistentClient(path=persist_dir)
    
    # Store the pre-warmed collection pool inside the application memory state
    app.state.vector_db = chroma_client.get_or_create_collection(name="medical_device_manuals")
    print("[LIFESPAN] 💾 Local ChromaDB Persistent Vector Registry cached to RAM.")
    
    yield  # 🟢 Server is now listening and handling client requests safely
    
    # Clean up operations on server shutdown
    print("[LIFESPAN] 🛑 Shutting down enterprise lifespan gateway workers. Flushing caches...")

# 2. Instantiate the FastAPI core configuration binding the lifespan hook
app = FastAPI(
    title="HealthTech Device Telemetry Analytics Suite",
    version="2.0.0",
    description="Production-grade clinical device data streaming, validation, and analytics platform.",
    lifespan=lifespan
)

# 3. Include System Routers
app.include_router(auth.router)          
app.include_router(telemetry.router)     
app.include_router(analytics.router)     
app.include_router(vision_ml.router)     
app.include_router(clinical_rag.router)  

@app.get("/healthz", tags=["Infrastructure"])
async def infrastructure_health_check():
    return {"status": "HEALTHY", "timestamp": "2026-09-19T11:42:00Z"}
