"""Test selective column quoting - only reserved keywords should be quoted"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from pha.services.dynamic_query_generator import DynamicQueryGenerator

def test_selective_quoting():
    """Test that only reserved keyword columns get quoted."""
    
    print("🧪 Testing Selective Column Quoting")
    print("=" * 50)
    
    # Test schema with mixed reserved and non-reserved column names
    test_schema = {
        "unified_schema": {
            "database_info": {
                "type": "postgresql",
                "name": "testdb"
            },
            "tables": [
                {
                    "name": "patients",
                    "fields": [
                        {"name": "id", "type": "integer", "primary_key": True},
                        {"name": "first_name", "type": "varchar"},  # Non-reserved
                        {"name": "last_name", "type": "varchar"},   # Non-reserved
                        {"name": "user", "type": "varchar"},        # Reserved keyword
                        {"name": "order", "type": "integer"},       # Reserved keyword
                        {"name": "start", "type": "timestamp"},     # Reserved keyword
                        {"name": "end", "type": "timestamp"},       # Reserved keyword
                        {"name": "email", "type": "varchar"},       # Non-reserved
                        {"name": "type", "type": "varchar"},        # Reserved keyword
                        {"name": "status", "type": "varchar"}       # Reserved keyword
                    ]
                },
                {
                    "name": "encounters", 
                    "fields": [
                        {"name": "encounter_id", "type": "integer", "primary_key": True},
                        {"name": "patient_id", "type": "integer"},
                        {"name": "date", "type": "date"},           # Reserved keyword
                        {"name": "description", "type": "text"},    # Non-reserved
                        {"name": "count", "type": "integer"},       # Reserved keyword
                        {"name": "level", "type": "varchar"}        # Reserved keyword
                    ]
                }
            ]
        }
    }
    
    generator = DynamicQueryGenerator()
    
    # Test the quote identifier method directly
    print("=== TESTING _quote_identifier METHOD ===")
    db_rules = generator.RESERVED_KEYWORDS['postgresql']
    
    test_columns = [
        ("id", False),           # Should NOT be quoted
        ("first_name", False),   # Should NOT be quoted  
        ("user", True),          # Should be quoted (reserved)
        ("order", True),         # Should be quoted (reserved)
        ("start", True),         # Should be quoted (reserved)
        ("end", True),           # Should be quoted (reserved)
        ("email", False),        # Should NOT be quoted
        ("type", True),          # Should be quoted (reserved)
        ("status", True),        # Should be quoted (reserved)
        ("date", True),          # Should be quoted (reserved)
        ("description", False),  # Should NOT be quoted
        ("count", True),         # Should be quoted (reserved)
        ("level", True)          # Should be quoted (reserved)
    ]
    
    for column, should_be_quoted in test_columns:
        quoted = generator._quote_identifier(column, db_rules)
        is_quoted = quoted != column
        
        status = "✅" if is_quoted == should_be_quoted else "❌"
        expected = f'"{column}"' if should_be_quoted else column
        
        print(f"{status} {column:15} -> {quoted:15} (expected: {expected})")
    
    # Test full query generation to see quoting in action
    print("\n=== TESTING FULL QUERY GENERATION ===")
    result = generator.generate_healthcare_query(
        schema=test_schema,
        patient_id="123",
        query_type="comprehensive",
        limit=10
    )
    
    if result['status'] == 'success':
        query = result['generated_query']
        print(f"Generated Query:")
        print(query)
        
        # Check if reserved keywords are properly quoted in the query
        print(f"\n=== ANALYZING QUERY FOR PROPER QUOTING ===")
        
        # These should be quoted in the query
        reserved_in_query = ['user', 'order', 'start', 'end', 'type', 'status', 'date', 'count', 'level']
        # These should NOT be quoted
        non_reserved_in_query = ['id', 'first_name', 'last_name', 'email', 'description']
        
        for keyword in reserved_in_query:
            if f'"{keyword}"' in query:
                print(f"✅ '{keyword}' is properly quoted as \"{keyword}\"")
            elif keyword in query:
                print(f"❌ '{keyword}' should be quoted but isn't")
            else:
                print(f"ℹ️  '{keyword}' not found in query")
                
        for non_keyword in non_reserved_in_query:
            if f'"{non_keyword}"' in query:
                print(f"❌ '{non_keyword}' is quoted but shouldn't be")
            elif non_keyword in query:
                print(f"✅ '{non_keyword}' is correctly NOT quoted")
            else:
                print(f"ℹ️  '{non_keyword}' not found in query")
                
    else:
        print(f"❌ Query generation failed: {result.get('error')}")

if __name__ == "__main__":
    test_selective_quoting()