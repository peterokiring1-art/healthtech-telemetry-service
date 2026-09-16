import psycopg2

def query_inserted_records():
    print("=== Verification Query Tool ===")
    try:
        connection = psycopg2.connect(
            host="localhost", database="postgres", user="postgres", password="postgres", port="5432"
        )
        cursor = connection.cursor()
        
        # Pull everything out of your live PulseOx logs table
        cursor.execute("SELECT * FROM pulse_ox_logs LIMIT 5;")
        records = cursor.fetchall()
        
        print(f"\n📋 FOUND {len(records)} TOTAL ENTRIES IN 'pulse_ox_logs':")
        for row in records:
            print(f"Row ID: {row[0]} | Time: {row[1]} | Patient: {row[2]} | SpO2: {row[3]}% | HR: {row[4]} bpm")
            
    except Exception as e:
        print(f"Query check stalled due to error: {e}")
    finally:
        if 'connection' in locals() and connection:
            cursor.close()
            connection.close()

if __name__ == "__main__":
    query_inserted_records()
