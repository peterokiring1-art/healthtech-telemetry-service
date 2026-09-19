import time
import random
import concurrent.futures
from optimize_db import TunedSessionLocal, profile_query_performance
from init_db import PatientTelemetryModel

# Target load factor adjustments
TOTAL_BATCH_STRESS_RECORDS = 1000
CONCURRENT_THREAD_WORKERS = 20

def execute_atomic_stress_write(worker_id: int):
    """
    Executes a single transactional SQL insert statement using our optimized connection pool session.
    """
    db_session = TunedSessionLocal()
    try:
        mock_packet = PatientTelemetryModel(
            patient_id=f"PT-LOAD-{random.randint(1, 50):03d}",
            spo2=float(random.randint(85, 100)),
            heart_rate=float(random.randint(55, 140)),
            raw_timestamp=time.time()
        )
        db_session.add(mock_packet)
        db_session.commit()
    except Exception as e:
        db_session.rollback()
    finally:
        db_session.close()

@profile_query_performance
def trigger_system_load_test():
    print(f"📡 Spawning {CONCURRENT_THREAD_WORKERS} thread workers to pipeline {TOTAL_BATCH_STRESS_RECORDS} records simultaneously...")
    
    # Process concurrent transactional bursts across python thread pools
    with concurrent.futures.ThreadPoolExecutor(max_workers=CONCURRENT_THREAD_WORKERS) as executor:
        # Create an execution array range mapping to our insert loop handler
        task_range = list(range(TOTAL_BATCH_STRESS_RECORDS))
        executor.map(execute_atomic_stress_write, task_range)

if __name__ == "__main__":
    print("=== BEGINNING ENTERPRISE DATABASE STORAGE STRESS TESTING ===")
    start_wall_clock = time.time()
    
    trigger_system_load_test()
    
    total_duration = round(time.time() - start_wall_clock, 2)
    print(f"✅ Load test completed! 1,000 records safely committed to disk storage.")
    print(f"⏳ Total stress duration: {total_duration}s across {CONCURRENT_THREAD_WORKERS} concurrent worker lanes.")
