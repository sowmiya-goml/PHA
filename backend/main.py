from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from pymongo import MongoClient
from typing import List, Optional
import os
from dotenv import load_dotenv
from datetime import datetime
from bson import ObjectId

# Load environment variables
load_dotenv()

# Create FastAPI app
app = FastAPI(title="PHA Database Connection Manager", version="1.0.0")

# MongoDB connection
MONGODB_URL = os.getenv("MONGODB_URL")
DATABASE_NAME = os.getenv("DATABASE_NAME", "pha_connections")

try:
    client = MongoClient(MONGODB_URL, serverSelectionTimeoutMS=5000)
    db = client[DATABASE_NAME]
    connections_collection = db.database_connections
    # Test connection
    client.admin.command('ping')
    print("✅ Connected to MongoDB successfully")
except Exception as e:
    print(f"⚠️  MongoDB connection failed: {e}")
    print("Starting without database connection...")
    client = None
    db = None
    connections_collection = None

# Pydantic models
class DatabaseConnection(BaseModel):
    connection_name: str
    database_type: str  # MySQL, PostgreSQL, MongoDB, etc.
    host: str
    port: int
    database_name: str
    username: str
    password: str
    additional_notes: Optional[str] = None

class DatabaseConnectionResponse(BaseModel):
    id: str
    connection_name: str
    database_type: str
    host: str
    port: int
    database_name: str
    username: str
    password: str
    additional_notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime

class ConnectionTestResult(BaseModel):
    status: str
    message: str

@app.get("/")
async def root():
    return {"message": "PHA Database Connection Manager is running"}

@app.post("/connections", response_model=DatabaseConnectionResponse)
async def create_connection(connection: DatabaseConnection):
    """Store database connection details"""
    if connections_collection is None:
        raise HTTPException(status_code=503, detail="Database not available")
    
    connection_doc = {
        "connection_name": connection.connection_name,
        "database_type": connection.database_type,
        "host": connection.host,
        "port": connection.port,
        "database_name": connection.database_name,
        "username": connection.username,
        "password": connection.password,
        "additional_notes": connection.additional_notes,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    result = connections_collection.insert_one(connection_doc)
    connection_doc["_id"] = result.inserted_id
    
    return DatabaseConnectionResponse(
        id=str(connection_doc["_id"]),
        connection_name=connection_doc["connection_name"],
        database_type=connection_doc["database_type"],
        host=connection_doc["host"],
        port=connection_doc["port"],
        database_name=connection_doc["database_name"],
        username=connection_doc["username"],
        password=connection_doc["password"],
        additional_notes=connection_doc["additional_notes"],
        created_at=connection_doc["created_at"],
        updated_at=connection_doc["updated_at"]
    )

@app.get("/connections", response_model=List[DatabaseConnectionResponse])
async def get_all_connections():
    """Get all stored database connections"""
    connections = []
    for doc in connections_collection.find():
        connections.append(DatabaseConnectionResponse(
            id=str(doc["_id"]),
            connection_name=doc["connection_name"],
            database_type=doc["database_type"],
            host=doc["host"],
            port=doc["port"],
            database_name=doc["database_name"],
            username=doc["username"],
            password=doc["password"],
            additional_notes=doc.get("additional_notes"),
            created_at=doc["created_at"],
            updated_at=doc["updated_at"]
        ))
    return connections

@app.get("/connections/{connection_id}", response_model=DatabaseConnectionResponse)
async def get_connection(connection_id: str):
    """Get a specific database connection by ID"""
    try:
        doc = connections_collection.find_one({"_id": ObjectId(connection_id)})
        if not doc:
            raise HTTPException(status_code=404, detail="Connection not found")
        
        return DatabaseConnectionResponse(
            id=str(doc["_id"]),
            connection_name=doc["connection_name"],
            database_type=doc["database_type"],
            host=doc["host"],
            port=doc["port"],
            database_name=doc["database_name"],
            username=doc["username"],
            password=doc["password"],
            additional_notes=doc.get("additional_notes"),
            created_at=doc["created_at"],
            updated_at=doc["updated_at"]
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid connection ID: {str(e)}")

@app.delete("/connections/{connection_id}")
async def delete_connection(connection_id: str):
    """Delete a database connection"""
    try:
        result = connections_collection.delete_one({"_id": ObjectId(connection_id)})
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Connection not found")
        return {"message": "Connection deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid connection ID: {str(e)}")

@app.post("/connections/{connection_id}/test", response_model=ConnectionTestResult)
async def test_connection(connection_id: str):
    """Test a database connection"""
    try:
        doc = connections_collection.find_one({"_id": ObjectId(connection_id)})
        if not doc:
            raise HTTPException(status_code=404, detail="Connection not found")
        
        # Basic connection test logic based on database type
        db_type = doc["database_type"].lower()
        
        if db_type == "mysql":
            try:
                import mysql.connector
                conn = mysql.connector.connect(
                    host=doc["host"],
                    port=doc["port"],
                    user=doc["username"],
                    password=doc["password"],
                    database=doc["database_name"]
                )
                conn.close()
                return ConnectionTestResult(status="success", message="MySQL connection successful")
            except ImportError:
                return ConnectionTestResult(status="error", message="MySQL connector not installed. Run: pip install mysql-connector-python")
            except Exception as e:
                return ConnectionTestResult(status="error", message=f"MySQL connection failed: {str(e)}")
        
        elif db_type == "postgresql":
            try:
                import psycopg2
                conn = psycopg2.connect(
                    host=doc["host"],
                    port=doc["port"],
                    user=doc["username"],
                    password=doc["password"],
                    database=doc["database_name"]
                )
                conn.close()
                return ConnectionTestResult(status="success", message="PostgreSQL connection successful")
            except ImportError:
                return ConnectionTestResult(status="error", message="PostgreSQL connector not installed. Run: pip install psycopg2-binary")
            except Exception as e:
                return ConnectionTestResult(status="error", message=f"PostgreSQL connection failed: {str(e)}")
        
        elif db_type == "mongodb":
            try:
                from pymongo import MongoClient
                mongo_uri = f"mongodb://{doc['username']}:{doc['password']}@{doc['host']}:{doc['port']}/{doc['database_name']}"
                test_client = MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)
                test_client.admin.command('ping')
                test_client.close()
                return ConnectionTestResult(status="success", message="MongoDB connection successful")
            except Exception as e:
                return ConnectionTestResult(status="error", message=f"MongoDB connection failed: {str(e)}")
        
        else:
            return ConnectionTestResult(status="info", message=f"Connection test not implemented for {db_type}")
            
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error testing connection: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
