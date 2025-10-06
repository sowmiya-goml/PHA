"""Schemas for custom query operations."""

from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
from datetime import datetime


class CustomQueryRequest(BaseModel):
    """Schema for custom query request."""
    connection_id: str = Field(..., description="Database connection ID")
    user_query: str = Field(..., description="Natural language query describing what data is needed")


class CustomQueryResponse(BaseModel):
    """Schema for custom query response."""
    status: str = Field(..., description="Operation status (success, error)")
    user_query: Optional[str] = Field(None, description="Original user query")
    generated_query: Optional[str] = Field(None, description="Generated SQL/NoSQL query")
    data: Optional[List[Dict[str, Any]]] = Field(None, description="Retrieved data from database")
    report: Optional[str] = Field(None, description="Generated comprehensive report")
    records_count: Optional[int] = Field(None, description="Number of records retrieved")
    execution_time_ms: Optional[float] = Field(None, description="Query execution time in milliseconds")
    database_info: Optional[Dict[str, Any]] = Field(None, description="Database connection information")
    error: Optional[str] = Field(None, description="Error message if operation failed")
    timestamp: str = Field(..., description="ISO timestamp when operation completed")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }