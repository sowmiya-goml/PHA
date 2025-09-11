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
from app.services.schema_extraction_service import DatabaseSchemaExtractor


class ConnectionService:
    """Service class for database connection operations."""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
        self.schema_extractor = DatabaseSchemaExtractor()
    
    async def create_connection(self, connection_data: DatabaseConnectionCreate) -> DatabaseConnectionResponse:
        """Create a new database connection."""
        collection = self.db_manager.get_connections_collection()
        
        # Create connection model
        connection = DatabaseConnection(
            connection_name=connection_data.connection_name,
            database_type=connection_data.database_type,
            connection_string=connection_data.connection_string,
            additional_notes=connection_data.additional_notes,
            # Legacy fields for backward compatibility
            host=connection_data.host,
            port=connection_data.port,
            database_name=connection_data.database_name,
            username=connection_data.username,
            password=connection_data.password
        )
        
        # Insert into database
        connection_doc = connection.to_dict()
        result = collection.insert_one(connection_doc)
        connection._id = result.inserted_id
        
        return DatabaseConnectionResponse(
            id=str(connection._id),
            connection_name=connection.connection_name,
            database_type=connection.database_type,
            connection_string=connection.connection_string,
            additional_notes=connection.additional_notes,
            # Legacy fields
            host=connection.host,
            port=connection.port,
            database_name=connection.database_name,
            username=connection.username,
            password=connection.password,
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
                connection_string=connection.connection_string,
                additional_notes=connection.additional_notes,
                # Legacy fields
                host=connection.host,
                port=connection.port,
                database_name=connection.database_name,
                username=connection.username,
                password=connection.password,
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
                connection_string=connection.connection_string,
                additional_notes=connection.additional_notes,
                # Legacy fields
                host=connection.host,
                port=connection.port,
                database_name=connection.database_name,
                username=connection.username,
                password=connection.password,
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

    async def _test_oracle_connection(self, connection: DatabaseConnection) -> ConnectionTestResult:
        """Test Oracle database connection."""
        try:
            import cx_Oracle
            
            # Oracle connection string format
            dsn = f"{connection.host}:{connection.port}/{connection.database_name}"
            conn = cx_Oracle.connect(
                user=connection.username,
                password=connection.password,
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
            
            # SQL Server connection string
            conn_str = f"DRIVER={{SQL Server}};SERVER={connection.host},{connection.port};DATABASE={connection.database_name};UID={connection.username};PWD={connection.password}"
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
            doc = collection.find_one({"_id": ObjectId(connection_id)})
            if not doc:
                return DatabaseSchemaResult(
                    status="error",
                    message="Connection not found"
                )
            
            connection = DatabaseConnection.from_dict(doc)
            
            # Use the new schema extractor for unified multi-database support
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
            doc = collection.find_one({"_id": ObjectId(connection_id)})
            if not doc:
                return {"status": "error", "message": "Connection not found"}
            
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

    async def _get_database_schema_by_type(self, connection: DatabaseConnection) -> DatabaseSchemaResult:
        """Get database schema based on database type."""
        db_type = connection.database_type.lower()
        
        if db_type in ["mysql", "aurora-mysql"]:
            return await self._get_mysql_schema(connection)
        elif db_type in ["postgresql", "aurora-postgresql"]:
            return await self._get_postgresql_schema(connection)
        elif db_type == "mongodb":
            return await self._get_mongodb_schema(connection)
        elif db_type in ["oracle", "oracle-db"]:
            return await self._get_oracle_schema(connection)
        elif db_type in ["sql-server", "mssql"]:
            return await self._get_sqlserver_schema(connection)
        else:
            return DatabaseSchemaResult(
                status="info",
                message=f"Schema retrieval not implemented for {db_type}",
                database_type=connection.database_type,
                database_name=connection.database_name
            )

    async def _get_mongodb_schema(self, connection: DatabaseConnection) -> DatabaseSchemaResult:
        """Get MongoDB collections and document structure analysis."""
        try:
            from pymongo import MongoClient
            from bson import ObjectId
            import datetime
            
            # Build connection URI based on host type
            if ".mongodb.net" in connection.host:
                # Atlas connection - don't specify database in URI for better discovery
                mongo_uri = f"mongodb+srv://{connection.username}:{connection.password}@{connection.host}/?retryWrites=true&w=majority"
            else:
                # Regular MongoDB
                mongo_uri = f"mongodb://{connection.username}:{connection.password}@{connection.host}:{connection.port}/"
            
            client = MongoClient(
                mongo_uri,
                serverSelectionTimeoutMS=10000,
                connectTimeoutMS=10000,
                socketTimeoutMS=10000
            )
            
            # First, check if the specified database exists
            available_dbs = client.list_database_names()
            target_db = connection.database_name
            
            print(f"🔍 Available databases: {available_dbs}")
            print(f"🔍 Looking for database: {target_db}")
            
            if target_db not in available_dbs:
                # Filter out system databases and use the first user database
                system_dbs = ['admin', 'local', 'config']
                user_dbs = [db for db in available_dbs if db not in system_dbs]
                
                if user_dbs:
                    target_db = user_dbs[0]
                    print(f"🔄 Database '{connection.database_name}' not found. Using first user database: {target_db}")
                elif available_dbs:
                    # If no user databases, use first available (might be system db)
                    target_db = available_dbs[0]
                    print(f"🔄 No user databases found. Using first available: {target_db}")
                else:
                    # No databases found at all
                    client.close()
                    return DatabaseSchemaResult(
                        status="error",
                        message=f"No databases found on this MongoDB instance. Check connection permissions.",
                        database_type=connection.database_type,
                        database_name=connection.database_name
                    )
            
            db = client[target_db]
            
            # Get list of collections
            collection_names = db.list_collection_names()
            print(f"🔍 Found {len(collection_names)} collections: {collection_names}")
            
            if not collection_names:
                client.close()
                return DatabaseSchemaResult(
                    status="success",
                    message=f"Database '{target_db}' exists but contains no collections. Available databases: {', '.join(available_dbs)}",
                    database_type=connection.database_type,
                    database_name=target_db,
                    tables=[]
                )
            
            collections_info = []
            
            for collection_name in collection_names:
                try:
                    coll = db[collection_name]
                    
                    # Get accurate document count
                    try:
                        doc_count = coll.count_documents({})
                    except:
                        doc_count = coll.estimated_document_count()
                    
                    print(f"� Collection '{collection_name}': {doc_count} documents")
                    
                    # Skip empty collections
                    if doc_count == 0:
                        collections_info.append(DatabaseTable(
                            name=collection_name,
                            type="collection",
                            fields=[DatabaseField(name="(empty)", type="no documents", nullable=True)],
                            row_count=0
                        ))
                        continue
                    
                    # Analyze document structure with larger sample
                    sample_size = min(20, doc_count)  # Sample up to 20 documents
                    sample_docs = list(coll.aggregate([{"$sample": {"size": sample_size}}]))
                    
                    # Comprehensive field analysis
                    field_analysis = {}
                    
                    for doc in sample_docs:
                        self._analyze_document_fields(doc, field_analysis)
                    
                    # Convert analysis to DatabaseField objects
                    fields = []
                    for field_path, info in field_analysis.items():
                        # Calculate field statistics
                        total_samples = len(sample_docs)
                        present_count = info['count']
                        field_frequency = (present_count / total_samples) * 100
                        
                        # Determine most common type
                        most_common_type = max(info['types'], key=info['types'].get)
                        all_types = list(info['types'].keys())
                        
                        # Format type information
                        if len(all_types) == 1:
                            type_info = most_common_type
                        else:
                            type_info = f"{most_common_type} (variants: {', '.join(all_types)})"
                        
                        fields.append(DatabaseField(
                            name=field_path,
                            type=type_info,
                            nullable=field_frequency < 100,  # If not in all documents, it's nullable
                            default=f"Present in {field_frequency:.1f}% of documents"
                        ))
                    
                    # Sort fields by frequency (most common first)
                    fields.sort(key=lambda f: float(f.default.split()[2].rstrip('%')), reverse=True)
                    
                    collections_info.append(DatabaseTable(
                        name=collection_name,
                        type="collection",
                        fields=fields,
                        row_count=doc_count
                    ))
                    
                except Exception as e:
                    print(f"❌ Error analyzing collection '{collection_name}': {e}")
                    # If we can't analyze a collection, add it with error info
                    collections_info.append(DatabaseTable(
                        name=collection_name,
                        type="collection",
                        fields=[DatabaseField(name="analysis_error", type=str(e)[:100], nullable=True)],
                        row_count=0
                    ))
            
            client.close()
            
            # Create comprehensive message
            total_docs = sum(table.row_count or 0 for table in collections_info)
            
            if target_db != connection.database_name:
                message = f"Database '{connection.database_name}' not found. Analyzed {len(collections_info)} collections with {total_docs:,} total documents in '{target_db}' (auto-selected from available databases: {', '.join(available_dbs)})"
            else:
                message = f"Analyzed {len(collections_info)} collections with {total_docs:,} total documents in database '{target_db}'"
            
            return DatabaseSchemaResult(
                status="success",
                message=message,
                database_type=connection.database_type,
                database_name=target_db,
                tables=collections_info
            )
            
        except ImportError:
            return DatabaseSchemaResult(
                status="error",
                message="PyMongo not installed. Run: pip install pymongo"
            )
        except Exception as e:
            return DatabaseSchemaResult(
                status="error",
                message=f"Failed to analyze MongoDB collections: {str(e)}"
            )
    
    def _analyze_document_fields(self, doc, field_analysis, prefix=""):
        """Recursively analyze document fields including nested objects and arrays."""
        if not isinstance(doc, dict):
            return
            
        for key, value in doc.items():
            field_path = f"{prefix}.{key}" if prefix else key
            
            # Initialize field analysis if not exists
            if field_path not in field_analysis:
                field_analysis[field_path] = {
                    'types': {},
                    'count': 0
                }
            
            field_analysis[field_path]['count'] += 1
            
            # Determine value type
            value_type = self._get_mongodb_type(value)
            
            if value_type in field_analysis[field_path]['types']:
                field_analysis[field_path]['types'][value_type] += 1
            else:
                field_analysis[field_path]['types'][value_type] = 1
            
            # Recursively analyze nested objects (but limit depth to avoid explosion)
            if isinstance(value, dict) and len(prefix.split('.')) < 3:
                self._analyze_document_fields(value, field_analysis, field_path)
            elif isinstance(value, list) and len(value) > 0 and len(prefix.split('.')) < 3:
                # Analyze first few array elements
                for i, item in enumerate(value[:3]):
                    if isinstance(item, dict):
                        self._analyze_document_fields(item, field_analysis, f"{field_path}[{i}]")
    
    def _get_mongodb_type(self, value):
        """Get MongoDB-specific type name for a value."""
        from bson import ObjectId
        import datetime
        
        if isinstance(value, ObjectId):
            return "ObjectId"
        elif isinstance(value, str):
            return "string"
        elif isinstance(value, int):
            return "int"
        elif isinstance(value, float):
            return "double"
        elif isinstance(value, bool):
            return "boolean"
        elif isinstance(value, datetime.datetime):
            return "date"
        elif isinstance(value, list):
            return f"array[{len(value)}]"
        elif isinstance(value, dict):
            return "object"
        elif value is None:
            return "null"
        else:
            return type(value).__name__

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

    async def _get_oracle_schema(self, connection: DatabaseConnection) -> DatabaseSchemaResult:
        """Get Oracle database schema using Oracle data dictionary views."""
        try:
            import cx_Oracle
            
            # Oracle connection
            dsn = f"{connection.host}:{connection.port}/{connection.database_name}"
            conn = cx_Oracle.connect(
                user=connection.username,
                password=connection.password,
                dsn=dsn
            )
            
            cursor = conn.cursor()
            
            # Query Oracle data dictionary for tables and columns
            # Using ALL_ views to get tables accessible to current user
            cursor.execute("""
                SELECT 
                    t.table_name,
                    CASE WHEN v.view_name IS NOT NULL THEN 'VIEW' ELSE 'TABLE' END as table_type,
                    c.column_name,
                    c.data_type,
                    c.data_length,
                    c.data_precision,
                    c.data_scale,
                    c.nullable,
                    c.data_default,
                    c.column_id
                FROM all_tables t
                LEFT JOIN all_tab_columns c ON t.table_name = c.table_name AND t.owner = c.owner
                LEFT JOIN all_views v ON t.table_name = v.view_name AND t.owner = v.owner
                WHERE t.owner = UPPER(:owner)
                    OR t.owner = USER  -- Include tables owned by current user
                ORDER BY t.table_name, c.column_id
            """, {"owner": connection.username.upper()})
            
            results = cursor.fetchall()
            
            # Group by table
            tables_dict = {}
            for row in results:
                table_name, table_type, column_name, data_type, data_length, data_precision, data_scale, nullable, data_default, column_id = row
                
                if table_name not in tables_dict:
                    tables_dict[table_name] = {
                        'type': table_type.lower(),
                        'fields': []
                    }
                
                if column_name:
                    # Format Oracle data types
                    formatted_type = data_type
                    if data_type in ['VARCHAR2', 'CHAR', 'NVARCHAR2', 'NCHAR'] and data_length:
                        formatted_type = f"{data_type}({data_length})"
                    elif data_type == 'NUMBER' and data_precision:
                        if data_scale and data_scale > 0:
                            formatted_type = f"NUMBER({data_precision},{data_scale})"
                        else:
                            formatted_type = f"NUMBER({data_precision})"
                    
                    tables_dict[table_name]['fields'].append(DatabaseField(
                        name=column_name,
                        type=formatted_type,
                        nullable=nullable == 'Y',
                        default=str(data_default).strip() if data_default else None
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
                message=f"Retrieved Oracle schema for {len(tables)} tables/views",
                database_type=connection.database_type,
                database_name=connection.database_name,
                tables=tables
            )
            
        except ImportError:
            return DatabaseSchemaResult(
                status="error",
                message="Oracle connector not installed. Run: pip install cx-Oracle"
            )
        except Exception as e:
            return DatabaseSchemaResult(
                status="error",
                message=f"Failed to retrieve Oracle schema: {str(e)}"
            )

    async def _get_sqlserver_schema(self, connection: DatabaseConnection) -> DatabaseSchemaResult:
        """Get SQL Server database schema using INFORMATION_SCHEMA views."""
        try:
            import pyodbc
            
            # SQL Server connection
            conn_str = f"DRIVER={{SQL Server}};SERVER={connection.host},{connection.port};DATABASE={connection.database_name};UID={connection.username};PWD={connection.password}"
            conn = pyodbc.connect(conn_str)
            
            cursor = conn.cursor()
            
            # Query INFORMATION_SCHEMA for tables and columns
            cursor.execute("""
                SELECT 
                    t.TABLE_NAME,
                    t.TABLE_TYPE,
                    c.COLUMN_NAME,
                    c.DATA_TYPE,
                    c.CHARACTER_MAXIMUM_LENGTH,
                    c.NUMERIC_PRECISION,
                    c.NUMERIC_SCALE,
                    c.IS_NULLABLE,
                    c.COLUMN_DEFAULT,
                    c.ORDINAL_POSITION
                FROM INFORMATION_SCHEMA.TABLES t
                LEFT JOIN INFORMATION_SCHEMA.COLUMNS c 
                    ON t.TABLE_NAME = c.TABLE_NAME 
                    AND t.TABLE_SCHEMA = c.TABLE_SCHEMA
                WHERE t.TABLE_SCHEMA = 'dbo'  -- Default schema
                    AND t.TABLE_TYPE IN ('BASE TABLE', 'VIEW')
                ORDER BY t.TABLE_NAME, c.ORDINAL_POSITION
            """)
            
            results = cursor.fetchall()
            
            # Group by table
            tables_dict = {}
            for row in results:
                table_name, table_type, column_name, data_type, char_length, num_precision, num_scale, is_nullable, column_default, ordinal_pos = row
                
                if table_name not in tables_dict:
                    tables_dict[table_name] = {
                        'type': 'table' if table_type == 'BASE TABLE' else 'view',
                        'fields': []
                    }
                
                if column_name:
                    # Format SQL Server data types
                    formatted_type = data_type.upper()
                    if data_type.upper() in ['VARCHAR', 'CHAR', 'NVARCHAR', 'NCHAR'] and char_length:
                        if char_length == -1:  # MAX length
                            formatted_type = f"{formatted_type}(MAX)"
                        else:
                            formatted_type = f"{formatted_type}({char_length})"
                    elif data_type.upper() in ['DECIMAL', 'NUMERIC'] and num_precision:
                        if num_scale and num_scale > 0:
                            formatted_type = f"{formatted_type}({num_precision},{num_scale})"
                        else:
                            formatted_type = f"{formatted_type}({num_precision})"
                    
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
                        cursor.execute(f'SELECT COUNT(*) FROM [{table_name}]')
                        row_count = cursor.fetchone()[0]
                    except Exception:
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
                message=f"Retrieved SQL Server schema for {len(tables)} tables/views",
                database_type=connection.database_type,
                database_name=connection.database_name,
                tables=tables
            )
            
        except ImportError:
            return DatabaseSchemaResult(
                status="error",
                message="SQL Server connector not installed. Run: pip install pyodbc"
            )
        except Exception as e:
            return DatabaseSchemaResult(
                status="error",
                message=f"Failed to retrieve SQL Server schema: {str(e)}"
            )
