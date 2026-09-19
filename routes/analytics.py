from fastapi import APIRouter, HTTPException
import pandas as pd
import numpy as np
from datetime import datetime

from optimize_db import TunedSessionLocal, profile_query_performance
from init_db import PatientTelemetryModel

router = APIRouter(
    prefix="/api/v1",
    tags=["Clinical Analytics Engine"]
)

@router.get("/telemetry/analytics/{patient_id}", summary="Fetch Formatted Patient Analytics & Clinical Summaries")
@profile_query_performance
def get_patient_analytics(patient_id: str):
    db_session = TunedSessionLocal()
    try:
        records = db_session.query(PatientTelemetryModel).filter(
            PatientTelemetryModel.patient_id == patient_id
        ).all()
        
        if not records:
            raise HTTPException(status_code=404, detail=f"No telemetry logs found for patient: {patient_id}")
        
        raw_data = [
            {
                "patient_id": r.patient_id,
                "spo2": r.spo2,
                "heart_rate": r.heart_rate,
                "timestamp": r.raw_timestamp
            } for r in records
        ]
        
        df = pd.DataFrame(raw_data).sort_values(by="timestamp")
        df['spo2'] = df['spo2'].ffill().fillna(98.0)
        df['heart_rate'] = df['heart_rate'].ffill().fillna(75.0)
        df['spo2'] = np.clip(df['spo2'], 0.0, 100.0)
        
        df['spo2_smoothed'] = df['spo2'].rolling(window=3, min_periods=1).mean().round(1)
        df['hr_smoothed'] = df['heart_rate'].rolling(window=3, min_periods=1).mean().round(1)
        
        df['readable_time'] = df['timestamp'].apply(
            lambda x: datetime.fromtimestamp(x).strftime('%Y-%m-%d %H:%M:%S')
        )
        
        total_alerts = int((df['spo2'] < 90).sum() + ((df['heart_rate'] < 50) | (df['heart_rate'] > 120)).sum())
        clinical_summary = {
            "overall_avg_spo2": float(df['spo2'].mean().round(1)),
            "overall_avg_heart_rate": float(df['heart_rate'].mean().round(1)),
            "monitored_duration_packets": len(df),
            "critical_anomaly_flags_raised": total_alerts,
            "clinical_status": "STABLE" if total_alerts == 0 else "ATTENTION_REQUIRED"
        }
        
        return {
            "patient_id": patient_id,
            "status": "ANALYTICS_TRANSFORMED",
            "clinical_summary_snapshot": clinical_summary,
            "data_timeline": df.to_dict(orient="records")
        }
    finally:
        db_session.close()
