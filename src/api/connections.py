"""Database connection API routes."""

from fastapi import APIRouter, HTTPException, Depends
from typing import List
from datetime import datetime

from schemas.connection import (
    LoginRequest,
    CreateDBRequest,
    DatabaseConnectionUpdate,
    DatabaseConnectionResponse,
    ConnectionTestResult,
    DatabaseSchemaResult
)
from services.connection_service import ConnectionService
from db.session import get_database_manager, DatabaseManager

router = APIRouter(
    prefix="/connections",
    tags=["Database Connections"],
    responses={404: {"description": "Not found"}}
)


def get_connection_service(db_manager: DatabaseManager = Depends(get_database_manager)) -> ConnectionService:
    """Dependency to get connection service."""
    if not db_manager.is_connected():
        raise HTTPException(
            status_code=503,
            detail="Database service unavailable. Please check MongoDB connection."
        )
    return ConnectionService(db_manager)


@router.post("/create_db_connection", response_model=ConnectionTestResult, status_code=201)
async def create_db_connection(
    request: CreateDBRequest,
    service: ConnectionService = Depends(get_connection_service)
):
    try:
        original_type = request.database_type.lower()
        connection_string_lower = request.connection_string.lower()

        if original_type in ['sql', 'database', 'db'] or original_type not in [
            'mysql', 'aurora-mysql', 'postgresql', 'aurora-postgresql',
            'mongodb', 'oracle', 'oracle-db', 'sql-server', 'mssql', 'sqlserver', 'snowflake'
        ]:
            if connection_string_lower.startswith('postgresql://') or connection_string_lower.startswith('postgres://'):
                final_db_type = 'postgresql'
            elif connection_string_lower.startswith('mysql://'):
                final_db_type = 'mysql'
            elif connection_string_lower.startswith('mongodb://') or connection_string_lower.startswith('mongodb+srv://'):
                final_db_type = 'mongodb'
            elif connection_string_lower.startswith('snowflake://'):
                final_db_type = 'snowflake'
            elif connection_string_lower.startswith('oracle://'):
                final_db_type = 'oracle'
            elif 'server=' in connection_string_lower and ('database=' in connection_string_lower or 'initial catalog=' in connection_string_lower):
                final_db_type = 'sqlserver'
            else:
                final_db_type = 'postgresql'
        else:
            final_db_type = request.database_type

        connection_data = {
            "username": request.username,
            "password": request.password,
            "database_type": final_db_type,
            "connection_string": request.connection_string,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }

        connection_response = await service.create_connection(connection_data)

        test_result = await service.test_connection(connection_response.id)
        if test_result.status.lower() == "success":
            return test_result
        else:
            raise HTTPException(status_code=400, detail=f"Connection test failed: {test_result.message}")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create & test connection: {str(e)}")


@router.post("/login")
async def login(
    request: LoginRequest,
    db_manager: DatabaseManager = Depends(get_database_manager)
):
    """Check if username/password exists in DB"""
    try:
        collection = db_manager.get_connections_collection()
        user = collection.find_one({"username": request.username, "password": request.password})

        if not user:
            raise HTTPException(status_code=401, detail="Invalid username or password")

        return {"message": "Login Success", "username": request.username}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Login failed: {str(e)}")
    
@router.get("/get_dbs", response_model=List[DatabaseConnectionResponse])
async def get_all_connections(
    service: ConnectionService = Depends(get_connection_service)
):
    """Get all database connections."""
    try:
        return await service.get_all_connections()
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve connections: {str(e)}")


@router.put("/{connection_id}", response_model=DatabaseConnectionResponse)
async def update_connection(
    connection_id: str,
    connection_update: DatabaseConnectionUpdate,
    service: ConnectionService = Depends(get_connection_service)
):
    """Update a database connection."""
    try:
        connection = await service.update_connection(connection_id, connection_update)
        if not connection:
            raise HTTPException(status_code=404, detail="Connection not found")
        return connection
    except HTTPException:
        raise
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to update connection: {str(e)}")


@router.delete("/{connection_id}")
async def delete_connection(
    connection_id: str,
    service: ConnectionService = Depends(get_connection_service)
):
    """Delete a database connection."""
    try:
        success = await service.delete_connection(connection_id)
        if not success:
            raise HTTPException(status_code=404, detail="Connection not found")
        return {"message": "Connection deleted successfully"}
    except HTTPException:
        raise
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to delete connection: {str(e)}")



@router.get("/{connection_id}/schema", response_model=DatabaseSchemaResult)
async def get_database_schema(
    connection_id: str,
    service: ConnectionService = Depends(get_connection_service)
):
    try:
        return await service.get_database_schema(connection_id)
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve database schema: {str(e)}")
