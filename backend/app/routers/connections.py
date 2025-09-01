"""Database connection API routes."""

from fastapi import APIRouter, HTTPException, Depends
from typing import List

from app.schemas.connection import (
    DatabaseConnectionCreate,
    DatabaseConnectionUpdate,
    DatabaseConnectionResponse,
    ConnectionTestResult,
    DatabaseSchemaResult
)
from app.services.connection_service import ConnectionService
from app.db.session import get_database_manager, DatabaseManager

router = APIRouter(
    prefix="/connections",
    tags=["Database Connections"],
    responses={404: {"description": "Not found"}}
)


def get_connection_service(db_manager: DatabaseManager = Depends(get_database_manager)) -> ConnectionService:
    """Dependency to get connection service."""
    return ConnectionService(db_manager)


@router.post("/", response_model=DatabaseConnectionResponse, status_code=201)
async def create_connection(
    connection: DatabaseConnectionCreate,
    service: ConnectionService = Depends(get_connection_service)
):
    """Create a new database connection."""
    try:
        return await service.create_connection(connection)
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create connection: {str(e)}")


@router.get("/", response_model=List[DatabaseConnectionResponse])
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


@router.get("/{connection_id}", response_model=DatabaseConnectionResponse)
async def get_connection(
    connection_id: str,
    service: ConnectionService = Depends(get_connection_service)
):
    """Get a specific database connection by ID."""
    try:
        connection = await service.get_connection_by_id(connection_id)
        if not connection:
            raise HTTPException(status_code=404, detail="Connection not found")
        return connection
    except HTTPException:
        raise
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid connection ID: {str(e)}")


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


@router.post("/{connection_id}/test", response_model=ConnectionTestResult)
async def test_connection(
    connection_id: str,
    service: ConnectionService = Depends(get_connection_service)
):
    """Test a database connection."""
    try:
        return await service.test_connection(connection_id)
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to test connection: {str(e)}")


@router.get("/{connection_id}/schema", response_model=DatabaseSchemaResult)
async def get_database_schema(
    connection_id: str,
    service: ConnectionService = Depends(get_connection_service)
):
    """Get the schema of a database connection."""
    try:
        return await service.get_database_schema(connection_id)
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve database schema: {str(e)}")


@router.get("/{connection_id}/databases")
async def list_databases(
    connection_id: str,
    service: ConnectionService = Depends(get_connection_service)
):
    """List all available databases for a connection."""
    try:
        return await service.list_available_databases(connection_id)
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list databases: {str(e)}")
