"""Database connection service layer for business logic."""

from typing import List, Optional, Dict, Any
from bson import ObjectId
from datetime import datetime
import urllib.parse
import re
import cx_Oracle
from models.connection import DatabaseConnection
from schemas.connection import (
    DatabaseConnectionUpdate,
    DatabaseConnectionResponse,
    ConnectionTestResult,
    DatabaseSchemaResult,
    DatabaseTable,
    DatabaseField
)
from db.session import DatabaseManager
from services.schema_extraction_service import DatabaseSchemaExtractor


class ConnectionService:
    """Service class for database connection operations."""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
        self.schema_extractor = DatabaseSchemaExtractor()
    
    def _auto_detect_database_type(self, connection_string: str) -> str:
        """Auto-detect database type from connection string."""
        connection_string_lower = connection_string.lower()
        
        if connection_string_lower.startswith(('postgresql://', 'postgres://')):
            return 'postgresql'
        elif connection_string_lower.startswith('mysql://'):
            return 'mysql'  
        elif connection_string_lower.startswith(('mongodb://', 'mongodb+srv://')):
            return 'mongodb'
        elif connection_string_lower.startswith('snowflake://'):
            return 'snowflake'
        elif connection_string_lower.startswith('oracle://'):
            return 'oracle'
        elif 'server=' in connection_string_lower and ('database=' in connection_string_lower or 'initial catalog=' in connection_string_lower):
            return 'sqlserver'
        else:
            return None
    
    def _is_supported_db_type(self, db_type: str) -> bool:
        """Check if a database type is supported."""
        supported_types = [
            "mysql", "aurora-mysql",
            "postgresql", "aurora-postgresql",
            "mongodb",
            "oracle", "oracle-db",
            "sql-server", "mssql", "sqlserver",
            "snowflake"
        ]
        return db_type in supported_types
    
    async def create_connection(self, connection_data: dict) -> DatabaseConnectionResponse:
        """Create a new database connection with username/password."""
        collection = self.db_manager.get_connections_collection()

        # Auto-generate connection name if not provided
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        connection_name = f"{connection_data['database_type'].lower()}connection{timestamp}"

        # Prepare connection doc (including username/password)
        connection_doc = {
            "connection_name": connection_name,
            "username": connection_data["username"],
            "password": connection_data["password"],   # ⚠️ In real apps hash this
            "database_type": connection_data["database_type"],
            "connection_string": connection_data["connection_string"],
            "created_at": connection_data.get("created_at"),
            "updated_at": connection_data.get("updated_at"),
        }

        # Insert into Mongo
        result = collection.insert_one(connection_doc)

        return DatabaseConnectionResponse(
            id=str(result.inserted_id),
            connection_name=connection_name,
            database_type=connection_data["database_type"],
            connection_string=connection_data["connection_string"],
            created_at=connection_data.get("created_at"),
            updated_at=connection_data.get("updated_at")
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
                connection_string=connection.connection_string,
                created_at=connection.created_at,
                updated_at=connection.updated_at
            ))
        
        return connections
    
    async def get_connection_by_id(self, connection_id: str) -> Optional[DatabaseConnection]:
        """Get a database connection by ID."""
        collection = self.db_manager.get_connections_collection()
        
        try:
            doc = collection.find_one({"_id": ObjectId(connection_id)})
            if not doc:
                return None
            
            connection = DatabaseConnection.from_dict(doc)
            return connection
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
            cleaned_id = connection_id.strip()
            
            # Try to find by ObjectId first
            doc = None
            try:
                if len(cleaned_id) == 24:  # Valid ObjectId length
                    doc = collection.find_one({"_id": ObjectId(cleaned_id)})
            except Exception:
                pass
            
            # If not found by ObjectId, try string search
            if not doc:
                doc = collection.find_one({"_id": cleaned_id})
            
            if not doc:
                return ConnectionTestResult(
                    status="error",
                    message=f"Connection not found with ID: {cleaned_id}"
                )
            
            connection = DatabaseConnection.from_dict(doc)
            return await self._test_database_connection(connection)
            
        except Exception as e:
            return ConnectionTestResult(
                status="error",
                message=f"Error testing connection: {str(e)}"
            )
    
    def _parse_connection_string(self, connection: DatabaseConnection) -> dict:
        """Parse connection string to extract connection parameters."""
        from urllib.parse import urlparse
        
        # If legacy fields are available and not None, use them
        if all([connection.host, connection.port, connection.username, connection.database_name]):
            return {
                'host': connection.host,
                'port': connection.port,
                'username': connection.username,
                'password': connection.password or '',
                'database_name': connection.database_name
            }
        
        # Parse the connection string
        connection_string = connection.connection_string
        
        try:
            # Handle different connection string formats
            if connection_string.startswith(('postgresql://', 'postgres://')):
                parsed = urlparse(connection_string)
                return {
                    'host': parsed.hostname or 'localhost',
                    'port': parsed.port or 5432,
                    'username': parsed.username or '',
                    'password': parsed.password or '',
                    'database_name': parsed.path.lstrip('/') if parsed.path else ''
                }
            elif connection_string.startswith('mysql://'):
                parsed = urlparse(connection_string)
                return {
                    'host': parsed.hostname or 'localhost',
                    'port': parsed.port or 3306,
                    'username': parsed.username or '',
                    'password': parsed.password or '',
                    'database_name': parsed.path.lstrip('/') if parsed.path else ''
                }
            elif connection_string.startswith(('mongodb://', 'mongodb+srv://')):
                parsed = urlparse(connection_string)
                return {
                    'host': parsed.hostname or 'localhost',
                    'port': parsed.port or 27017,
                    'username': parsed.username or '',
                    'password': parsed.password or '',
                    'database_name': parsed.path.lstrip('/') if parsed.path else ''
                }
            elif 'Server=' in connection_string:  # SQL Server format
                params = {}
                for pair in connection_string.split(';'):
                    if '=' in pair:
                        key, value = pair.split('=', 1)
                        params[key.strip().lower()] = value.strip()
                
                return {
                    'host': params.get('server', 'localhost').split(',')[0],
                    'port': int(params.get('server', 'localhost').split(',')[1]) if ',' in params.get('server', '') else 1433,
                    'username': params.get('user id', ''),
                    'password': params.get('password', ''),
                    'database_name': params.get('database', '')
                }
            else:
                # Try to parse as generic format: protocol://user:pass@host:port/database
                match = re.match(r'(\w+)://(?:([^:@]+)(?::([^@]*))?@)?([^:/]+)(?::(\d+))?(?:/(.+))?', connection_string)
                if match:
                    protocol, username, password, host, port, database = match.groups()
                    return {
                        'host': host or 'localhost',
                        'port': int(port) if port else 3306,
                        'username': username or '',
                        'password': password or '',
                        'database_name': database or ''
                    }
                else:
                    # Fallback to legacy fields if parsing fails
                    return {
                        'host': connection.host or 'localhost',
                        'port': connection.port or 3306,
                        'username': connection.username or '',
                        'password': connection.password or '',
                        'database_name': connection.database_name or ''
                    }
        except Exception:
            # Fallback to legacy fields if parsing fails
            return {
                'host': connection.host or 'localhost',
                'port': connection.port or 3306,
                'username': connection.username or '',
                'password': connection.password or '',
                'database_name': connection.database_name or ''
            }

    async def _test_database_connection(self, connection: DatabaseConnection) -> ConnectionTestResult:
        """Test the actual database connection based on type."""
        db_type = connection.database_type.lower()
        
        if db_type in ["mysql", "aurora-mysql"]:
            return await self._test_mysql_connection(connection)
        elif db_type in ["postgresql", "aurora-postgresql"]:
            return await self._test_postgresql_connection(connection)
        elif db_type == "mongodb":
            return await self._test_mongodb_connection(connection)
        elif db_type in ["oracle", "oracle-db"]:
            return await self._test_oracle_connection(connection)
        elif db_type in ["sql-server", "mssql"]:
            return await self._test_sqlserver_connection(connection)
        else:
            return ConnectionTestResult(
                status="info",
                message=f"Connection test not implemented for {db_type}"
            )
    
    async def _test_mysql_connection(self, connection: DatabaseConnection) -> ConnectionTestResult:
        """Test MySQL connection."""
        try:
            import mysql.connector
            
            params = self._parse_connection_string(connection)
            
            conn = mysql.connector.connect(
                host=params['host'],
                port=params['port'],
                user=params['username'],
                password=params['password'],
                database=params['database_name']
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
            
            params = self._parse_connection_string(connection)
            
            # Build connection with SSL support for cloud databases
            if "neon.tech" in params['host'] or "aws" in params['host']:
                conn = psycopg2.connect(
                    host=params['host'],
                    port=params['port'],
                    user=params['username'],
                    password=params['password'],
                    database=params['database_name'],
                    sslmode='require'
                )
            else:
                conn = psycopg2.connect(
                    host=params['host'],
                    port=params['port'],
                    user=params['username'],
                    password=params['password'],
                    database=params['database_name']
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
            
            params = self._parse_connection_string(connection)
            
            # Check if this is an Atlas connection (mongodb+srv)
            if ".mongodb.net" in params['host']:
                mongo_uri = f"mongodb+srv://{params['username']}:{params['password']}@{params['host']}/{params['database_name']}?retryWrites=true&w=majority"
            else:
                mongo_uri = f"mongodb://{params['username']}:{params['password']}@{params['host']}:{params['port']}/{params['database_name']}"
            
            # Create client with timeout settings
            test_client = MongoClient(
                mongo_uri, 
                serverSelectionTimeoutMS=10000,
                connectTimeoutMS=10000,
                socketTimeoutMS=10000
            )
            
            # Test the connection
            test_client.admin.command('ping')
            test_client.close()
            
            return ConnectionTestResult(
                status="success", 
                message="MongoDB connection successful"
            )
            
        except ImportError:
            return ConnectionTestResult(
                status="error",
                message="PyMongo not installed. Run: pip install pymongo"
            )
        except Exception as e:
            return ConnectionTestResult(
                status="error", 
                message=f"MongoDB connection failed: {str(e)}"
            )

    async def _test_oracle_connection(self, connection: DatabaseConnection) -> ConnectionTestResult:
        """Test Oracle database connection."""
        try:
            params = self._parse_connection_string(connection)
            
            dsn = f"{params['host']}:{params['port']}/{params['database_name']}"
            conn = cx_Oracle.connect(
                user=params['username'],
                password=params['password'],
                dsn=dsn
            )
            conn.close()
            return ConnectionTestResult(status="success", message="Oracle connection successful")
        except ImportError:
            return ConnectionTestResult(
                status="error",
                message="Oracle connector not installed. Run: pip install cx-Oracle"
            )
        except Exception as e:
            return ConnectionTestResult(status="error", message=f"Oracle connection failed: {str(e)}")

    async def _test_sqlserver_connection(self, connection: DatabaseConnection) -> ConnectionTestResult:
        """Test SQL Server connection."""
        try:
            import pyodbc
            
            params = self._parse_connection_string(connection)
            
            conn_str = f"DRIVER={{SQL Server}};SERVER={params['host']},{params['port']};DATABASE={params['database_name']};UID={params['username']};PWD={params['password']}"
            conn = pyodbc.connect(conn_str)
            conn.close()
            return ConnectionTestResult(status="success", message="SQL Server connection successful")
        except ImportError:
            return ConnectionTestResult(
                status="error",
                message="SQL Server connector not installed. Run: pip install pyodbc"
            )
        except Exception as e:
            return ConnectionTestResult(status="error", message=f"SQL Server connection failed: {str(e)}")

    async def get_database_schema(self, connection_id: str) -> DatabaseSchemaResult:
        """Get the schema of a database connection using the enhanced multi-database extractor."""
        collection = self.db_manager.get_connections_collection()
        
        try:
            cleaned_id = connection_id.strip()
            
            # Try to find by ObjectId first
            doc = None
            try:
                if len(cleaned_id) == 24:  # Valid ObjectId length
                    doc = collection.find_one({"_id": ObjectId(cleaned_id)})
            except Exception:
                pass
            
            # If not found by ObjectId, try string search
            if not doc:
                doc = collection.find_one({"_id": cleaned_id})
            
            # If still not found, try other common ID patterns
            if not doc:
                doc = collection.find_one({
                    "$or": [
                        {"connection_name": cleaned_id},
                        {"_id": cleaned_id}
                    ]
                })
            
            if not doc:
                return DatabaseSchemaResult(
                    status="error",
                    message=f"Connection not found with ID: {cleaned_id}"
                )
            
            connection = DatabaseConnection.from_dict(doc)
            
            # Use the schema extractor for unified multi-database support
            return await self.schema_extractor.extract_schema(connection)
            
        except Exception as e:
            return DatabaseSchemaResult(
                status="error",
                message=f"Error retrieving database schema: {str(e)}"
            )

    async def list_available_databases(self, connection_id: str):
        """List all available databases for a MongoDB connection."""
        collection = self.db_manager.get_connections_collection()
        
        try:
            cleaned_id = connection_id.strip()
            
            # Try to find by ObjectId first
            doc = None
            try:
                if len(cleaned_id) == 24:  # Valid ObjectId length
                    doc = collection.find_one({"_id": ObjectId(cleaned_id)})
            except Exception:
                pass
            
            # If not found by ObjectId, try string search
            if not doc:
                doc = collection.find_one({"_id": cleaned_id})
            
            if not doc:
                return {"status": "error", "message": f"Connection not found with ID: {cleaned_id}"}
            
            connection = DatabaseConnection.from_dict(doc)
            
            if connection.database_type.lower() == "mongodb":
                return await self._list_mongodb_databases(connection)
            else:
                return {"status": "info", "message": f"Database listing not implemented for {connection.database_type}"}
                
        except Exception as e:
            return {"status": "error", "message": f"Error listing databases: {str(e)}"}

    async def _list_mongodb_databases(self, connection: DatabaseConnection):
        """List MongoDB databases."""
        try:
            from pymongo import MongoClient
            
            # Build connection URI
            if ".mongodb.net" in connection.host:
                mongo_uri = f"mongodb+srv://{connection.username}:{connection.password}@{connection.host}/?retryWrites=true&w=majority"
            else:
                mongo_uri = f"mongodb://{connection.username}:{connection.password}@{connection.host}:{connection.port}/"
            
            client = MongoClient(
                mongo_uri,
                serverSelectionTimeoutMS=5000,
                connectTimeoutMS=5000,
                socketTimeoutMS=5000
            )
            
            # List all databases
            db_names = client.list_database_names()
            
            # Get database info
            databases = []
            for db_name in db_names:
                db = client[db_name]
                collections = db.list_collection_names()
                databases.append({
                    "name": db_name,
                    "collections_count": len(collections),
                    "collections": collections[:10]  # Show first 10 collections
                })
            
            client.close()
            
            return {
                "status": "success",
                "message": f"Found {len(databases)} databases",
                "databases": databases,
                "connection_info": {
                    "host": connection.host,
                    "username": connection.username,
                    "specified_database": connection.database_name
                }
            }
            
        except Exception as e:
            return {"status": "error", "message": f"Failed to list MongoDB databases: {str(e)}"}