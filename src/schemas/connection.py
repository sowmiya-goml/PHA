"""Database connection schemas for request/response validation."""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime


class DatabaseConnectionBase(BaseModel):
    """Base schema for database connection."""
    database_type: str = Field(..., description="Type of database (MySQL, PostgreSQL, MongoDB, Snowflake, Oracle, SQL Server)")
    connection_string: str = Field(..., description="Database connection string URI")
    
    # Auto-generated fields (not required in input)
    connection_name: Optional[str] = Field(None, description="Auto-generated name for the database connection")
    additional_notes: Optional[str] = Field(None, description="Additional notes or configuration")




class DatabaseConnectionUpdate(BaseModel):
    """Schema for updating a database connection."""
    database_type: Optional[str] = Field(None, description="Type of database")
    connection_string: Optional[str] = Field(None, description="Database connection string URI")
    connection_name: Optional[str] = Field(None, description="Name for the database connection")
    additional_notes: Optional[str] = Field(None, description="Additional notes or configuration")


class DatabaseConnectionResponse(BaseModel):
    """Schema for database connection response."""
    id: str = Field(..., description="Unique identifier for the connection")
    connection_name: str = Field(..., description="Auto-generated name for the database connection")
    database_type: str = Field(..., description="Type of database")
    connection_string: str = Field(..., description="Database connection string URI")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    
    model_config = ConfigDict(from_attributes=True)


class ConnectionTestRequest(BaseModel):
    """Schema for connection test request."""
    connection_id: str = Field(..., description="ID of the connection to test")


class ConnectionTestResult(BaseModel):
    """Schema for connection test result."""
    status: str = Field(..., description="Test status (success, error, info)")
    message: str = Field(..., description="Test result message")
    
    model_config = ConfigDict(from_attributes=True)


class DatabaseField(BaseModel):
    """Schema for database field information."""
    name: str = Field(..., description="Field/column name")
    type: str = Field(..., description="Field/column data type")
    nullable: Optional[bool] = Field(None, description="Whether field can be null")
    default: Optional[str] = Field(None, description="Default value")


class DatabaseTable(BaseModel):
    """Schema for database table/collection information."""
    name: str = Field(..., description="Table/collection name")
    type: str = Field(..., description="Type (table, collection, view)")
    fields: List[DatabaseField] = Field(..., description="List of fields/columns")
    row_count: Optional[int] = Field(None, description="Approximate number of rows/documents")


class DatabaseSchemaResult(BaseModel):
    """Schema for database schema result."""
    status: str = Field(..., description="Schema retrieval status (success, error)")
    message: str = Field(..., description="Status message")
    database_type: Optional[str] = Field(None, description="Type of database")
    database_name: Optional[str] = Field(None, description="Name of the database")
    tables: Optional[List[DatabaseTable]] = Field(None, description="List of tables/collections")
    unified_schema: Optional[dict] = Field(None, description="Unified JSON schema format across all databases")
    
    model_config = ConfigDict(from_attributes=True)

class CreateDBRequest(BaseModel):
    username: str
    password: str
    database_type: str
    connection_string: str

class LoginRequest(BaseModel):
    username: str
    password: str