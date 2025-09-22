"""Schemas for database operations including query execution and results."""

from typing import List, Dict, Any, Optional, Union
from pydantic import BaseModel, Field
from datetime import datetime


class QueryExecutionRequest(BaseModel):
    """Schema for query execution request."""
    connection_id: str = Field(..., description="Database connection ID")
    patient_id: str = Field(..., description="Patient ID for data extraction")
    query_type: str = Field(
        default="comprehensive", 
        description="Type of query: comprehensive, clinical, billing, basic"
    )
    execute_query: bool = Field(
        default=True, 
        description="Whether to execute the query against the database"
    )
    limit: Optional[int] = Field(
        default=100, 
        description="Maximum number of records to return (safety limit)"
    )


class DatabaseQueryResult(BaseModel):
    """Schema for individual database query result."""
    table_name: Optional[str] = Field(None, description="Name of the table/collection queried")
    query: str = Field(..., description="The actual query executed")
    row_count: int = Field(..., description="Number of rows returned")
    data: List[Dict[str, Any]] = Field(..., description="The actual data returned from the query")
    execution_time_ms: float = Field(..., description="Query execution time in milliseconds")


class QueryExecutionResponse(BaseModel):
    """Schema for complete query execution response."""
    # Query generation info (from existing endpoint)
    generated_query: str = Field(..., description="Generated SQL/MongoDB query")
    patient_id: str = Field(..., description="Patient ID used in the query")
    query_type: str = Field(..., description="Type of query executed")
    model_used: str = Field(..., description="AI model used for query generation")
    schema_tables_count: int = Field(..., description="Number of tables/collections in the schema")
    status: str = Field(..., description="Overall operation status")
    timestamp: str = Field(..., description="ISO timestamp when operation completed")
    
    # Database connection info
    connection_info: Dict[str, Any] = Field(..., description="Database connection information")
    
    # Query execution results (new functionality)
    query_executed: bool = Field(..., description="Whether the query was actually executed")
    execution_results: Optional[List[DatabaseQueryResult]] = Field(
        None, 
        description="Results from executing the query against the database"
    )
    total_records_found: Optional[int] = Field(
        None, 
        description="Total number of records found across all queries"
    )
    total_execution_time_ms: Optional[float] = Field(
        None, 
        description="Total time taken to execute all queries"
    )
    
    # Error handling
    execution_errors: Optional[List[str]] = Field(
        None, 
        description="Any errors encountered during query execution"
    )


class DatabaseConnectionInfo(BaseModel):
    """Schema for database connection information used in query execution."""
    connection_id: str = Field(..., description="Database connection ID")
    database_type: str = Field(..., description="Type of database (postgresql, mysql, mongodb, etc.)")
    database_name: str = Field(..., description="Name of the database")
    connection_string: str = Field(..., description="Database connection string")
    host: Optional[str] = Field(None, description="Database host")
    port: Optional[int] = Field(None, description="Database port")
    username: Optional[str] = Field(None, description="Database username")
    password: Optional[str] = Field(None, description="Database password")

class QueryValidationResult(BaseModel):
    """Schema for query validation results."""
    is_valid: bool = Field(..., description="Whether the query is considered safe to execute")
    validation_errors: List[str] = Field(default_factory=list, description="List of validation errors if any")
    is_read_only: bool = Field(..., description="Whether the query is read-only (SELECT/FIND operations only)")
    estimated_complexity: str = Field(..., description="Estimated query complexity: low, medium, high")
    safety_score: float = Field(..., description="Safety score from 0.0 to 1.0 (1.0 = completely safe)")
