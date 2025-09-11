"""Database connection schemas for request/response validation."""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime


class DatabaseConnectionBase(BaseModel):
    """Base schema for database connection."""
    connection_name: str = Field(..., description="Name for the database connection")
    database_type: str = Field(..., description="Type of database (MySQL, PostgreSQL, MongoDB, etc.)")
    connection_string: str = Field(..., description="Database connection string URI")
    additional_notes: Optional[str] = Field(None, description="Additional notes or configuration")
    
    # Optional: Keep legacy fields for backward compatibility (can be removed later)
    host: Optional[str] = Field(None, description="Database host address (legacy - use connection_string)")
    port: Optional[int] = Field(None, description="Database port number (legacy - use connection_string)")
    database_name: Optional[str] = Field(None, description="Name of the database (legacy - use connection_string)")
    username: Optional[str] = Field(None, description="Database username (legacy - use connection_string)")
    password: Optional[str] = Field(None, description="Database password (legacy - use connection_string)")


class DatabaseConnectionCreate(DatabaseConnectionBase):
    """Schema for creating a database connection."""
    pass


class DatabaseConnectionUpdate(BaseModel):
    """Schema for updating a database connection."""
    connection_name: Optional[str] = None
    database_type: Optional[str] = None
    connection_string: Optional[str] = None
    additional_notes: Optional[str] = None
    # Legacy fields (optional for backward compatibility)
    host: Optional[str] = None
    port: Optional[int] = None
    database_name: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None


class DatabaseConnectionResponse(DatabaseConnectionBase):
    """Schema for database connection response."""
    id: str = Field(..., description="Unique identifier for the connection")
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
