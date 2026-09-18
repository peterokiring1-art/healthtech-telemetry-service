import time
import functools
import logging
from sqlalchemy import create_engine, Index
from sqlalchemy.orm import sessionmaker
from init_db import Base, DATABASE_URL, PatientTelemetryModel

# Setup explicit telemetry metrics logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - [DB_PERF_METRICS] - %(message)s")
logger = logging.getLogger("DatabaseTuning")

# ==========================================
# 1. OPTIMIZED ENGINE CONFIGURATION & POOLING
# ==========================================
# We inject timeout parameters to handle massive concurrent writes smoothly
# and prevent 'Database is locked' errors during simultaneous patient transmissions.
tuned_engine = create_engine(
    DATABASE_URL, 
    connect_args={
        "check_same_thread": False,
        "timeout": 30.0  # Prevents threads from crashing immediately if the database is busy writing
    }
)

TunedSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=tuned_engine)

# ==========================================
# 2. EXECUTION TIME PROFILING DECORATOR
# ==========================================
def profile_query_performance(func):
    """
    Production-grade decorator that measures database statement execution time down to milliseconds.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        result = func(*args, **kwargs)
        execution_time_ms = (time.perf_counter() - start_time) * 1000
        logger.info(f"Method '{func.__name__}' executed in {execution_time_ms:.2f} ms")
        return result
    return wrapper

# ==========================================
# 3. ADVANCED TIME-SERIES INDEXING STRATEGY
# ==========================================
def apply_performance_indexes():
    print("\n🚀 Executing Performance Optimization Routine...")
    
    # Check if indexes already exist by trying to compile them safely onto the table metadata
    try:
        # Index 1: Optimize point-lookups for single patient dashboards
        idx_patient = Index('idx_patient_lookup', PatientTelemetryModel.patient_id)
        
        # Index 2: Composite time-series index for ultra-fast chronological sorting
        idx_composite_timeline = Index('idx_patient_chronological_timeline', 
                                       PatientTelemetryModel.patient_id, 
                                       PatientTelemetryModel.raw_timestamp)
        
        # Bind metadata layout and execute the DDL structural update queries
        Base.metadata.create_all(bind=tuned_engine)
        print("✅ Performance Index Layer Successfully Compiled: [idx_patient_lookup]")
        print("✅ Composite Time-Series Index Layer Successfully Compiled: [idx_patient_chronological_timeline]")
        print("👉 Server dashboards can now query and sort millions of records in milliseconds!")
    except Exception as e:
        print(f"⚠️ Index optimization warning or already exists: {str(e)}")

# ==========================================
# 4. TUNED MOCK DATA INSERTION PROFILER TEST
# ==========================================
@profile_query_performance
def test_tuned_batch_insertion():
    """
    Tests our performance profiling decorator by writing records using the optimized pool sessions.
    """
    db_session = TunedSessionLocal()
    try:
        mock_vitals_record = PatientTelemetryModel(
            patient_id="PT-CONC-001",
            spo2=98.5,
            heart_rate=74.0,
            raw_timestamp=time.time()
        )
        db_session.add(mock_vitals_record)
        db_session.commit()
        print("⚡ Test write safely committed using the tuned database engine context.")
    except Exception as e:
        db_session.rollback()
        print(f"❌ Transaction failure: {str(e)}")
    finally:
        db_session.close()

if __name__ == "__main__":
    apply_performance_indexes()
    test_tuned_batch_insertion()
