"""Database connection service layer for business logic."""

from typing import List, Optional
from bson import ObjectId
from datetime import datetime

from app.models.connection import DatabaseConnection
from app.schemas.connection import (
    DatabaseConnectionCreate,
    DatabaseConnectionUpdate,
    DatabaseConnectionResponse,
    ConnectionTestResult
)
from app.db.session import DatabaseManager


class ConnectionService:
    """Service class for database connection operations."""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
    
    async def create_connection(self, connection_data: DatabaseConnectionCreate) -> DatabaseConnectionResponse:
        """Create a new database connection."""
        collection = self.db_manager.get_connections_collection()
        
        # Create connection model
        connection = DatabaseConnection(
            connection_name=connection_data.connection_name,
            database_type=connection_data.database_type,
            host=connection_data.host,
            port=connection_data.port,
            database_name=connection_data.database_name,
            username=connection_data.username,
            password=connection_data.password,
            additional_notes=connection_data.additional_notes
        )
        
        # Insert into database
        connection_doc = connection.to_dict()
        result = collection.insert_one(connection_doc)
        connection._id = result.inserted_id
        
        return DatabaseConnectionResponse(
            id=str(connection._id),
            connection_name=connection.connection_name,
            database_type=connection.database_type,
            host=connection.host,
            port=connection.port,
            database_name=connection.database_name,
            username=connection.username,
            password=connection.password,
            additional_notes=connection.additional_notes,
            created_at=connection.created_at,
            updated_at=connection.updated_at
        )
    
    async def get_all_connections(self) -> List[DatabaseConnectionResponse]:
        """Get all database connections."""
        collection = self.db_manager.get_connections_collection()
        connections = []
        
        for doc in collection.find():
            connection = DatabaseConnection.from_dict(doc)
            connections.append(DatabaseConnectionResponse(
                id=str(connection._id),
                connection_name=connection.connection_name,
                database_type=connection.database_type,
                host=connection.host,
                port=connection.port,
                database_name=connection.database_name,
                username=connection.username,
                password=connection.password,
                additional_notes=connection.additional_notes,
                created_at=connection.created_at,
                updated_at=connection.updated_at
            ))
        
        return connections
    
    async def get_connection_by_id(self, connection_id: str) -> Optional[DatabaseConnectionResponse]:
        """Get a database connection by ID."""
        collection = self.db_manager.get_connections_collection()
        
        try:
            doc = collection.find_one({"_id": ObjectId(connection_id)})
            if not doc:
                return None
            
            connection = DatabaseConnection.from_dict(doc)
            return DatabaseConnectionResponse(
                id=str(connection._id),
                connection_name=connection.connection_name,
                database_type=connection.database_type,
                host=connection.host,
                port=connection.port,
                database_name=connection.database_name,
                username=connection.username,
                password=connection.password,
                additional_notes=connection.additional_notes,
                created_at=connection.created_at,
                updated_at=connection.updated_at
            )
        except Exception:
            return None
    
    async def update_connection(
        self, 
        connection_id: str, 
        update_data: DatabaseConnectionUpdate
    ) -> Optional[DatabaseConnectionResponse]:
        """Update a database connection."""
        collection = self.db_manager.get_connections_collection()
        
        try:
            # Build update document
            update_doc = {}
            if update_data.connection_name is not None:
                update_doc["connection_name"] = update_data.connection_name
            if update_data.database_type is not None:
                update_doc["database_type"] = update_data.database_type
            if update_data.host is not None:
                update_doc["host"] = update_data.host
            if update_data.port is not None:
                update_doc["port"] = update_data.port
            if update_data.database_name is not None:
                update_doc["database_name"] = update_data.database_name
            if update_data.username is not None:
                update_doc["username"] = update_data.username
            if update_data.password is not None:
                update_doc["password"] = update_data.password
            if update_data.additional_notes is not None:
                update_doc["additional_notes"] = update_data.additional_notes
            
            update_doc["updated_at"] = datetime.utcnow()
            
            result = collection.update_one(
                {"_id": ObjectId(connection_id)},
                {"$set": update_doc}
            )
            
            if result.matched_count == 0:
                return None
            
            # Return updated connection
            return await self.get_connection_by_id(connection_id)
            
        except Exception:
            return None
    
    async def delete_connection(self, connection_id: str) -> bool:
        """Delete a database connection."""
        collection = self.db_manager.get_connections_collection()
        
        try:
            result = collection.delete_one({"_id": ObjectId(connection_id)})
            return result.deleted_count > 0
        except Exception:
            return False
    
    async def test_connection(self, connection_id: str) -> ConnectionTestResult:
        """Test a database connection."""
        collection = self.db_manager.get_connections_collection()
        
        try:
            doc = collection.find_one({"_id": ObjectId(connection_id)})
            if not doc:
                return ConnectionTestResult(
                    status="error",
                    message="Connection not found"
                )
            
            connection = DatabaseConnection.from_dict(doc)
            return await self._test_database_connection(connection)
            
        except Exception as e:
            return ConnectionTestResult(
                status="error",
                message=f"Error testing connection: {str(e)}"
            )
    
    async def _test_database_connection(self, connection: DatabaseConnection) -> ConnectionTestResult:
        """Test the actual database connection based on type."""
        db_type = connection.database_type.lower()
        
        if db_type == "mysql":
            return await self._test_mysql_connection(connection)
        elif db_type == "postgresql":
            return await self._test_postgresql_connection(connection)
        elif db_type == "mongodb":
            return await self._test_mongodb_connection(connection)
        else:
            return ConnectionTestResult(
                status="info",
                message=f"Connection test not implemented for {db_type}"
            )
    
    async def _test_mysql_connection(self, connection: DatabaseConnection) -> ConnectionTestResult:
        """Test MySQL connection."""
        try:
            import mysql.connector
            conn = mysql.connector.connect(
                host=connection.host,
                port=connection.port,
                user=connection.username,
                password=connection.password,
                database=connection.database_name
            )
            conn.close()
            return ConnectionTestResult(status="success", message="MySQL connection successful")
        except ImportError:
            return ConnectionTestResult(
                status="error",
                message="MySQL connector not installed. Run: pip install mysql-connector-python"
            )
        except Exception as e:
            return ConnectionTestResult(status="error", message=f"MySQL connection failed: {str(e)}")
    
    async def _test_postgresql_connection(self, connection: DatabaseConnection) -> ConnectionTestResult:
        """Test PostgreSQL connection."""
        try:
            import psycopg2
            conn = psycopg2.connect(
                host=connection.host,
                port=connection.port,
                user=connection.username,
                password=connection.password,
                database=connection.database_name
            )
            conn.close()
            return ConnectionTestResult(status="success", message="PostgreSQL connection successful")
        except ImportError:
            return ConnectionTestResult(
                status="error",
                message="PostgreSQL connector not installed. Run: pip install psycopg2-binary"
            )
        except Exception as e:
            return ConnectionTestResult(status="error", message=f"PostgreSQL connection failed: {str(e)}")
    
    async def _test_mongodb_connection(self, connection: DatabaseConnection) -> ConnectionTestResult:
        """Test MongoDB connection."""
        try:
            from pymongo import MongoClient
            mongo_uri = f"mongodb://{connection.username}:{connection.password}@{connection.host}:{connection.port}/{connection.database_name}"
            test_client = MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)
            test_client.admin.command('ping')
            test_client.close()
            return ConnectionTestResult(status="success", message="MongoDB connection successful")
        except Exception as e:
            return ConnectionTestResult(status="error", message=f"MongoDB connection failed: {str(e)}")
