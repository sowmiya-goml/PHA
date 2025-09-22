"""
Dynamic SQL Query Generator - Simplified healthcare query generation.
Generates SQL queries based on database schema with proper reserved keyword handling.
"""
import re
import json
from typing import Dict, List, Any, Optional, Union
from datetime import datetime


class DynamicQueryGenerator:
    """Simplified SQL query generator for healthcare databases."""
    
    # Simplified reserved keywords - only the ones that actually matter
    COMMON_RESERVED_WORDS = {'user', 'order', 'group', 'table', 'key', 'type', 'status', 'class', 'level', 'date', 'time'}
    
    # Database-specific quote characters and limit syntax
    DB_RULES = {
        'postgresql': {'quote': '"', 'limit': 'LIMIT {limit}'},
        'mysql': {'quote': '`', 'limit': 'LIMIT {limit}'},
        'sqlserver': {'quote': '[', 'quote_end': ']', 'limit': 'TOP {limit}'},
        'oracle': {'quote': '"', 'limit': 'ROWNUM <= {limit}'},
        'snowflake': {'quote': '"', 'limit': 'LIMIT {limit}'}
    }
    
    def generate_healthcare_query(
        self,
        schema: Union[str, Dict],
        patient_id: str,
        query_type: str = "comprehensive",
        limit: int = 100
    ) -> Dict[str, Any]:
        """
        Generate SQL queries based on database schema.
        
        Args:
            schema: Database schema (unified format from schema extraction)
            patient_id: Patient ID to query for
            query_type: Type of query ('comprehensive', 'clinical', 'billing', 'basic')
            limit: Maximum number of records to return
            
        Returns:
            Dict containing generated query and metadata
        """
        try:
            # Parse schema input
            if isinstance(schema, str):
                schema_dict = json.loads(schema) if schema.startswith('{') else {"raw_schema": schema}
            else:
                schema_dict = schema
            
            # Extract database info and tables
            db_info = schema_dict.get('unified_schema', {}).get('database_info', {})
            db_type = db_info.get('type', 'postgresql').lower()
            tables = schema_dict.get('unified_schema', {}).get('tables', [])
            
            if not tables:
                return {
                    "status": "error",
                    "error": "No tables found in schema",
                    "query_type": query_type,
                    "patient_id": patient_id
                }
            
            # Get database rules
            db_rules = self.DB_RULES.get(db_type, self.DB_RULES['postgresql'])
            
            # Find patient table
            patient_table = self._find_patient_table(tables)
            if not patient_table:
                return {
                    "status": "error",
                    "error": "No patient table found in schema",
                    "query_type": query_type,
                    "patient_id": patient_id
                }
            
            # Find related tables based on query type
            related_tables = self._find_related_tables(tables, query_type)
            
            # Build and construct query
            query = self._build_query(patient_table, related_tables, patient_id, query_type, db_rules, limit)
            
            return {
                "status": "success",
                "generated_query": query,
                "query_type": query_type,
                "patient_id": patient_id,
                "database_type": db_type,
                "metadata": {
                    "patient_table": patient_table['name'],
                    "related_tables": [t['name'] for t in related_tables],
                    "tables_analyzed": len(tables)
                },
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": f"Query generation failed: {str(e)}",
                "query_type": query_type,
                "patient_id": patient_id
            }
    
    def _find_patient_table(self, tables: List[Dict]) -> Optional[Dict]:
        """Find the primary patient table."""
        # Look for table with 'patient' in name
        for table in tables:
            if 'patient' in table['name'].lower():
                return self._prepare_table_info(table)
        
        # Look for tables with patient_id columns
        for table in tables:
            table_info = self._prepare_table_info(table)
            if table_info['patient_id_columns']:
                return table_info
        
        # Fallback to first table with ID column
        for table in tables:
            table_info = self._prepare_table_info(table)
            if table_info['id_columns']:
                return table_info
        
        return None
    
    def _prepare_table_info(self, table: Dict) -> Dict:
        """Prepare table info with column analysis."""
        columns = table.get('fields', table.get('columns', []))
        
        table_info = {
            'name': table['name'],
            'columns': columns,
            'patient_id_columns': [],
            'id_columns': []
        }
        
        # Find patient ID and ID columns
        for col in columns:
            col_name_lower = col['name'].lower()
            if 'patient' in col_name_lower and 'id' in col_name_lower:
                table_info['patient_id_columns'].append(col['name'])
            elif 'id' in col_name_lower or col.get('primary_key', False):
                table_info['id_columns'].append(col['name'])
        
        return table_info
    
    def _find_related_tables(self, tables: List[Dict], query_type: str) -> List[Dict]:
        """Find related tables based on query type."""
        related_tables = []
        
        # Simple categorization patterns
        patterns = {
            'clinical': ['diagnos', 'condition', 'medication', 'procedure', 'lab', 'test', 'vital', 'encounter', 'visit'],
            'billing': ['bill', 'payment', 'claim', 'insurance', 'charge'],
            'basic': ['appointment', 'provider']
        }
        
        # Select patterns based on query type
        if query_type == "comprehensive":
            search_patterns = patterns['clinical'] + patterns['billing'] + patterns['basic']
            max_tables = 5
        elif query_type == "clinical":
            search_patterns = patterns['clinical']
            max_tables = 4
        elif query_type == "billing":
            search_patterns = patterns['billing'] + patterns['basic']
            max_tables = 3
        else:  # basic
            search_patterns = patterns['basic']
            max_tables = 2
        
        # Find matching tables
        for table in tables:
            if len(related_tables) >= max_tables:
                break
                
            table_name_lower = table['name'].lower()
            if any(pattern in table_name_lower for pattern in search_patterns):
                table_info = self._prepare_table_info(table)
                # Only include if it has patient_id or can be joined
                if table_info['patient_id_columns'] or table_info['id_columns']:
                    related_tables.append(table_info)
        
        return related_tables
    
    def _build_query(
        self, 
        patient_table: Dict, 
        related_tables: List[Dict], 
        patient_id: str, 
        query_type: str,
        db_rules: Dict,
        limit: int
    ) -> str:
        """Build the complete SQL query."""
        
        # Select columns from patient table
        patient_alias = 'p'
        select_fields = []
        
        patient_columns = self._select_columns(patient_table, query_type, is_patient_table=True)
        for col in patient_columns:
            quoted_col = self._quote_if_needed(col, db_rules)
            select_fields.append(f"{patient_alias}.{quoted_col}")
        
        # Build FROM clause
        patient_table_quoted = self._quote_if_needed(patient_table['name'], db_rules)
        from_clause = f"{patient_table_quoted} {patient_alias}"
        
        # Build JOINs and add columns from related tables
        join_clauses = []
        alias_counter = 1
        
        for related_table in related_tables:
            alias = f"t{alias_counter}"
            related_table_quoted = self._quote_if_needed(related_table['name'], db_rules)
            
            # Find join condition (simple patient_id matching)
            join_condition = self._get_join_condition(patient_table, related_table, patient_alias, alias, db_rules)
            if join_condition:
                join_clauses.append(f"LEFT JOIN {related_table_quoted} {alias} ON {join_condition}")
                
                # Add columns from related table
                related_columns = self._select_columns(related_table, query_type)
                for col in related_columns[:5]:  # Limit columns per table
                    quoted_col = self._quote_if_needed(col, db_rules)
                    select_fields.append(f"{alias}.{quoted_col}")
            
            alias_counter += 1
        
        # Build WHERE clause
        patient_id_col = self._get_patient_id_column(patient_table)
        if patient_id_col:
            patient_id_quoted = self._quote_if_needed(patient_id_col, db_rules)
            escaped_patient_id = patient_id.replace("'", "''")
            where_clause = f"{patient_alias}.{patient_id_quoted} = '{escaped_patient_id}'"
        else:
            where_clause = "1=1"  # Fallback
        
        # Construct final query
        query_parts = []
        
        # Handle database-specific limit syntax
        if db_rules.get('limit') == 'TOP {limit}':
            query_parts.append(f"SELECT TOP {limit} {', '.join(select_fields)}")
        else:
            query_parts.append(f"SELECT {', '.join(select_fields)}")
        
        query_parts.append(f"FROM {from_clause}")
        query_parts.extend(join_clauses)
        query_parts.append(f"WHERE {where_clause}")
        
        # Add LIMIT for databases that support it
        if db_rules.get('limit') == 'LIMIT {limit}':
            query_parts.append(f"LIMIT {limit}")
        elif db_rules.get('limit') == 'ROWNUM <= {limit}':
            # Oracle - modify WHERE clause
            query_parts[-1] += f" AND ROWNUM <= {limit}"
        
        return " ".join(query_parts)
    
    def _select_columns(self, table: Dict, query_type: str, is_patient_table: bool = False) -> List[str]:
        """Select important columns from a table."""
        columns = table['columns']
        selected = []
        
        # Always include ID columns
        for col in columns:
            col_name_lower = col['name'].lower()
            if 'id' in col_name_lower or col.get('primary_key', False):
                selected.append(col['name'])
        
        # Add query-type specific columns
        if is_patient_table:
            # Essential patient info
            patterns = ['name', 'birth', 'gender', 'email', 'phone']
            if query_type == "comprehensive":
                patterns.extend(['address', 'ssn', 'mrn', 'insurance'])
        else:
            # Related table columns based on query type
            if query_type in ["comprehensive", "clinical"]:
                patterns = ['name', 'description', 'code', 'date', 'status', 'value', 'result']
            elif query_type == "billing":
                patterns = ['amount', 'cost', 'payment', 'insurance', 'claim']
            else:  # basic
                patterns = ['name', 'date', 'status']
        
        # Find matching columns
        for col in columns:
            col_name_lower = col['name'].lower()
            if (any(pattern in col_name_lower for pattern in patterns) and 
                col['name'] not in selected):
                selected.append(col['name'])
                if len(selected) >= 10:  # Reasonable limit
                    break
        
        # Ensure we have at least a few columns
        if len(selected) < 3:
            for col in columns[:5]:
                if col['name'] not in selected:
                    selected.append(col['name'])
        
        return selected[:12]  # Max 12 columns per table
    
    def _get_join_condition(
        self, 
        patient_table: Dict, 
        related_table: Dict, 
        patient_alias: str, 
        related_alias: str, 
        db_rules: Dict
    ) -> Optional[str]:
        """Get join condition between patient table and related table."""
        
        # Get patient ID column from patient table
        patient_id_col = self._get_patient_id_column(patient_table)
        if not patient_id_col:
            return None
        
        # Look for patient_id column in related table
        for patient_id_col_name in related_table['patient_id_columns']:
            patient_id_quoted = self._quote_if_needed(patient_id_col, db_rules)
            related_id_quoted = self._quote_if_needed(patient_id_col_name, db_rules)
            return f"{patient_alias}.{patient_id_quoted} = {related_alias}.{related_id_quoted}"
        
        # Fallback: look for common ID patterns
        for col in related_table['columns']:
            col_name_lower = col['name'].lower()
            if col_name_lower in ['patient_id', 'patientid', 'pid']:
                patient_id_quoted = self._quote_if_needed(patient_id_col, db_rules)
                related_id_quoted = self._quote_if_needed(col['name'], db_rules)
                return f"{patient_alias}.{patient_id_quoted} = {related_alias}.{related_id_quoted}"
        
        return None
    
    def _get_patient_id_column(self, table: Dict) -> Optional[str]:
        """Get the patient ID column from a table."""
        # Check patient_id columns first
        if table['patient_id_columns']:
            return table['patient_id_columns'][0]
        
        # Check for common patient ID patterns
        for col in table['columns']:
            col_name_lower = col['name'].lower()
            if col_name_lower in ['id', 'patient_id', 'patientid', 'pid']:
                return col['name']
        
        # Fallback to first ID column
        if table['id_columns']:
            return table['id_columns'][0]
        
        return None
    
    def _quote_if_needed(self, identifier: str, db_rules: Dict) -> str:
        """Quote identifier if it's a reserved word."""
        if identifier.lower() in self.COMMON_RESERVED_WORDS:
            quote_char = db_rules['quote']
            quote_end = db_rules.get('quote_end', quote_char)
            return f"{quote_char}{identifier}{quote_end}"
        return identifier