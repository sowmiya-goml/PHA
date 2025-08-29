"""Database connection data models."""

from typing import Optional, Dict, Any
from datetime import datetime
from bson import ObjectId


class DatabaseConnection:
    """Database connection model for MongoDB operations."""
    
    def __init__(
        self,
        connection_name: str,
        database_type: str,
        host: str,
        port: int,
        database_name: str,
        username: str,
        password: str,
        additional_notes: Optional[str] = None,
        _id: Optional[ObjectId] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None
    ):
        self._id = _id
        self.connection_name = connection_name
        self.database_type = database_type
        self.host = host
        self.port = port
        self.database_name = database_name
        self.username = username
        self.password = password
        self.additional_notes = additional_notes
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary for MongoDB storage."""
        return {
            "connection_name": self.connection_name,
            "database_type": self.database_type,
            "host": self.host,
            "port": self.port,
            "database_name": self.database_name,
            "username": self.username,
            "password": self.password,
            "additional_notes": self.additional_notes,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DatabaseConnection":
        """Create model instance from MongoDB document."""
        return cls(
            _id=data.get("_id"),
            connection_name=data["connection_name"],
            database_type=data["database_type"],
            host=data["host"],
            port=data["port"],
            database_name=data["database_name"],
            username=data["username"],
            password=data["password"],
            additional_notes=data.get("additional_notes"),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at")
        )
    
    def update_timestamp(self):
        """Update the last modified timestamp."""
        self.updated_at = datetime.utcnow()
