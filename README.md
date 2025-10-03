# 🚀 LLM Integration Pipeline

**AI-powered data analysis and anomaly detection pipeline** that connects internal data sources (logs, databases, APIs) to LLMs for automated insights and reporting.

> **דוגמה מעשית**: Agent שמזהה Anomalies בלוגים של משחק → מייצר דוח אוטומטי לצוות DevOps.

## 🎯 Value Proposition

- **שילוב "Data → LLM → Insights" ברמה Production**
- **זיהוי אנומליות אוטומטי** בלוגים, מסדי נתונים ו-APIs
- **דוחות אוטומטיים** עם המלצות מעשיות
- **ממשק ניהול מתקדם** עם דשבורד מודרני
- **תמיכה במספר LLM providers** (OpenAI, Anthropic)

## ✨ Features

- **Multi-Source Data Connectors**: Support for logs, databases, and APIs
- **LLM Integration**: OpenAI and Anthropic support with extensible architecture
- **Anomaly Detection**: AI-powered anomaly detection with statistical and semantic analysis
- **Automated Reporting**: Generate beautiful HTML and JSON reports
- **Web Dashboard**: Modern, responsive dashboard for monitoring and management
- **Background Processing**: Celery-based task queue for scalable processing
- **REST API**: Complete REST API for integration

## 🏗️ Architecture

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

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Docker & Docker Compose
- OpenAI API Key (or Anthropic API Key)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd llm-integration-pipeline
   ```

2. **Set up environment variables**
   ```bash
   cp env.example .env
   # Edit .env with your API keys and configuration
   ```

3. **Start with Docker Compose**
   ```bash
   # Windows
   run.bat
   
   # Linux/Mac
   python run.py
   ```

4. **Access the dashboard**
   - Web Dashboard: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

### 🎮 Example: Game Logs Analysis

Run the practical example:
```bash
python examples/game_logs_analysis.py
```

This will:
- Create sample game server logs
- Analyze them for anomalies
- Generate HTML and JSON reports
- Show practical usage of the pipeline

### Manual Installation

1. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up database**
   ```bash
   # Start PostgreSQL and Redis
   docker-compose up -d db redis
   ```

3. **Run the application**
   ```bash
   # Start the main application
   uvicorn app.main:app --host 0.0.0.0 --port 8000

   # Start the worker (in another terminal)
   celery -A app.worker worker --loglevel=info
   ```

## 📊 Usage Examples

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

## 🔧 Configuration

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

## 🎯 Use Cases

### 1. Game Server Monitoring
- Monitor game server logs for crashes, errors, and performance issues
- Detect unusual player behavior patterns
- Generate automated reports for DevOps team

### 2. E-commerce Analytics
- Analyze transaction logs for fraud detection
- Monitor API performance and error rates
- Generate business intelligence reports

### 3. Security Monitoring
- Detect security threats in access logs
- Monitor for suspicious patterns
- Generate security incident reports

### 4. Application Performance
- Monitor application logs for performance issues
- Detect memory leaks and resource problems
- Generate performance optimization recommendations

## 🔌 API Reference

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

## 🛠️ Development

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

## 📈 Monitoring

The application includes built-in monitoring capabilities:

- **Health Checks**: `/health` endpoint for service health
- **Metrics**: Prometheus-compatible metrics
- **Logging**: Structured logging with configurable levels
- **Background Tasks**: Celery task monitoring

## 🔒 Security

- API key management for LLM providers
- Database connection security
- Input validation and sanitization
- Rate limiting and request throttling

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Create an issue in the repository
- Check the API documentation at `/docs`
- Review the example configurations

---

**Built with ❤️ for modern data analysis and AI integration**
