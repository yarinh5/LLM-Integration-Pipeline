"""Main FastAPI application."""

from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
import os
from datetime import datetime, timedelta

from app.config import settings
from app.database import get_db, DataSource, AnalysisJob, Anomaly, Report
from app.data_connectors.factory import DataConnectorFactory
from app.llm.factory import LLMProviderFactory
from app.llm.manager import LLMManager
from app.agents.anomaly_detector import AnomalyDetectorAgent
from app.reports.factory import ReportGeneratorFactory
from app.reports.base import ReportData

# Create FastAPI app
app = FastAPI(
  title="LLM Integration Pipeline",
  description="AI-powered data analysis and anomaly detection pipeline",
  version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
  CORSMiddleware,
  allow_origins=["*"],
  allow_credentials=True,
  allow_methods=["*"],
  allow_headers=["*"],
)

# Mount static files
if not os.path.exists("static"):
  os.makedirs("static")
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/", response_class=HTMLResponse)
async def dashboard():
  """Main dashboard page."""
  return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>LLM Integration Pipeline Dashboard</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            color: #333;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }
        
        .header {
            text-align: center;
            margin-bottom: 40px;
            color: white;
        }
        
        .header h1 {
            font-size: 3rem;
            margin-bottom: 10px;
            font-weight: 700;
            text-shadow: 0 2px 4px rgba(0,0,0,0.3);
        }
        
        .header p {
            font-size: 1.2rem;
            opacity: 0.9;
        }
        
        .dashboard-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 30px;
            margin-bottom: 40px;
        }
        
        .card {
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            padding: 30px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
            border: 1px solid rgba(255, 255, 255, 0.2);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }
        
        .card:hover {
            transform: translateY(-5px);
            box-shadow: 0 12px 40px rgba(0, 0, 0, 0.15);
        }
        
        .card h2 {
            color: #2c3e50;
            margin-bottom: 20px;
            font-size: 1.5rem;
            font-weight: 600;
        }
        
        .card p {
            color: #7f8c8d;
            line-height: 1.6;
            margin-bottom: 20px;
        }
        
        .btn {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 25px;
            font-size: 1rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            text-decoration: none;
            display: inline-block;
            text-align: center;
        }
        
        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
        }
        
        .btn-secondary {
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        }
        
        .btn-success {
            background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        }
        
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        
        .stat-card {
            background: rgba(255, 255, 255, 0.9);
            border-radius: 15px;
            padding: 25px;
            text-align: center;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
        }
        
        .stat-number {
            font-size: 2.5rem;
            font-weight: 700;
            color: #2c3e50;
            margin-bottom: 5px;
        }
        
        .stat-label {
            color: #7f8c8d;
            font-size: 0.9rem;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        
        .api-section {
            background: rgba(255, 255, 255, 0.95);
            border-radius: 20px;
            padding: 30px;
            margin-top: 30px;
        }
        
        .api-endpoint {
            background: #f8f9fa;
            border-radius: 10px;
            padding: 15px;
            margin: 10px 0;
            font-family: 'Courier New', monospace;
            border-left: 4px solid #667eea;
        }
        
        .method {
            color: #28a745;
            font-weight: bold;
        }
        
        .endpoint {
            color: #007bff;
        }
        
        @media (max-width: 768px) {
            .header h1 {
                font-size: 2rem;
            }
            
            .dashboard-grid {
                grid-template-columns: 1fr;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 LLM Integration Pipeline</h1>
            <p>AI-Powered Data Analysis & Anomaly Detection</p>
        </div>
        
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-number" id="data-sources">0</div>
                <div class="stat-label">Data Sources</div>
            </div>
            <div class="stat-card">
                <div class="stat-number" id="analysis-jobs">0</div>
                <div class="stat-label">Analysis Jobs</div>
            </div>
            <div class="stat-card">
                <div class="stat-number" id="anomalies">0</div>
                <div class="stat-label">Anomalies Detected</div>
            </div>
            <div class="stat-card">
                <div class="stat-number" id="reports">0</div>
                <div class="stat-label">Reports Generated</div>
            </div>
        </div>
        
        <div class="dashboard-grid">
            <div class="card">
                <h2>📊 Data Sources</h2>
                <p>Connect and manage various data sources including logs, databases, and APIs for analysis.</p>
                <a href="/api/data-sources" class="btn">Manage Sources</a>
            </div>
            
            <div class="card">
                <h2>🔍 Analysis Jobs</h2>
                <p>Create and monitor analysis jobs to detect anomalies and generate insights from your data.</p>
                <a href="/api/analysis-jobs" class="btn btn-secondary">View Jobs</a>
            </div>
            
            <div class="card">
                <h2>🚨 Anomalies</h2>
                <p>Review detected anomalies and security issues with detailed analysis and recommendations.</p>
                <a href="/api/anomalies" class="btn">View Anomalies</a>
            </div>
            
            <div class="card">
                <h2>📋 Reports</h2>
                <p>Generate comprehensive reports in multiple formats with actionable insights and recommendations.</p>
                <a href="/api/reports" class="btn btn-success">Generate Reports</a>
            </div>
        </div>
        
        <div class="api-section">
            <h2>🔌 API Endpoints</h2>
            <p>Use these REST API endpoints to integrate with the LLM Pipeline:</p>
            
            <div class="api-endpoint">
                <span class="method">GET</span> <span class="endpoint">/api/data-sources</span> - List all data sources
            </div>
            
            <div class="api-endpoint">
                <span class="method">POST</span> <span class="endpoint">/api/data-sources</span> - Create new data source
            </div>
            
            <div class="api-endpoint">
                <span class="method">POST</span> <span class="endpoint">/api/analysis-jobs</span> - Start analysis job
            </div>
            
            <div class="api-endpoint">
                <span class="method">GET</span> <span class="endpoint">/api/anomalies</span> - Get detected anomalies
            </div>
            
            <div class="api-endpoint">
                <span class="method">POST</span> <span class="endpoint">/api/reports/generate</span> - Generate report
            </div>
            
            <div class="api-endpoint">
                <span class="method">GET</span> <span class="endpoint">/docs</span> - Interactive API documentation
            </div>
        </div>
    </div>
    
    <script>
        // Load dashboard statistics
        async function loadStats() {
            try {
                const [sourcesRes, jobsRes, anomaliesRes, reportsRes] = await Promise.all([
                    fetch('/api/data-sources'),
                    fetch('/api/analysis-jobs'),
                    fetch('/api/anomalies'),
                    fetch('/api/reports')
                ]);
                
                const sources = await sourcesRes.json();
                const jobs = await jobsRes.json();
                const anomalies = await anomaliesRes.json();
                const reports = await reportsRes.json();
                
                document.getElementById('data-sources').textContent = sources.length || 0;
                document.getElementById('analysis-jobs').textContent = jobs.length || 0;
                document.getElementById('anomalies').textContent = anomalies.length || 0;
                document.getElementById('reports').textContent = reports.length || 0;
            } catch (error) {
                console.error('Failed to load stats:', error);
            }
        }
        
        // Load stats on page load
        loadStats();
        
        // Refresh stats every 30 seconds
        setInterval(loadStats, 30000);
    </script>
</body>
</html>
  """


# API Endpoints

@app.get("/api/data-sources")
async def get_data_sources(db: Session = Depends(get_db)):
  """Get all data sources."""
  return db.query(DataSource).all()


@app.post("/api/data-sources")
async def create_data_source(
  name: str,
  type: str,
  config: Dict[str, Any],
  db: Session = Depends(get_db)
):
  """Create a new data source."""
  data_source = DataSource(
    name=name,
    type=type,
    config=config
  )
  db.add(data_source)
  db.commit()
  db.refresh(data_source)
  return data_source


@app.get("/api/analysis-jobs")
async def get_analysis_jobs(db: Session = Depends(get_db)):
  """Get all analysis jobs."""
  return db.query(AnalysisJob).all()


@app.post("/api/analysis-jobs")
async def create_analysis_job(
  name: str,
  data_source_id: int,
  config: Dict[str, Any],
  background_tasks: BackgroundTasks,
  db: Session = Depends(get_db)
):
  """Create and start a new analysis job."""
  job = AnalysisJob(
    name=name,
    data_source_id=data_source_id,
    config=config,
    status="pending"
  )
  db.add(job)
  db.commit()
  db.refresh(job)
  
  # Start analysis in background
  background_tasks.add_task(run_analysis_job, job.id, db)
  
  return job


@app.get("/api/anomalies")
async def get_anomalies(
  severity: Optional[str] = None,
  limit: int = 100,
  db: Session = Depends(get_db)
):
  """Get detected anomalies."""
  query = db.query(Anomaly)
  
  if severity:
    query = query.filter(Anomaly.severity == severity)
  
  return query.limit(limit).all()


@app.get("/api/reports")
async def get_reports(db: Session = Depends(get_db)):
  """Get all generated reports."""
  return db.query(Report).all()


@app.post("/api/reports/generate")
async def generate_report(
  job_id: int,
  format: str = "html",
  db: Session = Depends(get_db)
):
  """Generate a report for a specific job."""
  job = db.query(AnalysisJob).filter(AnalysisJob.id == job_id).first()
  if not job:
    raise HTTPException(status_code=404, detail="Job not found")
  
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
  content = await generator.generate_report(report_data)
  
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
  
  return {"report_id": report.id, "content": content}


async def run_analysis_job(job_id: int, db: Session):
  """Run analysis job in background."""
  try:
    # Get job
    job = db.query(AnalysisJob).filter(AnalysisJob.id == job_id).first()
    if not job:
      return
    
    # Update status
    job.status = "running"
    db.commit()
    
    # Get data source
    data_source = db.query(DataSource).filter(DataSource.id == job.data_source_id).first()
    if not data_source:
      job.status = "failed"
      job.error_message = "Data source not found"
      db.commit()
      return
    
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
    result = await detector.analyze(data)
    
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
    
  except Exception as e:
    # Update job status
    job.status = "failed"
    job.error_message = str(e)
    db.commit()


if __name__ == "__main__":
  import uvicorn
  uvicorn.run(app, host="0.0.0.0", port=8000)
