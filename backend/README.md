# PHA Database Connection Manager

Simple FastAPI app to store database credentials in MongoDB.

## What it does
- Store database connection details (host, port, username, password)
- Retrieve stored connections
- Test database connections
- Basic CRUD operations

## Quick Start
1. Make sure MongoDB is running on localhost:27017
2. Run: `start.bat`
3. Access: http://localhost:8000/docs

## Files
- `main.py` - Main FastAPI application
- `cli_client.py` - Simple CLI to test the API
- `start.bat` - Startup script
- `.env` - MongoDB configuration

No Docker, no complex authentication, just basic database connection storage.
