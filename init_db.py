import os
from sqlalchemy import create_engine, Column, Integer, Float, String, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime

# 1. Define secure local storage string path context
DATABASE_URL = "sqlite:///C:/Users/peter/OneDrive/Desktop/healthtech-telemetry-service/telemetry_storage.db"

# 2. Spin up the local transactional query storage database engine
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

# 3. Create a thread-safe custom transactional database session maker
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 4. Declarative base structure class required for tracking table mapping schemas
Base = declarative_base()

# 5. Define explicit clinical relational database table schema layout
class PatientTelemetryModel(Base):
    __tablename__ = "patient_telemetry_logs"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    patient_id = Column(String(50), index=True, nullable=False)
    spo2 = Column(Float, nullable=True)
    heart_rate = Column(Float, nullable=True)
    raw_timestamp = Column(Float, nullable=False)
    recorded_at = Column(DateTime, default=datetime.utcnow)

# 6. Database Table Initialization Handler
def initialize_database_tables():
    print("🔩 Initializing secure local relational database storage schema layer...")
    Base.metadata.create_all(bind=engine)
    print("✅ System successfully compiled 'patient_telemetry_logs' inside telemetry_storage.db!")

if __name__ == "__main__":
    initialize_database_tables()
