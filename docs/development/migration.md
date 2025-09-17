# Project Structure Migration

This document explains the new clean project structure implemented for the PHA Backend.

## 🏗️ New Structure Overview

```
PHA/                                    # Project root
├── .env                               # Environment variables (git-ignored)
├── .env.example                       # Template for environment setup
├── .gitignore                         # Git ignore patterns
├── .python-version                    # Python version specification
├── pyproject.toml                     # Modern Python project configuration
├── requirements.txt                   # Dependency list (legacy support)
├── uv.lock                           # UV lock file
├── README.md                         # Main project documentation
│
├── src/                              # Source code directory
│   └── pha/                          # Main package (renamed from 'app')
│       ├── __init__.py
│       ├── main.py                   # FastAPI application entry point
│       ├── api/                      # API layer (renamed from 'routers')
│       │   ├── __init__.py
│       │   ├── routes.py             # Main route aggregator
│       │   └── v1/                   # API versioning
│       │       ├── __init__.py
│       │       ├── connections.py    # Database connections endpoints
│       │       ├── healthcare.py     # Healthcare query endpoints
│       │       ├── mongodb.py        # MongoDB specific endpoints
│       │       └── query.py          # Query generation endpoints
│       ├── core/                     # Core configuration and settings
│       ├── db/                       # Database layer
│       ├── models/                   # Data models
│       ├── schemas/                  # Pydantic schemas
│       ├── services/                 # Business logic layer
│       └── utils/                    # Utility functions
│
├── tests/                            # Test suite
│   ├── unit/                         # Unit tests
│   ├── integration/                  # Integration tests
│   └── fixtures/                     # Test fixtures and data
│
├── docs/                             # Documentation
│   ├── api/                          # API documentation
│   ├── deployment/                   # Deployment guides
│   └── development/                  # Development guides
│
├── scripts/                          # Utility scripts
│   ├── start.py                      # Application startup script
│   └── test.py                       # Test runner script
│
└── config/                           # Configuration files
```

## 🔄 Key Changes Made

### 1. **Package Restructuring**
- Moved from `backend/app/` to `src/pha/`
- Renamed `routers/` to `api/v1/` for better API versioning
- Added API route aggregation in `api/routes.py`

### 2. **Import Path Updates**
All imports updated from:
```python
from app.core.config import settings
from app.routers import connections
```

To:
```python
from pha.core.config import settings
from pha.api.v1 import connections
```

### 3. **Test Organization**
- Moved unit tests to `tests/unit/`
- Created `tests/integration/` for integration tests
- Added `tests/fixtures/` for test data

### 4. **Documentation Structure**
- Moved architecture docs to `docs/`
- Organized by category (api, deployment, development)
- Centralized documentation approach

### 5. **Configuration Management**
- Updated `pyproject.toml` with modern Python packaging standards
- Added development dependencies
- Configured testing, linting, and formatting tools

## 🚀 Running the Application

### Using Scripts
```bash
# Start the application
python scripts/start.py

# Run tests
python scripts/test.py
```

### Using UV
```bash
# Install dependencies
uv pip install -e .

# Start development server
uv run uvicorn pha.main:app --host 0.0.0.0 --port 8000 --reload

# Run tests
uv run pytest
```

### Using Python Module
```bash
# From project root
python -m uvicorn pha.main:app --host 0.0.0.0 --port 8000 --reload
```

## 📋 Benefits

1. **🎯 Standardized Structure**: Follows Python packaging best practices
2. **📈 Scalable**: Easy to add new API versions and features
3. **🧪 Better Testing**: Organized test suite with proper separation
4. **📚 Centralized Docs**: All documentation in one place
5. **🔧 Modern Tooling**: Updated pyproject.toml with dev tools
6. **🚀 Production Ready**: Clean deployment structure

## 🔧 Development Tools

The new structure includes configuration for:
- **pytest**: Testing framework
- **black**: Code formatting
- **isort**: Import sorting
- **flake8**: Linting
- **mypy**: Type checking
- **coverage**: Test coverage reporting

## 📝 Migration Notes

- All import statements have been updated
- Old `backend/` directory structure preserved for reference
- New structure is backward compatible with existing functionality
- Environment variables and configuration remain unchanged