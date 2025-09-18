"""Enhanced AI query generation with improved prompts and database-specific optimization."""

from typing import Dict, List, Any, Optional
import re


class QueryGenerationOptimizer:
    """Enhanced query generation logic for different databases and scenarios."""
    
    def __init__(self):
        self.database_specific_rules = {
            'snowflake': {
                'identifier_quotes': '"',
                'string_quotes': "'",
                'limit_syntax': 'LIMIT',
                'case_sensitivity': 'preserve',
                'reserved_words': ['ORDER', 'GROUP', 'USER', 'TABLE', 'SELECT', 'IS', 'IN', 'ON', 'START', 'END', 'DATE', 'TIME', 'TIMESTAMP', 'VALUE', 'TYPE', 'STATUS', 'DESCRIPTION', 'CODE', 'CLASS']
            },
            'postgresql': {
                'identifier_quotes': '"',
                'string_quotes': "'",
                'limit_syntax': 'LIMIT',
                'case_sensitivity': 'lower',
                'reserved_words': ['ORDER', 'GROUP', 'USER', 'TABLE', 'SELECT', 'IS', 'IN', 'ON']
            },
            'mysql': {
                'identifier_quotes': '`',
                'string_quotes': "'",
                'limit_syntax': 'LIMIT',
                'case_sensitivity': 'preserve',
                'reserved_words': ['ORDER', 'GROUP', 'USER', 'TABLE', 'SELECT', 'IS', 'IN', 'ON']
            },
            'sqlserver': {
                'identifier_quotes': '[',
                'string_quotes': "'",
                'limit_syntax': 'TOP',
                'case_sensitivity': 'preserve',
                'reserved_words': ['ORDER', 'GROUP', 'USER', 'TABLE', 'SELECT', 'IS', 'IN', 'ON']
            }
        }
    
    def analyze_schema_relationships(self, schema_dict: Dict) -> Dict[str, Any]:
        """Analyze schema to identify proper table relationships."""
        relationships = {}
        tables = {}
        
        # Extract table information
        unified_schema = schema_dict.get('unified_schema', {})
        if isinstance(unified_schema, dict) and 'tables' in unified_schema:
            schema_tables = unified_schema['tables']
        else:
            schema_tables = []
        
        # Build table information map
        for table in schema_tables:
            table_name = table.get('name', '')
            if table_name:
                tables[table_name.lower()] = {
                    'name': table_name,
                    'fields': table.get('fields', []),
                    'primary_keys': [],
                    'foreign_keys': []
                }
                
                # Identify primary and foreign keys
                for field in table.get('fields', []):
                    field_name = field.get('name', '').lower()
                    if field.get('primary_key', False):
                        tables[table_name.lower()]['primary_keys'].append(field_name)
                    
                    # Common foreign key patterns
                    if field_name.endswith('_id') and field_name != 'id':
                        tables[table_name.lower()]['foreign_keys'].append({
                            'column': field_name,
                            'references_table': field_name.replace('_id', '').replace('patient', 'patients')
                        })
        
        # Identify core healthcare tables
        core_tables = self._identify_core_tables(tables)
        
        return {
            'tables': tables,
            'relationships': relationships,
            'core_tables': core_tables
        }
    
    def _identify_core_tables(self, tables: Dict) -> Dict[str, str]:
        """Identify core healthcare tables by name patterns."""
        core_patterns = {
            'patients': ['patient', 'person', 'individual'],
            'encounters': ['encounter', 'visit', 'admission', 'episode'],
            'conditions': ['condition', 'diagnosis', 'problem', 'disorder'],
            'medications': ['medication', 'drug', 'prescription', 'medicine'],
            'procedures': ['procedure', 'treatment', 'operation', 'intervention'],
            'observations': ['observation', 'vital', 'lab', 'result', 'measurement'],
            'organizations': ['organization', 'facility', 'provider', 'hospital'],
            'practitioners': ['practitioner', 'physician', 'doctor', 'provider']
        }
        
        core_tables = {}
        for table_name in tables.keys():
            for category, patterns in core_patterns.items():
                if any(pattern in table_name for pattern in patterns):
                    if category not in core_tables:  # Use first match
                        core_tables[category] = tables[table_name]['name']
                    break
        
        return core_tables
    
    def create_optimized_prompt(
        self, 
        schema_dict: Dict, 
        patient_id: str, 
        query_type: str,
        database_type: str = 'postgresql'
    ) -> str:
        """Create optimized, database-specific prompts."""
        
        # Analyze schema for smart query generation
        schema_analysis = self.analyze_schema_relationships(schema_dict)
        
        # Get database rules
        db_rules = self.database_specific_rules.get(database_type.lower(), self.database_specific_rules['postgresql'])
        
        # Create base prompt structure
        escaped_patient_id = patient_id.replace("'", "''")
        
        prompt = f"""You are a {database_type.upper()} healthcare database expert. Generate an EFFICIENT, TARGETED query for patient ID '{escaped_patient_id}'.

{self._create_schema_summary(schema_analysis)}

QUERY REQUIREMENTS FOR {database_type.upper()}:
{self._create_database_specific_requirements(db_rules)}

{self._create_query_type_requirements(query_type, schema_analysis)}

CRITICAL RULES:
1. 🎯 BE SELECTIVE: Only join tables that are ESSENTIAL for the requested data
2. 🔗 VALIDATE JOINS: Only create JOINs where foreign key relationships actually exist in the schema
3. 📊 LIMIT RESULTS: Always include {db_rules['limit_syntax']} clause for performance
4. 🏷️ USE ALIASES: Use short, clear table aliases (p for patients, e for encounters, etc.)
5. 🔍 VERIFY COLUMNS: Use only column names that exist in the provided schema

Generate ONLY the SQL query - no explanations, no markdown, no extra text."""
        
        return prompt
    
    def _create_schema_summary(self, schema_analysis: Dict) -> str:
        """Create a concise schema summary focusing on key relationships."""
        tables = schema_analysis['tables']
        core_tables = schema_analysis['core_tables']
        
        summary = "AVAILABLE TABLES:\n"
        
        # Show core tables first
        for category, table_name in core_tables.items():
            if table_name.lower() in tables:
                table_info = tables[table_name.lower()]
                key_fields = [f['name'] for f in table_info['fields'][:5]]  # Show first 5 fields
                summary += f"- {table_name} ({category}): {', '.join(key_fields)}\n"
        
        # Show other important tables
        other_tables = [name for name in tables.keys() if name not in [t.lower() for t in core_tables.values()]]
        if other_tables:
            summary += "\nOTHER TABLES:\n"
            for table_name in other_tables[:10]:  # Limit to 10 to avoid prompt bloat
                table_info = tables[table_name]
                key_fields = [f['name'] for f in table_info['fields'][:3]]  # Show first 3 fields
                summary += f"- {table_info['name']}: {', '.join(key_fields)}\n"
        
        return summary
    
    def _create_database_specific_requirements(self, db_rules: Dict) -> str:
        """Create database-specific formatting requirements."""
        reserved_examples = []
        if 'START' in db_rules['reserved_words']:
            reserved_examples.append(f'e.{db_rules["identifier_quotes"]}START{db_rules["identifier_quotes"]} AS encounter_date')
        if 'END' in db_rules['reserved_words']:
            reserved_examples.append(f'e.{db_rules["identifier_quotes"]}END{db_rules["identifier_quotes"]} AS end_date')
        if 'CODE' in db_rules['reserved_words']:
            reserved_examples.append(f'c.{db_rules["identifier_quotes"]}CODE{db_rules["identifier_quotes"]} AS condition_code')
        
        return f"""
- Identifier Quotes: ALWAYS use {db_rules['identifier_quotes']} for reserved words as column names
- String Quotes: Use {db_rules['string_quotes']} for string values
- Limit Clause: Use {db_rules['limit_syntax']} for result limiting
- Reserved Words: {', '.join(db_rules['reserved_words'][:8])} (MUST wrap these in {db_rules['identifier_quotes']} quotes)
- CRITICAL EXAMPLES: {', '.join(reserved_examples) if reserved_examples else 'Quote reserved words like "START", "END", "CODE"'}
"""
    
    def _create_query_type_requirements(self, query_type: str, schema_analysis: Dict) -> str:
        """Create query-type specific requirements."""
        core_tables = schema_analysis['core_tables']
        
        if query_type == "basic":
            return f"""
BASIC QUERY FOCUS:
- Primary table: {core_tables.get('patients', 'patients')} 
- Include: Basic demographics, contact info, ID
- Joins: NONE (single table query preferred)
- Limit: 10 records maximum
"""
        
        elif query_type == "clinical":
            return f"""
CLINICAL QUERY FOCUS:
- Primary table: {core_tables.get('patients', 'patients')}
- Essential joins: {core_tables.get('conditions', 'conditions')}, {core_tables.get('medications', 'medications')}
- Optional joins: {core_tables.get('procedures', 'procedures')}, {core_tables.get('observations', 'observations')}
- Focus: Medical conditions, treatments, lab results
- Limit: 50 records maximum
"""
        
        elif query_type == "billing":
            return f"""
BILLING QUERY FOCUS:
- Primary table: {core_tables.get('patients', 'patients')}
- Essential joins: Claims, billing, payments (if available)
- Optional joins: {core_tables.get('encounters', 'encounters')} (for billing context)
- Focus: Financial data, insurance, claims
- Limit: 100 records maximum
"""
        
        else:  # comprehensive
            return f"""
COMPREHENSIVE QUERY FOCUS (SMART APPROACH):
- Primary table: {core_tables.get('patients', 'patients')}
- Core joins: {core_tables.get('encounters', 'encounters')}, {core_tables.get('conditions', 'conditions')}
- Secondary joins: {core_tables.get('medications', 'medications')}, {core_tables.get('procedures', 'procedures')}
- Optional joins: Maximum 2 additional tables that are directly related
- Strategy: Focus on most important relationships, avoid creating a massive query
- Limit: 25 records maximum for performance
"""


def test_optimizer():
    """Test the query generation optimizer."""
    optimizer = QueryGenerationOptimizer()
    
    # Mock schema
    sample_schema = {
        'unified_schema': {
            'tables': [
                {
                    'name': 'PATIENTS',
                    'fields': [
                        {'name': 'ID', 'type': 'VARCHAR', 'primary_key': True},
                        {'name': 'FIRST', 'type': 'VARCHAR'},
                        {'name': 'LAST', 'type': 'VARCHAR'},
                        {'name': 'BIRTHDATE', 'type': 'DATE'}
                    ]
                },
                {
                    'name': 'CONDITIONS',
                    'fields': [
                        {'name': 'ID', 'type': 'VARCHAR', 'primary_key': True},
                        {'name': 'PATIENT', 'type': 'VARCHAR'},
                        {'name': 'CODE', 'type': 'VARCHAR'},
                        {'name': 'DESCRIPTION', 'type': 'VARCHAR'}
                    ]
                }
            ]
        }
    }
    
    # Test analysis
    analysis = optimizer.analyze_schema_relationships(sample_schema)
    print("Schema Analysis:")
    print(f"Core Tables: {analysis['core_tables']}")
    
    # Test prompt generation
    prompt = optimizer.create_optimized_prompt(
        sample_schema, 
        "test-patient-123", 
        "clinical", 
        "snowflake"
    )
    
    print("\nGenerated Prompt:")
    print(prompt[:500] + "...")


if __name__ == "__main__":
    test_optimizer()