#!/usr/bin/env python3
"""Query validation and post-processing utilities."""

import re
from typing import Dict, List, Tuple

class SQLQueryValidator:
    """Validates and fixes common SQL issues, especially reserved word problems."""
    
    def __init__(self, database_type: str = 'snowflake'):
        self.database_type = database_type.lower()
        self.reserved_words = self._get_reserved_words()
        self.quote_char = self._get_quote_char()
    
    def _get_reserved_words(self) -> List[str]:
        """Get reserved words for the database type."""
        reserved_words_map = {
            'snowflake': ['ORDER', 'GROUP', 'USER', 'TABLE', 'SELECT', 'IS', 'IN', 'ON', 
                         'START', 'END', 'DATE', 'TIME', 'TIMESTAMP', 'VALUE', 'TYPE', 
                         'STATUS', 'DESCRIPTION', 'CODE', 'CLASS', 'KEY'],
            'postgresql': ['ORDER', 'GROUP', 'USER', 'TABLE', 'SELECT', 'IS', 'IN', 'ON'],
            'mysql': ['ORDER', 'GROUP', 'USER', 'TABLE', 'SELECT', 'IS', 'IN', 'ON'],
            'sqlserver': ['ORDER', 'GROUP', 'USER', 'TABLE', 'SELECT', 'IS', 'IN', 'ON']
        }
        return reserved_words_map.get(self.database_type, reserved_words_map['snowflake'])
    
    def _get_quote_char(self) -> str:
        """Get the identifier quote character for the database type."""
        quote_chars = {
            'snowflake': '"',
            'postgresql': '"',
            'mysql': '`',
            'sqlserver': '['
        }
        return quote_chars.get(self.database_type, '"')
    
    def validate_and_fix_query(self, query: str) -> Tuple[str, List[str]]:
        """
        Validate and fix common SQL issues in the query.
        
        Returns:
            Tuple of (fixed_query, list_of_issues_found)
        """
        issues = []
        fixed_query = query.strip()
        
        # Fix reserved word issues
        fixed_query, reserved_issues = self._fix_reserved_words(fixed_query)
        issues.extend(reserved_issues)
        
        # Fix other common issues
        fixed_query, other_issues = self._fix_common_issues(fixed_query)
        issues.extend(other_issues)
        
        return fixed_query, issues
    
    def _fix_reserved_words(self, query: str) -> Tuple[str, List[str]]:
        """Fix unquoted reserved words in the query."""
        issues = []
        fixed_query = query
        
        # Pattern to find table_alias.column_name references
        pattern = r'\b([a-zA-Z]\w*)\s*\.\s*([a-zA-Z_]\w*)\b'
        
        def fix_column_reference(match):
            alias = match.group(1)
            column = match.group(2).upper()
            
            if column in self.reserved_words:
                # Check if already quoted
                if not (column.startswith(self.quote_char) and column.endswith(self.quote_char)):
                    issues.append(f"Fixed unquoted reserved word: {alias}.{column}")
                    return f'{alias}.{self.quote_char}{column}{self.quote_char}'
            
            return match.group(0)  # Return original if no fix needed
        
        fixed_query = re.sub(pattern, fix_column_reference, fixed_query)
        
        return fixed_query, issues
    
    def _fix_common_issues(self, query: str) -> Tuple[str, List[str]]:
        """Fix other common SQL issues."""
        issues = []
        fixed_query = query
        
        # Add LIMIT if missing (for performance)
        if 'LIMIT' not in fixed_query.upper() and 'TOP' not in fixed_query.upper():
            if self.database_type == 'sqlserver':
                # SQL Server uses TOP
                fixed_query = re.sub(r'\bSELECT\b', 'SELECT TOP 100', fixed_query, flags=re.IGNORECASE)
                issues.append("Added TOP 100 for performance")
            else:
                # Most other databases use LIMIT
                fixed_query = fixed_query.rstrip(';') + ' LIMIT 100'
                issues.append("Added LIMIT 100 for performance")
        
        # Fix common spacing issues
        fixed_query = re.sub(r'\s+', ' ', fixed_query)  # Multiple spaces to single
        fixed_query = re.sub(r'\s*,\s*', ', ', fixed_query)  # Spacing around commas
        
        return fixed_query, issues
    
    def get_query_analysis(self, query: str) -> Dict:
        """Analyze the query for potential issues."""
        analysis = {
            'has_reserved_words': False,
            'reserved_words_found': [],
            'has_limit': False,
            'estimated_complexity': 'low',
            'table_count': 0,
            'join_count': 0
        }
        
        query_upper = query.upper()
        
        # Check for reserved words
        for word in self.reserved_words:
            if f'.{word}' in query_upper and f'.{self.quote_char}{word}{self.quote_char}' not in query:
                analysis['has_reserved_words'] = True
                analysis['reserved_words_found'].append(word)
        
        # Check for LIMIT/TOP
        analysis['has_limit'] = 'LIMIT' in query_upper or 'TOP' in query_upper
        
        # Estimate complexity
        analysis['table_count'] = len(re.findall(r'\bFROM\s+\w+|\bJOIN\s+\w+', query_upper))
        analysis['join_count'] = len(re.findall(r'\bJOIN\b', query_upper))
        
        if analysis['join_count'] > 3:
            analysis['estimated_complexity'] = 'high'
        elif analysis['join_count'] > 1:
            analysis['estimated_complexity'] = 'medium'
        
        return analysis

def test_query_validator():
    """Test the query validator with problematic queries."""
    
    print("🧪 Testing SQL Query Validator")
    print("=" * 50)
    
    # Test cases with the exact issue from the user's query
    test_queries = [
        {
            'name': 'User\'s failing query',
            'query': 'SELECT DISTINCT p.id AS patient_id, p.first, p.last, e.start AS encounter_date, c.description AS condition FROM patients p JOIN encounters e ON p.id = e.patient LEFT JOIN conditions c ON e.id = c.encounter WHERE p.id = \'123\' ORDER BY e.start DESC LIMIT 25'
        },
        {
            'name': 'Multiple reserved words',
            'query': 'SELECT p.id, e.start, e.end, c.code, c.description FROM patients p JOIN encounters e ON p.id = e.patient'
        },
        {
            'name': 'Already properly quoted',
            'query': 'SELECT p.id, e."START", e."END" FROM patients p JOIN encounters e ON p.id = e.patient'
        }
    ]
    
    validator = SQLQueryValidator('snowflake')
    
    for i, test in enumerate(test_queries, 1):
        print(f"\n🔬 Test {i}: {test['name']}")
        print("-" * 40)
        print(f"Original: {test['query'][:100]}...")
        
        # Analyze the query
        analysis = validator.get_query_analysis(test['query'])
        print(f"Issues found: {analysis['reserved_words_found']}")
        
        # Fix the query
        fixed_query, issues = validator.validate_and_fix_query(test['query'])
        
        if issues:
            print("✅ Fixes applied:")
            for issue in issues:
                print(f"   - {issue}")
            print(f"Fixed: {fixed_query[:100]}...")
        else:
            print("✅ No fixes needed")

if __name__ == "__main__":
    test_query_validator()