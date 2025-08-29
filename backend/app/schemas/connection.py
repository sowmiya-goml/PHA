"""Database connection schemas for request/response validation."""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime


class DatabaseConnectionBase(BaseModel):
    """Base schema for database connection."""
    connection_name: str = Field(..., description="Name for the database connection")
    database_type: str = Field(..., description="Type of database (MySQL, PostgreSQL, MongoDB, etc.)")
    host: str = Field(..., description="Database host address")
    port: int = Field(..., description="Database port number")
    database_name: str = Field(..., description="Name of the database")
    username: str = Field(..., description="Database username")
    password: str = Field(..., description="Database password")
    additional_notes: Optional[str] = Field(None, description="Additional notes or configuration")


class DatabaseConnectionCreate(DatabaseConnectionBase):
    """Schema for creating a database connection."""
    pass


class DatabaseConnectionUpdate(BaseModel):
    """Schema for updating a database connection."""
    connection_name: Optional[str] = None
    database_type: Optional[str] = None
    host: Optional[str] = None
    port: Optional[int] = None
    database_name: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None
    additional_notes: Optional[str] = None


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
