"""Database operation service for executing queries against different database types."""

import time
import re
import json
import asyncio
from typing import List, Dict, Any, Optional, Union, Tuple
from datetime import datetime
from bson import ObjectId
import pymongo
import psycopg2
import mysql.connector

# Optional imports for other database types
try:
    import cx_Oracle
except ImportError:
    cx_Oracle = None

try:
    import pyodbc
except ImportError:
    pyodbc = None

try:
    from sqlalchemy import create_engine, text
except ImportError:
    create_engine = None
    text = None
from urllib.parse import urlparse

from pha.schemas.database_operations import (
    DatabaseQueryResult, 
    QueryValidationResult, 
    DatabaseConnectionInfo
)
from pha.services.connection_service import ConnectionService


class DatabaseOperationService:
    """Service for executing queries against different database types."""
    
    def __init__(self, db_manager):
        self.db_manager = db_manager
        self.connection_service = ConnectionService(db_manager)
        
        # SQL injection patterns to block
        self.dangerous_patterns = [
            r'\b(DROP|DELETE|UPDATE|INSERT|CREATE|ALTER|TRUNCATE)\b',
            r'\b(EXEC|EXECUTE)\b',
            r';\s*--',
            r'/\*.*\*/',
            r'\bUNION\s+SELECT\b',
            r'\bINTO\s+OUTFILE\b',
            r'\bLOAD_FILE\b',
            r'\bxp_cmdshell\b'
        ]
    
    def validate_query_safety(self, query: str, database_type: str = "sql") -> QueryValidationResult:
        """
        Validate that a query is safe to execute (read-only, no injections).
        
        Args:
            query: The query string to validate
            database_type: Type of database ("sql", "mongodb", etc.)
            
        Returns:
            QueryValidationResult with validation details
        """
        validation_errors = []
        is_read_only = True
        safety_score = 1.0
        
        if database_type.lower() == "mongodb":
            return self._validate_mongodb_query(query)
        else:
            return self._validate_sql_query(query)
    
    def _validate_sql_query(self, query: str) -> QueryValidationResult:
        """Validate SQL query safety."""
        validation_errors = []
        is_read_only = True
        safety_score = 1.0
        
        # Normalize query for checking
        normalized_query = query.upper().strip()
        
        # Check if query starts with SELECT
        if not normalized_query.startswith('SELECT'):
            is_read_only = False
            validation_errors.append("Query must be a SELECT statement only")
            safety_score -= 0.5
        
        # Check for dangerous patterns
        for pattern in self.dangerous_patterns:
            if re.search(pattern, normalized_query, re.IGNORECASE):
                validation_errors.append(f"Dangerous pattern detected: {pattern}")
                safety_score -= 0.3
                is_read_only = False
        
        # Estimate complexity based on query features
        complexity_score = 0
        if 'JOIN' in normalized_query:
            complexity_score += 2
        if 'SUBQUERY' in normalized_query or '(' in normalized_query:
            complexity_score += 2
        if 'GROUP BY' in normalized_query or 'ORDER BY' in normalized_query:
            complexity_score += 1
            
        if complexity_score >= 4:
            estimated_complexity = "high"
        elif complexity_score >= 2:
            estimated_complexity = "medium"
        else:
            estimated_complexity = "low"
        
        return QueryValidationResult(
            is_valid=len(validation_errors) == 0,
            validation_errors=validation_errors,
            is_read_only=is_read_only,
            estimated_complexity=estimated_complexity,
            safety_score=max(0.0, safety_score)
        )
    
    def _validate_mongodb_query(self, query: str) -> QueryValidationResult:
        """Validate MongoDB query safety."""
        validation_errors = []
        is_read_only = True
        safety_score = 1.0
        
        try:
            # Try to parse as JSON to ensure it's valid MongoDB query
            if query.strip().startswith('{'):
                parsed_query = json.loads(query)
            else:
                # Assume it's a find query if not JSON
                parsed_query = {"operation": "find", "filter": {}}
            
            # Check for write operations
            dangerous_ops = ['insert', 'update', 'delete', 'drop', 'create', 'remove']
            query_lower = query.lower()
            
            for op in dangerous_ops:
                if op in query_lower:
                    is_read_only = False
                    validation_errors.append(f"Write operation detected: {op}")
                    safety_score -= 0.4
            
            estimated_complexity = "low"  # Most MongoDB queries are relatively simple
            
        except json.JSONDecodeError:
            validation_errors.append("Invalid MongoDB query format")
            safety_score = 0.0
            estimated_complexity = "unknown"
        
        return QueryValidationResult(
            is_valid=len(validation_errors) == 0,
            validation_errors=validation_errors,
            is_read_only=is_read_only,
            estimated_complexity=estimated_complexity,
            safety_score=max(0.0, safety_score)
        )
    
    async def execute_query(
        self, 
        connection_id: str, 
        query: str, 
        limit: int = 100
    ) -> List[DatabaseQueryResult]:
        """
        Execute a query against the specified database connection.
        
        Args:
            connection_id: Database connection ID
            query: The query to execute
            limit: Maximum number of records to return
            
        Returns:
            List of DatabaseQueryResult objects
        """
        # Get connection details
        connection = await self.connection_service.get_connection_by_id(connection_id)
        if not connection:
            raise ValueError(f"Connection not found: {connection_id}")
        
        # Validate query safety first
        validation_result = self.validate_query_safety(query, connection.database_type)
        if not validation_result.is_valid:
            raise ValueError(f"Query validation failed: {validation_result.validation_errors}")
        
        # Execute based on database type
        database_type = connection.database_type.lower()
        
        if database_type == "mongodb":
            return await self._execute_mongodb_query(connection, query, limit)
        elif database_type in ["postgresql", "postgres"]:
            return await self._execute_postgresql_query(connection, query, limit)
        elif database_type == "mysql":
            return await self._execute_mysql_query(connection, query, limit)
        elif database_type == "oracle":
            return await self._execute_oracle_query(connection, query, limit)
        elif database_type in ["sqlserver", "mssql"]:
            return await self._execute_sqlserver_query(connection, query, limit)
        else:
            raise ValueError(f"Unsupported database type: {database_type}")
    
    async def _execute_mongodb_query(
        self, 
        connection, 
        query: str, 
        limit: int
    ) -> List[DatabaseQueryResult]:
        """Execute MongoDB query."""
        start_time = time.time()
        
        try:
            # Parse connection string or build from components
            if connection.connection_string:
                client = pymongo.MongoClient(connection.connection_string)
            else:
                client = pymongo.MongoClient(
                    host=connection.host,
                    port=connection.port,
                    username=connection.username,
                    password=connection.password
                )
            
            db = client[connection.database_name]
            
            # Parse the MongoDB query
            if query.strip().startswith('{'):
                # JSON query format
                query_data = json.loads(query)
                collection_name = query_data.get('collection', 'patients')
                filter_query = query_data.get('filter', {})
                projection = query_data.get('projection', {})
            else:
                # Simple query - assume it's a filter for patients collection
                collection_name = 'patients'
                filter_query = json.loads(query) if query.strip() else {}
                projection = {}
            
            collection = db[collection_name]
            
            # Execute query with limit
            cursor = collection.find(filter_query, projection).limit(limit)
            results = list(cursor)
            
            # Convert ObjectId to string for JSON serialization
            for result in results:
                if '_id' in result:
                    result['_id'] = str(result['_id'])
            
            execution_time = (time.time() - start_time) * 1000
            
            return [DatabaseQueryResult(
                table_name=collection_name,
                query=query,
                row_count=len(results),
                data=results,
                execution_time_ms=execution_time
            )]
            
        except Exception as e:
            raise Exception(f"MongoDB query execution failed: {str(e)}")
        finally:
            if 'client' in locals():
                client.close()
    
    async def _execute_postgresql_query(
        self, 
        connection, 
        query: str, 
        limit: int
    ) -> List[DatabaseQueryResult]:
        """Execute PostgreSQL query."""
        start_time = time.time()
        
        try:
            # Add LIMIT clause if not present
            if 'LIMIT' not in query.upper():
                query = f"{query} LIMIT {limit}"
            
            # Connect to PostgreSQL
            if connection.connection_string:
                conn = psycopg2.connect(connection.connection_string)
            else:
                conn = psycopg2.connect(
                    host=connection.host,
                    port=connection.port,
                    database=connection.database_name,
                    user=connection.username,
                    password=connection.password
                )
            
            cursor = conn.cursor()
            cursor.execute(query)
            
            # Fetch results
            results = cursor.fetchall()
            column_names = [desc[0] for desc in cursor.description]
            
            # Convert to list of dictionaries
            data = [dict(zip(column_names, row)) for row in results]
            
            execution_time = (time.time() - start_time) * 1000
            
            return [DatabaseQueryResult(
                table_name="query_result",
                query=query,
                row_count=len(data),
                data=data,
                execution_time_ms=execution_time
            )]
            
        except Exception as e:
            raise Exception(f"PostgreSQL query execution failed: {str(e)}")
        finally:
            if 'conn' in locals():
                conn.close()
    
    async def _execute_mysql_query(
        self, 
        connection, 
        query: str, 
        limit: int
    ) -> List[DatabaseQueryResult]:
        """Execute MySQL query."""
        start_time = time.time()
        
        try:
            # Add LIMIT clause if not present
            if 'LIMIT' not in query.upper():
                query = f"{query} LIMIT {limit}"
            
            # Connect to MySQL
            if connection.connection_string:
                # Parse connection string for MySQL
                parsed = urlparse(connection.connection_string)
                conn = mysql.connector.connect(
                    host=parsed.hostname,
                    port=parsed.port or 3306,
                    database=parsed.path.lstrip('/'),
                    user=parsed.username,
                    password=parsed.password
                )
            else:
                conn = mysql.connector.connect(
                    host=connection.host,
                    port=connection.port,
                    database=connection.database_name,
                    user=connection.username,
                    password=connection.password
                )
            
            cursor = conn.cursor(dictionary=True)
            cursor.execute(query)
            results = cursor.fetchall()
            
            execution_time = (time.time() - start_time) * 1000
            
            return [DatabaseQueryResult(
                table_name="query_result",
                query=query,
                row_count=len(results),
                data=results,
                execution_time_ms=execution_time
            )]
            
        except Exception as e:
            raise Exception(f"MySQL query execution failed: {str(e)}")
        finally:
            if 'conn' in locals():
                conn.close()
    
    async def _execute_oracle_query(
        self, 
        connection, 
        query: str, 
        limit: int
    ) -> List[DatabaseQueryResult]:
        """Execute Oracle query."""
        if cx_Oracle is None:
            raise Exception("cx_Oracle package is not installed. Install with: pip install cx_Oracle")
            
        start_time = time.time()
        
        try:
            # Add ROWNUM limit if not present
            if 'ROWNUM' not in query.upper() and 'LIMIT' not in query.upper():
                query = f"SELECT * FROM ({query}) WHERE ROWNUM <= {limit}"
            
            # Connect to Oracle
            if connection.connection_string:
                conn = cx_Oracle.connect(connection.connection_string)
            else:
                dsn = cx_Oracle.makedsn(connection.host, connection.port, connection.database_name)
                conn = cx_Oracle.connect(connection.username, connection.password, dsn)
            
            cursor = conn.cursor()
            cursor.execute(query)
            
            # Fetch results
            results = cursor.fetchall()
            column_names = [desc[0] for desc in cursor.description]
            
            # Convert to list of dictionaries
            data = [dict(zip(column_names, row)) for row in results]
            
            execution_time = (time.time() - start_time) * 1000
            
            return [DatabaseQueryResult(
                table_name="query_result",
                query=query,
                row_count=len(data),
                data=data,
                execution_time_ms=execution_time
            )]
            
        except Exception as e:
            raise Exception(f"Oracle query execution failed: {str(e)}")
        finally:
            if 'conn' in locals():
                conn.close()
    
    async def _execute_sqlserver_query(
        self, 
        connection, 
        query: str, 
        limit: int
    ) -> List[DatabaseQueryResult]:
        """Execute SQL Server query."""
        if pyodbc is None:
            raise Exception("pyodbc package is not installed. Install with: pip install pyodbc")
            
        start_time = time.time()
        
        try:
            # Add TOP clause if not present
            if 'TOP' not in query.upper() and 'LIMIT' not in query.upper():
                query = query.replace('SELECT', f'SELECT TOP {limit}', 1)
            
            # Connect to SQL Server
            if connection.connection_string:
                conn = pyodbc.connect(connection.connection_string)
            else:
                conn_str = f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={connection.host},{connection.port};DATABASE={connection.database_name};UID={connection.username};PWD={connection.password}"
                conn = pyodbc.connect(conn_str)
            
            cursor = conn.cursor()
            cursor.execute(query)
            
            # Fetch results
            results = cursor.fetchall()
            column_names = [column[0] for column in cursor.description]
            
            # Convert to list of dictionaries
            data = [dict(zip(column_names, row)) for row in results]
            
            execution_time = (time.time() - start_time) * 1000
            
            return [DatabaseQueryResult(
                table_name="query_result",
                query=query,
                row_count=len(data),
                data=data,
                execution_time_ms=execution_time
            )]
            
        except Exception as e:
            raise Exception(f"SQL Server query execution failed: {str(e)}")
        finally:
            if 'conn' in locals():
                conn.close()
