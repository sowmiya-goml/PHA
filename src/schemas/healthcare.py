"""Healthcare query generation schemas for request/response validation."""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime


class ConnectionInfo(BaseModel):
    """Connection information schema."""
    connection_id: str = Field(..., description="Database connection ID")
    database_type: str = Field(..., description="Type of database")
    database_name: str = Field(..., description="Name of the database")  
    total_tables: int = Field(..., description="Total number of tables/collections")


class HealthcareQueryResponse(BaseModel):
    """Schema for healthcare query generation response."""
    generated_query: str = Field(..., description="Generated SQL/MongoDB query")
    patient_id: str = Field(..., description="Patient ID used in the query")
    query_type: str = Field(..., description="Type of query (comprehensive, clinical, billing, basic)")
    model_used: str = Field(..., description="AI model used for query generation")
    schema_tables_count: int = Field(..., description="Number of tables/collections in the schema")
    status: str = Field(..., description="Query generation status")
    timestamp: str = Field(..., description="ISO timestamp when query was generated")
    connection_info: ConnectionInfo = Field(..., description="Database connection information")
    
    
    class config:
        populate_by_name = True

class HealthcareQueryError(BaseModel):
    """Schema for healthcare query generation error response."""
    error: str = Field(..., description="Error message")
    patient_id: str = Field(..., description="Patient ID that was requested")
    query_type: str = Field(..., description="Type of query that was requested")
    status: str = Field(..., description="Error status")
    timestamp: str = Field(..., description="ISO timestamp when error occurred")
    connection_info: Optional[ConnectionInfo] = Field(None, description="Database connection information if available")