#!/usr/bin/env python3
"""Test direct query execution without full schema discovery."""

import sys
import os
import asyncio

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from pha.db.session import db_manager
from pha.services.connection_service import ConnectionService
from pha.services.database_operation_service import DatabaseOperationService

async def test_direct_query():
    """Test direct query without full schema discovery."""
    try:
        print("Testing direct query execution...")
        
        # Connect to database
        await db_manager.connect()
        
        # Create services
        connection_service = ConnectionService(db_manager)
        db_operation_service = DatabaseOperationService(db_manager)
        
        connection_id = "68c8ea1dcee430be497cee25"
        patient_id = "687b0aca-ca63-4926-800b-90d5e92e5a0a"
        
        print(f"Testing with connection_id: {connection_id}")
        print(f"Testing with patient_id: {patient_id}")
        
        # Try a simple query to see what's in the database
        test_queries = [
            "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' LIMIT 10;",
            "SELECT * FROM patients LIMIT 1;",  # Try a common table name
            "SELECT * FROM patient_vitals LIMIT 1;",  # Try another common name
        ]
        
        for i, query in enumerate(test_queries):
            try:
                print(f"\nExecuting query {i+1}: {query}")
                
                results = await db_operation_service.execute_query(
                    connection_id=connection_id,
                    query=query,
                    limit=1
                )
                
                if results and results[0].data:
                    print(f"Query {i+1} SUCCESS: {len(results[0].data)} rows")
                    if results[0].data:
                        print(f"First row keys: {list(results[0].data[0].keys())}")
                else:
                    print(f"Query {i+1}: No data returned")
                    
            except Exception as e:
                print(f"Query {i+1} FAILED: {e}")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_direct_query())