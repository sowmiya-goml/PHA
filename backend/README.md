# AWS Health PHI Report Generator

## � Overview

The AWS Health PHI Report Generator is a secure, AI-powered system that connects to client databases, extracts schemas, and enables multi-database operations without storing PHI data. The system supports comprehensive database connections, schema analysis, and MongoDB-specific advanced operations.

## 🏗️ Architecture

```
FastAPI Backend (EC2) → MongoDB Atlas (Metadata) → Client Databases (Live Query)
```

**Key Features:**
- Multi-database schema extraction (PostgreSQL, MySQL, MariaDB, Oracle, SQL Server, MongoDB)
- MongoDB comprehensive schema analysis with webhook support
- Real-time database connections with SSL/TLS support
- Unified JSON schema format for consistent data representation
- HIPAA-compliant architecture with zero PHI storage

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- MongoDB Atlas account
- uv package manager (recommended) or pip

### Installation

1. **Clone the repository:**
```bash
git clone https://github.com/sowmiya-goml/PHA.git
cd PHA/backend
```

2. **Set up Python environment:**
```bash
# Using uv (recommended)
uv venv
uv pip install -r requirements.txt

# Or using pip
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

3. **Configure environment variables:**
```bash
cp .env.example .env
# Edit .env with your MongoDB Atlas connection string
```

4. **Run the application:**
```bash
# Using uv
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Or using python directly
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

5. **Access the API:**
- API Documentation: http://localhost:8000/docs
- Health Check: http://localhost:8000/health
- Database Status: http://localhost:8000/database/status

## � API Endpoints

### Core Endpoints
- `GET /` - Root endpoint with API information
- `GET /health` - Health check with database status
- `GET /database/status` - Detailed database connection status
- `POST /database/reconnect` - Manual database reconnection

### Database Connections (`/api/v1/connections/`)
- `GET /` - List all database connections
- `POST /` - Create new database connection
- `GET /{connection_id}` - Get specific connection
- `PUT /{connection_id}` - Update connection
- `DELETE /{connection_id}` - Delete connection
- `POST /{connection_id}/test` - Test database connectivity
- `GET /{connection_id}/schema` - Extract database schema
- `GET /{connection_id}/databases` - List available databases

### MongoDB Schema Analysis (`/api/v1/mongodb-schema/`)
- `GET /test` - MongoDB service health check
- `POST /analyze-direct` - Direct MongoDB schema analysis
- `POST /test-atlas-connection` - Test MongoDB Atlas connections
- `POST /webhook/test` - Test webhook URL connectivity
- `POST /webhook/notify` - Send schema change notifications
- `POST /schema/compare` - Compare schema versions with hash detection
- `POST /webhook-receiver` - Receive webhook notifications

## 🔧 Database Support

### Supported Database Types
| Database | Connection String Format | Status |
|----------|--------------------------|--------|
| **PostgreSQL** | `postgresql://user:pass@host:port/db` | ✅ Complete |
| **MySQL** | `mysql://user:pass@host:port/db` | ✅ Complete |
| **MariaDB** | `mariadb://user:pass@host:port/db` | ✅ Complete |
| **Oracle** | `oracle://user:pass@host:port/service` | ✅ Complete |
| **SQL Server** | `Server=host;Database=db;User Id=user;Password=pass;` | ✅ Complete |
| **MongoDB** | `mongodb+srv://user:pass@cluster/db` | ✅ Complete |

### Cloud Database Support
- **AWS RDS/Aurora**: Full PostgreSQL and MySQL support
- **MongoDB Atlas**: Complete integration with advanced features
- **Azure Database**: PostgreSQL, MySQL, and SQL Server support
- **Google Cloud SQL**: PostgreSQL and MySQL support
- **Neon, PlanetScale, Supabase**: Direct connection string support

## 📁 Project Structure

```
backend/
├── app/
│   ├── core/           # Configuration and settings
│   ├── db/            # Database connection management
│   ├── models/        # Data models and schemas
│   ├── routers/       # API endpoint routes
│   ├── schemas/       # Pydantic schemas for validation
│   ├── services/      # Business logic layer
│   └── utils/         # Helper utilities
├── tests/             # Test suite
├── .env.example       # Environment variables template
├── requirements.txt   # Python dependencies
└── README.md         # This file
```

## 🔒 Security Features

### Database Security
- **SSL/TLS Encryption**: Automatic for cloud providers
- **Connection Timeouts**: Configurable timeout settings
- **IP Whitelisting**: Support for client IP restrictions
- **Read-Only Operations**: Schema extraction only, no data modification

### Data Protection
- **Zero PHI Storage**: No patient data stored in the system
- **In-Memory Processing**: All operations performed in memory
- **Secure Connections**: All database connections use SSL/TLS
- **Audit Logging**: Comprehensive operation logging

## 🧪 Testing

### Run the Test Suite
```bash
# Using uv
uv run pytest tests/ -v

# Or using python
python -m pytest tests/ -v
```

### Manual API Testing
Use the comprehensive testing guide:
- See `MONGODB_SCHEMA_API_TESTING.md` for detailed endpoint testing
- Access interactive docs at `/docs` endpoint
- Use provided curl commands and PowerShell scripts

### Example Test Connection
```bash
curl -X POST "http://localhost:8000/api/v1/connections/" \
  -H "Content-Type: application/json" \
  -d '{
    "connection_name": "Test PostgreSQL",
    "database_type": "postgresql",
    "connection_string": "postgresql://user:pass@localhost:5432/testdb"
  }'
```

## 🚀 Deployment

### Environment Variables
```bash
# MongoDB Configuration
MONGODB_URL=mongodb+srv://user:pass@cluster.mongodb.net/?retryWrites=true&w=majority&appName=PHA
DATABASE_NAME=pha_connections

# Server Configuration
HOST=0.0.0.0
PORT=8000

# Database Connection Settings
DB_CONNECTION_TIMEOUT_MS=30000
DB_SERVER_SELECTION_TIMEOUT_MS=30000
```

### Production Deployment
1. Set up MongoDB Atlas cluster
2. Configure environment variables
3. Deploy to AWS EC2 with fixed Elastic IP
4. Set up client database IP whitelisting
5. Configure SSL/TLS certificates
6. Set up monitoring and logging

## 📖 Documentation

- **API Documentation**: Available at `/docs` when running
- **Architecture**: See `IMPROVED_ARCHITECTURE.md`
- **Implementation Details**: See `FINAL_FLOW_SUMMARY.md`
- **Testing Guide**: See `MONGODB_SCHEMA_API_TESTING.md`

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## 📜 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Create an issue in the GitHub repository
- Check the documentation in `/docs`
- Review the testing guide for API usage examples

---

**Version**: 2.0.0  
**Last Updated**: September 2025  
**Status**: Production Ready
