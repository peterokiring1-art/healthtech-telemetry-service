from fastapi import FastAPI
from routes import telemetry, analytics, auth, vision_ml, clinical_rag

# Initialize the Enterprise Telemetry Gateway Application
app = FastAPI(
    title="HealthTech Device Telemetry Analytics Suite",
    version="2.0.0",
    description="Production-grade clinical device data streaming, validation, and analytics platform."
)

# Register Global Phase 1, Phase 2, and Phase 3 Core Routes
app.include_router(auth.router)          
app.include_router(telemetry.router)     
app.include_router(analytics.router)     
app.include_router(vision_ml.router)     
app.include_router(clinical_rag.router)  

@app.get("/healthz", tags=["Infrastructure"])
async def infrastructure_health_check():
    return {"status": "HEALTHY", "timestamp": "2026-09-19T11:09:00Z"}
