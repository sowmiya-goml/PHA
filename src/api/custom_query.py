"""Custom query API endpoint for dynamic database queries."""

from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Dict, Any
from schemas.custom_query import CustomQueryRequest, CustomQueryResponse
from services.custom_query_service import CustomQueryService
from services.bedrock_service import BedrockService
from services.database_operation_service import DatabaseOperationService
from db.session import get_database_manager, DatabaseManager

router = APIRouter(
    prefix="/custom-query",
    tags=["Custom Query Agent"],
    responses={404: {"description": "Not found"}}
)


def get_custom_query_service(db_manager: DatabaseManager = Depends(get_database_manager)) -> CustomQueryService:
    """Dependency to get custom query service."""
    bedrock_service = BedrockService(db_manager)
    db_ops_service = DatabaseOperationService(db_manager)
    return CustomQueryService(db_manager, bedrock_service, db_ops_service)


@router.post("/process", response_model=CustomQueryResponse)
async def process_custom_query(
    request: CustomQueryRequest,
    service: CustomQueryService = Depends(get_custom_query_service)
):
    """
    Process a custom database query with natural language input.
    
    This endpoint:
    1. Takes a connection ID and natural language query
    2. Extracts the database schema
    3. Generates SQL/NoSQL query using AWS Bedrock
    4. Executes the query against the database
    5. Generates a comprehensive report based on the results
    
    Example usage:
    POST /api/v1/custom-query/process
    {
        "connection_id": "507f1f77bcf86cd799439011",
        "user_query": "Show me all patients admitted in the last month with their diagnosis"
    }
    """
    try:
        result = await service.process_custom_query(
            connection_id=request.connection_id,
            user_query=request.user_query
        )
        
        return CustomQueryResponse(**result)
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing custom query: {str(e)}"
        )


@router.get("/process-get", response_model=CustomQueryResponse)
async def process_custom_query_get(
    connection_id: str = Query(..., description="Database connection ID"),
    user_query: str = Query(..., description="Natural language query describing what data is needed"),
    service: CustomQueryService = Depends(get_custom_query_service)
):
    """
    Process a custom database query using GET method.
    
    Alternative GET endpoint for the same functionality as POST /process.
    Useful for simple queries and testing.
    
    Example usage:
    GET /api/v1/custom-query/process-get?connection_id=507f1f77bcf86cd799439011&user_query=Show me all patients with diabetes
    """
    try:
        result = await service.process_custom_query(
            connection_id=connection_id,
            user_query=user_query
        )
        
        return CustomQueryResponse(**result)
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing custom query: {str(e)}"
        )
    
    