#!/usr/bin/env python3
"""Test the enhanced reserved word handling directly."""

def test_snowflake_reserved_words():
    """Test that Snowflake reserved words are properly handled."""
    
    print("🧪 Testing Snowflake Reserved Word Handling")
    print("=" * 50)
    
    # Simulate the database_specific_rules for Snowflake
    snowflake_rules = {
        'identifier_quotes': '"',
        'string_quotes': "'",
        'limit_syntax': 'LIMIT',
        'case_sensitivity': 'preserve',
        'reserved_words': ['ORDER', 'GROUP', 'USER', 'TABLE', 'SELECT', 'IS', 'IN', 'ON', 'START', 'END', 'DATE', 'TIME', 'TIMESTAMP', 'VALUE', 'TYPE', 'STATUS', 'DESCRIPTION', 'CODE', 'CLASS']
    }
    
    print("✅ Snowflake Reserved Words:")
    print(f"   {', '.join(snowflake_rules['reserved_words'])}")
    
    print("\n🔍 Key Reserved Words for Healthcare Schemas:")
    healthcare_reserved = ['START', 'END', 'DATE', 'TIME', 'STATUS', 'TYPE', 'VALUE', 'DESCRIPTION', 'CODE']
    for word in healthcare_reserved:
        if word in snowflake_rules['reserved_words']:
            quoted_example = f'e.{snowflake_rules["identifier_quotes"]}{word}{snowflake_rules["identifier_quotes"]}'
            print(f"   ✅ {word} -> {quoted_example}")
        else:
            print(f"   ⚠️  {word} (not in reserved list)")
    
    print("\n📝 Example Query Corrections:")
    print("❌ WRONG: SELECT e.start AS encounter_date")
    print('✅ RIGHT: SELECT e."START" AS encounter_date')
    print("❌ WRONG: ORDER BY e.start DESC")
    print('✅ RIGHT: ORDER BY e."START" DESC')
    print("❌ WRONG: SELECT e.end AS end_date")
    print('✅ RIGHT: SELECT e."END" AS end_date')
    
    print("\n🚀 Database-Specific Requirements Generated:")
    
    # Simulate the _create_database_specific_requirements function
    reserved_examples = []
    if 'START' in snowflake_rules['reserved_words']:
        reserved_examples.append(f'e.{snowflake_rules["identifier_quotes"]}START{snowflake_rules["identifier_quotes"]} AS encounter_date')
    if 'END' in snowflake_rules['reserved_words']:
        reserved_examples.append(f'e.{snowflake_rules["identifier_quotes"]}END{snowflake_rules["identifier_quotes"]} AS end_date')
    
    requirements = f"""
- Identifier Quotes: ALWAYS use {snowflake_rules['identifier_quotes']} for reserved words as column names
- String Quotes: Use {snowflake_rules['string_quotes']} for string values
- Limit Clause: Use {snowflake_rules['limit_syntax']} for result limiting
- Reserved Words: {', '.join(snowflake_rules['reserved_words'][:8])} (MUST wrap these in {snowflake_rules['identifier_quotes']} quotes)
- Examples: {', '.join(reserved_examples) if reserved_examples else 'Use quotes for reserved words'}
"""
    
    print(requirements)

if __name__ == "__main__":
    test_snowflake_reserved_words()