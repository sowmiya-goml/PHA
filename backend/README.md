# PHA Database Connection Manager

A FastAPI-based backend service for managing database connections with support for multiple database types including MySQL, PostgreSQL, and MongoDB.

## Project Structure

```
backend/
├── app/                          # Main application package
│   ├── __init__.py
│   ├── main.py                   # FastAPI application entry point
│   ├── core/                     # Core configurations
│   │   ├── __init__.py
│   │   └── config.py            # Application settings
│   ├── routers/                  # API route handlers
│   │   ├── __init__.py
│   │   └── connections.py       # Database connection routes
│   ├── services/                 # Business logic layer
│   │   ├── __init__.py
│   │   └── connection_service.py # Connection management service
│   ├── models/                   # Data models
│   │   ├── __init__.py
│   │   └── connection.py        # Database connection model
│   ├── schemas/                  # Pydantic schemas (Request/Response)
│   │   ├── __init__.py
│   │   └── connection.py        # Connection validation schemas
│   ├── utils/                    # Helper functions and utilities
│   │   ├── __init__.py
│   │   └── helpers.py           # Common utility functions
│   └── db/                       # Database session management
│       ├── __init__.py
│       └── session.py           # MongoDB connection manager
├── tests/                        # Unit and integration tests
│   ├── conftest.py              # Test configuration and fixtures
│   └── test_connections.py     # Connection API tests
├── requirements.txt              # Python dependencies
├── pyproject.toml               # Project configuration
├── .env.example                 # Environment variables template
└── README.md                    # This file
```

## Features

- **Database Connection Management**: Store, retrieve, update, and delete database connection configurations
- **Multiple Database Support**: MySQL, PostgreSQL, MongoDB
- **Connection Testing**: Test database connections before storing
- **RESTful API**: Clean REST endpoints with comprehensive documentation
- **Data Validation**: Request/response validation using Pydantic
- **Error Handling**: Comprehensive error handling and logging
- **Modular Architecture**: Clean separation of concerns for maintainability

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
