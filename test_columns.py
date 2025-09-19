"""Test the improved column selection"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from pha.services.dynamic_query_generator import DynamicQueryGenerator

# Create a more comprehensive test schema
test_schema = {
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
                    {"name": "mrn", "type": "varchar"},
                    {"name": "first_name", "type": "varchar"},
                    {"name": "last_name", "type": "varchar"},
                    {"name": "middle_name", "type": "varchar"},
                    {"name": "date_of_birth", "type": "date"},
                    {"name": "gender", "type": "varchar"},
                    {"name": "email", "type": "varchar"},
                    {"name": "phone", "type": "varchar"},
                    {"name": "address", "type": "varchar"},
                    {"name": "city", "type": "varchar"},
                    {"name": "state", "type": "varchar"},
                    {"name": "zip_code", "type": "varchar"},
                    {"name": "ssn", "type": "varchar"},
                    {"name": "insurance_id", "type": "varchar"},
                    {"name": "emergency_contact", "type": "varchar"},
                    {"name": "created_at", "type": "timestamp"},
                    {"name": "updated_at", "type": "timestamp"}
                ]
            },
            {
                "name": "diagnoses",
                "fields": [
                    {"name": "id", "type": "integer", "primary_key": True},
                    {"name": "patient_id", "type": "integer", "foreign_key": True},
                    {"name": "diagnosis_code", "type": "varchar"},
                    {"name": "diagnosis_description", "type": "text"},
                    {"name": "diagnosis_date", "type": "date"},
                    {"name": "severity", "type": "varchar"},
                    {"name": "status", "type": "varchar"},
                    {"name": "provider_id", "type": "integer"},
                    {"name": "notes", "type": "text"},
                    {"name": "created_at", "type": "timestamp"},
                    {"name": "updated_at", "type": "timestamp"}
                ]
            }
        ]
    }
}

generator = DynamicQueryGenerator()

# Debug table analysis
print("=== DEBUGGING TABLE ANALYSIS ===")
tables = test_schema['unified_schema']['tables']
table_analysis = generator._analyze_healthcare_tables(tables)

print("Table Analysis Results:")
for category, table_list in table_analysis.items():
    print(f"  {category}: {len(table_list)} tables")
    for table in table_list:
        print(f"    - {table['name']} (patient_id_cols: {table['patient_id_columns']}, key_cols: {table['key_columns']})")

print("\n=== TESTING IMPROVED COLUMN SELECTION ===")
for query_type in ["basic", "clinical", "comprehensive"]:
    print(f"\n--- Testing {query_type.upper()} query ---")
    result = generator.generate_healthcare_query(
        schema=test_schema,
        patient_id="123",
        query_type=query_type,
        limit=50
    )
    
    if result['status'] == 'success':
        query = result['generated_query']
        print(f"Generated Query:\n{query}\n")
        
        # Count how many columns are selected
        select_part = query.split(' FROM ')[0].replace('SELECT ', '')
        columns = [col.strip() for col in select_part.split(',')]
        print(f"Total columns selected: {len(columns)}")
        print(f"Columns: {', '.join(columns[:10])}{'...' if len(columns) > 10 else ''}")
        
        # Check for JOINs
        if 'JOIN' in query:
            joins = query.count('JOIN')
            print(f"Number of JOINs: {joins}")
        else:
            print("No JOINs found")
        
        print(f"Full Query: {query}")
    else:
        print(f"Error: {result.get('error')}")

print("\n=== TEST COMPLETE ===")