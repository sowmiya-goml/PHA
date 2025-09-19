"""Direct test of selective column quoting functionality - shows terminal output"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from pha.services.dynamic_query_generator import DynamicQueryGenerator

def demonstrate_selective_quoting():
    """Demonstrate selective column quoting with terminal output."""
    
    print("🔥 PHA SELECTIVE COLUMN QUOTING DEMONSTRATION")
    print("=" * 70)
    print("Only reserved keyword columns get quoted, others remain unquoted")
    print("=" * 70)
    
    # Test schema with reserved keyword columns (like those causing syntax errors)
    test_schema = {
        "unified_schema": {
            "database_info": {
                "type": "postgresql",
                "name": "healthcare_db"
            },
            "tables": [
                {
                    "name": "patients",
                    "fields": [
                        {"name": "id", "type": "integer", "primary_key": True},
                        {"name": "patient_name", "type": "varchar"},     # Normal column
                        {"name": "user", "type": "varchar"},            # RESERVED KEYWORD ⚠️
                        {"name": "email", "type": "varchar"},           # Normal column
                        {"name": "order", "type": "integer"},           # RESERVED KEYWORD ⚠️
                        {"name": "phone", "type": "varchar"}            # Normal column
                    ]
                },
                {
                    "name": "encounters",
                    "fields": [
                        {"name": "encounter_id", "type": "integer", "primary_key": True},
                        {"name": "patient_id", "type": "integer"},
                        {"name": "start", "type": "timestamp"},         # RESERVED KEYWORD ⚠️
                        {"name": "end", "type": "timestamp"},           # RESERVED KEYWORD ⚠️
                        {"name": "description", "type": "text"},        # Normal column
                        {"name": "type", "type": "varchar"},            # RESERVED KEYWORD ⚠️
                        {"name": "status", "type": "varchar"},          # RESERVED KEYWORD ⚠️
                        {"name": "provider_name", "type": "varchar"}    # Normal column
                    ]
                },
                {
                    "name": "diagnoses",
                    "fields": [
                        {"name": "diagnosis_id", "type": "integer", "primary_key": True},
                        {"name": "patient_id", "type": "integer"},
                        {"name": "date", "type": "date"},               # RESERVED KEYWORD ⚠️
                        {"name": "code", "type": "varchar"},            # Normal column
                        {"name": "level", "type": "varchar"},           # RESERVED KEYWORD ⚠️
                        {"name": "count", "type": "integer"}            # RESERVED KEYWORD ⚠️
                    ]
                }
            ]
        }
    }
    
    generator = DynamicQueryGenerator()
    
    # Test comprehensive query generation
    print("📊 GENERATING COMPREHENSIVE HEALTHCARE QUERY...")
    print("-" * 70)
    
    result = generator.generate_healthcare_query(
        schema=test_schema,
        patient_id="PATIENT-123",
        query_type="comprehensive",
        limit=50
    )
    
    if result['status'] == 'success':
        query = result['generated_query']
        print("✅ GENERATED QUERY:")
        print(query)
        print()
        
        # Analyze the query to show selective quoting
        print("🔍 SELECTIVE QUOTING ANALYSIS:")
        print("-" * 70)
        
        # Reserved keywords that should be quoted
        reserved_found = []
        normal_found = []
        
        test_columns = [
            ("id", False), ("patient_name", False), ("user", True), ("email", False),
            ("order", True), ("phone", False), ("start", True), ("end", True),
            ("description", False), ("type", True), ("status", True), ("provider_name", False),
            ("date", True), ("code", False), ("level", True), ("count", True)
        ]
        
        for column, is_reserved in test_columns:
            if f'"{column}"' in query:
                if is_reserved:
                    reserved_found.append(f"✅ \"{column}\" - RESERVED KEYWORD (properly quoted)")
                else:
                    reserved_found.append(f"❌ \"{column}\" - NOT RESERVED (unnecessarily quoted)")
            elif column in query:
                if not is_reserved:
                    normal_found.append(f"✅ {column} - NORMAL COLUMN (correctly unquoted)")
                else:
                    normal_found.append(f"❌ {column} - RESERVED KEYWORD (missing quotes!)")
        
        print("🔒 RESERVED KEYWORDS (should be quoted):")
        for item in reserved_found:
            print(f"   {item}")
        
        print()
        print("📝 NORMAL COLUMNS (should NOT be quoted):")
        for item in normal_found:
            print(f"   {item}")
        
        print()
        print("📈 QUERY METADATA:")
        print(f"   • Database Type: {result.get('database_type')}")
        print(f"   • Tables Analyzed: {result.get('tables_analyzed')}")
        print(f"   • Patient Table: {result.get('patient_table')}")
        print(f"   • Related Tables: {', '.join(result.get('related_tables', []))}")
        
    else:
        print(f"❌ QUERY GENERATION FAILED: {result.get('error')}")
    
    print()
    print("=" * 70)
    print("🎯 SUMMARY: Only columns that are SQL reserved keywords get quoted!")
    print("   This prevents 'Syntax error: unexpected [KEYWORD]' errors")
    print("=" * 70)

if __name__ == "__main__":
    demonstrate_selective_quoting()