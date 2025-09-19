"""
Dynamic SQL Query Generator - Single function approach
Generates SQL queries based on actual database schema with proper reserved keyword handling.
"""

import re
import json
from typing import Dict, List, Any, Optional, Union


class DynamicQueryGenerator:
    """Single-function SQL query generator that dynamically uses database schema."""
    
    # Database-specific reserved keywords and quoting rules
    RESERVED_KEYWORDS = {
        'postgresql': {
            'keywords': {'user', 'order', 'group', 'table', 'column', 'index', 'view', 'key', 'primary', 'foreign', 
                        'references', 'constraint', 'check', 'unique', 'default', 'null', 'not', 'and', 'or', 'in', 
                        'exists', 'between', 'like', 'is', 'case', 'when', 'then', 'else', 'end', 'select', 'from', 
                        'where', 'having', 'limit', 'offset', 'join', 'inner', 'left', 'right', 'full', 'outer',
                        'union', 'intersect', 'except', 'distinct', 'all', 'any', 'some', 'start', 'date', 'time',
                        'type', 'status', 'level', 'class', 'position', 'rank', 'value', 'count', 'sum', 'avg',
                        'min', 'max', 'desc', 'asc', 'true', 'false', 'current', 'session', 'system'},
            'quote_char': '"',
            'string_quote': "'",
            'limit_syntax': 'LIMIT {limit}'
        },
        'mysql': {
            'keywords': {'user', 'order', 'group', 'table', 'column', 'index', 'view', 'key', 'primary', 'foreign',
                        'references', 'constraint', 'check', 'unique', 'default', 'null', 'not', 'and', 'or', 'in',
                        'exists', 'between', 'like', 'is', 'case', 'when', 'then', 'else', 'end', 'select', 'from',
                        'where', 'having', 'limit', 'offset', 'join', 'inner', 'left', 'right', 'full', 'outer',
                        'union', 'intersect', 'except', 'distinct', 'all', 'any', 'some', 'start', 'date', 'time',
                        'type', 'status', 'level', 'class', 'position', 'rank', 'value', 'count', 'sum', 'avg',
                        'min', 'max', 'desc', 'asc', 'true', 'false', 'current', 'session', 'system'},
            'quote_char': '`',
            'string_quote': "'",
            'limit_syntax': 'LIMIT {limit}'
        },
        'sqlserver': {
            'keywords': {'user', 'order', 'group', 'table', 'column', 'index', 'view', 'key', 'primary', 'foreign',
                        'references', 'constraint', 'check', 'unique', 'default', 'null', 'not', 'and', 'or', 'in',
                        'exists', 'between', 'like', 'is', 'case', 'when', 'then', 'else', 'end', 'select', 'from',
                        'where', 'having', 'top', 'join', 'inner', 'left', 'right', 'full', 'outer',
                        'union', 'intersect', 'except', 'distinct', 'all', 'any', 'some', 'start', 'date', 'time',
                        'type', 'status', 'level', 'class', 'position', 'rank', 'value', 'count', 'sum', 'avg',
                        'min', 'max', 'desc', 'asc', 'true', 'false', 'current', 'session', 'system'},
            'quote_char': '[',
            'quote_char_end': ']',
            'string_quote': "'",
            'limit_syntax': 'TOP {limit}'
        },
        'oracle': {
            'keywords': {'user', 'order', 'group', 'table', 'column', 'index', 'view', 'key', 'primary', 'foreign',
                        'references', 'constraint', 'check', 'unique', 'default', 'null', 'not', 'and', 'or', 'in',
                        'exists', 'between', 'like', 'is', 'case', 'when', 'then', 'else', 'end', 'select', 'from',
                        'where', 'having', 'rownum', 'join', 'inner', 'left', 'right', 'full', 'outer',
                        'union', 'intersect', 'minus', 'distinct', 'all', 'any', 'some', 'start', 'date', 'time',
                        'type', 'status', 'level', 'class', 'position', 'rank', 'value', 'count', 'sum', 'avg',
                        'min', 'max', 'desc', 'asc', 'true', 'false', 'current', 'session', 'system'},
            'quote_char': '"',
            'string_quote': "'",
            'limit_syntax': 'ROWNUM <= {limit}'
        },
        'snowflake': {
            'keywords': {'user', 'order', 'group', 'table', 'column', 'index', 'view', 'key', 'primary', 'foreign',
                        'references', 'constraint', 'check', 'unique', 'default', 'null', 'not', 'and', 'or', 'in',
                        'exists', 'between', 'like', 'is', 'case', 'when', 'then', 'else', 'end', 'select', 'from',
                        'where', 'having', 'limit', 'offset', 'join', 'inner', 'left', 'right', 'full', 'outer',
                        'union', 'intersect', 'except', 'distinct', 'all', 'any', 'some', 'start', 'date', 'time',
                        'type', 'status', 'level', 'class', 'position', 'rank', 'value', 'count', 'sum', 'avg',
                        'min', 'max', 'desc', 'asc', 'true', 'false', 'current', 'session', 'system'},
            'quote_char': '"',
            'string_quote': "'",
            'limit_syntax': 'LIMIT {limit}'
        }
    }
    
    def generate_healthcare_query(
        self,
        schema: Union[str, Dict],
        patient_id: str,
        query_type: str = "comprehensive",
        limit: int = 100
    ) -> Dict[str, Any]:
        """
        Single function that generates SQL queries based on actual database schema.
        
        This function:
        1. Parses the actual database schema
        2. Identifies healthcare-related tables dynamically
        3. Builds appropriate JOINs based on actual foreign key relationships
        4. Handles reserved keywords with database-specific quoting
        5. Generates optimized queries for different healthcare use cases
        
        Args:
            schema: Actual database schema (unified format from schema extraction)
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
            db_name = db_info.get('name', 'unknown')
            tables = schema_dict.get('unified_schema', {}).get('tables', [])
            
            if not tables:
                return {
                    "status": "error",
                    "error": "No tables found in schema",
                    "query_type": query_type,
                    "patient_id": patient_id
                }
            
            # Get database-specific rules
            db_rules = self.RESERVED_KEYWORDS.get(db_type, self.RESERVED_KEYWORDS['postgresql'])
            
            # Analyze schema to identify healthcare tables
            table_analysis = self._analyze_healthcare_tables(tables)
            
            # Find patient table and build primary query structure
            patient_table = self._find_patient_table(table_analysis)
            if not patient_table:
                return {
                    "status": "error",
                    "error": "No patient table found in schema",
                    "query_type": query_type,
                    "patient_id": patient_id
                }
            
            # Build query based on type
            query_parts = self._build_query_structure(
                patient_table, table_analysis, query_type, patient_id, db_rules, limit
            )
            
            # Construct final query
            final_query = self._construct_final_query(query_parts, db_type, db_rules)
            
            return {
                "status": "success",
                "generated_query": final_query,
                "query_type": query_type,
                "patient_id": patient_id,
                "database_type": db_type,
                "database_name": db_name,
                "tables_analyzed": len(tables),
                "patient_table": patient_table['name'],
                "related_tables": [t['name'] for t in table_analysis.get('related_tables', [])],
                "timestamp": self._get_timestamp()
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": f"Query generation failed: {str(e)}",
                "query_type": query_type,
                "patient_id": patient_id
            }
    
    def _analyze_healthcare_tables(self, tables: List[Dict]) -> Dict[str, Any]:
        """Analyze schema tables to identify healthcare-related ones."""
        healthcare_patterns = {
            'patient': ['patient', 'person', 'individual', 'client', 'member'],
            'clinical': ['diagnos', 'condition', 'procedure', 'medication', 'prescription', 
                        'lab', 'test', 'result', 'vital', 'observation', 'encounter', 'visit',
                        'allerg', 'symptom', 'treatment', 'therapy', 'immuniz', 'vaccin',
                        'problem', 'disorder', 'disease', 'illness', 'medical'],
            'billing': ['bill', 'invoice', 'payment', 'claim', 'insurance', 'charge', 'fee',
                       'account', 'financial', 'cost', 'price', 'revenue'],
            'administrative': ['appointment', 'schedule', 'provider', 'doctor', 'physician', 
                              'staff', 'employee', 'user', 'role', 'department', 'facility']
        }
        
        categorized_tables = {
            'patient_tables': [],
            'clinical_tables': [],
            'billing_tables': [],
            'administrative_tables': [],
            'other_tables': []
        }
        
        for table in tables:
            table_name_lower = table['name'].lower()
            categorized = False
            
            # Enhanced table analysis with column inspection
            table_info = {
                'name': table['name'],
                'type': table.get('type', 'table'),
                'columns': table.get('fields', table.get('columns', [])),  # Support both 'fields' and 'columns'
                'row_count': table.get('row_count', 0),
                'patient_id_columns': [],
                'key_columns': []
            }
            
            # Find patient ID and key columns
            for col in table_info['columns']:
                col_name_lower = col['name'].lower()
                if 'patient' in col_name_lower and 'id' in col_name_lower:
                    table_info['patient_id_columns'].append(col['name'])
                if any(key in col_name_lower for key in ['id', 'key', 'pk']):
                    table_info['key_columns'].append(col['name'])
            
            # Categorize tables (check both table name and column names)
            for category, patterns in healthcare_patterns.items():
                # Check table name
                table_matches = any(pattern in table_name_lower for pattern in patterns)
                
                # Also check column names for additional context
                column_matches = 0
                for col in table_info['columns']:
                    col_name_lower = col['name'].lower()
                    if any(pattern in col_name_lower for pattern in patterns):
                        column_matches += 1
                
                # Categorize if table name matches OR if multiple columns match
                if table_matches or column_matches >= 2:
                    if category == 'patient':
                        categorized_tables['patient_tables'].append(table_info)
                    elif category == 'clinical':
                        categorized_tables['clinical_tables'].append(table_info)
                    elif category == 'billing':
                        categorized_tables['billing_tables'].append(table_info)
                    elif category == 'administrative':
                        categorized_tables['administrative_tables'].append(table_info)
                    categorized = True
                    break
            
            if not categorized:
                categorized_tables['other_tables'].append(table_info)
        
        return categorized_tables
    
    def _find_patient_table(self, table_analysis: Dict) -> Optional[Dict]:
        """Find the primary patient table."""
        # Prefer dedicated patient tables
        if table_analysis['patient_tables']:
            return table_analysis['patient_tables'][0]
        
        # Look for tables with patient_id columns
        for category in ['clinical_tables', 'billing_tables', 'administrative_tables', 'other_tables']:
            for table in table_analysis[category]:
                if table['patient_id_columns']:
                    return table
        
        # Fallback to first table with ID-like column
        for category in table_analysis.values():
            if isinstance(category, list):
                for table in category:
                    if table['key_columns']:
                        return table
        
        return None
    
    def _build_query_structure(
        self, 
        patient_table: Dict, 
        table_analysis: Dict, 
        query_type: str,
        patient_id: str,
        db_rules: Dict,
        limit: int
    ) -> Dict[str, Any]:
        """Build the core query structure based on query type and available tables."""
        
        # Quote patient ID for safety
        quoted_patient_id = db_rules['string_quote'] + patient_id.replace("'", "''") + db_rules['string_quote']
        
        # Start with patient table
        patient_table_quoted = self._quote_identifier(patient_table['name'], db_rules)
        patient_alias = 'p'
        
        query_structure = {
            'select_fields': [],
            'from_clause': f"{patient_table_quoted} {patient_alias}",
            'join_clauses': [],
            'where_clause': '',
            'limit_clause': ''
        }
        
        # Add patient table fields (use smart column selection with patient-specific logic)
        if 'patient' in patient_table['name'].lower():
            # For patient tables, ensure we include essential patient info
            patient_columns = self._select_patient_columns(patient_table, query_type)
        else:
            patient_columns = self._select_important_columns(patient_table, query_type)
        
        for col_name in patient_columns:
            col_quoted = self._quote_identifier(col_name, db_rules)
            query_structure['select_fields'].append(f"{patient_alias}.{col_quoted}")
        
        # Build WHERE clause for patient ID
        patient_id_col = self._find_patient_id_column(patient_table)
        if patient_id_col:
            patient_id_quoted = self._quote_identifier(patient_id_col, db_rules)
            query_structure['where_clause'] = f"{patient_alias}.{patient_id_quoted} = {quoted_patient_id}"
        
        # Add related tables based on query type
        related_tables = self._select_related_tables(table_analysis, query_type)
        alias_counter = 1
        
        for related_table in related_tables:
            alias = f"t{alias_counter}"
            related_table_quoted = self._quote_identifier(related_table['name'], db_rules)
            
            # Find join condition
            join_condition = self._find_join_condition(patient_table, related_table, patient_alias, alias, db_rules)
            if join_condition:
                query_structure['join_clauses'].append(
                    f"LEFT JOIN {related_table_quoted} {alias} ON {join_condition}"
                )
                
                # Add selected fields from related table
                important_cols = self._select_important_columns(related_table, query_type)
                for col in important_cols:
                    col_quoted = self._quote_identifier(col, db_rules)
                    query_structure['select_fields'].append(f"{alias}.{col_quoted}")
            
            alias_counter += 1
        
        # Add limit clause
        if limit and limit > 0:
            if db_rules['limit_syntax'] == 'TOP {limit}':
                # SQL Server uses TOP in SELECT clause
                query_structure['top_clause'] = f"TOP {limit}"
            elif db_rules['limit_syntax'] == 'ROWNUM <= {limit}':
                # Oracle uses ROWNUM in WHERE clause
                where_addition = f"ROWNUM <= {limit}"
                if query_structure['where_clause']:
                    query_structure['where_clause'] += f" AND {where_addition}"
                else:
                    query_structure['where_clause'] = where_addition
            else:
                # PostgreSQL, MySQL, Snowflake use LIMIT clause
                query_structure['limit_clause'] = f"LIMIT {limit}"
        
        return query_structure
    
    def _select_related_tables(self, table_analysis: Dict, query_type: str) -> List[Dict]:
        """Select which related tables to include based on query type."""
        related_tables = []
        
        if query_type == "comprehensive":
            # Include all relevant tables
            related_tables.extend(table_analysis['clinical_tables'][:5])  # Limit to prevent huge queries
            related_tables.extend(table_analysis['billing_tables'][:3])
            related_tables.extend(table_analysis['administrative_tables'][:2])
        elif query_type == "clinical":
            related_tables.extend(table_analysis['clinical_tables'][:8])
        elif query_type == "billing":
            related_tables.extend(table_analysis['billing_tables'][:5])
            related_tables.extend(table_analysis['administrative_tables'][:2])
        elif query_type == "basic":
            related_tables.extend(table_analysis['clinical_tables'][:2])
        
        # Filter tables that have patient_id columns or can be joined
        return [t for t in related_tables if t['patient_id_columns'] or t['key_columns']]
    
    def _find_join_condition(
        self, 
        patient_table: Dict, 
        related_table: Dict, 
        patient_alias: str, 
        related_alias: str, 
        db_rules: Dict
    ) -> Optional[str]:
        """Find appropriate join condition between patient table and related table."""
        
        # Look for patient_id columns in related table
        for patient_id_col in related_table['patient_id_columns']:
            patient_id_col_quoted = self._quote_identifier(patient_id_col, db_rules)
            
            # Find corresponding column in patient table
            patient_key_col = self._find_patient_id_column(patient_table)
            if patient_key_col:
                patient_key_quoted = self._quote_identifier(patient_key_col, db_rules)
                return f"{patient_alias}.{patient_key_quoted} = {related_alias}.{patient_id_col_quoted}"
        
        # Fallback: look for ID column matches
        patient_id_col = self._find_patient_id_column(patient_table)
        if patient_id_col:
            patient_id_quoted = self._quote_identifier(patient_id_col, db_rules)
            
            # Try common patterns
            common_patterns = ['patient_id', 'patientid', 'pid', 'id']
            for pattern in common_patterns:
                for col in related_table['columns']:
                    if pattern in col['name'].lower():
                        col_quoted = self._quote_identifier(col['name'], db_rules)
                        return f"{patient_alias}.{patient_id_quoted} = {related_alias}.{col_quoted}"
        
        return None
    
    def _find_patient_id_column(self, table: Dict) -> Optional[str]:
        """Find the patient ID column in a table."""
        # Direct patient ID columns
        if table['patient_id_columns']:
            return table['patient_id_columns'][0]
        
        # Look for ID-like columns
        for col in table['columns']:
            col_name_lower = col['name'].lower()
            if col_name_lower in ['id', 'patient_id', 'patientid', 'pid']:
                return col['name']
        
        # Fallback to first key column
        if table['key_columns']:
            return table['key_columns'][0]
        
        return None
    
    def _select_important_columns(self, table: Dict, query_type: str) -> List[str]:
        """Select important columns from a table based on query type."""
        columns = table['columns']
        important_columns = []
        
        # Always include ID columns (primary keys and foreign keys)
        for col in columns:
            col_name_lower = col['name'].lower()
            if ('id' in col_name_lower or 
                col.get('primary_key', False) or 
                col.get('foreign_key', False)):
                important_columns.append(col['name'])
        
        # Include more comprehensive columns based on query type
        if query_type == "comprehensive":
            # For comprehensive queries, include most columns except system/audit columns
            excluded_keywords = ['created_at', 'updated_at', 'deleted_at', 'created_by', 'updated_by', 
                                'deleted_by', 'version', 'revision', 'hash', 'checksum', 'metadata']
            for col in columns:
                col_name_lower = col['name'].lower()
                if (col['name'] not in important_columns and 
                    not any(excluded in col_name_lower for excluded in excluded_keywords)):
                    important_columns.append(col['name'])
        
        elif query_type == "clinical":
            # Clinical-focused columns
            clinical_keywords = ['diagnosis', 'condition', 'medication', 'dose', 'dosage', 'result', 
                               'value', 'status', 'date', 'time', 'code', 'description', 'name', 
                               'type', 'category', 'severity', 'onset', 'procedure', 'treatment',
                               'lab', 'test', 'vital', 'observation', 'encounter', 'visit', 
                               'allergy', 'symptom', 'note', 'comment']
            for col in columns:
                col_name_lower = col['name'].lower()
                if (any(keyword in col_name_lower for keyword in clinical_keywords) and
                    col['name'] not in important_columns):
                    important_columns.append(col['name'])
        
        elif query_type == "billing":
            # Billing-focused columns
            billing_keywords = ['amount', 'cost', 'price', 'charge', 'payment', 'insurance', 
                              'claim', 'bill', 'invoice', 'fee', 'balance', 'total', 'subtotal',
                              'tax', 'discount', 'copay', 'deductible', 'coverage', 'policy',
                              'provider', 'payer', 'plan', 'group', 'member', 'account']
            for col in columns:
                col_name_lower = col['name'].lower()
                if (any(keyword in col_name_lower for keyword in billing_keywords) and
                    col['name'] not in important_columns):
                    important_columns.append(col['name'])
        
        elif query_type == "basic":
            # Basic patient information
            basic_keywords = ['name', 'first', 'last', 'email', 'phone', 'address', 'birth', 
                            'age', 'gender', 'sex', 'race', 'ethnicity', 'ssn', 'mrn',
                            'contact', 'emergency', 'language', 'marital', 'status']
            for col in columns:
                col_name_lower = col['name'].lower()
                if (any(keyword in col_name_lower for keyword in basic_keywords) and
                    col['name'] not in important_columns):
                    important_columns.append(col['name'])
        
        # If still no columns (other than IDs), include some basic columns
        if len(important_columns) <= 2:  # Only IDs found
            for col in columns:
                col_name_lower = col['name'].lower()
                # Include common informative columns
                if (col['name'] not in important_columns and
                    any(keyword in col_name_lower for keyword in 
                        ['name', 'title', 'description', 'code', 'type', 'status', 'date', 'time'])):
                    important_columns.append(col['name'])
                    if len(important_columns) >= 8:  # Reasonable limit
                        break
        
        # Increase the limit for more comprehensive queries but keep it reasonable
        max_columns = 20 if query_type == "comprehensive" else 15
        return important_columns[:max_columns]
    
    def _select_patient_columns(self, patient_table: Dict, query_type: str) -> List[str]:
        """Select columns specifically for patient tables with healthcare focus."""
        columns = patient_table['columns']
        selected_columns = []
        
        # Priority 1: Essential patient identifiers
        essential_patterns = ['id', 'mrn', 'patient_id', 'medical_record_number']
        for col in columns:
            col_name_lower = col['name'].lower()
            if (any(pattern in col_name_lower for pattern in essential_patterns) or
                col.get('primary_key', False)):
                selected_columns.append(col['name'])
        
        # Priority 2: Basic demographic info (always include for patients)
        demographic_patterns = ['first_name', 'last_name', 'name', 'birth_date', 'dob', 
                               'date_of_birth', 'gender', 'sex', 'email', 'phone', 'ssn']
        for col in columns:
            col_name_lower = col['name'].lower()
            if (any(pattern in col_name_lower for pattern in demographic_patterns) and
                col['name'] not in selected_columns):
                selected_columns.append(col['name'])
        
        # Priority 3: Query type specific additions
        if query_type == "comprehensive":
            # Include most columns for comprehensive view
            comprehensive_patterns = ['address', 'city', 'state', 'zip', 'country', 'race', 
                                    'ethnicity', 'language', 'marital_status', 'occupation',
                                    'emergency_contact', 'insurance', 'provider', 'status',
                                    'active', 'deceased', 'height', 'weight']
            for col in columns:
                col_name_lower = col['name'].lower()
                if (any(pattern in col_name_lower for pattern in comprehensive_patterns) and
                    col['name'] not in selected_columns):
                    selected_columns.append(col['name'])
        
        elif query_type == "basic":
            # Keep it minimal - just what we already have
            pass
        
        elif query_type == "clinical":
            # Add clinically relevant patient info
            clinical_patterns = ['allergy', 'condition', 'medication', 'provider', 'status', 'active']
            for col in columns:
                col_name_lower = col['name'].lower()
                if (any(pattern in col_name_lower for pattern in clinical_patterns) and
                    col['name'] not in selected_columns):
                    selected_columns.append(col['name'])
        
        elif query_type == "billing":
            # Add billing-relevant patient info
            billing_patterns = ['insurance', 'policy', 'group', 'plan', 'member', 'account', 
                              'billing_address', 'guarantor', 'employer']
            for col in columns:
                col_name_lower = col['name'].lower()
                if (any(pattern in col_name_lower for pattern in billing_patterns) and
                    col['name'] not in selected_columns):
                    selected_columns.append(col['name'])
        
        # If we still don't have many columns, add some reasonable defaults
        if len(selected_columns) < 5:
            default_patterns = ['title', 'suffix', 'middle_name', 'nick_name', 'preferred_name',
                              'home_phone', 'work_phone', 'mobile_phone', 'created_date', 'registration_date']
            for col in columns:
                col_name_lower = col['name'].lower()
                if (any(pattern in col_name_lower for pattern in default_patterns) and
                    col['name'] not in selected_columns and
                    len(selected_columns) < 15):
                    selected_columns.append(col['name'])
        
        return selected_columns
    
    def _quote_identifier(self, identifier: str, db_rules: Dict) -> str:
        """Quote an identifier if it's a reserved keyword."""
        if identifier.lower() in db_rules['keywords']:
            quote_char = db_rules['quote_char']
            quote_end = db_rules.get('quote_char_end', quote_char)
            return f"{quote_char}{identifier}{quote_end}"
        return identifier
    
    def _construct_final_query(self, query_parts: Dict, db_type: str, db_rules: Dict) -> str:
        """Construct the final SQL query from parts."""
        # Build SELECT clause
        select_fields = ", ".join(query_parts['select_fields'])
        
        # Handle TOP clause for SQL Server
        top_clause = query_parts.get('top_clause', '')
        if top_clause:
            select_clause = f"SELECT {top_clause} {select_fields}"
        else:
            select_clause = f"SELECT {select_fields}"
        
        # Build query
        query_parts_list = [select_clause]
        query_parts_list.append(f"FROM {query_parts['from_clause']}")
        
        if query_parts['join_clauses']:
            query_parts_list.extend(query_parts['join_clauses'])
        
        if query_parts['where_clause']:
            query_parts_list.append(f"WHERE {query_parts['where_clause']}")
        
        if query_parts.get('limit_clause'):
            query_parts_list.append(query_parts['limit_clause'])
        
        # Join with proper spacing
        final_query = " ".join(query_parts_list)
        
        # Clean up the query
        final_query = re.sub(r'\s+', ' ', final_query).strip()
        
        return final_query
    
    def _get_timestamp(self) -> str:
        """Get current timestamp."""
        from datetime import datetime
        return datetime.now().isoformat()