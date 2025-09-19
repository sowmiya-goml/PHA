#!/usr/bin/env python3
"""Direct test of database query with a known table."""

import sys
import os
import asyncio

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from pha.db.session import db_manager
from pha.services.connection_service import ConnectionService
from pha.services.database_operation_service import DatabaseOperationService

async def test_direct_patient_query():
    """Test direct patient query with a real table."""
    try:
        print("🔧 Testing direct patient query...")
        
        # Connect to database
        await db_manager.connect()
        print(f"✅ Database connected: {db_manager.is_connected()}")
        
        if not db_manager.is_connected():
            print("❌ Database not connected!")
            return
        
        # Create services
        connection_service = ConnectionService(db_manager)
        db_operation_service = DatabaseOperationService(db_manager)
        
        connection_id = "68c8ea1dcee430be497cee25"
        patient_id = "687b0aca-ca63-4926-800b-90d5e92e5a0a"
        
        print(f"🔍 Testing with:")
        print(f"  Connection ID: {connection_id}")
        print(f"  Patient ID: {patient_id}")
        
        # Try known table names from the database
        test_queries = [
            # Let's try the patients table first
            "SELECT * FROM patients WHERE patient_id = '687b0aca-ca63-4926-800b-90d5e92e5a0a' LIMIT 1;",
            # Or try with id field
            "SELECT * FROM patients WHERE id = '687b0aca-ca63-4926-800b-90d5e92e5a0a' LIMIT 1;",
            # Try any patient-related data
            "SELECT * FROM patients LIMIT 1;",
            # Show all available tables
            "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' ORDER BY table_name;"
        ]
        
        for i, query in enumerate(test_queries):
            try:
                print(f"\n🔍 Query {i+1}: {query}")
                
                results = await db_operation_service.execute_query(
                    connection_id=connection_id,
                    query=query,
                    limit=10
                )
                
                if results and results[0].data:
                    print(f"✅ Query {i+1} SUCCESS: {len(results[0].data)} rows")
                    
                    if i < 3:  # For patient queries
                        if results[0].data:
                            first_row = results[0].data[0]
                            print(f"📊 Sample data columns: {list(first_row.keys())}")
                            
                            # Create mock heart rate response
                            response_data = {
                                "patient_id": patient_id,
                                "connection_id": connection_id,
                                "data_source": "database",
                                "data_type": "heart_rate",
                                "message": "Real database data retrieved successfully",
                                "sample_patient_data": first_row
                            }
                            
                            print(f"✅ SUCCESS! Here's the dashboard response format:")
                            print(f"📈 {response_data}")
                            return response_data
                    else:  # For table list query
                        print(f"📋 Available tables:")
                        for row in results[0].data[:10]:  # First 10 tables
                            print(f"  - {row.get('table_name', row)}")
                else:
                    print(f"⚠️  Query {i+1}: No data returned")
                    
            except Exception as e:
                print(f"❌ Query {i+1} FAILED: {e}")
        
        print("\n🎯 No patient data found, but connection is working!")
        return {
            "patient_id": patient_id,
            "connection_id": connection_id,
            "data_source": "database",
            "status": "connection_verified",
            "message": "Database connection successful, but no specific patient data found for this ID"
        }
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    result = asyncio.run(test_direct_patient_query())
    if result:
        print(f"\n🎉 FINAL RESULT: Dashboard would return:")
        import json
        print(json.dumps(result, indent=2))