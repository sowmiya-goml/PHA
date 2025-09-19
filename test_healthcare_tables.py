#!/usr/bin/env python3
"""Test finding healthcare tables in the database."""

import sys
import os
import asyncio

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from pha.db.session import db_manager
from pha.services.connection_service import ConnectionService

async def test_healthcare_tables():
    """Test finding healthcare tables."""
    try:
        print("Testing healthcare table discovery...")
        
        # Connect to database
        await db_manager.connect()
        
        # Create services
        connection_service = ConnectionService(db_manager)
        
        connection_id = "68c8ea1dcee430be497cee25"
        
        # Get database schema
        schema_result = await connection_service.get_database_schema(connection_id)
        
        if schema_result.tables:
            print(f"Found {len(schema_result.tables)} tables")
            
            # Look for healthcare-related tables
            healthcare_patterns = ["heart_rate", "heartrate", "hr", "cardiac", "vitals", "vital_signs", "patient_vitals", "blood_pressure", "bp"]
            healthcare_tables = []
            
            all_table_names = [t.name.lower() for t in schema_result.tables]
            print("\nAll tables:")
            for i, table_name in enumerate(all_table_names[:20]):  # First 20 tables
                print(f"  {i+1}. {table_name}")
            
            for table in schema_result.tables:
                table_name_lower = table.name.lower()
                for pattern in healthcare_patterns:
                    if pattern in table_name_lower:
                        healthcare_tables.append(table.name)
                        break
            
            print(f"\nHealthcare tables found: {healthcare_tables}")
            
            if not healthcare_tables:
                # Look for any table that might contain patient data
                patient_patterns = ["patient", "medical", "health", "clinical", "record"]
                patient_tables = []
                
                for table in schema_result.tables:
                    table_name_lower = table.name.lower()
                    for pattern in patient_patterns:
                        if pattern in table_name_lower:
                            patient_tables.append(table.name)
                            break
                
                print(f"Patient-related tables found: {patient_tables}")
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_healthcare_tables())