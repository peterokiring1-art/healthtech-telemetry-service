import psycopg2

def apply_optimization():
    try:
        # Connecting directly to the default 'postgres' database engine
        conn = psycopg2.connect(
            dbname="postgres",
            user="postgres",
            password="postgres",
            host="127.0.0.1",
            port="5432"
        )
        cursor = conn.cursor()
        
        print("⚡ Initiating database performance tuning...")
        
        # 1. Composite Index for fast time-series queries per patient
        idx_patient_time = """
        CREATE INDEX IF NOT EXISTS idx_logs_patient_time 
        ON pulse_ox_logs (patient_id, timestamp DESC);
        """
        cursor.execute(idx_patient_time)
        print("✅ Created Composite Index: (patient_id, timestamp DESC)")
        
        # 2. Partial Index for immediate retrieval of active clinical alerts
        idx_alerts = """
        CREATE INDEX IF NOT EXISTS idx_logs_low_spo2
        ON pulse_ox_logs (spo2) 
        WHERE spo2 < 90;
        """
        cursor.execute(idx_alerts)
        print("✅ Created Partial Index for critical SpO2 alerts (< 90%)")
        
        # Commit the transaction safely
        conn.commit()
        print("\n🚀 Database optimization successfully applied!")
        
    except Exception as e:
        print(f"❌ Optimization failed: {e}")
    finally:
        if 'conn' in locals() and conn:
            cursor.close()
            conn.close()

if __name__ == "__main__":
    apply_optimization()
