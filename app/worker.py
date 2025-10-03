"""Celery worker for background tasks."""

from celery import Celery
from app.config import settings
from app.database import SessionLocal
from app.data_connectors.factory import DataConnectorFactory
from app.agents.anomaly_detector import AnomalyDetectorAgent
from app.reports.factory import ReportGeneratorFactory
from app.reports.base import ReportData
from datetime import datetime, timedelta
import asyncio

# Create Celery app
celery_app = Celery(
  "llm_pipeline",
  broker=settings.redis_url,
  backend=settings.redis_url
)

celery_app.conf.update(
  task_serializer="json",
  accept_content=["json"],
  result_serializer="json",
  timezone="UTC",
  enable_utc=True,
)


@celery_app.task
def run_analysis_job(job_id: int):
  """Run analysis job as Celery task."""
  db = SessionLocal()
  
  try:
    # Get job
    job = db.query(AnalysisJob).filter(AnalysisJob.id == job_id).first()
    if not job:
      return {"status": "failed", "error": "Job not found"}
    
    # Update status
    job.status = "running"
    db.commit()
    
    # Get data source
    data_source = db.query(DataSource).filter(DataSource.id == job.data_source_id).first()
    if not data_source:
      job.status = "failed"
      job.error_message = "Data source not found"
      db.commit()
      return {"status": "failed", "error": "Data source not found"}
    
    # Create connector
    connector = DataConnectorFactory.create_connector(
      data_source.type,
      data_source.config
    )
    
    # Fetch data
    end_time = datetime.utcnow()
    start_time = end_time - timedelta(hours=24)  # Last 24 hours
    
    data = list(connector.fetch_data(start_time, end_time))
    
    # Create anomaly detector
    detector = AnomalyDetectorAgent({
      "llm_provider": "openai",
      "sensitivity": "medium"
    })
    
    # Analyze data
    result = asyncio.run(detector.analyze(data))
    
    # Save anomalies
    for anomaly in result.anomalies:
      db_anomaly = Anomaly(
        job_id=job_id,
        severity=anomaly.severity,
        category=anomaly.category,
        description=anomaly.description,
        data=anomaly.data,
        confidence=anomaly.confidence
      )
      db.add(db_anomaly)
    
    # Update job status
    job.status = "completed"
    job.result = {
      "anomalies_count": len(result.anomalies),
      "summary": result.summary,
      "metrics": result.metrics
    }
    job.completed_at = datetime.utcnow()
    db.commit()
    
    return {
      "status": "completed",
      "anomalies_count": len(result.anomalies),
      "summary": result.summary
    }
    
  except Exception as e:
    # Update job status
    job.status = "failed"
    job.error_message = str(e)
    db.commit()
    return {"status": "failed", "error": str(e)}
  
  finally:
    db.close()


@celery_app.task
def generate_report_task(job_id: int, format: str = "html"):
  """Generate report as Celery task."""
  db = SessionLocal()
  
  try:
    # Get job
    job = db.query(AnalysisJob).filter(AnalysisJob.id == job_id).first()
    if not job:
      return {"status": "failed", "error": "Job not found"}
    
    # Get anomalies for this job
    anomalies = db.query(Anomaly).filter(Anomaly.job_id == job_id).all()
    
    # Create report data
    report_data = ReportData(
      title=f"Analysis Report for {job.name}",
      summary=f"Analysis completed with {len(anomalies)} anomalies detected",
      anomalies=[anomaly.__dict__ for anomaly in anomalies],
      metrics={"total_anomalies": len(anomalies)},
      recommendations=["Review detected anomalies", "Implement monitoring"],
      generated_at=datetime.utcnow(),
      data_source="Unknown",
      analysis_period={"start": "2024-01-01", "end": "2024-01-02"}
    )
    
    # Generate report
    generator = ReportGeneratorFactory.create_generator(format, {})
    content = asyncio.run(generator.generate_report(report_data))
    
    # Save report
    report = Report(
      job_id=job_id,
      title=report_data.title,
      content=content,
      format=format
    )
    db.add(report)
    db.commit()
    db.refresh(report)
    
    return {
      "status": "completed",
      "report_id": report.id,
      "format": format
    }
    
  except Exception as e:
    return {"status": "failed", "error": str(e)}
  
  finally:
    db.close()


if __name__ == "__main__":
  celery_app.start()
