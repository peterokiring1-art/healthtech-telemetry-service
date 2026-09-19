# HealthTech Telemetry Service Gateway 📡 (Phase 2 Enterprise Capstone)

A production-grade, containerized clinical microservice framework engineered to ingest real-time biomedical time-series loops, secure transmissions using token-gated checkpoints, cleanse communication drops, and visualize smoothed tracking lines dynamically.

---

## 🏗️ System Architecture & Data Pipeline Blueprint

The platform implements an enterprise decoupled routing layout to maximize throughput under heavy concurrent loads. For the complete system architecture diagram, setup instructions, and deployment assets, please check the project repository documentation.

1. **Token Protection Layer (JWT):** Gated endpoints secure ingestion pipelines by authenticating users and edge devices via signed JSON Web Tokens using native `bcrypt` algorithms.
2. **Ingestion Core Pipeline (POST):** Asynchronous route managers capture device traffic data packets and instantly drop payloads onto thread-safe processing queues (`queue.Queue`).
3. **Decoupled Persistence Stack:** A dedicated background worker thread manages transactions to an optimized relational SQLite file pool with composite chronological indexing.
4. **Vectorized Analytics Engine (GET):** Pulls raw patient histories, employing Pandas forward-fill for sensor packet drops and NumPy clipping for signal noise suppression.
5. **Interactive Operations Center UI:** A responsive data dashboard running via Streamlit that renders live KPI summary panels and trend line graphs.

---

## 🚀 Advanced Technical Implementations
* **Lifespan Task Decoupling:** Uses FastAPI asynchronous `lifespan` context managers to orchestrate thread workers safely.
* **HIPAA-Compliant JWT Shielding:** Modular authorization filters using native `bcrypt` password compilation.
* **Population Quality Inspector:** Direct analytical testing scripts (`check_data.py`) with composite query profiling.
* **Automated Contract Matrices:** Thorough integration testing pipeline using `PyTest` modules.

---

## ⚙️ Local Development & Deployment Guide

### 1. Development Environment Initialization
```powershell
cd C:\Users\peter\OneDrive\Desktop\healthtech-telemetry-service
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process
.\venv\Scripts\activate
pip install fastapi uvicorn pydantic pandas numpy requests python-jose[cryptography] passlib bcrypt streamlit pytest httpx
```

### 2. Launching Services & Enterprise Deployment
* **Boot API Server:** `uvicorn app:app --host 127.0.0.1 --port 8080 --reload`
* **Boot Dashboard:** `streamlit run dashboard.py`
* **Run Tests:** `pytest -v .\test_app.py`
* **Docker Deployment:** `docker compose up --build`

---

## 📊 Secure Endpoints Schema
* **`POST /api/v1/auth/login`**: OAuth2PasswordRequestForm authentication endpoint returning signed bearer tokens.
* **`POST /api/v1/telemetry`**: Token-gated telemetry data ingestion endpoint.
* **`GET /api/v1/telemetry/analytics/{patient_id}`**: Retrieves formatted analytics timeline and clinical severity summaries.
