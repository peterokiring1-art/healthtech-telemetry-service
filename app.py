from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from routes import telemetry, analytics, auth

app = FastAPI(
    title="🏥 HealthTech Clinical Telemetry Platform Core Gateway",
    description="""
    ## Advanced Distributed Medical IoT Gateway System
    This documentation layer exposes secure interfaces designed for hospital hardware nodes.
    
    ### Core Infrastructure Layout:
    * **Authentication:** OAuth2 Signed JWT bearer tokens with native Bcrypt constraints.
    * **Broker Framework:** Event-Driven message pipelines running via distributed **RabbitMQ**.
    * **Storage Architecture:** High-throughput transactional data pooling running on **PostgreSQL**.
    * **Data Engineering Analytics:** Real-time moving trend evaluations powered by **Pandas & NumPy**.
    """,
    version="6.0.0"
)

# Root path automatic redirect straight to interactive Swagger docs
@app.get("/", include_in_schema=False)
async def redirect_to_swagger():
    return RedirectResponse(url="/docs")

# Mount separate router architectures elegantly
app.include_router(auth.router)
app.include_router(telemetry.router)
app.include_router(analytics.router)
