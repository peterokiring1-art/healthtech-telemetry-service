import os
from sqlalchemy import create_engine, Column, Integer, Float, String, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime

# Read from environment variables (Defaulting to local if Docker variables are absent)
POSTGRES_USER = os.getenv("POSTGRES_USER", "postgres")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "postgres_secure_2026")
POSTGRES_DB = os.getenv("POSTGRES_DB", "healthtech_telemetry")
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "127.0.0.1")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")

DATABASE_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"

# PostgreSQL uses explicit connection pooling parameters natively
engine = create_engine(
    DATABASE_URL,
    pool_size=20,
    max_overflow=10,
    pool_timeout=30
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class PatientTelemetryModel(Base):
    __tablename__ = "patient_telemetry_logs"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    patient_id = Column(String(50), index=True, nullable=False)
    spo2 = Column(Float, nullable=True)
    heart_rate = Column(Float, nullable=True)
    raw_timestamp = Column(Float, nullable=False)
    recorded_at = Column(DateTime, default=datetime.utcnow)

def initialize_database_tables():
    print("🔩 Connecting to PostgreSQL Cluster and creating tables...")
    Base.metadata.create_all(bind=engine)
    print("✅ System successfully compiled 'patient_telemetry_logs' inside PostgreSQL database!")

if __name__ == "__main__":
    initialize_database_tables()
