# AWS Health PHI Report Generator

🏥 **AI-powered healthcare report generation system** that securely connects to client databases, extracts schemas, and generates personalized health reports using AWS Bedrock - **without storing any PHI data**.

## 🎯 **System Overview**

Our system enables healthcare providers to generate comprehensive patient reports through natural language queries while maintaining strict HIPAA compliance and data security.

### **Key Value Proposition**
- 🤖 **AI-Powered**: Convert plain English to SQL/NoSQL queries using AWS Bedrock
- 🔒 **Zero PHI Storage**: All patient data processed in-memory only
- ⚡ **Real-time Processing**: Live database queries with instant report generation
- 🌐 **Multi-Database Support**: PostgreSQL, MySQL, MongoDB compatibility
- 📊 **Professional Reports**: PDF/CSV output with medical visualizations
- 🛡️ **Enterprise Security**: IP whitelisting, encryption, audit logging

## 🚀 **Core Features**

### **🔄 Complete Workflow**
1. **Database Registration** - Healthcare clients register their database connections
2. **Schema Extraction** - Automated schema analysis and metadata storage  
3. **Natural Language Processing** - *"Extract patient P1234's visits from last 6 months"*
4. **AI Query Generation** - AWS Bedrock converts requests to safe SQL/NoSQL queries
5. **Live Data Retrieval** - Real-time execution against client databases
6. **Health Report Creation** - AI-generated PDF/CSV reports with medical insights
7. **Secure Delivery** - Temporary S3 storage with expiring download links

### **🎯 AI-Powered Query Generation**
- ✅ **Natural Language Input**: Plain English medical queries
- ✅ **Schema-Aware Processing**: AI understands database structure
- ✅ **Safety Validation**: Prevents destructive operations (DROP, DELETE)
- ✅ **Parameterized Queries**: SQL injection prevention
- ✅ **Multi-Database Support**: Generates SQL, NoSQL, and custom queries

### **📋 Report Generation Capabilities**  
- ✅ **Medical Summaries**: Patient history, medications, diagnoses
- ✅ **Visit Analytics**: Timeline analysis with key metrics
- ✅ **Custom Reports**: Doctor-specific requirements and formats
- ✅ **Data Visualizations**: Charts, graphs, and medical timelines
- ✅ **Export Formats**: PDF (professional), CSV (data analysis)

## 🏗️ **Architecture Overview**

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Healthcare    │───▶│    AWS Bedrock   │───▶│   Client DB     │
│   Provider      │    │   (AI Queries)   │    │  (Live PHI)     │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                        │                       │
         ▼                        ▼                       ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│  FastAPI (EC2)  │───▶│  MongoDB Atlas   │    │  Report Gen     │
│ Fixed Elastic IP│    │ (Schema Only)    │    │  (PDF/CSV)      │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## 📁 **Project Structure**

```
backend/
├── app/                          # Main application package
│   ├── main.py                   # FastAPI application entry point
│   ├── core/                     # Core configurations
│   │   └── config.py            # AWS, DB, and security settings
│   ├── routers/                  # API route handlers
│   │   ├── connections.py       # Database connection management
│   │   ├── queries.py           # AI query generation endpoints
│   │   └── reports.py           # Health report generation
│   ├── services/                 # Business logic layer
│   │   ├── connection_service.py # Database connection management
│   │   ├── bedrock_service.py   # AWS Bedrock AI integration
│   │   ├── query_service.py     # Live database query execution
│   │   └── report_service.py    # PDF/CSV report generation
│   ├── models/                   # Data models
│   │   ├── __init__.py
│   │   └── connection.py        # MongoDB document models
│   ├── schemas/                  # Pydantic validation schemas
│   │   ├── __init__.py
│   │   └── connection.py        # Request/response validation models
│   ├── utils/                    # Helper functions and utilities
│   │   ├── __init__.py
│   │   └── helpers.py           # Logging, validation, serialization
│   └── db/                       # Database session management
│       ├── __init__.py
│       └── session.py           # MongoDB connection manager
├── tests/                        # Unit and integration tests
│   ├── conftest.py              # Test configuration and fixtures
│   └── test_connections.py     # API endpoint tests
├── requirements.txt              # Python dependencies (legacy)
├── pyproject.toml               # Modern project configuration with uv
├── uv.lock                      # Dependency lock file
├── .env                         # Environment variables
└── README.md                    # This documentation
```

## 🛠️ Technology Stack

### Core Framework
- **FastAPI**: Modern, fast web framework with automatic API documentation
- **Uvicorn**: High-performance ASGI server
- **Pydantic**: Data validation and serialization

### Database Drivers
- **PyMongo**: MongoDB driver with Atlas SRV support
- **psycopg2-binary**: PostgreSQL adapter with SSL capabilities
- **mysql-connector-python**: MySQL database connector

### Development Tools
- **uv**: Modern Python package management (replaces pip)
- **pytest**: Testing framework with async support
- **python-dotenv**: Environment variable management

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- uv package manager
- MongoDB Atlas account (optional)
- PostgreSQL/Neon database (optional)

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/sowmiya-goml/PHA.git
cd PHA/backend
```

2. **Install dependencies**
```bash
uv sync
```

3. **Configure environment**
```bash
cp .env.example .env
# Edit .env with your MongoDB connection details
```

4. **Start the server**
```bash
uv run python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

5. **Access the API**
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- API Base: http://localhost:8000/api/v1

## 📚 API Documentation

### Endpoints Overview

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/v1/connections/` | Create new database connection |
| `GET` | `/api/v1/connections/` | List all connections |
| `GET` | `/api/v1/connections/{id}` | Get specific connection |
| `PUT` | `/api/v1/connections/{id}` | Update connection |
| `DELETE` | `/api/v1/connections/{id}` | Delete connection |
| `POST` | `/api/v1/connections/test` | Test connection |
| `GET` | `/api/v1/connections/{id}/schema` | **Extract database schema** |
| `GET` | `/api/v1/connections/{id}/databases` | **Discover available databases** |

### Schema Extraction Response Format

#### MongoDB Collections
```json
{
  "status": "success",
  "message": "Analyzed 5 collections with 1,250 total documents in database 'production'",
  "database_type": "MongoDB",
  "database_name": "production",
  "tables": [
    {
      "name": "users",
      "type": "collection",
      "fields": [
        {
          "name": "_id",
          "type": "ObjectId",
          "nullable": false,
          "default": "Present in 100.0% of documents"
        },
        {
          "name": "email",
          "type": "string",
          "nullable": true,
          "default": "Present in 95.2% of documents"
        },
        {
          "name": "profile.address.city",
          "type": "string",
          "nullable": true,
          "default": "Present in 78.5% of documents"
        }
      ],
      "row_count": 1250
    }
  ]
}
```

#### PostgreSQL Tables
```json
{
  "status": "success",
  "message": "Retrieved schema for 8 tables/views",
  "database_type": "PostgreSQL",
  "database_name": "neon_db",
  "tables": [
    {
      "name": "users",
      "type": "table",
      "fields": [
        {
          "name": "id",
          "type": "integer",
          "nullable": false,
          "default": "nextval('users_id_seq'::regclass)"
        },
        {
          "name": "email",
          "type": "character varying(255)",
          "nullable": false,
          "default": null
        }
      ],
      "row_count": 1250
    }
  ]
}
```

## 🔧 Configuration

### Environment Variables

```bash
# MongoDB Configuration (for storing connection metadata)
MONGODB_URL=mongodb+srv://user:password@cluster.mongodb.net/?retryWrites=true&w=majority
DATABASE_NAME=pha_connections

# Server Configuration
HOST=0.0.0.0
PORT=8000

# Security
SECRET_KEY=your-secret-key-here
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Database Connection Timeout
DB_CONNECTION_TIMEOUT_MS=10000
```

### Supported Connection Strings

#### MongoDB Atlas
```bash
mongodb+srv://username:password@cluster.mongodb.net/?retryWrites=true&w=majority
```

#### PostgreSQL (Neon)
```bash
postgresql://username:password@host:5432/database?sslmode=require
```

#### MySQL
```bash
mysql://username:password@host:3306/database
```

## 🧪 Testing

### Run All Tests
```bash
cd backend
uv run pytest
```

### Run Specific Test File
```bash
uv run pytest tests/test_connections.py
```

### Run Tests with Coverage
```bash
uv run pytest --cov=app tests/
```

### Test Connection Examples

#### Create MongoDB Connection
```bash
curl -X POST "http://localhost:8000/api/v1/connections/" \
  -H "Content-Type: application/json" \
  -d '{
    "connection_name": "Production MongoDB",
    "database_type": "MongoDB",
    "host": "cluster0.mongodb.net",
    "port": 27017,
    "database_name": "production",
    "username": "dbuser",
    "password": "password123",
    "additional_notes": "Production database cluster"
  }'
```

#### Extract Schema
```bash
curl -X GET "http://localhost:8000/api/v1/connections/{connection_id}/schema"
```

## 🏗️ Architecture

### Layered Architecture
```
API Layer (FastAPI Routes)
    ↓
Service Layer (Business Logic)
    ↓
Model Layer (Data Models)
    ↓
Database Layer (MongoDB)
```

### Key Components

#### Connection Service (`connection_service.py`)
- **850+ lines** of business logic
- MongoDB collection analysis with document sampling
- PostgreSQL schema extraction with SSL support
- Dynamic database discovery
- Comprehensive error handling

#### API Routes (`connections.py`)
- RESTful endpoint implementation
- Request/response validation
- Dependency injection
- Error handling and status codes

#### Data Models (`connection.py`)
- MongoDB document mapping
- ObjectId handling
- Timestamp management
- Dictionary serialization

#### Validation Schemas (`schemas/connection.py`)
- Pydantic models for API validation
- Request/response type safety
- Field validation and documentation

## 🔒 Security Considerations

### Current Implementation
- Input validation with Pydantic
- CORS middleware configuration
- Connection timeout protection
- Error message sanitization

### Production Recommendations
- Implement API key authentication
- Encrypt stored passwords
- Add rate limiting
- Use HTTPS in production
- Implement IP whitelisting
- Add audit logging

## 📈 Performance Features

### MongoDB Optimizations
- Document sampling (up to 20 docs per collection)
- Connection pooling and timeout management
- Efficient field type inference
- Smart database discovery

### PostgreSQL Optimizations
- SSL connection support for cloud databases
- Efficient schema queries using information_schema
- Row count optimization for large tables

### General Performance
- Async/await throughout the codebase
- Connection timeout configuration
- Efficient error handling
- Minimal memory footprint

## 🚀 Deployment

### Local Development
```bash
uv run python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Production (using uv)
```bash
uv run python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Docker (Future Enhancement)
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY . .
RUN pip install uv && uv sync
CMD ["uv", "run", "python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## 🐛 Troubleshooting

### Common Issues

#### MongoDB Connection Failed
- Verify Atlas IP whitelist includes your IP
- Check username/password credentials
- Ensure user has proper database permissions
- Verify network connectivity

#### PostgreSQL SSL Error
- Ensure `psycopg2-binary` is installed
- Check if SSL is required for your PostgreSQL provider
- Verify connection string format

#### Schema Extraction Returns Empty
- Check if target database exists
- Verify user has read permissions
- Use `/databases` endpoint to discover available databases

### Debug Mode
Enable detailed logging by setting environment variable:
```bash
LOG_LEVEL=DEBUG
```

## 🤝 Contributing

### Development Setup
1. Fork the repository
2. Create a feature branch
3. Install dependencies with `uv sync`
4. Make changes and add tests
5. Run tests with `pytest`
6. Submit pull request

### Code Style
- Follow PEP 8 guidelines
- Use type hints throughout
- Write comprehensive docstrings
- Add unit tests for new features

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 👥 Authors

- **Sowmiya** - Initial work and architecture
- **Development Team** - Feature enhancements and testing

## 🔗 Related Projects

- [MongoDB Atlas](https://www.mongodb.com/atlas)
- [Neon PostgreSQL](https://neon.tech/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)

---

**Status**: Production Ready ✅  
**Last Updated**: September 2025  
**Version**: 1.0.0

## Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd backend
   ```

2. **Create virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Setup**:
   ```bash
   cp .env.example .env
   # Edit .env with your MongoDB connection details
   ```

5. **Install optional database drivers** (as needed):
   ```bash
   # For MySQL support
   pip install mysql-connector-python
   
   # For PostgreSQL support
   pip install psycopg2-binary
   ```

## Configuration

Update the `.env` file with your settings:

```env
MONGODB_URL=mongodb://localhost:27017
DATABASE_NAME=pha_connections
HOST=0.0.0.0
PORT=8000
SECRET_KEY=your-secret-key-here
DB_CONNECTION_TIMEOUT_MS=5000
```

## Running the Application

### Development Mode
```bash
# From the backend directory
python -m app.main

# Or using uvicorn directly
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Production Mode
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

## API Documentation

Once running, access the interactive API documentation:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## API Endpoints

### Core Endpoints
- `GET /` - API information and health status
- `GET /health` - Health check endpoint

### Database Connections
- `POST /api/v1/connections/` - Create a new database connection
- `GET /api/v1/connections/` - Get all database connections
- `GET /api/v1/connections/{id}` - Get a specific connection
- `PUT /api/v1/connections/{id}` - Update a connection
- `DELETE /api/v1/connections/{id}` - Delete a connection
- `POST /api/v1/connections/{id}/test` - Test a connection

## Testing

### Run all tests
```bash
pytest
```

### Run tests with coverage
```bash
pytest --cov=app
```

### Run specific test files
```bash
pytest tests/test_connections.py
```

## Project Architecture

### Layer Separation
- **Routers**: Handle HTTP requests and responses
- **Services**: Contain business logic and orchestration
- **Models**: Define data structures and database operations
- **Schemas**: Handle request/response validation
- **Utils**: Common helper functions and utilities
- **Core**: Application configuration and settings
- **DB**: Database connection and session management

### Design Principles
- **Separation of Concerns**: Each layer has a specific responsibility
- **Dependency Injection**: Services and dependencies are injected
- **Error Handling**: Comprehensive error handling at all levels
- **Validation**: Input validation using Pydantic schemas
- **Logging**: Structured logging throughout the application

## Development Guidelines

### Adding New Features
1. Define schemas in `app/schemas/`
2. Create or update models in `app/models/`
3. Implement business logic in `app/services/`
4. Add API routes in `app/routers/`
5. Write tests in `tests/`

### Code Style
- Follow PEP 8 conventions
- Use type hints throughout
- Add docstrings to all functions and classes
- Keep functions small and focused

## Deployment

### Docker (Recommended)
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY app/ ./app/
EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Environment Variables for Production
- Set `SECRET_KEY` to a secure random value
- Configure `MONGODB_URL` for your production database
- Adjust `DB_CONNECTION_TIMEOUT_MS` as needed
- Set appropriate CORS origins in production

## Troubleshooting

### Common Issues
1. **MongoDB Connection Failed**: Ensure MongoDB is running and accessible
2. **Import Errors**: Ensure you're running from the correct directory
3. **Database Driver Missing**: Install the appropriate database driver for your database type

### Logs
The application uses structured logging. Check logs for detailed error information.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes following the project structure
4. Write tests for new functionality
5. Submit a pull request

## License

[Add your license information here]
