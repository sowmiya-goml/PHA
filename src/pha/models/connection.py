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
        connection_string: str,
        additional_notes: Optional[str] = None,
        # Legacy fields for backward compatibility
        host: Optional[str] = None,
        port: Optional[int] = None,
        database_name: Optional[str] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
        _id: Optional[ObjectId] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None
    ):
        self._id = _id
        self.connection_name = connection_name
        self.database_type = database_type
        self.connection_string = connection_string
        self.additional_notes = additional_notes
        
        # Legacy fields (for backward compatibility with existing code)
        self.host = host
        self.port = port
        self.database_name = database_name
        self.username = username
        self.password = password
        
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary for MongoDB storage."""
        return {
            "connection_name": self.connection_name,
            "database_type": self.database_type,
            "connection_string": self.connection_string,
            "additional_notes": self.additional_notes,
            # Legacy fields (can be None)
            "host": self.host,
            "port": self.port,
            "database_name": self.database_name,
            "username": self.username,
            "password": self.password,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DatabaseConnection":
        """Create model instance from MongoDB document."""
        # Handle backward compatibility - if connection_string doesn't exist, create from legacy fields
        connection_string = data.get("connection_string")
        if not connection_string:
            # Generate connection string from legacy fields for backward compatibility
            host = data.get("host", "localhost")
            port = data.get("port", 3306)  # Default to MySQL port
            username = data.get("username", "")
            password = data.get("password", "")
            database_name = data.get("database_name", "")
            database_type = data.get("database_type", "mysql").lower()
            
            if database_type in ["mysql", "aurora_mysql"]:
                connection_string = f"mysql://{username}:{password}@{host}:{port}/{database_name}"
            elif database_type in ["postgresql", "aurora_postgresql"]:
                connection_string = f"postgresql://{username}:{password}@{host}:{port}/{database_name}"
            elif database_type == "mongodb":
                connection_string = f"mongodb://{username}:{password}@{host}:{port}/{database_name}"
            elif database_type == "sql_server":
                connection_string = f"Server={host},{port};Database={database_name};User Id={username};Password={password};"
            elif database_type == "oracle":
                connection_string = f"oracle://{username}:{password}@{host}:{port}/{database_name}"
            else:
                connection_string = f"{database_type}://{username}:{password}@{host}:{port}/{database_name}"
        
        return cls(
            _id=data.get("_id"),
            connection_name=data["connection_name"],
            database_type=data["database_type"],
            connection_string=connection_string,
            additional_notes=data.get("additional_notes"),
            # Legacy fields for backward compatibility
            host=data.get("host"),
            port=data.get("port"),
            database_name=data.get("database_name"),
            username=data.get("username"),
            password=data.get("password"),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at")
        )
    
    def update_timestamp(self):
        """Update the last modified timestamp."""
        self.updated_at = datetime.utcnow()
