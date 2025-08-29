"""Database connection service layer for business logic."""

from typing import List, Optional
from bson import ObjectId
from datetime import datetime

from app.models.connection import DatabaseConnection
from app.schemas.connection import (
    DatabaseConnectionCreate,
    DatabaseConnectionUpdate,
    DatabaseConnectionResponse,
    ConnectionTestResult,
    DatabaseSchemaResult,
    DatabaseTable,
    DatabaseField
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
            
            # Build connection with SSL support for Neon
            if "neon.tech" in connection.host or "aws" in connection.host:
                # Neon PostgreSQL connection with SSL
                conn = psycopg2.connect(
                    host=connection.host,
                    port=connection.port,
                    user=connection.username,
                    password=connection.password,
                    database=connection.database_name,
                    sslmode='require'
                )
            else:
                # Regular PostgreSQL connection
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
            
            # Check if this is an Atlas connection (mongodb+srv)
            if ".mongodb.net" in connection.host:
                # Atlas connection - use srv format without port
                mongo_uri = f"mongodb+srv://{connection.username}:{connection.password}@{connection.host}/{connection.database_name}?retryWrites=true&w=majority"
            else:
                # Regular MongoDB connection
                mongo_uri = f"mongodb://{connection.username}:{connection.password}@{connection.host}:{connection.port}/{connection.database_name}"
            
            # Create client with timeout settings
            test_client = MongoClient(
                mongo_uri, 
                serverSelectionTimeoutMS=10000,  # 10 seconds timeout
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

    async def get_database_schema(self, connection_id: str) -> DatabaseSchemaResult:
        """Get the schema of a database connection."""
        collection = self.db_manager.get_connections_collection()
        
        try:
            doc = collection.find_one({"_id": ObjectId(connection_id)})
            if not doc:
                return DatabaseSchemaResult(
                    status="error",
                    message="Connection not found"
                )
            
            connection = DatabaseConnection.from_dict(doc)
            return await self._get_database_schema_by_type(connection)
            
        except Exception as e:
            return DatabaseSchemaResult(
                status="error",
                message=f"Error retrieving database schema: {str(e)}"
            )

    async def _get_database_schema_by_type(self, connection: DatabaseConnection) -> DatabaseSchemaResult:
        """Get database schema based on database type."""
        db_type = connection.database_type.lower()
        
        if db_type == "mysql":
            return await self._get_mysql_schema(connection)
        elif db_type == "postgresql":
            return await self._get_postgresql_schema(connection)
        elif db_type == "mongodb":
            return await self._get_mongodb_schema(connection)
        else:
            return DatabaseSchemaResult(
                status="info",
                message=f"Schema retrieval not implemented for {db_type}",
                database_type=connection.database_type,
                database_name=connection.database_name
            )

    async def _get_mongodb_schema(self, connection: DatabaseConnection) -> DatabaseSchemaResult:
        """Get MongoDB database schema."""
        try:
            from pymongo import MongoClient
            
            # Build connection URI based on host type
            if ".mongodb.net" in connection.host:
                # Atlas connection
                mongo_uri = f"mongodb+srv://{connection.username}:{connection.password}@{connection.host}/{connection.database_name}?retryWrites=true&w=majority"
            else:
                # Regular MongoDB
                mongo_uri = f"mongodb://{connection.username}:{connection.password}@{connection.host}:{connection.port}/{connection.database_name}"
            
            client = MongoClient(
                mongo_uri,
                serverSelectionTimeoutMS=5000,  # Reduced to 5 seconds
                connectTimeoutMS=5000,
                socketTimeoutMS=5000
            )
            
            db = client[connection.database_name]
            
            # Get list of collections
            collection_names = db.list_collection_names()
            tables = []
            
            for collection_name in collection_names:
                try:
                    coll = db[collection_name]
                    
                    # Get document count
                    doc_count = coll.estimated_document_count()
                    
                    # Sample a few documents to infer schema
                    sample_docs = list(coll.aggregate([{"$sample": {"size": 5}}]))
                    
                    # Infer fields from sample documents
                    fields = []
                    field_types = {}
                    
                    for doc in sample_docs:
                        for key, value in doc.items():
                            if key not in field_types:
                                field_types[key] = set()
                            field_types[key].add(type(value).__name__)
                    
                    # Convert to DatabaseField objects
                    for field_name, types in field_types.items():
                        field_type = ", ".join(sorted(types)) if len(types) > 1 else list(types)[0]
                        fields.append(DatabaseField(
                            name=field_name,
                            type=field_type,
                            nullable=True  # MongoDB fields are generally nullable
                        ))
                    
                    tables.append(DatabaseTable(
                        name=collection_name,
                        type="collection",
                        fields=fields,
                        row_count=doc_count
                    ))
                    
                except Exception as e:
                    # If we can't analyze a collection, add it with minimal info
                    tables.append(DatabaseTable(
                        name=collection_name,
                        type="collection",
                        fields=[DatabaseField(name="error", type="unknown", nullable=True)],
                        row_count=0
                    ))
            
            client.close()
            
            return DatabaseSchemaResult(
                status="success",
                message=f"Retrieved schema for {len(tables)} collections",
                database_type=connection.database_type,
                database_name=connection.database_name,
                tables=tables
            )
            
        except ImportError:
            return DatabaseSchemaResult(
                status="error",
                message="PyMongo not installed. Run: pip install pymongo"
            )
        except Exception as e:
            return DatabaseSchemaResult(
                status="error",
                message=f"Failed to retrieve MongoDB schema: {str(e)}"
            )

    async def _get_postgresql_schema(self, connection: DatabaseConnection) -> DatabaseSchemaResult:
        """Get PostgreSQL database schema."""
        try:
            import psycopg2
            
            # Build connection string with SSL support for Neon
            if "neon.tech" in connection.host or "aws" in connection.host:
                # Neon PostgreSQL connection with SSL
                conn = psycopg2.connect(
                    host=connection.host,
                    port=connection.port,
                    user=connection.username,
                    password=connection.password,
                    database=connection.database_name,
                    sslmode='require'
                )
            else:
                # Regular PostgreSQL connection
                conn = psycopg2.connect(
                    host=connection.host,
                    port=connection.port,
                    user=connection.username,
                    password=connection.password,
                    database=connection.database_name
                )
            
            cursor = conn.cursor()
            
            # Get tables, views, and their columns with more detailed information
            cursor.execute("""
                SELECT 
                    t.table_name,
                    t.table_type,
                    c.column_name,
                    c.data_type,
                    c.character_maximum_length,
                    c.is_nullable,
                    c.column_default,
                    c.ordinal_position
                FROM information_schema.tables t
                LEFT JOIN information_schema.columns c ON t.table_name = c.table_name 
                    AND t.table_schema = c.table_schema
                WHERE t.table_schema = 'public'
                    AND t.table_type IN ('BASE TABLE', 'VIEW')
                ORDER BY t.table_name, c.ordinal_position
            """)
            
            results = cursor.fetchall()
            
            # Group by table
            tables_dict = {}
            for row in results:
                table_name, table_type, column_name, data_type, max_length, is_nullable, column_default, ordinal_pos = row
                
                if table_name not in tables_dict:
                    tables_dict[table_name] = {
                        'type': 'table' if table_type == 'BASE TABLE' else 'view',
                        'fields': []
                    }
                
                if column_name:  # Some tables might not have columns in the result
                    # Format data type with length if applicable
                    formatted_type = data_type
                    if max_length and data_type in ['character varying', 'character', 'varchar', 'char']:
                        formatted_type = f"{data_type}({max_length})"
                    
                    tables_dict[table_name]['fields'].append(DatabaseField(
                        name=column_name,
                        type=formatted_type,
                        nullable=is_nullable == 'YES',
                        default=str(column_default) if column_default else None
                    ))
            
            # Get row counts for tables (not views)
            tables = []
            for table_name, table_info in tables_dict.items():
                row_count = None
                if table_info['type'] == 'table':
                    try:
                        cursor.execute(f'SELECT COUNT(*) FROM "{table_name}"')
                        row_count = cursor.fetchone()[0]
                    except Exception:
                        row_count = None  # Skip if we can't count rows
                
                tables.append(DatabaseTable(
                    name=table_name,
                    type=table_info['type'],
                    fields=table_info['fields'],
                    row_count=row_count
                ))
            
            # Get additional database information
            cursor.execute("SELECT current_database(), version()")
            db_info = cursor.fetchone()
            db_name = db_info[0] if db_info else connection.database_name
            
            conn.close()
            
            return DatabaseSchemaResult(
                status="success",
                message=f"Retrieved schema for {len(tables)} tables/views",
                database_type=connection.database_type,
                database_name=db_name,
                tables=tables
            )
            
        except ImportError:
            return DatabaseSchemaResult(
                status="error",
                message="psycopg2 not installed. Run: pip install psycopg2-binary"
            )
        except Exception as e:
            return DatabaseSchemaResult(
                status="error",
                message=f"Failed to retrieve PostgreSQL schema: {str(e)}"
            )

    async def _get_mysql_schema(self, connection: DatabaseConnection) -> DatabaseSchemaResult:
        """Get MySQL database schema."""
        try:
            import mysql.connector
            
            conn = mysql.connector.connect(
                host=connection.host,
                port=connection.port,
                user=connection.username,
                password=connection.password,
                database=connection.database_name
            )
            
            cursor = conn.cursor()
            
            # Get tables and their columns
            cursor.execute("""
                SELECT 
                    t.TABLE_NAME,
                    t.TABLE_TYPE,
                    c.COLUMN_NAME,
                    c.DATA_TYPE,
                    c.IS_NULLABLE,
                    c.COLUMN_DEFAULT
                FROM information_schema.TABLES t
                LEFT JOIN information_schema.COLUMNS c ON t.TABLE_NAME = c.TABLE_NAME
                WHERE t.TABLE_SCHEMA = %s
                ORDER BY t.TABLE_NAME, c.ORDINAL_POSITION
            """, (connection.database_name,))
            
            results = cursor.fetchall()
            
            # Group by table
            tables_dict = {}
            for row in results:
                table_name, table_type, column_name, data_type, is_nullable, column_default = row
                
                if table_name not in tables_dict:
                    tables_dict[table_name] = {
                        'type': table_type.lower(),
                        'fields': []
                    }
                
                if column_name:
                    tables_dict[table_name]['fields'].append(DatabaseField(
                        name=column_name,
                        type=data_type,
                        nullable=is_nullable == 'YES',
                        default=column_default
                    ))
            
            # Get row counts
            tables = []
            for table_name, table_info in tables_dict.items():
                try:
                    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                    row_count = cursor.fetchone()[0]
                except:
                    row_count = None
                
                tables.append(DatabaseTable(
                    name=table_name,
                    type=table_info['type'],
                    fields=table_info['fields'],
                    row_count=row_count
                ))
            
            conn.close()
            
            return DatabaseSchemaResult(
                status="success",
                message=f"Retrieved schema for {len(tables)} tables",
                database_type=connection.database_type,
                database_name=connection.database_name,
                tables=tables
            )
            
        except ImportError:
            return DatabaseSchemaResult(
                status="error",
                message="MySQL connector not installed. Run: pip install mysql-connector-python"
            )
        except Exception as e:
            return DatabaseSchemaResult(
                status="error",
                message=f"Failed to retrieve MySQL schema: {str(e)}"
            )
