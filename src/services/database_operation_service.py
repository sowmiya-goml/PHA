"""Database operation service for executing queries against different database types."""

import time
import re
import json
from typing import List, Dict, Any
from urllib.parse import urlparse
import pymongo
import psycopg2
import mysql.connector
import oracledb
import pyodbc
import snowflake.connector
import datetime
from datetime import datetime as dt

from schemas.database_operations import DatabaseQueryResult, QueryValidationResult
from services.connection_service import ConnectionService

class DatabaseOperationService:
    """Service for executing queries against different database types."""
    
    def __init__(self, db_manager):
        self.db_manager = db_manager
        self.connection_service = ConnectionService(db_manager)
        
        # Basic SQL injection patterns for read-only validation
        self.dangerous_patterns = [
            r'\b(DROP|DELETE|UPDATE|INSERT|CREATE|ALTER|TRUNCATE)\b',
            r'\b(EXEC|EXECUTE)\b',
            r';\s*--',
            r'/\*.*\*/'
        ]
    
    def _serialize_datetime_objects(self, data: List[Dict]) -> List[Dict]:
        """Convert datetime objects to ISO format strings for JSON serialization."""
        serialized_data = []
        for item in data:
            serialized_item = {}
            for key, value in item.items():
                if isinstance(value, (datetime.datetime, datetime.date, datetime.time)):
                    serialized_item[key] = value.isoformat()
                elif value is None:
                    serialized_item[key] = None
                else:
                    serialized_item[key] = value
            serialized_data.append(serialized_item)
        return serialized_data
    
    def validate_query_safety(self, query: str, database_type: str = "sql") -> QueryValidationResult:
        """Validate that a query is safe to execute (read-only, no injections)."""
        if database_type.lower() == "mongodb":
            return self._validate_mongodb_query(query)
        else:
            return self._validate_sql_query(query)
    
    def _validate_sql_query(self, query: str) -> QueryValidationResult:
        """Validate SQL query safety."""
        validation_errors = []
        normalized_query = query.upper().strip()
        
        # Check if query starts with SELECT
        if not normalized_query.startswith('SELECT'):
            validation_errors.append("Query must be a SELECT statement only")
        
        # Check for dangerous patterns
        for pattern in self.dangerous_patterns:
            if re.search(pattern, normalized_query, re.IGNORECASE):
                validation_errors.append(f"Dangerous pattern detected")
                break
        
        is_valid = len(validation_errors) == 0
        
        return QueryValidationResult(
            is_valid=is_valid,
            validation_errors=validation_errors,
            is_read_only=is_valid,
            estimated_complexity="medium",
            safety_score=1.0 if is_valid else 0.0
        )
    
    def _validate_mongodb_query(self, query: str) -> QueryValidationResult:
        """Validate MongoDB query safety."""
        validation_errors = []
        
        # Check for write operations
        dangerous_ops = ['insert', 'update', 'delete', 'drop', 'create', 'remove']
        query_lower = query.lower()
        
        for op in dangerous_ops:
            if op in query_lower:
                validation_errors.append(f"Write operation detected: {op}")
                break
        
        # Try to parse as JSON
        if query.strip().startswith('{'):
            try:
                json.loads(query)
            except json.JSONDecodeError:
                validation_errors.append("Invalid MongoDB query format")
        
        is_valid = len(validation_errors) == 0
        
        return QueryValidationResult(
            is_valid=is_valid,
            validation_errors=validation_errors,
            is_read_only=is_valid,
            estimated_complexity="low",
            safety_score=1.0 if is_valid else 0.0
        )
    
    async def execute_query(
        self, 
        connection_id: str, 
        query: str, 
        params: dict = None,
        limit: int = 100
    ) -> List[DatabaseQueryResult]:
        """Execute a query against the specified database connection."""
        # Get connection details
        connection = await self.connection_service.get_connection_by_id(connection_id)
        if not connection:
            raise ValueError(f"Connection not found: {connection_id}")
        
        # Validate query safety
        validation_result = self.validate_query_safety(query, connection.database_type)
        if not validation_result.is_valid:
            raise ValueError(f"Query validation failed: {validation_result.validation_errors}")
        
        # Execute based on database type
        database_type = connection.database_type.lower()
        
        if database_type == "mongodb":
            return await self._execute_mongodb_query(connection, query, limit, params)
        elif database_type in ["postgresql", "postgres"]:
            return await self._execute_postgresql_query(connection, query, limit, params)
        elif database_type == "mysql":
            return await self._execute_mysql_query(connection, query, limit, params)
        elif database_type == "oracle":
            return await self._execute_oracle_query(connection, query, limit, params)
        elif database_type in ["sqlserver", "mssql"]:
            return await self._execute_sqlserver_query(connection, query, limit, params)
        elif database_type == "snowflake":
            return await self._execute_snowflake_query(connection, query, limit, params)
        else:
            raise ValueError(f"Unsupported database type: {database_type}")
    
    def _get_connection_params(self, connection):
        """Get connection parameters using existing connection service logic."""
        return self.connection_service._parse_connection_string(connection)
    
    async def _execute_mongodb_query(self, connection, query: str, limit: int, params: dict = None) -> List[DatabaseQueryResult]:
        """Execute MongoDB query."""
        start_time = time.time()
        client = None
        
        try:
            conn_params = self._get_connection_params(connection)
            
            # Build MongoDB URI
            if ".mongodb.net" in conn_params['host']:
                mongo_uri = f"mongodb+srv://{conn_params['username']}:{conn_params['password']}@{conn_params['host']}/{conn_params['database_name']}?retryWrites=true&w=majority"
            else:
                mongo_uri = f"mongodb://{conn_params['username']}:{conn_params['password']}@{conn_params['host']}:{conn_params['port']}/{conn_params['database_name']}"
            
            client = pymongo.MongoClient(mongo_uri)
            db = client[conn_params['database_name']]
            
            # Parse MongoDB query
            if query.strip().startswith('{'):
                query_data = json.loads(query)
                collection_name = query_data.get('collection', 'patients')
                filter_query = query_data.get('filter', {})
                projection = query_data.get('projection', {})
            else:
                collection_name = 'patients'
                filter_query = json.loads(query) if query.strip() else {}
                projection = {}
                
            if params:
                filter_query.update(params)
            
            collection = db[collection_name]
            cursor = collection.find(filter_query, projection).limit(limit)
            results = list(cursor)
            
            # Convert ObjectId to string and handle datetime serialization
            data = []
            for result in results:
                if '_id' in result:
                    result['_id'] = str(result['_id'])
                data.append(result)
            
            # Serialize datetime objects
            serialized_data = self._serialize_datetime_objects(data)
            
            execution_time = (time.time() - start_time) * 1000
            
            return [DatabaseQueryResult(
                table_name=collection_name,
                query=query,
                row_count=len(serialized_data),
                data=serialized_data,
                execution_time_ms=execution_time
            )]
            
        except Exception as e:
            raise Exception(f"MongoDB query execution failed: {str(e)}")
        finally:
            if client:
                client.close()
    
    async def _execute_postgresql_query(self, connection, query: str, limit: int, params: dict = None) -> List[DatabaseQueryResult]:
        """Execute PostgreSQL query."""
        start_time = time.time()
        conn = None
        
        try:
            #print("👍👍👍👍👍👍👍👍")
            conn_params = self._get_connection_params(connection)
            
            # Add LIMIT if not present
            if 'LIMIT' not in query.upper():
                query = f"{query} LIMIT {limit}"
            
            # Handle SSL for cloud databases
            if "neon.tech" in conn_params['host'] or "aws" in conn_params['host']:
                conn = psycopg2.connect(
                    host=conn_params['host'],
                    port=conn_params['port'],
                    database=conn_params['database_name'],
                    user=conn_params['username'],
                    password=conn_params['password'],
                    sslmode='require'
                )
            else:
                conn = psycopg2.connect(
                    host=conn_params['host'],
                    port=conn_params['port'],
                    database=conn_params['database_name'],
                    user=conn_params['username'],
                    password=conn_params['password']
                )
            
            cursor = conn.cursor()
            cursor.execute(query)
            results = cursor.fetchall()
            column_names = [desc[0] for desc in cursor.description]
            data = [dict(zip(column_names, row)) for row in results]
            
            # Serialize datetime objects
            serialized_data = self._serialize_datetime_objects(data)
            
            execution_time = (time.time() - start_time) * 1000
            
            #print("🎶🎶🎶🎶🎶🎶🎶🎶🎶🎶🎶")
            return [DatabaseQueryResult(
                table_name="query_result",
                query=query,
                row_count=len(serialized_data),
                data=serialized_data,
                execution_time_ms=execution_time
            )]
            
        except Exception as e:
            raise Exception(f"PostgreSQL query execution failed: {str(e)}")
        finally:
            if conn:
                conn.close()
    
    async def _execute_mysql_query(self, connection, query: str, limit: int, params: dict = None) -> List[DatabaseQueryResult]:
        """Execute MySQL query."""
        start_time = time.time()
        conn = None
        
        try:
            conn_params = self._get_connection_params(connection)
            
            # Add LIMIT if not present
            if 'LIMIT' not in query.upper():
                query = f"{query} LIMIT {limit}"
            
            conn = mysql.connector.connect(
                host=conn_params['host'],
                port=conn_params['port'],
                database=conn_params['database_name'],
                user=conn_params['username'],
                password=conn_params['password']
            )
            
            cursor = conn.cursor(dictionary=True)
            cursor.execute(query)
            results = cursor.fetchall()
            
            # Serialize datetime objects
            serialized_data = self._serialize_datetime_objects(results)
            
            execution_time = (time.time() - start_time) * 1000
            
            return [DatabaseQueryResult(
                table_name="query_result",
                query=query,
                row_count=len(serialized_data),
                data=serialized_data,
                execution_time_ms=execution_time
            )]
            
        except Exception as e:
            raise Exception(f"MySQL query execution failed: {str(e)}")
        finally:
            if conn:
                conn.close()
    
    async def _execute_oracle_query(self, connection, query: str, limit: int, params: dict = None) -> List[DatabaseQueryResult]:
        """Execute Oracle query."""
        start_time = time.time()
        conn = None
        
        try:
            conn_params = self._get_connection_params(connection)
            
            # Add ROWNUM limit if not present
            if 'ROWNUM' not in query.upper() and 'LIMIT' not in query.upper():
                query = f"SELECT * FROM ({query}) WHERE ROWNUM <= {limit}"
            
            dsn = oracledb.makedsn(conn_params['host'], conn_params['port'], conn_params['database_name'])
            conn = oracledb.connect(conn_params['username'], conn_params['password'], dsn)
            
            cursor = conn.cursor()
            cursor.execute(query)
            results = cursor.fetchall()
            column_names = [desc[0] for desc in cursor.description]
            data = [dict(zip(column_names, row)) for row in results]
            
            # Serialize datetime objects
            serialized_data = self._serialize_datetime_objects(data)
            
            execution_time = (time.time() - start_time) * 1000
            
            return [DatabaseQueryResult(
                table_name="query_result",
                query=query,
                row_count=len(serialized_data),
                data=serialized_data,
                execution_time_ms=execution_time
            )]
            
        except Exception as e:
            raise Exception(f"Oracle query execution failed: {str(e)}")
        finally:
            if conn:
                conn.close()
    
    async def _execute_sqlserver_query(self, connection, query: str, limit: int, params: dict = None) -> List[DatabaseQueryResult]:
        """Execute SQL Server query."""
        start_time = time.time()
        conn = None
        
        try:
            conn_params = self._get_connection_params(connection)
            
            # Add TOP clause if not present
            if 'TOP' not in query.upper() and 'LIMIT' not in query.upper():
                query = query.replace('SELECT', f'SELECT TOP {limit}', 1)
            
            conn_str = f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={conn_params['host']},{conn_params['port']};DATABASE={conn_params['database_name']};UID={conn_params['username']};PWD={conn_params['password']}"
            conn = pyodbc.connect(conn_str)
            
            cursor = conn.cursor()
            cursor.execute(query)
            results = cursor.fetchall()
            column_names = [column[0] for column in cursor.description]
            data = [dict(zip(column_names, row)) for row in results]
            
            # Serialize datetime objects
            serialized_data = self._serialize_datetime_objects(data)
            
            execution_time = (time.time() - start_time) * 1000
            
            return [DatabaseQueryResult(
                table_name="query_result",
                query=query,
                row_count=len(serialized_data),
                data=serialized_data,
                execution_time_ms=execution_time
            )]
            
        except Exception as e:
            raise Exception(f"SQL Server query execution failed: {str(e)}")
        finally:
            if conn:
                conn.close()

    async def _execute_snowflake_query(self, connection, query: str, limit: int, params: dict = None) -> List[DatabaseQueryResult]:
        """Execute Snowflake query."""
        start_time = time.time()
        conn = None
        
        try:
            conn_params = self._get_connection_params(connection)
            
            # Add LIMIT if not present
            if 'LIMIT' not in query.upper():
                query = f"{query} LIMIT {limit}"
            
            # Prepare Snowflake connection parameters
            snowflake_params = {
                'user': conn_params['username'],
                'password': conn_params['password'],
                'account': conn_params['host'].replace('.snowflakecomputing.com', ''),
                'database': conn_params['database_name'],
                'schema': 'PUBLIC'
            }
            
            # Handle account identifier format
            if '.ap-south-1.aws' in snowflake_params['account']:
                snowflake_params['account'] = snowflake_params['account'].replace('.ap-south-1.aws', '')
            elif '.aws' in snowflake_params['account'] or '.azure' in snowflake_params['account'] or '.gcp' in snowflake_params['account']:
                snowflake_params['account'] = snowflake_params['account'].split('.')[0]
            
            conn = snowflake.connector.connect(**snowflake_params)
            cursor = conn.cursor()
            cursor.execute(query)
            results = cursor.fetchall()
            column_names = [desc[0] for desc in cursor.description]
            data = [dict(zip(column_names, row)) for row in results]
            
            # Serialize datetime objects
            serialized_data = self._serialize_datetime_objects(data)
            
            execution_time = (time.time() - start_time) * 1000
            
            return [DatabaseQueryResult(
                table_name="query_result",
                query=query,
                row_count=len(serialized_data),
                data=serialized_data,
                execution_time_ms=execution_time
            )]
            
        except Exception as e:
            raise Exception(f"Snowflake query execution failed: {str(e)}")
        finally:
            if conn:
                conn.close()