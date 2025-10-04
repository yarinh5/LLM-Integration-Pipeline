# LLM Integration Pipeline

An intelligent data analysis and anomaly detection system that seamlessly connects your internal data sources to advanced language models, providing automated insights and comprehensive reporting.

> **Practical Example**: An intelligent agent that detects anomalies in game server logs and automatically generates actionable reports for your DevOps team.

## What This System Does

This pipeline bridges the gap between your data and actionable insights by:

- **Production-Ready Data Integration**: Connect logs, databases, and APIs to LLMs in a robust, scalable way
- **Intelligent Anomaly Detection**: Automatically identify unusual patterns across multiple data sources
- **Automated Reporting**: Generate detailed reports with practical recommendations
- **Modern Management Interface**: Access everything through an intuitive web dashboard
- **Multi-Provider Support**: Works with OpenAI, Anthropic, and other LLM providers

## Key Features

- **Flexible Data Connectors**: Seamlessly integrate with logs, databases, and APIs
- **Advanced LLM Integration**: Support for multiple providers with extensible architecture
- **Smart Anomaly Detection**: Combines statistical analysis with AI-powered semantic understanding
- **Professional Reporting**: Generate polished HTML and JSON reports
- **Interactive Dashboard**: Modern, responsive interface for monitoring and management
- **Scalable Processing**: Background task processing using Celery
- **Complete API**: Full REST API for easy integration

## System Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Data Sources  │    │  LLM Providers  │    │   Output Layer  │
│                 │    │                 │    │                 │
│ • Log Files     │───▶│ • OpenAI        │───▶│ • HTML Reports  │
│ • Databases     │    │ • Anthropic     │    │ • JSON Reports  │
│ • APIs          │    │ • Extensible    │    │ • Dashboard     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Processing Pipeline                          │
│                                                                 │
│ • Data Connectors  • Anomaly Detection  • Report Generation    │
│ • Background Tasks • Statistical Analysis • LLM Enhancement     │
└─────────────────────────────────────────────────────────────────┘
```

## Getting Started

### What You'll Need

- Python 3.11 or newer
- Docker and Docker Compose
- An OpenAI API Key (or Anthropic API Key)

### Quick Setup

1. **Get the code**
   ```bash
   git clone <repository-url>
   cd llm-integration-pipeline
   ```

2. **Configure your environment**
   ```bash
   cp env.example .env
   # Edit .env with your API keys and settings
   ```

3. **Launch the system**
   ```bash
   # On Windows
   run.bat
   
   # On Linux/Mac
   python run.py
   ```

4. **Access your dashboard**
   - Web Interface: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

### Try the Game Logs Example

See the system in action with a practical example:
```bash
python examples/game_logs_analysis.py
```

This demonstration will:
- Create realistic game server log data
- Run anomaly detection on the logs
- Generate both HTML and JSON reports
- Show you exactly how the pipeline works

### Manual Installation

If you prefer to set up the system manually:

1. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Start the database services**
   ```bash
   # Launch PostgreSQL and Redis
   docker-compose up -d db redis
   ```

3. **Run the application components**
   ```bash
   # Start the main web application
   uvicorn app.main:app --host 0.0.0.0 --port 8000

   # Start the background worker (in a separate terminal)
   celery -A app.worker worker --loglevel=info
   ```

## Usage Examples

### 1. Create a Data Source

```bash
curl -X POST "http://localhost:8000/api/data-sources" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Game Server Logs",
    "type": "log",
    "config": {
      "file_path": "/var/log/game-server.log",
      "log_format": "json"
    }
  }'
```

### 2. Start Analysis Job

```bash
curl -X POST "http://localhost:8000/api/analysis-jobs" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Daily Log Analysis",
    "data_source_id": 1,
    "config": {
      "sensitivity": "medium",
      "llm_provider": "openai"
    }
  }'
```

### 3. Generate Report

```bash
curl -X POST "http://localhost:8000/api/reports/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "job_id": 1,
    "format": "html"
  }'
```

## Configuration

### Data Source Types

#### Log Connector
```json
{
  "file_path": "/path/to/logfile.log",
  "log_format": "json|apache_common|nginx|custom",
  "regex_pattern": "custom regex for custom format"
}
```

#### Database Connector
```json
{
  "connection_string": "postgresql://user:pass@host:port/db",
  "query": "SELECT * FROM logs WHERE timestamp BETWEEN '{start_time}' AND '{end_time}'"
}
```

#### API Connector
```json
{
  "base_url": "https://api.example.com",
  "endpoint": "/logs",
  "headers": {"Authorization": "Bearer token"},
  "supports_pagination": true,
  "supports_time_filter": true
}
```

### LLM Providers

#### OpenAI
```json
{
  "provider": "openai",
  "config": {
    "default_model": "gpt-3.5-turbo",
    "embedding_model": "text-embedding-ada-002"
  }
}
```

#### Anthropic
```json
{
  "provider": "anthropic",
  "config": {
    "default_model": "claude-3-sonnet-20240229"
  }
}
```

## Real-World Applications

### Game Server Monitoring
Keep your game servers running smoothly by monitoring logs for crashes, errors, and performance issues. The system can detect unusual player behavior patterns and automatically generate reports for your DevOps team.

### E-commerce Analytics
Protect your business by analyzing transaction logs for fraud detection. Monitor API performance and error rates, then generate business intelligence reports to help optimize your operations.

### Security Monitoring
Enhance your security posture by detecting threats in access logs. The system monitors for suspicious patterns and generates security incident reports when issues are found.

### Application Performance
Maintain optimal performance by monitoring application logs for issues. Detect memory leaks and resource problems, then receive performance optimization recommendations.

## API Reference

### Data Sources
- `GET /api/data-sources` - List all data sources
- `POST /api/data-sources` - Create new data source
- `GET /api/data-sources/{id}` - Get specific data source
- `PUT /api/data-sources/{id}` - Update data source
- `DELETE /api/data-sources/{id}` - Delete data source

### Analysis Jobs
- `GET /api/analysis-jobs` - List all analysis jobs
- `POST /api/analysis-jobs` - Create new analysis job
- `GET /api/analysis-jobs/{id}` - Get specific job
- `POST /api/analysis-jobs/{id}/run` - Run job manually

### Anomalies
- `GET /api/anomalies` - List detected anomalies
- `GET /api/anomalies?severity=critical` - Filter by severity
- `GET /api/anomalies/{id}` - Get specific anomaly

### Reports
- `GET /api/reports` - List all reports
- `POST /api/reports/generate` - Generate new report
- `GET /api/reports/{id}` - Get specific report
- `GET /api/reports/{id}/download` - Download report file

## Development

### Project Structure
```
app/
├── agents/           # AI agents (anomaly detection, etc.)
├── data_connectors/  # Data source connectors
├── llm/             # LLM provider integrations
├── reports/         # Report generation
├── database.py      # Database models
├── config.py        # Configuration
└── main.py          # FastAPI application
```

### Adding New Data Connectors

1. Create a new connector class inheriting from `BaseDataConnector`
2. Implement required methods: `validate_config`, `connect`, `fetch_data`
3. Register in `DataConnectorFactory`

### Adding New LLM Providers

1. Create a new provider class inheriting from `BaseLLMProvider`
2. Implement required methods: `generate_response`, `generate_embeddings`
3. Register in `LLMProviderFactory`

### Adding New Report Formats

1. Create a new generator class inheriting from `BaseReportGenerator`
2. Implement required methods: `generate_report`
3. Register in `ReportGeneratorFactory`

## Monitoring and Observability

The system includes comprehensive monitoring capabilities:

- **Health Checks**: Monitor service health via the `/health` endpoint
- **Metrics**: Prometheus-compatible metrics for system monitoring
- **Logging**: Structured logging with configurable levels
- **Background Tasks**: Monitor Celery task execution and performance

## Security Features

- Secure API key management for LLM providers
- Protected database connections
- Input validation and sanitization
- Rate limiting and request throttling

## Contributing

We welcome contributions! Here's how you can help:

1. Fork the repository
2. Create a feature branch for your changes
3. Implement your improvements
4. Add appropriate tests
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Getting Help

If you need assistance:
- Create an issue in the repository
- Check the API documentation at `/docs`
- Review the example configurations and documentation

---

**Built for modern data analysis and AI integration**
