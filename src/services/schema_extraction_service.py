"""Multi-database schema extraction service with URI-based connections support."""

from typing import Dict, List, Any, Optional
from datetime import datetime
import json
import re
from urllib.parse import urlparse, parse_qs

from models.connection import DatabaseConnection
from schemas.connection import (
    DatabaseSchemaResult,
    DatabaseTable,
    DatabaseField
)

class DatabaseSchemaExtractor:
    """Unified database schema extraction service supporting multiple database types."""
    
    # Database type mappings for Aurora and other variants
    DB_TYPE_MAPPINGS = {
        'aurora-mysql': 'mysql',
        'aurora-postgresql': 'postgresql', 
        'oracle-db': 'oracle',
        'sql-server': 'sqlserver',
        'mssql': 'sqlserver',
        'mariadb': 'mysql',  # MariaDB uses MySQL connector
        'mongodb atlas': 'mongodb',  # MongoDB Atlas
        'mongo atlas': 'mongodb',   # Alternative naming
        'atlas': 'mongodb',         # Short form
        'mongo': 'mongodb'          # Generic MongoDB
    }
    
    def __init__(self):
        """Initialize the schema extractor."""
        pass
    
    def _parse_connection_string(self, connection_string: str, db_type: str) -> Dict[str, Any]:
        """
        Parse connection string and extract connection parameters.
        
        Supported formats:
        - PostgreSQL: postgresql://username:password@host:port/database
        - MySQL: mysql://username:password@host:port/database
        - MongoDB: mongodb://username:password@host:port/database or mongodb+srv://...
        - SQL Server: Server=host,port;Database=database;User Id=username;Password=password;
        - Oracle: oracle://username:password@host:port/service_name
        """
        try:
            db_type = self._normalize_db_type(db_type)
            
            if db_type in ['postgresql', 'mysql', 'mongodb']:
                # Standard URI format: scheme://username:password@host:port/database
                #print("😁😁😁😁😁😁😁😁😁")
                parsed = urlparse(connection_string)
                return {
                    'host': parsed.hostname,
                    'port': parsed.port,
                    'username': parsed.username,
                    'password': parsed.password,
                    'database': parsed.path.lstrip('/'),
                    'scheme': parsed.scheme,
                    'query': parse_qs(parsed.query)
                }
            
            elif db_type == 'snowflake':
                # Snowflake format: snowflake://username:password@account/database/schema?warehouse=WH&role=ROLE
                parsed = urlparse(connection_string)
                
                # Extract account identifier - handle different formats
                hostname = parsed.hostname
                account = hostname.replace('.snowflakecomputing.com', '') if hostname else ''
                
                # Handle different account identifier formats
                if '.ap-south-1.aws' in account:
                    account = account.replace('.ap-south-1.aws', '')
                elif '.aws' in account or '.azure' in account or '.gcp' in account:
                    # Other cloud regions - use account part only
                    parts = account.split('.')
                    account = parts[0]
                
                # Parse path components
                path_parts = [p for p in parsed.path.split('/') if p]
                database = path_parts[0] if len(path_parts) > 0 else 'PHA'
                schema = path_parts[1] if len(path_parts) > 1 else 'PUBLIC'
                
                # Parse query parameters
                query_params = parse_qs(parsed.query)
                
                return {
                    'account': account,
                    'username': parsed.username,
                    'password': parsed.password,
                    'database': database,
                    'schema': schema,
                    'warehouse': query_params.get('warehouse', [''])[0],
                    'role': query_params.get('role', [''])[0],
                    'host': hostname,
                    'scheme': parsed.scheme,
                    'query': query_params
                }
            
            elif db_type == 'sqlserver':
                # SQL Server format: Server=host,port;Database=database;User Id=username;Password=password;
                params = {}
                pairs = connection_string.split(';')
                for pair in pairs:
                    if '=' in pair:
                        key, value = pair.split('=', 1)
                        params[key.strip().lower()] = value.strip()
                
                # Handle Server format (host,port or just host)
                server = params.get('server', '')
                if ',' in server:
                    host, port = server.split(',', 1)
                    params['host'] = host.strip()
                    params['port'] = int(port.strip()) if port.strip().isdigit() else 1433
                else:
                    params['host'] = server
                    params['port'] = 1433
                
                return {
                    'host': params.get('host'),
                    'port': params.get('port', 1433),
                    'username': params.get('user id') or params.get('uid'),
                    'password': params.get('password') or params.get('pwd'),
                    'database': params.get('database') or params.get('initial catalog'),
                    'raw_params': params
                }
            
            elif db_type == 'oracle':
                # Oracle format: oracle://username:password@host:port/service_name
                # or: Data Source=host:port/service_name;User Id=username;Password=password;
                if connection_string.startswith('oracle://'):
                    parsed = urlparse(connection_string)
                    return {
                        'host': parsed.hostname,
                        'port': parsed.port or 1521,
                        'username': parsed.username,
                        'password': parsed.password,
                        'service_name': parsed.path.lstrip('/'),
                        'dsn': f"{parsed.hostname}:{parsed.port or 1521}/{parsed.path.lstrip('/')}"
                    }
                else:
                    # Oracle connection string format
                    params = {}
                    pairs = connection_string.split(';')
                    for pair in pairs:
                        if '=' in pair:
                            key, value = pair.split('=', 1)
                            params[key.strip().lower()] = value.strip()
                    
                    return {
                        'host': params.get('data source', '').split(':')[0] if ':' in params.get('data source', '') else params.get('data source'),
                        'port': int(params.get('data source', '').split(':')[1].split('/')[0]) if ':' in params.get('data source', '') and '/' in params.get('data source', '') else 1521,
                        'username': params.get('user id') or params.get('uid'),
                        'password': params.get('password') or params.get('pwd'),
                        'service_name': params.get('data source', '').split('/')[-1] if '/' in params.get('data source', '') else 'ORCL',
                        'dsn': params.get('data source', ''),
                        'raw_params': params
                    }
            
            else:
                # Fallback: try to parse as generic URI
                parsed = urlparse(connection_string)
                return {
                    'host': parsed.hostname,
                    'port': parsed.port,
                    'username': parsed.username,
                    'password': parsed.password,
                    'database': parsed.path.lstrip('/'),
                    'scheme': parsed.scheme
                }
                
        except Exception as e:
            raise ValueError(f"Invalid connection string format for {db_type}: {str(e)}")
    
    async def extract_schema(self, connection: DatabaseConnection) -> DatabaseSchemaResult:
        """
        Extract database schema with unified JSON format.
        
        Returns:
            DatabaseSchemaResult with consistent structure across all DB types
        """
        try:
            # Normalize database type
            db_type = self._normalize_db_type(connection.database_type)
            
            # Route to appropriate extractor
            if db_type == 'postgresql':
                return await self._extract_postgresql_schema(connection)
            elif db_type == 'mysql':
                return await self._extract_mysql_schema(connection)
            elif db_type == 'oracle':
                return await self._extract_oracle_schema(connection)
            elif db_type == 'sqlserver':
                return await self._extract_sqlserver_schema(connection)
            elif db_type == 'mongodb':
                return await self._extract_mongodb_schema(connection)
            elif db_type == 'snowflake':
                return await self._extract_snowflake_schema(connection)
            else:
                return DatabaseSchemaResult(
                    status="error",
                    message=f"Unsupported database type: {connection.database_type}",
                    database_type=connection.database_type,
                    database_name=connection.database_name
                )
                
        except Exception as e:
            return DatabaseSchemaResult(
                status="error",
                message=f"Schema extraction failed: {str(e)}",
                database_type=connection.database_type,
                database_name=connection.database_name
            )
    
    def _normalize_db_type(self, db_type: str) -> str:
        """Normalize database type for consistent processing."""
        normalized = db_type.lower().strip()
        return self.DB_TYPE_MAPPINGS.get(normalized, normalized)
    
    def _create_unified_schema_result(
        self, 
        tables: List[DatabaseTable], 
        connection: DatabaseConnection,
        additional_info: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Create unified JSON schema format for all databases.
        
        Unified Format:
        {
            "database_info": {
                "name": "database_name",
                "type": "postgresql", 
                "version": "13.2",
                "host": "localhost",
                "schema_extracted_at": "2025-01-01T12:00:00Z"
            },
            "tables": [
                {
                    "name": "users",
                    "type": "table",
                    "row_count": 1500,
                    "columns": [
                        {
                            "name": "id",
                            "type": "integer",
                            "nullable": false,
                            "primary_key": true,
                            "default": "nextval('users_id_seq')",
                            "max_length": null,
                            "precision": null,
                            "scale": null
                        }
                    ],
                    "constraints": {
                        "primary_keys": ["id"],
                        "foreign_keys": [],
                        "unique_constraints": [],
                        "check_constraints": []
                    }
                }
            ],
            "summary": {
                "total_tables": 5,
                "total_views": 2,
                "total_columns": 47,
                "total_rows": 15000
            }
        }
        """
        # Calculate summary statistics
        total_tables = len([t for t in tables if t.type == 'table'])
        total_views = len([t for t in tables if t.type == 'view'])
        total_collections = len([t for t in tables if t.type == 'collection'])
        total_columns = sum(len(t.fields) for t in tables)
        total_rows = sum(t.row_count or 0 for t in tables)
        
        # Build unified schema
        unified_schema = {
            "database_info": {
                "name": connection.database_name,
                "type": self._normalize_db_type(connection.database_type),
                "host": connection.host,
                "port": connection.port,
                "schema_extracted_at": datetime.utcnow().isoformat() + "Z",
                **(additional_info or {})
            },
            "tables": [],
            "summary": {
                "total_tables": total_tables,
                "total_views": total_views,
                "total_collections": total_collections,
                "total_columns": total_columns,
                "total_rows": total_rows,
                "extraction_time_ms": None  # Can be populated by caller
            }
        }
        
        # Convert tables to unified format
        for table in tables:
            unified_table = {
                "name": table.name,
                "type": table.type,
                "row_count": table.row_count,
                "columns": [],
                "constraints": {
                    "primary_keys": [],
                    "foreign_keys": [],
                    "unique_constraints": [],
                    "check_constraints": []
                }
            }
            
            # Convert columns to unified format
            for field in table.fields:
                unified_column = {
                    "name": field.name,
                    "type": field.type,
                    "nullable": field.nullable,
                    "primary_key": self._is_primary_key(field),
                    "default": field.default,
                    "max_length": self._extract_max_length(field.type),
                    "precision": self._extract_precision(field.type),
                    "scale": self._extract_scale(field.type)
                }
                unified_table["columns"].append(unified_column)
            
            unified_schema["tables"].append(unified_table)
        
        return unified_schema
    
    def _is_primary_key(self, field: DatabaseField) -> bool:
        """Detect if field is likely a primary key based on name and type."""
        pk_indicators = ['id', '_id', 'pk_', 'primary']
        return any(indicator in field.name.lower() for indicator in pk_indicators)
    
    def _extract_max_length(self, type_str: str) -> Optional[int]:
        """Extract max length from type string like varchar(255)."""
        import re
        if not type_str:
            return None
        match = re.search(r'\((\d+)\)', type_str.lower())
        if match and 'char' in type_str.lower():
            return int(match.group(1))
        return None
    
    def _extract_precision(self, type_str: str) -> Optional[int]:
        """Extract precision from type string like decimal(10,2)."""
        import re
        if not type_str:
            return None
        match = re.search(r'\((\d+),\d+\)', type_str.lower())
        if match and any(t in type_str.lower() for t in ['decimal', 'numeric', 'number']):
            return int(match.group(1))
        return None
    
    def _extract_scale(self, type_str: str) -> Optional[int]:
        """Extract scale from type string like decimal(10,2)."""
        import re
        if not type_str:
            return None
        match = re.search(r'\(\d+,(\d+)\)', type_str.lower())
        if match and any(t in type_str.lower() for t in ['decimal', 'numeric', 'number']):
            return int(match.group(1))
        return None

    async def _extract_postgresql_schema(self, connection: DatabaseConnection) -> DatabaseSchemaResult:
        """Extract PostgreSQL/Aurora PostgreSQL schema using connection string URI."""
        try:
            import psycopg2
            
            # Parse connection string
            conn_params = self._parse_connection_string(connection.connection_string, connection.database_type)
            
            # Connect using the connection string directly
            conn = psycopg2.connect(connection.connection_string)
            cursor = conn.cursor()
            
            # Get PostgreSQL version
            cursor.execute("SELECT version()")
            version_info = cursor.fetchone()[0]
            
            # Get database name from connection
            cursor.execute("SELECT current_database()")
            current_db = cursor.fetchone()[0]
            
            # Enhanced schema query with constraints
            cursor.execute("""
                SELECT DISTINCT
                    t.table_name,
                    t.table_type,
                    c.column_name,
                    c.data_type,
                    c.character_maximum_length,
                    c.numeric_precision,
                    c.numeric_scale,
                    c.is_nullable,
                    c.column_default,
                    c.ordinal_position,
                    tc.constraint_type,
                    kcu.constraint_name
                FROM information_schema.tables t
                LEFT JOIN information_schema.columns c 
                    ON t.table_name = c.table_name 
                    AND t.table_schema = c.table_schema
                LEFT JOIN information_schema.key_column_usage kcu 
                    ON c.table_name = kcu.table_name 
                    AND c.column_name = kcu.column_name
                    AND c.table_schema = kcu.table_schema
                LEFT JOIN information_schema.table_constraints tc 
                    ON kcu.constraint_name = tc.constraint_name
                    AND kcu.table_schema = tc.table_schema
                WHERE t.table_schema = 'public'
                    AND t.table_type IN ('BASE TABLE', 'VIEW')
                ORDER BY t.table_name, c.ordinal_position
            """)
            
            results = cursor.fetchall()
            
            # Process results
            tables_dict = {}
            for row in results:
                table_name, table_type, column_name, data_type, char_length, num_precision, num_scale, is_nullable, column_default, ordinal_pos, constraint_type, constraint_name = row
                
                if table_name not in tables_dict:
                    tables_dict[table_name] = {
                        'type': 'table' if table_type == 'BASE TABLE' else 'view',
                        'fields': [],
                        'processed_columns': set()
                    }
                
                # Avoid duplicate columns
                if column_name and column_name not in tables_dict[table_name]['processed_columns']:
                    # Format PostgreSQL data types
                    formatted_type = data_type
                    if char_length and data_type in ['character varying', 'character', 'varchar', 'char']:
                        formatted_type = f"{data_type}({char_length})"
                    elif num_precision and data_type in ['numeric', 'decimal']:
                        if num_scale and num_scale > 0:
                            formatted_type = f"{data_type}({num_precision},{num_scale})"
                        else:
                            formatted_type = f"{data_type}({num_precision})"
                    
                    field = DatabaseField(
                        name=column_name,
                        type=formatted_type,
                        nullable=is_nullable == 'YES',
                        default=str(column_default) if column_default else None
                    )
                    
                    tables_dict[table_name]['fields'].append(field)
                    tables_dict[table_name]['processed_columns'].add(column_name)
            
            # Get row counts and create final table objects
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
            
            # Create unified schema format
            unified_schema = self._create_unified_schema_result(
                tables, 
                connection,
                {
                    "version": version_info.split()[1] if version_info else "unknown",
                    "current_database": current_db,
                    "connection_method": "connection_string"
                }
            )
            
            return DatabaseSchemaResult(
                status="success",
                message=f"Retrieved PostgreSQL schema: {len(tables)} tables/views from connection string",
                database_type=connection.database_type,
                database_name=current_db,
                tables=tables,
                unified_schema=unified_schema
            )
            
        except ImportError:
            return DatabaseSchemaResult(
                status="error",
                message="PostgreSQL connector not installed. Run: pip install psycopg2-binary",
                database_type=connection.database_type,
                database_name=None
            )
        except Exception as e:
            return DatabaseSchemaResult(
                status="error",
                message=f"PostgreSQL schema extraction failed: {str(e)}",
                database_type=connection.database_type,
                database_name=None
            )

    async def _extract_mysql_schema(self, connection: DatabaseConnection) -> DatabaseSchemaResult:
        """Extract MySQL/Aurora MySQL schema using connection string URI."""
        try:
            import mysql.connector
            
            # Parse connection string to extract parameters
            conn_params = self._parse_connection_string(connection.connection_string, connection.database_type)
            
            # Create connection using parsed parameters
            config = {
                'host': conn_params.get('host', 'localhost'),
                'port': int(conn_params.get('port', 3306)),
                'user': conn_params.get('username'),
                'password': conn_params.get('password'),
                'database': conn_params.get('database_name'),
                'ssl_disabled': False,  # Enable SSL for Aurora
                'autocommit': True
            }
            
            # Remove None values to avoid MySQL connector issues
            config = {k: v for k, v in config.items() if v is not None}
            
            conn = mysql.connector.connect(**config)
            cursor = conn.cursor()
            
            # Ensure we're using the correct database for MariaDB/MySQL
            if conn_params.get('database_name'):
                cursor.execute(f"USE `{conn_params.get('database_name')}`")
            else:
                # For MariaDB/MySQL, if no database specified, list available databases
                cursor.execute("SHOW DATABASES")
                databases = [row[0] for row in cursor.fetchall()]
                # Filter out system databases
                user_databases = [db for db in databases if db not in ['information_schema', 'performance_schema', 'mysql', 'sys']]
                if user_databases:
                    cursor.execute(f"USE `{user_databases[0]}`")
                    print(f"DEBUG: Auto-selected database: {user_databases[0]}")
            
            # Get MySQL version
            cursor.execute("SELECT VERSION()")
            version_info = cursor.fetchone()[0]
            
            # Get database name - try multiple methods for MariaDB compatibility
            try:
                cursor.execute("SELECT DATABASE()")
                current_db_result = cursor.fetchone()
                current_db = current_db_result[0] if current_db_result and current_db_result[0] else None
            except:
                current_db = None
                
            # If still no database, try to get from connection params or use default
            if not current_db:
                current_db = conn_params.get('database_name')
                if not current_db:
                    # List databases and pick first non-system one
                    try:
                        cursor.execute("SHOW DATABASES")
                        databases = [row[0] for row in cursor.fetchall()]
                        user_databases = [db for db in databases if db not in ['information_schema', 'performance_schema', 'mysql', 'sys']]
                        if user_databases:
                            current_db = user_databases[0]
                            cursor.execute(f"USE `{current_db}`")
                        else:
                            current_db = 'mysql'  # fallback to mysql system database
                    except:
                        current_db = 'unknown'
            
            # Enhanced MySQL schema query - use the actual database name
            if not current_db:
                current_db = conn_params.get('database_name', 'pha')  # fallback to connection string db name
                
            cursor.execute("""
                SELECT DISTINCT
                    t.TABLE_NAME,
                    t.TABLE_TYPE,
                    c.COLUMN_NAME,
                    c.DATA_TYPE,
                    c.CHARACTER_MAXIMUM_LENGTH,
                    c.NUMERIC_PRECISION,
                    c.NUMERIC_SCALE,
                    c.IS_NULLABLE,
                    c.COLUMN_DEFAULT,
                    c.ORDINAL_POSITION,
                    c.COLUMN_KEY,
                    c.EXTRA
                FROM information_schema.TABLES t
                LEFT JOIN information_schema.COLUMNS c 
                    ON t.TABLE_NAME = c.TABLE_NAME 
                    AND t.TABLE_SCHEMA = c.TABLE_SCHEMA
                WHERE t.TABLE_SCHEMA = %s
                    AND t.TABLE_TYPE IN ('BASE TABLE', 'VIEW')
                ORDER BY t.TABLE_NAME, c.ORDINAL_POSITION
            """, (current_db,))
            
            results = cursor.fetchall()
            
            # Process results
            tables_dict = {}
            for row in results:
                table_name, table_type, column_name, data_type, char_length, num_precision, num_scale, is_nullable, column_default, ordinal_pos, column_key, extra = row
                
                if table_name not in tables_dict:
                    tables_dict[table_name] = {
                        'type': 'table' if table_type == 'BASE TABLE' else 'view',
                        'fields': []
                    }
                
                if column_name:
                    # Format MySQL data types
                    formatted_type = data_type.upper()
                    if char_length and data_type.upper() in ['VARCHAR', 'CHAR', 'TEXT']:
                        formatted_type = f"{formatted_type}({char_length})"
                    elif num_precision and data_type.upper() in ['DECIMAL', 'NUMERIC']:
                        if num_scale and num_scale > 0:
                            formatted_type = f"{formatted_type}({num_precision},{num_scale})"
                        else:
                            formatted_type = f"{formatted_type}({num_precision})"
                    
                    # Include MySQL-specific info in default
                    default_info = str(column_default) if column_default else None
                    if extra and extra.upper() == 'AUTO_INCREMENT':
                        default_info = f"AUTO_INCREMENT {default_info or ''}".strip()
                    
                    field = DatabaseField(
                        name=column_name,
                        type=formatted_type,
                        nullable=is_nullable == 'YES',
                        default=default_info
                    )
                    
                    tables_dict[table_name]['fields'].append(field)
            
            # Get row counts
            tables = []
            for table_name, table_info in tables_dict.items():
                row_count = None
                if table_info['type'] == 'table':
                    try:
                        cursor.execute(f"SELECT COUNT(*) FROM `{table_name}`")
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
            
            # Create unified schema
            unified_schema = self._create_unified_schema_result(
                tables, 
                connection,
                {
                    "version": version_info,
                    "current_database": current_db,
                    "connection_method": "connection_string"
                }
            )
            
            return DatabaseSchemaResult(
                status="success",
                message=f"Retrieved MySQL schema: {len(tables)} tables/views from connection string",
                database_type=connection.database_type,
                database_name=current_db,
                tables=tables,
                unified_schema=unified_schema
            )
            
        except ImportError:
            return DatabaseSchemaResult(
                status="error",
                message="MySQL connector not installed. Run: pip install mysql-connector-python",
                database_type=connection.database_type,
                database_name=connection.database_name
            )
        except Exception as e:
            return DatabaseSchemaResult(
                status="error",
                message=f"MySQL schema extraction failed: {str(e)}",
                database_type=connection.database_type,
                database_name=connection.database_name
            )

    async def _extract_oracle_schema(self, connection: DatabaseConnection) -> DatabaseSchemaResult:
        """Extract Oracle database schema using connection string URI."""
        try:
            import oracledb
            
            # Parse connection string
            conn_params = self._parse_connection_string(connection.connection_string, connection.database_type)
            
            # Create Oracle connection based on connection string format
            if 'oracle://' in connection.connection_string.lower():
                # Oracle URI format: oracle://user:password@host:port/service_name
                dsn = f"{conn_params.get('host')}:{conn_params.get('port', 1521)}/{conn_params.get('database_name')}"
                conn = oracledb.connect(
                    user=conn_params.get('username'),
                    password=conn_params.get('password'),
                    dsn=dsn
                )
            else:
                # Traditional Oracle connection string (Data Source= format)
                # Extract from parsed parameters or use connection string directly
                conn = oracledb.connect(connection.connection_string)
            
            cursor = conn.cursor()
            
            # Get Oracle version
            cursor.execute("SELECT * FROM v$version WHERE banner LIKE 'Oracle%'")
            version_result = cursor.fetchone()
            version_info = version_result[0] if version_result else "Unknown"
            
            # Get current schema/user
            cursor.execute("SELECT USER FROM DUAL")
            current_user = cursor.fetchone()[0]
            
            # Oracle schema query using data dictionary views
            cursor.execute("""
                SELECT 
                    t.table_name,
                    CASE WHEN v.view_name IS NOT NULL THEN 'VIEW' ELSE 'TABLE' END as object_type,
                    c.column_name,
                    c.data_type,
                    c.data_length,
                    c.data_precision,
                    c.data_scale,
                    c.nullable,
                    c.data_default,
                    c.column_id,
                    cc.constraint_type
                FROM all_tables t
                LEFT JOIN all_tab_columns c ON t.table_name = c.table_name AND t.owner = c.owner
                LEFT JOIN all_views v ON t.table_name = v.view_name AND t.owner = v.owner  
                LEFT JOIN all_cons_columns acc ON c.table_name = acc.table_name 
                    AND c.column_name = acc.column_name AND c.owner = acc.owner
                LEFT JOIN all_constraints cc ON acc.constraint_name = cc.constraint_name 
                    AND acc.owner = cc.owner
                WHERE (t.owner = UPPER(:owner) OR t.owner = USER)
                    AND t.table_name NOT LIKE 'BIN$%'  -- Exclude recycle bin objects
                ORDER BY t.table_name, c.column_id
            """, {"owner": conn_params.get('username', current_user).upper()})
            
            results = cursor.fetchall()
            
            # Process results
            tables_dict = {}
            for row in results:
                table_name, object_type, column_name, data_type, data_length, data_precision, data_scale, nullable, data_default, column_id, constraint_type = row
                
                if table_name not in tables_dict:
                    tables_dict[table_name] = {
                        'type': object_type.lower(),
                        'fields': [],
                        'processed_columns': set()
                    }
                
                if column_name and column_name not in tables_dict[table_name]['processed_columns']:
                    # Format Oracle data types
                    formatted_type = data_type
                    if data_type in ['VARCHAR2', 'CHAR', 'NVARCHAR2', 'NCHAR'] and data_length:
                        formatted_type = f"{data_type}({data_length})"
                    elif data_type == 'NUMBER':
                        if data_precision:
                            if data_scale and data_scale > 0:
                                formatted_type = f"NUMBER({data_precision},{data_scale})"
                            else:
                                formatted_type = f"NUMBER({data_precision})"
                        else:
                            formatted_type = "NUMBER"
                    
                    field = DatabaseField(
                        name=column_name,
                        type=formatted_type,
                        nullable=nullable == 'Y',
                        default=str(data_default).strip() if data_default else None
                    )
                    
                    tables_dict[table_name]['fields'].append(field)
                    tables_dict[table_name]['processed_columns'].add(column_name)
            
            # Get row counts
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
            
            # Create unified schema
            unified_schema = self._create_unified_schema_result(
                tables, 
                connection,
                {
                    "version": version_info,
                    "current_user": current_user,
                    "connection_method": "connection_string"
                }
            )
            
            return DatabaseSchemaResult(
                status="success",
                message=f"Retrieved Oracle schema: {len(tables)} tables/views from connection string",
                database_type=connection.database_type,
                database_name=conn_params.get('database_name') or current_user,
                tables=tables,
                unified_schema=unified_schema
            )
            
        except ImportError:
            return DatabaseSchemaResult(
                status="error",
                message="Oracle connector not installed. Run: pip install cx-Oracle",
                database_type=connection.database_type,
                database_name=connection.database_name
            )
        except Exception as e:
            return DatabaseSchemaResult(
                status="error",
                message=f"Oracle schema extraction failed: {str(e)}",
                database_type=connection.database_type,
                database_name=connection.database_name
            )

    async def _extract_sqlserver_schema(self, connection: DatabaseConnection) -> DatabaseSchemaResult:
        """Extract SQL Server schema using connection string URI."""
        try:
            import pyodbc
            
            # Parse connection string
            conn_params = self._parse_connection_string(connection.connection_string, connection.database_type)
            
            # SQL Server connection - use connection string directly or build from parsed params
            if 'Server=' in connection.connection_string:
                # Use connection string directly (SQL Server format)
                conn = pyodbc.connect(connection.connection_string)
            else:
                # Build from parsed URI format
                conn_str = (f"DRIVER={{ODBC Driver 17 for SQL Server}};"
                           f"SERVER={conn_params.get('host')},{conn_params.get('port', 1433)};"
                           f"DATABASE={conn_params.get('database_name')};"
                           f"UID={conn_params.get('username')};"
                           f"PWD={conn_params.get('password')}")
                conn = pyodbc.connect(conn_str)
            
            cursor = conn.cursor()
            
            # Get SQL Server version
            cursor.execute("SELECT @@VERSION")
            version_info = cursor.fetchone()[0].split('\n')[0]
            
            # Get current database
            cursor.execute("SELECT DB_NAME()")
            current_db = cursor.fetchone()[0]
            
            # SQL Server schema query
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
                    c.ORDINAL_POSITION,
                    tc.CONSTRAINT_TYPE
                FROM INFORMATION_SCHEMA.TABLES t
                LEFT JOIN INFORMATION_SCHEMA.COLUMNS c 
                    ON t.TABLE_NAME = c.TABLE_NAME 
                    AND t.TABLE_SCHEMA = c.TABLE_SCHEMA
                LEFT JOIN INFORMATION_SCHEMA.KEY_COLUMN_USAGE kcu 
                    ON c.TABLE_NAME = kcu.TABLE_NAME 
                    AND c.COLUMN_NAME = kcu.COLUMN_NAME
                    AND c.TABLE_SCHEMA = kcu.TABLE_SCHEMA
                LEFT JOIN INFORMATION_SCHEMA.TABLE_CONSTRAINTS tc 
                    ON kcu.CONSTRAINT_NAME = tc.CONSTRAINT_NAME
                WHERE t.TABLE_SCHEMA = 'dbo'
                    AND t.TABLE_TYPE IN ('BASE TABLE', 'VIEW')
                ORDER BY t.TABLE_NAME, c.ORDINAL_POSITION
            """)
            
            results = cursor.fetchall()
            
            # Process results
            tables_dict = {}
            for row in results:
                table_name, table_type, column_name, data_type, char_length, num_precision, num_scale, is_nullable, column_default, ordinal_pos, constraint_type = row
                
                if table_name not in tables_dict:
                    tables_dict[table_name] = {
                        'type': 'table' if table_type == 'BASE TABLE' else 'view',
                        'fields': [],
                        'processed_columns': set()
                    }
                
                if column_name and column_name not in tables_dict[table_name]['processed_columns']:
                    # Format SQL Server data types
                    formatted_type = data_type.upper()
                    if char_length and data_type.upper() in ['VARCHAR', 'CHAR', 'NVARCHAR', 'NCHAR']:
                        if char_length == -1:
                            formatted_type = f"{formatted_type}(MAX)"
                        else:
                            formatted_type = f"{formatted_type}({char_length})"
                    elif num_precision and data_type.upper() in ['DECIMAL', 'NUMERIC']:
                        if num_scale and num_scale > 0:
                            formatted_type = f"{formatted_type}({num_precision},{num_scale})"
                        else:
                            formatted_type = f"{formatted_type}({num_precision})"
                    
                    field = DatabaseField(
                        name=column_name,
                        type=formatted_type,
                        nullable=is_nullable == 'YES',
                        default=str(column_default) if column_default else None
                    )
                    
                    tables_dict[table_name]['fields'].append(field)
                    tables_dict[table_name]['processed_columns'].add(column_name)
            
            # Get row counts
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
            
            # Create unified schema
            unified_schema = self._create_unified_schema_result(
                tables, 
                connection,
                {
                    "version": version_info,
                    "current_database": current_db,
                    "connection_method": "connection_string"
                }
            )
            
            return DatabaseSchemaResult(
                status="success",
                message=f"Retrieved SQL Server schema: {len(tables)} tables/views from connection string",
                database_type=connection.database_type,
                database_name=current_db,
                tables=tables,
                unified_schema=unified_schema
            )
            
        except ImportError:
            return DatabaseSchemaResult(
                status="error",
                message="SQL Server connector not installed. Run: pip install pyodbc",
                database_type=connection.database_type,
                database_name=connection.database_name
            )
        except Exception as e:
            return DatabaseSchemaResult(
                status="error",
                message=f"SQL Server schema extraction failed: {str(e)}",
                database_type=connection.database_type,
                database_name=connection.database_name
            )

    async def _extract_mongodb_schema(self, connection: DatabaseConnection) -> DatabaseSchemaResult:
        """Extract MongoDB schema using connection string URI."""
        try:
            from pymongo import MongoClient
            from bson import ObjectId
            import datetime
            
            # Parse connection string
            conn_params = self._parse_connection_string(connection.connection_string, connection.database_type)
            
            # MongoDB connection using connection string
            client = MongoClient(
                connection.connection_string,
                serverSelectionTimeoutMS=10000,
                connectTimeoutMS=10000,
                socketTimeoutMS=10000
            )
            
            # Get MongoDB version
            server_info = client.server_info()
            version_info = server_info.get('version', 'unknown')
            
            # Get target database name from parsed params or connection string
            target_db = conn_params.get('database_name')
            
            # If no database specified, find available databases
            if not target_db:
                available_dbs = client.list_database_names()
                system_dbs = ['admin', 'local', 'config']
                user_dbs = [db for db in available_dbs if db not in system_dbs]
                if user_dbs:
                    target_db = user_dbs[0]
                elif available_dbs:
                    target_db = available_dbs[0]
                else:
                    client.close()
                    return DatabaseSchemaResult(
                        status="error",
                        message="No accessible databases found",
                        database_type=connection.database_type,
                        database_name=None
                    )
            
            # Verify database exists
            available_dbs = client.list_database_names()
            if target_db not in available_dbs:
                system_dbs = ['admin', 'local', 'config']
                user_dbs = [db for db in available_dbs if db not in system_dbs]
                if user_dbs:
                    target_db = user_dbs[0]
            
            db = client[target_db]
            collection_names = db.list_collection_names()
            
            if not collection_names:
                client.close()
                return DatabaseSchemaResult(
                    status="success",
                    message=f"Database '{target_db}' contains no collections",
                    database_type=connection.database_type,
                    database_name=target_db,
                    tables=[]
                )
            
            # Analyze collections
            tables = []
            for collection_name in collection_names:
                coll = db[collection_name]
                
                # Get document count
                try:
                    doc_count = coll.count_documents({})
                except:
                    doc_count = coll.estimated_document_count()
                
                if doc_count == 0:
                    tables.append(DatabaseTable(
                        name=collection_name,
                        type="collection",
                        fields=[DatabaseField(name="(empty)", type="no documents", nullable=True)],
                        row_count=0
                    ))
                    continue
                
                # Sample and analyze documents
                sample_size = min(20, doc_count)
                sample_docs = list(coll.aggregate([{"$sample": {"size": sample_size}}]))
                
                # Field analysis
                field_analysis = {}
                for doc in sample_docs:
                    self._analyze_document_fields(doc, field_analysis)
                
                # Convert to fields
                fields = []
                for field_path, info in field_analysis.items():
                    total_samples = len(sample_docs)
                    present_count = info['count']
                    field_frequency = (present_count / total_samples) * 100
                    
                    most_common_type = max(info['types'], key=info['types'].get)
                    all_types = list(info['types'].keys())
                    
                    type_info = most_common_type
                    if len(all_types) > 1:
                        type_info = f"{most_common_type} (variants: {', '.join(all_types)})"
                    
                    fields.append(DatabaseField(
                        name=field_path,
                        type=type_info,
                        nullable=field_frequency < 100,
                        default=f"Present in {field_frequency:.1f}% of documents"
                    ))
                
                fields.sort(key=lambda f: float(f.default.split()[2].rstrip('%')), reverse=True)
                
                tables.append(DatabaseTable(
                    name=collection_name,
                    type="collection",
                    fields=fields,
                    row_count=doc_count
                ))
            
            client.close()
            
            # Create unified schema
            unified_schema = self._create_unified_schema_result(
                tables, 
                connection,
                {
                    "version": version_info, 
                    "target_database": target_db,
                    "connection_method": "connection_string"
                }
            )
            
            total_docs = sum(table.row_count or 0 for table in tables)
            message = f"Analyzed {len(tables)} collections with {total_docs:,} total documents from connection string"
            
            return DatabaseSchemaResult(
                status="success",
                message=message,
                database_type=connection.database_type,
                database_name=target_db,
                tables=tables,
                unified_schema=unified_schema
            )
            
        except ImportError:
            return DatabaseSchemaResult(
                status="error",
                message="PyMongo not installed. Run: pip install pymongo",
                database_type=connection.database_type,
                database_name=connection.database_name
            )
        except Exception as e:
            return DatabaseSchemaResult(
                status="error",
                message=f"MongoDB schema extraction failed: {str(e)}",
                database_type=connection.database_type,
                database_name=connection.database_name
            )

    def _analyze_document_fields(self, doc, field_analysis, prefix=""):
        """Recursively analyze MongoDB document fields."""
        if not isinstance(doc, dict):
            return
            
        for key, value in doc.items():
            field_path = f"{prefix}.{key}" if prefix else key
            
            if field_path not in field_analysis:
                field_analysis[field_path] = {'types': {}, 'count': 0}
            
            field_analysis[field_path]['count'] += 1
            
            value_type = self._get_mongodb_type(value)
            
            if value_type in field_analysis[field_path]['types']:
                field_analysis[field_path]['types'][value_type] += 1
            else:
                field_analysis[field_path]['types'][value_type] = 1
            
            # Limit nesting depth
            if isinstance(value, dict) and len(prefix.split('.')) < 3:
                self._analyze_document_fields(value, field_analysis, field_path)
            elif isinstance(value, list) and len(value) > 0 and len(prefix.split('.')) < 3:
                for i, item in enumerate(value[:3]):
                    if isinstance(item, dict):
                        self._analyze_document_fields(item, field_analysis, f"{field_path}[{i}]")

    def _get_mongodb_type(self, value):
        """Get MongoDB-specific type name."""
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

    async def _extract_snowflake_schema(self, connection: DatabaseConnection) -> DatabaseSchemaResult:
        """Extract Snowflake schema using connection string URI."""
        try:
            # Check if snowflake package is available
            try:
                import snowflake.connector
            except ImportError:
                return DatabaseSchemaResult(
                    status="error",
                    message="snowflake-connector-python package is not installed. Install with: pip install snowflake-connector-python",
                    database_type=connection.database_type,
                    database_name=connection.database_name
                )
            
            # Parse connection string
            conn_params = self._parse_connection_string(connection.connection_string, connection.database_type)
            
            # Connect to Snowflake
            conn = snowflake.connector.connect(
                user=conn_params['username'],
                password=conn_params['password'],
                account=conn_params['account'],
                database=conn_params['database'],
                schema=conn_params['schema'],
                warehouse=conn_params.get('warehouse'),
                role=conn_params.get('role')
            )
            
            cursor = conn.cursor()
            
            # Get Snowflake version info
            cursor.execute("SELECT CURRENT_VERSION()")
            version_info = cursor.fetchone()[0]
            
            # Get current context
            cursor.execute("SELECT CURRENT_DATABASE(), CURRENT_SCHEMA(), CURRENT_WAREHOUSE(), CURRENT_ROLE()")
            context = cursor.fetchone()
            current_database = context[0]
            current_schema = context[1]
            current_warehouse = context[2]
            current_role = context[3]
            
            # Simplified Snowflake schema query using INFORMATION_SCHEMA
            cursor.execute(f"""
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
                    AND t.TABLE_CATALOG = c.TABLE_CATALOG
                WHERE t.TABLE_SCHEMA = '{current_schema}'
                    AND t.TABLE_CATALOG = '{current_database}'
                    AND t.TABLE_TYPE IN ('BASE TABLE', 'VIEW')
                ORDER BY t.TABLE_NAME, c.ORDINAL_POSITION
            """)
            
            results = cursor.fetchall()
            
            # Process results into tables and fields
            tables_dict = {}
            for row in results:
                (table_name, table_type, column_name, data_type, 
                 char_length, num_precision, num_scale, is_nullable, 
                 column_default, ordinal_position) = row
                
                if table_name not in tables_dict:
                    tables_dict[table_name] = {
                        'name': table_name,
                        'type': 'view' if table_type == 'VIEW' else 'table',
                        'fields': [],
                        'processed_columns': set()
                    }
                
                # Process column if we haven't seen it yet (handle duplicates from joins)
                if column_name and column_name not in tables_dict[table_name]['processed_columns']:
                    # Format data type
                    formatted_type = data_type
                    if char_length and data_type.upper() in ['VARCHAR', 'CHAR', 'TEXT']:
                        formatted_type = f"{formatted_type}({char_length})"
                    elif num_precision and data_type.upper() in ['DECIMAL', 'NUMERIC', 'NUMBER']:
                        if num_scale and num_scale > 0:
                            formatted_type = f"{formatted_type}({num_precision},{num_scale})"
                        else:
                            formatted_type = f"{formatted_type}({num_precision})"
                    
                    field = DatabaseField(
                        name=column_name,
                        type=formatted_type,
                        nullable=is_nullable == 'YES',
                        default=str(column_default) if column_default else None
                    )
                    
                    tables_dict[table_name]['fields'].append(field)
                    tables_dict[table_name]['processed_columns'].add(column_name)
            
            # Get row counts for tables
            tables = []
            for table_name, table_info in tables_dict.items():
                row_count = None
                if table_info['type'] == 'table':
                    try:
                        cursor.execute(f"SELECT COUNT(*) FROM {current_database}.{current_schema}.{table_name}")
                        row_count = cursor.fetchone()[0]
                    except Exception:
                        row_count = None  # Skip if we can't get row count
                
                table = DatabaseTable(
                    name=table_name,
                    type=table_info['type'],
                    fields=table_info['fields'],
                    row_count=row_count
                )
                tables.append(table)
            
            # Close connection
            cursor.close()
            conn.close()
            
            # Create unified schema
            unified_schema = self._create_unified_schema_result(
                tables, 
                connection,
                additional_info={
                    'version': version_info,
                    'current_database': current_database,
                    'current_schema': current_schema,
                    'current_warehouse': current_warehouse,
                    'current_role': current_role
                }
            )
            
            return DatabaseSchemaResult(
                status="success",
                message=f"Successfully extracted Snowflake schema from database '{current_database}', schema '{current_schema}'",
                database_type=connection.database_type,
                database_name=current_database,
                tables=tables,
                unified_schema=unified_schema
            )
            
        except Exception as e:
            return DatabaseSchemaResult(
                status="error",
                message=f"Failed to extract Snowflake schema: {str(e)}",
                database_type=connection.database_type,
                database_name=connection.database_name
            ) 