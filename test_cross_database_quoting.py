"""Test selective quoting across different database types"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from pha.services.dynamic_query_generator import DynamicQueryGenerator

def test_cross_database_quoting():
    """Test selective quoting across different database types."""
    
    print("🧪 Testing Cross-Database Selective Quoting")
    print("=" * 60)
    
    generator = DynamicQueryGenerator()
    
    # Test columns with reserved keywords
    test_columns = ["id", "user", "order", "start", "end", "type", "status", "date"]
    
    databases = [
        ("postgresql", '"'),
        ("mysql", '`'),
        ("sqlserver", '[', ']'),
        ("oracle", '"'),
        ("snowflake", '"')
    ]
    
    for db_type, quote_char, *quote_end in databases:
        db_rules = generator.RESERVED_KEYWORDS[db_type]
        quote_end_char = quote_end[0] if quote_end else quote_char
        
        print(f"\n=== {db_type.upper()} DATABASE ===")
        print(f"Quote character: {quote_char}{quote_end_char}")
        
        for column in test_columns:
            quoted = generator._quote_identifier(column, db_rules)
            is_reserved = column.lower() in db_rules['keywords']
            
            if is_reserved:
                expected = f"{quote_char}{column}{quote_end_char}"
                status = "✅" if quoted == expected else "❌"
                print(f"{status} {column:10} -> {quoted:15} (reserved keyword, properly quoted)")
            else:
                status = "✅" if quoted == column else "❌"
                print(f"{status} {column:10} -> {quoted:15} (not reserved, correctly unquoted)")

def test_query_generation_per_database():
    """Test query generation with reserved keywords for each database type."""
    
    print(f"\n" + "=" * 60)
    print("🧪 Testing Query Generation Per Database Type")
    print("=" * 60)
    
    generator = DynamicQueryGenerator()
    
    # Schema with reserved keywords
    base_schema = {
        "unified_schema": {
            "database_info": {
                "type": "postgresql",  # Will be changed per test
                "name": "testdb"
            },
            "tables": [
                {
                    "name": "patients",
                    "fields": [
                        {"name": "id", "type": "integer", "primary_key": True},
                        {"name": "user", "type": "varchar"},        # Reserved
                        {"name": "order", "type": "integer"},       # Reserved
                        {"name": "start", "type": "timestamp"},     # Reserved
                        {"name": "status", "type": "varchar"}       # Reserved
                    ]
                }
            ]
        }
    }
    
    databases = ["postgresql", "mysql", "sqlserver", "oracle", "snowflake"]
    
    for db_type in databases:
        print(f"\n=== {db_type.upper()} QUERY GENERATION ===")
        
        # Update schema for this database type
        test_schema = base_schema.copy()
        test_schema["unified_schema"]["database_info"]["type"] = db_type
        
        result = generator.generate_healthcare_query(
            schema=test_schema,
            patient_id="123",
            query_type="basic",
            limit=5
        )
        
        if result['status'] == 'success':
            query = result['generated_query']
            print(f"Query: {query}")
            
            # Check for proper quoting based on database type
            db_rules = generator.RESERVED_KEYWORDS[db_type]
            quote_char = db_rules['quote_char']
            quote_end_char = db_rules.get('quote_char_end', quote_char)
            
            reserved_keywords = ['user', 'order', 'start', 'status']
            quoted_correctly = 0
            
            for keyword in reserved_keywords:
                expected_quoted = f"{quote_char}{keyword}{quote_end_char}"
                if expected_quoted in query:
                    quoted_correctly += 1
                    print(f"✅ '{keyword}' correctly quoted as {expected_quoted}")
                elif keyword in query:
                    print(f"❌ '{keyword}' found but not properly quoted")
                else:
                    print(f"ℹ️  '{keyword}' not in selected columns")
            
            print(f"Summary: {quoted_correctly}/{len([k for k in reserved_keywords if k in query])} reserved keywords properly quoted")
            
        else:
            print(f"❌ Query generation failed: {result.get('error')}")

if __name__ == "__main__":
    test_cross_database_quoting()
    test_query_generation_per_database()