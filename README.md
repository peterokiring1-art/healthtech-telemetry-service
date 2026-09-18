# HealthTech Telemetry Service Gateway 📡 (Phase 1 Capstone)

A production-ready, concurrent microservice designed to ingest real-time clinical IoT biomedical streams (e.g., Pulse Oximeter telemetry), cleanse transmission anomalies on the fly, and serve smoothed physiological trends via optimized RESTful endpoints.

Built as part of an accelerated 3-week advanced backend software sprint.

---

## 🏗️ System Architecture & Data Pipeline Blueprint

The microservice decouples the ingestion layer from the analytics layer to ensure massive system throughput under heavy concurrent loads.

```text
[ 10 Concurrent Patients ]
         │ (Simultaneous IoT Hardware Transmissions)
         ▼
 ┌───────────────┐
 │ FastAPI App   │ ──► [ Threshold Alert Guard ] ──► (Terminal Flagging)
 └───────────────┘
         │
         ├───► [ Fast Write Memory Cache Array ] ──► [ Pandas / NumPy Cleansing Engine ]
         │                                                        │ (ffill + np.clip)
         ▼                                                        ▼
 ┌───────────────┐                                     ┌──────────────────────┐
 │ Thread Queue  │ ──► [ Async Background Worker ]     │  GET /analytics UI   │
 └───────────────┘                                     └──────────────────────┘
```

1. **Ingestion Layer (POST):** Asynchronous API endpoint handles concurrent device data packets, validates constraints using Pydantic, filters instant threshold hazards, and drops payloads into a safe internal queue thread.
2. **Analytics Engine (GET):** Reads raw, time-series metrics. Uses **Pandas** to forward-fill (`ffill`) missing transmission packets and **NumPy** to clip hardware boundary spikes, outputting a 3-period rolling moving average for clinical dashboards.

---

## 🚀 Technical Core Accomplishments
* **FastAPI Concurency:** Built fully decoupled background task worker threads via `queue.Queue` to handle complex multi-device loads without slowing down the active API.
* **Pydantic Structural Contracts:** Implemented rigorous data parsing contracts ensuring clinical integers (`spo2`, `heart_rate`) conform exactly to physical parameters.
* **Vectorized Data Science Cleansing:** Replaced slow loop algorithms with high-performance Pandas and NumPy processing pipelines to address data gaps and sensor noise.

---

## ⚙️ Local Development & Deployment Guide

### 1. Prerequisites & Environment Initialization
Ensure you are using Python 3.11+ on a Windows environment. Execute the terminal startup sequence to initialize isolates and packages:

```powershell
# Navigate into the service root directory
cd C:\Users\peter\OneDrive\Desktop\healthtech-telemetry-service

# Configure PowerShell policy access and activate the environment
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process
.\venv\Scripts\activate

# Install essential dependencies
pip install fastapi uvicorn pydantic pandas numpy requests
```

### 2. Booting the Application Gateway Server
Launch the asynchronous Uvicorn worker bound to your explicit local configurations:
```powershell
uvicorn app:app --host 127.0.0.1 --port 8080 --reload
```
*Verify gateway initialization via the interactive visual interface portal at:* `http://localhost:8080/docs`

### 3. Launching the Multi-Patient Concurrent Simulator
In a separate terminal tab (with the virtual environment activated), trigger the simultaneous device client script:
```powershell
python .\simulate_client.py
```

### 4. Fetching Real-time Transformed Data Logs
Query the production analytics engine directly from the command line tool to parse the results:
```powershell
Invoke-RestMethod http://localhost:8080/api/v1/telemetry/analytics/PT-CONC-001
```

---

## 📊 Endpoints Schema

### 📤 1. Ingest Telemetry
* **Route:** `POST /api/v1/telemetry`
* **Payload Type:** `application/json`
* **Sample Request:**
```json
{
  "patient_id": "PT-CONC-001",
  "spo2": 97.0,
  "heart_rate": 72.0,
  "timestamp": 1789712000.0
}
```

### 📥 2. Retrieve Cleaned Analytics
* **Route:** `GET /api/v1/telemetry/analytics/{patient_id}`
* **Response Type:** `application/json`
* **Status Returned:** `ANALYTICS_TRANSFORMED` (Includes missing value interpolation & smoothed moving average values).
