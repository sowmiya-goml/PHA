#!/usr/bin/env python3
"""Test the enhanced query cleaning with reserved word fixing."""

import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_enhanced_cleaning():
    """Test the enhanced query cleaning method."""
    
    print("🧪 Testing Enhanced Query Cleaning")
    print("=" * 50)
    
    # Simulate the BedrockService _clean_query and _fix_reserved_words methods
    import re
    
    def _fix_reserved_words(query: str) -> str:
        """Fix unquoted reserved words in the query for Snowflake."""
        
        # Snowflake reserved words that commonly appear in healthcare schemas
        reserved_words = ['START', 'END', 'DATE', 'TIME', 'TIMESTAMP', 'VALUE', 'TYPE', 
                         'STATUS', 'DESCRIPTION', 'CODE', 'CLASS', 'KEY', 'ORDER', 'GROUP']
        
        # Pattern to find table_alias.column_name references
        pattern = r'\b([a-zA-Z]\w*)\s*\.\s*([a-zA-Z_]\w*)\b'
        
        def fix_column_reference(match):
            alias = match.group(1)
            column = match.group(2).upper()
            
            if column in reserved_words:
                # Check if already quoted
                if not (match.group(2).startswith('"') and match.group(2).endswith('"')):
                    return f'{alias}."{column}"'
            
            return match.group(0)  # Return original if no fix needed
        
        fixed_query = re.sub(pattern, fix_column_reference, query)
        return fixed_query
    
    def _clean_query(query: str) -> str:
        """Enhanced cleaning with reserved word fixing."""
        # Basic cleaning
        query = query.replace('\\', '')
        query = query.replace('\n', ' ').replace('\r', ' ')
        query = re.sub(r'\s+', ' ', query).strip()
        
        # Remove markdown
        if query.startswith('```sql'):
            query = query.replace('```sql', '').replace('```', '').strip()
        elif query.startswith('```'):
            query = query.replace('```', '').strip()
        
        # Fix reserved words
        query = _fix_reserved_words(query)
        
        return query
    
    # Test the exact problematic query from the user
    test_queries = [
        {
            'name': 'User\'s exact failing query',
            'query': 'SELECT DISTINCT p.id AS patient_id, p.first, p.last, e.start AS encounter_date, c.description AS condition, m.description AS medication, pr.description AS procedure FROM patients p JOIN encounters e ON p.id = e.patient LEFT JOIN conditions c ON e.id = c.encounter LEFT JOIN medications m ON e.id = m.encounter LEFT JOIN procedures pr ON e.id = pr.encounter WHERE p.id = \'edc17058-55fb-08c7-12df-ece93a402e50\' ORDER BY e.start DESC LIMIT 25'
        },
        {
            'name': 'Already quoted query',
            'query': 'SELECT p.id, e."START", e."END" FROM patients p JOIN encounters e ON p.id = e.patient'
        },
        {
            'name': 'Mixed quoted and unquoted',
            'query': 'SELECT p.id, e.start, e."END", c.code FROM patients p JOIN encounters e ON p.id = e.patient'
        }
    ]
    
    for i, test in enumerate(test_queries, 1):
        print(f"\n🔬 Test {i}: {test['name']}")
        print("-" * 40)
        print(f"Original: {test['query'][:80]}...")
        
        cleaned_query = _clean_query(test['query'])
        
        print(f"Cleaned:  {cleaned_query[:80]}...")
        
        # Check for fixes
        fixes_applied = []
        if 'e."START"' in cleaned_query and 'e.start' in test['query']:
            fixes_applied.append('e.start -> e."START"')
        if 'c."DESCRIPTION"' in cleaned_query and 'c.description' in test['query']:
            fixes_applied.append('c.description -> c."DESCRIPTION"')
        if 'e."START" DESC' in cleaned_query and 'e.start DESC' in test['query']:
            fixes_applied.append('ORDER BY e.start -> e."START"')
        
        if fixes_applied:
            print("✅ Fixes applied:")
            for fix in fixes_applied:
                print(f"   - {fix}")
        else:
            print("ℹ️  No reserved word fixes needed")

if __name__ == "__main__":
    test_enhanced_cleaning()