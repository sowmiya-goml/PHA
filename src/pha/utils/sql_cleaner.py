"""SQL Query Cleaner Utility

This module provides functionality to clean SQL queries by removing unwanted characters
and properly formatting quotes around identifiers and keywords.
"""

import re
from typing import Set


class SQLQueryCleaner:
    """Clean and format SQL queries for proper execution."""
    
    # SQL reserved keywords that should remain quoted if needed for compatibility
    SQL_KEYWORDS = {
        'SELECT', 'FROM', 'WHERE', 'JOIN', 'INNER', 'LEFT', 'RIGHT', 'FULL', 'OUTER',
        'ON', 'AND', 'OR', 'NOT', 'IN', 'EXISTS', 'BETWEEN', 'LIKE', 'IS', 'NULL',
        'ORDER', 'BY', 'GROUP', 'HAVING', 'DISTINCT', 'ALL', 'UNION', 'INTERSECT',
        'EXCEPT', 'INSERT', 'UPDATE', 'DELETE', 'CREATE', 'DROP', 'ALTER', 'TABLE',
        'INDEX', 'VIEW', 'DATABASE', 'SCHEMA', 'CONSTRAINT', 'PRIMARY', 'FOREIGN',
        'KEY', 'REFERENCES', 'CHECK', 'UNIQUE', 'DEFAULT', 'AUTO_INCREMENT',
        'TIMESTAMP', 'DATETIME', 'DATE', 'TIME', 'YEAR', 'MONTH', 'DAY',
        'LIMIT', 'OFFSET', 'FETCH', 'FIRST', 'NEXT', 'ROWS', 'ONLY',
        'CASE', 'WHEN', 'THEN', 'ELSE', 'END', 'IF', 'COALESCE', 'NULLIF',
        'CAST', 'CONVERT', 'SUBSTRING', 'LENGTH', 'UPPER', 'LOWER', 'TRIM',
        'COUNT', 'SUM', 'AVG', 'MIN', 'MAX', 'ROUND', 'FLOOR', 'CEIL',
        'AS', 'ASC', 'DESC', 'WITH', 'RECURSIVE', 'WINDOW', 'OVER', 'PARTITION'
    }
    
    def clean_query(self, sql_query: str) -> str:
        """
        Clean SQL query by removing unwanted characters and fixing quotes.
        
        Args:
            sql_query (str): Raw SQL query with potential unwanted characters
            
        Returns:
            str: Cleaned SQL query ready for execution
        """
        if not sql_query or not isinstance(sql_query, str):
            return ""
        
        # Step 1: Remove backslashes and forward slashes
        cleaned = self._remove_unwanted_chars(sql_query)
        
        # Step 2: Fix quotes around identifiers
        cleaned = self._fix_identifier_quotes(cleaned)
        
        # Step 3: Clean up whitespace and formatting
        cleaned = self._normalize_whitespace(cleaned)
        
        return cleaned
    
    def _remove_unwanted_chars(self, query: str) -> str:
        """
        Remove backslashes and forward slashes from the query,
        but preserve them within string literals.
        """
        # Split the query into tokens, preserving string literals
        tokens = []
        i = 0
        current_token = ""
        in_string = False
        string_char = None
        
        while i < len(query):
            char = query[i]
            
            # Check for string literal start/end
            if char in ("'", '"') and not in_string:
                # Starting a string literal
                if current_token:
                    # Process the non-string token
                    processed_token = current_token.replace('\\', '').replace('/', '')
                    tokens.append(processed_token)
                    current_token = ""
                
                in_string = True
                string_char = char
                current_token = char
                
            elif char == string_char and in_string:
                # Check if it's an escaped quote
                if i > 0 and query[i-1] == '\\':
                    current_token += char
                else:
                    # End of string literal
                    current_token += char
                    tokens.append(current_token)  # Keep string literal as-is
                    current_token = ""
                    in_string = False
                    string_char = None
                    
            else:
                current_token += char
            
            i += 1
        
        # Handle remaining token
        if current_token:
            if in_string:
                # Unclosed string literal - keep as is
                tokens.append(current_token)
            else:
                # Process non-string token
                processed_token = current_token.replace('\\', '').replace('/', '')
                tokens.append(processed_token)
        
        return ''.join(tokens)
    
    def _fix_identifier_quotes(self, query: str) -> str:
        """
        Remove unnecessary quotes around column names, table names, and aliases.
        Keep quotes only where absolutely necessary (reserved keywords, special chars).
        Handles both regular quotes (") and escaped quotes (\").
        """
        # First, handle escaped quotes (\") - convert them to regular quotes temporarily
        # to use the same processing logic
        temp_query = query.replace('\\"', '"')
        
        # Pattern to match quoted identifiers (e.g., "patient_id", "first_name")
        # This captures: optional table alias + dot + quoted identifier
        pattern = r'(\w+\.)?\"([^\"]+)\"'
        
        def replace_quoted_identifier(match):
            prefix = match.group(1) or ''  # Table alias with dot (e.g., "p.")
            identifier = match.group(2)    # The quoted identifier
            
            # Check if the identifier needs quotes
            if self._needs_quotes(identifier):
                return f'{prefix}"{identifier}"'
            else:
                return f'{prefix}{identifier}'
        
        # Replace all quoted identifiers
        result = re.sub(pattern, replace_quoted_identifier, temp_query)
        
        return result
    
    def _needs_quotes(self, identifier: str) -> bool:
        """
        Determine if an identifier needs to be quoted.
        
        Args:
            identifier (str): The database identifier (column, table, etc.)
            
        Returns:
            bool: True if quotes are needed, False otherwise
        """
        # Convert to uppercase for keyword check
        upper_identifier = identifier.upper()
        
        # Check if it's a SQL keyword
        if upper_identifier in self.SQL_KEYWORDS:
            return True
        
        # Check if it contains special characters (spaces, hyphens, etc.)
        if re.search(r'[^a-zA-Z0-9_]', identifier):
            return True
        
        # Check if it starts with a number
        if identifier and identifier[0].isdigit():
            return True
        
        # No quotes needed for regular identifiers
        return False
    
    def _normalize_whitespace(self, query: str) -> str:
        """Clean up whitespace and formatting in the query."""
        # Remove extra spaces
        query = re.sub(r'\s+', ' ', query)
        
        # Clean up spaces around operators and punctuation
        query = re.sub(r'\s*,\s*', ', ', query)
        query = re.sub(r'\s*=\s*', ' = ', query)
        query = re.sub(r'\s*\(\s*', '(', query)
        query = re.sub(r'\s*\)\s*', ') ', query)
        
        # Clean up line breaks and indentation (optional - you can remove this if you want to preserve formatting)
        lines = query.split('\n')
        cleaned_lines = []
        for line in lines:
            stripped = line.strip()
            if stripped:
                cleaned_lines.append(stripped)
        
        query = ' '.join(cleaned_lines)
        
        # Trim and ensure single space separation
        query = query.strip()
        
        return query


# Convenience function for direct usage
def clean_sql_query(sql_query: str) -> str:
    """
    Clean a SQL query by removing unwanted characters and fixing quotes.
    
    Args:
        sql_query (str): Raw SQL query to clean
        
    Returns:
        str: Cleaned SQL query ready for execution
    """
    cleaner = SQLQueryCleaner()
    return cleaner.clean_query(sql_query)


# Example usage and testing
if __name__ == "__main__":
    # Test with the provided example
    test_query = '''SELECT DISTINCT p.\"patient_id\", p.\"first_name\", p.\"last_name\", p.\"date_of_birth\", e.\"visit_date\", e.\"visit_type\", d.\"diagnosis_name\", m.\"medication_name\" 
FROM peds_patient_demographics p 
JOIN peds_visit_types e ON p.\"patient_id\" = e.\"patient_id\" 
LEFT JOIN peds_diagnosis_types d ON e.\"visit_id\" = d.\"visit_id\" 
LEFT JOIN peds_medications m ON p.\"patient_id\" = m.\"patient_id\" 
WHERE p.\"patient_id\" = '5' 
ORDER BY e.\"visit_date\" DESC 
LIMIT 25;'''
    
    print("Original Query:")
    print(test_query)
    print("\n" + "="*80 + "\n")
    
    cleaned = clean_sql_query(test_query)
    print("Cleaned Query:")
    print(cleaned)
    
    print("\n" + "="*80 + "\n")
    print("Test Results:")
    
    # Check results without backslashes in f-strings
    has_quoted_identifier = '"patient_id"' not in cleaned
    has_table_alias = 'p.patient_id' in cleaned
    has_literal = "'5'" in cleaned
    has_sql_keywords = 'SELECT' in cleaned and 'FROM' in cleaned
    
    print(f"✓ Removed quotes from identifiers: {has_quoted_identifier}")
    print(f"✓ Preserved table aliases: {has_table_alias}")
    print(f"✓ Preserved string literals: {has_literal}")
    print(f"✓ Maintained SQL structure: {has_sql_keywords}")