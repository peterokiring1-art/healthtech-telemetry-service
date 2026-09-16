import psycopg2

def query_inserted_records():
    print("=== Verification Query Tool ===")
    try:
        connection = psycopg2.connect(
            host="localhost", database="postgres", user="postgres", password="postgres", port="5432"
        )
        cursor = connection.cursor()
        
        # Pull everything out of your live PulseOx logs table ordered by insertion sequence
        cursor.execute("SELECT id, timestamp, patient_id, spo2, heart_rate FROM pulse_ox_logs ORDER BY id ASC;")
        records = cursor.fetchall()
        
        print(f"\n📋 FOUND {len(records)} TOTAL ENTRIES IN 'pulse_ox_logs':")
        for row in records:
            # Safely unpack the precise SQL tuple entries row by row
            row_id, timestamp, patient_id, spo2, heart_rate = row
            spo2_text = f"{spo2}%" if spo2 is not None else "None%"
            print(f"Row ID: {row_id} | Time: {timestamp} | Patient: {patient_id} | SpO2: {spo2_text} | HR: {heart_rate} bpm")
            
    except Exception as e:
        print(f"Query check stalled due to error: {e}")
    finally:
        if 'connection' in locals() and connection:
            cursor.close()
            connection.close()

if __name__ == "__main__":
    query_inserted_records()
