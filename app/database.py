"""Database configuration and models."""

from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, JSON, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from app.config import settings

# Database setup
engine = create_engine(settings.database_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class DataSource(Base):
  """Data source configuration."""
  __tablename__ = "data_sources"
  
  id = Column(Integer, primary_key=True, index=True)
  name = Column(String(100), nullable=False)
  type = Column(String(50), nullable=False)  # log, database, api
  config = Column(JSON, nullable=False)
  is_active = Column(Boolean, default=True)
  created_at = Column(DateTime, default=datetime.utcnow)
  updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class AnalysisJob(Base):
  """Analysis job tracking."""
  __tablename__ = "analysis_jobs"
  
  id = Column(Integer, primary_key=True, index=True)
  name = Column(String(200), nullable=False)
  data_source_id = Column(Integer, nullable=False)
  status = Column(String(50), default="pending")  # pending, running, completed, failed
  config = Column(JSON, nullable=False)
  result = Column(JSON)
  error_message = Column(Text)
  created_at = Column(DateTime, default=datetime.utcnow)
  completed_at = Column(DateTime)


class Anomaly(Base):
  """Detected anomalies."""
  __tablename__ = "anomalies"
  
  id = Column(Integer, primary_key=True, index=True)
  job_id = Column(Integer, nullable=False)
  severity = Column(String(20), nullable=False)  # low, medium, high, critical
  category = Column(String(100), nullable=False)
  description = Column(Text, nullable=False)
  data = Column(JSON)
  detected_at = Column(DateTime, default=datetime.utcnow)
  resolved = Column(Boolean, default=False)


class Report(Base):
  """Generated reports."""
  __tablename__ = "reports"
  
  id = Column(Integer, primary_key=True, index=True)
  job_id = Column(Integer, nullable=False)
  title = Column(String(200), nullable=False)
  content = Column(Text, nullable=False)
  format = Column(String(20), default="html")  # html, pdf, json
  file_path = Column(String(500))
  created_at = Column(DateTime, default=datetime.utcnow)


# Create tables
Base.metadata.create_all(bind=engine)


def get_db():
  """Get database session."""
  db = SessionLocal()
  try:
    yield db
  finally:
    db.close()
