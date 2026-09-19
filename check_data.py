import pandas as pd
from sqlalchemy import func
from init_db import PatientTelemetryModel
from optimize_db import TunedSessionLocal, profile_query_performance

@profile_query_performance
def run_clinical_database_audit():
    print("=== Phase 1: Establishing Direct SQL Connection Pool ===")
    db_session = TunedSessionLocal()
    
    try:
        # 1. Fetch total entry metric count across the entire table
        total_records = db_session.query(PatientTelemetryModel).count()
        print(f"📊 Total Persistent Packets Registered in SQL Table: {total_records}")
        
        if total_records == 0:
            print("⚠️ The database table is currently empty. Run your simulator client first!")
            return

        # 2. Extract every single record into a Pandas DataFrame for heavy analytical slicing
        print("\n=== Phase 2: Ingesting Raw Disk Tables into Pandas DataFrame ===")
        query_stmt = db_session.query(PatientTelemetryModel).statement
        df = pd.read_sql(query_stmt, db_session.bind)
        
        print(f"Successfully vectorized {len(df)} database records.")

        print("\n=== Phase 3: Cross-Patient Population Clinical Insights ===")
        
        # 3. Pull extreme boundary anomalies across the entire device network
        min_spo2 = df['spo2'].min()
        max_hr = df['heart_rate'].max()
        mean_hr = df['heart_rate'].mean()
        
        print(f"🚨 Lowest SpO2 reading captured across population: {min_spo2:.1f}%")
        print(f"❤️ Highest Heart Rate captured across population: {max_hr:.1f} BPM")
        print(f"📈 Mean population baseline Heart Rate: {mean_hr:.1f} BPM")

        print("\n=== Phase 4: Breakdown Summary Per Patient Node ===")
        # 4. Group data by patient_id to calculate packet distributions and average metrics
        patient_groups = df.groupby('patient_id').agg(
            total_transmissions=('id', 'count'),
            avg_spo2=('spo2', 'mean'),
            avg_heart_rate=('heart_rate', 'mean')
        ).round(1)
        
        print(patient_groups)
        print("\n=======================================================")
        
    except Exception as e:
        print(f"❌ Database audit failure occurred: {str(e)}")
    finally:
        db_session.close()

if __name__ == "__main__":
    print("📡 Launching Production-Grade Clinical Database Inspector Tool...")
    run_clinical_database_audit()
