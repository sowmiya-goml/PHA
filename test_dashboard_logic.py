#!/usr/bin/env python3
"""Test dashboard endpoint directly."""

import sys
import os
import asyncio

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from pha.db.session import db_manager
from pha.services.connection_service import ConnectionService
from pha.services.database_operation_service import DatabaseOperationService

async def test_dashboard_endpoint():
    """Test the dashboard endpoint logic directly."""
    try:
        print("Testing dashboard endpoint logic...")
        
        # Connect to database
        await db_manager.connect()
        print(f"Database connected: {db_manager.is_connected()}")
        
        if not db_manager.is_connected():
            print("Database not connected!")
            return
        
        # Create services
        connection_service = ConnectionService(db_manager)
        db_operation_service = DatabaseOperationService(db_manager)
        
        connection_id = "68c8ea1dcee430be497cee25"
        patient_id = "687b0aca-ca63-4926-800b-90d5e92e5a0a"
        
        print(f"Testing with connection_id: {connection_id}")
        print(f"Testing with patient_id: {patient_id}")
        
        # Get the database connection configuration
        connection = await connection_service.get_connection_by_id(connection_id)
        if not connection:
            print("Connection not found!")
            return
        
        print(f"Connection found: {connection.connection_name}")
        
        # Test the connection 
        print("Testing connection...")
        test_result = await connection_service.test_connection(connection_id)
        print(f"Connection test status: {test_result.status}")
        print(f"Connection test message: {test_result.message}")
        
        if test_result.status != "success":
            print("Connection test failed!")
            return
            
        # Get database schema
        print("Getting database schema...")
        schema_result = await connection_service.get_database_schema(connection_id)
        print(f"Schema status: {schema_result.status}")
        if schema_result.tables:
            print(f"Found {len(schema_result.tables)} tables")
            table_names = [t.name for t in schema_result.tables[:5]]  # First 5 tables
            print(f"First 5 tables: {table_names}")
        else:
            print("No tables found!")
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_dashboard_endpoint())