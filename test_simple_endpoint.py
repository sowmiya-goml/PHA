#!/usr/bin/env python3
"""Simple test endpoint to debug the dashboard issue."""

from fastapi import FastAPI

app = FastAPI()

@app.get("/test")
async def test_endpoint():
    """Simple test endpoint."""
    return {"message": "Server is working", "status": "ok"}

@app.get("/test-dashboard")
async def test_dashboard():
    """Test dashboard endpoint without dependencies."""
    return {
        "patient_id": "687b0aca-ca63-4926-800b-90d5e92e5a0a",
        "connection_id": "68c8ea1dcee430be497cee25",
        "data_type": "heart_rate",
        "data": [
            {
                "heart_rate": 75,
                "status": "normal", 
                "recorded_at": "2024-01-15T10:30:00Z",
                "device_id": "monitor_001"
            }
        ],
        "message": "Test data - real database integration in progress"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)