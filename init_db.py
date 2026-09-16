import psycopg2

def create_telemetry_tables():
    print("=== Initializing Relational Telemetry Database ===")
    
    try:
        # Connect to the default PostgreSQL database instance running locally
        connection = psycopg2.connect(
            host="localhost",
            database="postgres",
            user="postgres",
            password="postgres", # Uses your master installation password
            port="5432"
        )
        
        # Open a communication pointer cursor to run commands
        cursor = connection.cursor()
        
        # 1. Create table structure for Pulse Oximeter logs
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS pulse_ox_logs (
                id SERIAL PRIMARY KEY,
                timestamp TIMESTAMPTZ NOT NULL,
                patient_id VARCHAR(50) NOT NULL,
                spo2 INT,
                heart_rate INT
            );
        """)
        
        # 2. Create table structure for ECG Monitor logs
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ecg_logs (
                id SERIAL PRIMARY KEY,
                timestamp TIMESTAMPTZ NOT NULL,
                patient_id VARCHAR(50) NOT NULL,
                lead_ii_mv NUMERIC(5, 2),
                status VARCHAR(50) DEFAULT 'UNKNOWN'
            );
        """)
        
        # Commit the transaction permanently to the system registry
        connection.commit()
        print("[SUCCESS] Relational tables 'pulse_ox_logs' and 'ecg_logs' are live.")
        
    except Exception as e:
        print(f"[DATABASE ERROR] Could not initialize tables due to: {e}")
        
    finally:
        if 'connection' in locals() and connection:
            cursor.close()
            connection.close()
            print("[INFO] Database connection closed safely.")

if __name__ == "__main__":
    create_telemetry_tables()
