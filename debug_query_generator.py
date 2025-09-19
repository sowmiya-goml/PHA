"""
Quick test script to debug the dynamic query generator issue
"""
import asyncio
import sys
import os

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from pha.services.dynamic_query_generator import DynamicQueryGenerator

def test_dynamic_query_generator():
    """Test the dynamic query generator with sample data."""
    
    # Create a sample schema that matches what we'd expect from a PostgreSQL database
    sample_schema = {
        "unified_schema": {
            "database_info": {
                "type": "postgresql",
                "name": "neondb"
            },
            "tables": [
                {
                    "name": "patients",
                    "fields": [
                        {"name": "id", "type": "integer", "primary_key": True},
                        {"name": "first_name", "type": "varchar"},
                        {"name": "last_name", "type": "varchar"},
                        {"name": "email", "type": "varchar"},
                        {"name": "phone", "type": "varchar"}
                    ]
                },
                {
                    "name": "encounters",
                    "fields": [
                        {"name": "id", "type": "integer", "primary_key": True},
                        {"name": "patient_id", "type": "integer", "foreign_key": True},
                        {"name": "encounter_date", "type": "timestamp"},
                        {"name": "encounter_type", "type": "varchar"}
                    ]
                },
                {
                    "name": "diagnoses",
                    "fields": [
                        {"name": "id", "type": "integer", "primary_key": True},
                        {"name": "patient_id", "type": "integer", "foreign_key": True},
                        {"name": "diagnosis_code", "type": "varchar"},
                        {"name": "diagnosis_description", "type": "text"}
                    ]
                }
            ]
        }
    }
    
    # Initialize generator
    generator = DynamicQueryGenerator()
    
    # Test query generation
    result = generator.generate_healthcare_query(
        schema=sample_schema,
        patient_id="10",
        query_type="comprehensive",
        limit=100
    )
    
    print("=== DYNAMIC QUERY GENERATOR TEST ===")
    print(f"Status: {result.get('status')}")
    print(f"Generated Query: {result.get('generated_query')}")
    print(f"Error (if any): {result.get('error')}")
    print(f"Patient Table: {result.get('patient_table')}")
    print(f"Tables Analyzed: {result.get('tables_analyzed')}")
    print("=====================================")
    
    return result

if __name__ == "__main__":
    test_dynamic_query_generator()