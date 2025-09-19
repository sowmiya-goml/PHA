"""Database connection API routes."""

from fastapi import APIRouter, HTTPException, Depends
from typing import List

from pha.schemas.connection import (
    DatabaseConnectionCreate,
    DatabaseConnectionUpdate,
    DatabaseConnectionResponse,
    ConnectionTestResult,
    DatabaseSchemaResult
)
from pha.services.connection_service import ConnectionService
from pha.db.session import get_database_manager, DatabaseManager

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


@router.post("/", response_model=DatabaseConnectionResponse, status_code=201)
async def create_connection(
    connection: DatabaseConnectionCreate,
    service: ConnectionService = Depends(get_connection_service)
):
    """Create a new database connection."""
    try:
        # Simple auto-detection logic that ALWAYS works
        original_type = connection.database_type.lower()
        connection_string_lower = connection.connection_string.lower()
        
        # Auto-detect if the type is generic or unsupported
        if original_type in ['sql', 'database', 'db'] or original_type not in [
            'mysql', 'aurora-mysql', 'postgresql', 'aurora-postgresql', 
            'mongodb', 'oracle', 'oracle-db', 'sql-server', 'mssql', 'sqlserver', 'snowflake'
        ]:
            # Direct string matching for auto-detection
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
                final_db_type = 'postgresql'  # Default fallback
        else:
            final_db_type = connection.database_type
        
        # Create new connection object with correct type
        corrected_connection = DatabaseConnectionCreate(
            database_type=final_db_type,
            connection_string=connection.connection_string
        )
        
        return await service.create_connection(corrected_connection)
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
    """
    Get the schema of a database connection with unified multi-database support.
    
    **Supported Database Types:**
    - PostgreSQL / Aurora PostgreSQL
    - MySQL / Aurora MySQL  
    - Oracle Database
    - Microsoft SQL Server
    - MongoDB
    
    **Returns:**
    - **tables**: List of tables/collections with columns and metadata
    - **unified_schema**: Consistent JSON format across all database types
    - **database_info**: Version, connection details, extraction timestamp
    - **summary**: Statistics (table count, column count, total rows)
    
    **Unified Schema Format:**
    The response includes a `unified_schema` field with consistent structure
    optimized for AI query generation and database-agnostic processing.
    
    **Example Usage:**
    ```
    GET /api/v1/connections/507f1f77bcf86cd799439011/schema
    ```
    
    **AI Integration Ready:**
    Use the `unified_schema.database_info.type` and `unified_schema.tables` 
    for AWS Bedrock query generation.
    """
    try:
        return await service.get_database_schema(connection_id)
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve database schema: {str(e)}")
