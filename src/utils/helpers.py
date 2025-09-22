"""Utility functions for the PHA Database Connection Manager."""

import logging
from datetime import datetime
from typing import Any, Dict
from bson import ObjectId


def setup_logging(level: str = "INFO") -> None:
    """Setup application logging configuration."""
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )


def serialize_object_id(obj: Any) -> Any:
    """Convert ObjectId to string for JSON serialization."""
    if isinstance(obj, ObjectId):
        return str(obj)
    elif isinstance(obj, dict):
        return {key: serialize_object_id(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [serialize_object_id(item) for item in obj]
    return obj


def validate_connection_parameters(connection_data: Dict[str, Any]) -> bool:
    """Validate database connection parameters."""
    required_fields = [
        "connection_name", "database_type", "host", 
        "port", "database_name", "username", "password"
    ]
    
    for field in required_fields:
        if field not in connection_data or not connection_data[field]:
            return False
    
    # Validate port is a positive integer
    try:
        port = int(connection_data["port"])
        if port <= 0 or port > 65535:
            return False
    except (ValueError, TypeError):
        return False
    
    return True


def get_current_timestamp() -> datetime:
    """Get current UTC timestamp."""
    return datetime.utcnow()


def mask_password(connection_data: Dict[str, Any]) -> Dict[str, Any]:
    """Mask password in connection data for logging."""
    masked_data = connection_data.copy()
    if "password" in masked_data:
        masked_data["password"] = "***masked***"
    return masked_data
