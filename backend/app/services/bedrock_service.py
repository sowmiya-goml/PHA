"""Bedrock service for static connection management and healthcare query generation."""

import os
import json
import boto3
from botocore.exceptions import ClientError
from datetime import datetime
from typing import Dict, Any, Optional, Union
from bson import ObjectId

from app.core.config import settings
from app.models.connection import DatabaseConnection
from app.schemas.connection import DatabaseConnectionResponse


class BedrockService:
    """Service to manage static Bedrock connection and generate healthcare queries."""
    
    BEDROCK_CONNECTION_ID = "bedrock_static_connection"
    
    def __init__(self, db_manager):
        self.db_manager = db_manager
        self._ensure_bedrock_connection()
    
    def _ensure_bedrock_connection(self):
        """Ensure static Bedrock connection exists in database."""
        collection = self.db_manager.get_connections_collection()
        
        # Check if Bedrock connection already exists
        existing = collection.find_one({"connection_name": "Static Bedrock Connection"})
        if existing:
            return
        
        # Create static Bedrock connection
        bedrock_connection = DatabaseConnection(
            connection_name="Static Bedrock Connection",
            database_type="bedrock",
            connection_string=f"bedrock://{os.getenv('AWS_DEFAULT_REGION', 'us-east-1')}",
            additional_notes=f"Bedrock AI service - Model: {os.getenv('BEDROCK_MODEL_ID', 'anthropic.claude-3.5-sonnet-20240620-v1:0')}"
        )
        
        # Insert with custom ID for easy reference
        connection_doc = bedrock_connection.to_dict()
        connection_doc["_id"] = self.BEDROCK_CONNECTION_ID
        # Add Bedrock-specific fields to the document
        connection_doc["aws_region"] = os.getenv('AWS_DEFAULT_REGION', 'us-east-1')
        connection_doc["model_id"] = os.getenv('BEDROCK_MODEL_ID', 'anthropic.claude-3.5-sonnet-20240620-v1:0')
        
        try:
            collection.insert_one(connection_doc)
            print("✅ Static Bedrock connection created successfully")
        except Exception as e:
            print(f"⚠️ Failed to create Bedrock connection: {e}")
    
    def get_bedrock_connection(self) -> Dict[str, Any]:
        """Get the static Bedrock connection."""
        collection = self.db_manager.get_connections_collection()
        return collection.find_one({"_id": self.BEDROCK_CONNECTION_ID})
    
    def get_bedrock_connection_response(self) -> DatabaseConnectionResponse:
        """Get Bedrock connection as response object."""
        connection_doc = self.get_bedrock_connection()
        if not connection_doc:
            raise RuntimeError("Bedrock connection not found")
        
        connection = DatabaseConnection.from_dict(connection_doc)
        return DatabaseConnectionResponse(
            id=str(connection._id),
            connection_name=connection.connection_name,
            database_type=connection.database_type,
            connection_string=connection.connection_string,
            host=connection.host,
            port=connection.port,
            database_name=connection.database_name,
            username=connection.username,
            password=connection.password,
            additional_notes=connection.additional_notes,
            created_at=connection.created_at,
            updated_at=connection.updated_at
        )

    def generate_mongodb_query(
        self, 
        schema: Union[str, Dict], 
        patient_id: str,
        query_type: str = "comprehensive"
    ) -> Dict[str, Any]:
        """
        Generate healthcare-specific MongoDB queries using Claude 3.5 Sonnet.
        
        Args:
            schema: Database schema (can be JSON string or dict)
            patient_id: Patient ID to query for
            query_type: Type of query ('comprehensive', 'basic', 'billing', 'clinical')
            
        Returns:
            Dict with generated MongoDB query and metadata
        """
        try:
            # Parse schema if it's a JSON string
            if isinstance(schema, str):
                try:
                    schema_dict = json.loads(schema)
                except json.JSONDecodeError:
                    # If not JSON, treat as plain text schema
                    schema_dict = {"raw_schema": schema}
            else:
                schema_dict = schema
            
            # Initialize Bedrock client
            bedrock_client = self._get_bedrock_client()
            
            # Generate MongoDB-specific prompt
            prompt = self._create_mongodb_prompt(schema_dict, patient_id, query_type)
            
            # Try different model IDs
            model_ids = [
                "arn:aws:bedrock:ap-south-1:422228628797:inference-profile/apac.anthropic.claude-3-5-sonnet-20240620-v1:0",
                "anthropic.claude-3-5-sonnet-20240620-v1:0",
            ]
            
            for model_id in model_ids:
                try:
                    print(f"🔄 Trying model: {model_id}")
                    
                    response = bedrock_client.invoke_model(
                        modelId=model_id,
                        body=json.dumps({
                            "anthropic_version": "bedrock-2023-05-31",
                            "max_tokens": 4000,
                            "messages": [
                                {
                                    "role": "user",
                                    "content": prompt
                                }
                            ],
                            "temperature": 0.1,
                            "top_p": 0.9,
                            "stop_sequences": []
                        }),
                        contentType="application/json"
                    )
                    
                    response_body = json.loads(response['body'].read())
                    generated_query = response_body['content'][0]['text']
                    
                    # Clean the generated query for MongoDB
                    cleaned_query = self._clean_mongodb_query(generated_query)
                    
                    return {
                        "status": "success",
                        "query": cleaned_query,
                        "query_type": "mongodb_" + query_type,
                        "model_used": model_id,
                        "patient_id": patient_id,
                        "generated_at": datetime.now().isoformat(),
                        "collections_count": self._count_collections(schema_dict),
                        "prompt_length": len(prompt)
                    }
                    
                except ClientError as e:
                    error_code = e.response['Error']['Code']
                    print(f"❌ Model {model_id} failed: {error_code}")
                    
                    if model_id == model_ids[-1]:  # Last model in list
                        return {
                            "status": "failed",
                            "error": f"All models failed. Last error: {str(e)}",
                            "error_code": error_code,
                            "query_type": "mongodb_" + query_type,
                            "patient_id": patient_id
                        }
                    continue  # Try next model
                    
        except Exception as e:
            return {
                "status": "failed",
                "error": f"MongoDB query generation failed: {str(e)}",
                "query_type": "mongodb_" + query_type,
                "patient_id": patient_id
            }

    def generate_healthcare_query(
        self, 
        schema: Union[str, Dict], 
        patient_id: str,
        query_type: str = "comprehensive"
    ) -> Dict[str, Any]:
        """
        Generate healthcare-specific SQL queries using Claude 3.5 Sonnet.
        
        Args:
            schema: Database schema (can be JSON string or dict)
            patient_id: Patient ID to query for
            query_type: Type of query ('comprehensive', 'basic', 'billing', 'clinical')
            
        Returns:
            Dict with generated query and metadata
        """
        try:
            # Parse schema if it's a JSON string
            if isinstance(schema, str):
                try:
                    schema_dict = json.loads(schema)
                except json.JSONDecodeError:
                    # If not JSON, treat as plain text schema
                    schema_dict = {"raw_schema": schema}
            else:
                schema_dict = schema
            
            # Initialize Bedrock client
            bedrock_client = self._get_bedrock_client()
            
            # Generate query-type specific prompt
            prompt = self._create_healthcare_prompt(schema_dict, patient_id, query_type)
            
            # Try different model IDs
            model_ids = [
                "arn:aws:bedrock:ap-south-1:422228628797:inference-profile/apac.anthropic.claude-3-5-sonnet-20240620-v1:0",
                "anthropic.claude-3-5-sonnet-20240620-v1:0",
            ]
            
            response = None
            model_used = None
            
            for model_id in model_ids:
                try:
                    response = bedrock_client.invoke_model(
                        modelId=model_id,
                        contentType="application/json",
                        accept="application/json",
                        body=json.dumps({
                            "anthropic_version": "bedrock-2023-05-31",
                            "max_tokens": 2000,  # Increased for complex healthcare queries
                            "temperature": 0.1,
                            "messages": [
                                {
                                    "role": "user",
                                    "content": prompt
                                }
                            ]
                        })
                    )
                    model_used = model_id
                    break
                except ClientError as e:
                    print(f"Failed to use model {model_id}: {str(e)}")
                    continue
                except Exception as e:
                    print(f"Unexpected error with model {model_id}: {str(e)}")
                    continue
            
            if not response:
                raise Exception("No compatible Claude model available")
            
            # Parse response
            result = json.loads(response['body'].read())
            generated_query = result['content'][0]['text'].strip()
            
            # Clean up the generated query
            generated_query = self._clean_query(generated_query)
            
            return {
                "generated_query": generated_query,
                "patient_id": patient_id,
                "query_type": query_type,
                "model_used": model_used,
                "schema_tables_count": self._count_tables(schema_dict),
                "status": "success",
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "error": str(e),
                "patient_id": patient_id,
                "query_type": query_type,
                "status": "failed",
                "timestamp": datetime.now().isoformat()
            }
    
    def _get_bedrock_client(self):
        """Initialize and return Bedrock client."""
        aws_access_key = os.getenv("AWS_ACCESS_KEY_ID")
        aws_secret_key = os.getenv("AWS_SECRET_ACCESS_KEY") 
        aws_region = os.getenv("AWS_DEFAULT_REGION", "ap-south-1")
        
        if not aws_access_key or not aws_secret_key:
            raise Exception("AWS credentials not configured properly")
        
        return boto3.client(
            "bedrock-runtime",
            region_name=aws_region,
            aws_access_key_id=aws_access_key,
            aws_secret_access_key=aws_secret_key
        )
    
    def _create_healthcare_prompt(
        self, 
        schema_dict: Dict, 
        patient_id: str, 
        query_type: str
    ) -> str:
        """Create healthcare-specific prompts based on query type."""
        
        # Escape patient ID for SQL safety
        escaped_patient_id = patient_id.replace("'", "''")
        
        # Extract schema information
        schema_info = self._extract_schema_info(schema_dict)
        
        base_requirements = """
🚨 CRITICAL SQL OUTPUT FORMAT:
- MANDATORY: Always output the SQL query as raw SQL, not as a string.
- ABSOLUTELY FORBIDDEN: Do not include backslashes (\) to escape quotes anywhere in the query.
- RESERVED KEYWORDS: If a reserved keyword is used as a table or column name, wrap it with the correct identifier quoting for the target database (e.g., "order" for PostgreSQL, `order` for MySQL, [order] for SQL Server).
- FINAL REQUIREMENT: The final output must be a syntactically valid query that can run directly in the database client.

🔥 EXAMPLES OF FORBIDDEN PATTERNS (DO NOT GENERATE THESE):
❌ WRONG: LEFT JOIN \"order\" o ON...        (contains backslash)
❌ WRONG: SELECT p.\"patient_id\"...          (contains backslash)
❌ WRONG: FROM \"patients\" p...               (contains backslash)

✅ CORRECT PATTERNS (GENERATE THESE INSTEAD):
✅ RIGHT: LEFT JOIN "order" o ON...          (clean double quotes)
✅ RIGHT: SELECT p."patient_id"...           (clean double quotes)
✅ RIGHT: FROM "patients" p...               (clean double quotes)

🚨 CRITICAL JOIN REQUIREMENTS:
- BEFORE creating any JOIN: Check the actual column names in BOTH tables from the schema
- NEVER assume foreign key column names exist without verifying them in the schema
- Map child table *_id columns to parent table primary keys BY EXACT NAME MATCH
- If a foreign key column doesn't exist in the schema, DO NOT create that JOIN
- If multiple foreign keys point to the same parent table, create separate JOINs with different table aliases
- Only use column names that actually exist in the provided schema

🚨 JOIN VALIDATION PROCESS:
1. Identify the primary table (usually the patient table)
2. For each potential child table, check if it has a column that matches the primary table's primary key
3. Only create JOIN if BOTH columns exist in the schema
4. Use the EXACT column names from the schema (not assumed names)

Requirements:
- CRITICAL: Use ONLY the exact table and column names provided in the schema above - verify each column exists before using it
- Before creating any JOIN, verify that BOTH the foreign key and primary key columns exist in their respective tables
- Return a complete, optimized SQL query that retrieves patient information
- Use proper PostgreSQL syntax with correct keywords
- Do NOT use line breaks, newline characters, backslashes, or forward slashes in the query
- Return the query as a single line with spaces between clauses
- Only return the SQL query, nothing else - no explanations or markdown
- Use safe, descriptive table aliases based on actual table names
- Always qualify columns with table aliases when joining multiple tables
- Handle UUID patient IDs properly as string values in single quotes
- Ensure efficient query performance with proper indexing considerations
- VERIFY: All table and column names in your query must exist in the schema provided above
- IMPORTANT: For reserved keywords as table names (like "order", "user", "group"), wrap them in double quotes like "order", "user", "group"
- IMPORTANT: Do not include any backslash or forward slash characters in your response
- IMPORTANT: Use double quotes around table names that are SQL reserved words
"""
        
        if query_type == "comprehensive":
            prompt = f"""
You are a healthcare database expert. Generate a comprehensive SQL query to extract ALL medical information for patient ID '{escaped_patient_id}'.

{schema_info}

Patient ID: {escaped_patient_id}

Generate a query that includes ALL relevant patient data from the database tables listed above.
Look for tables that likely contain:
- Patient demographics (look for tables with patient information)
- Medical encounters/visits (look for encounter/visit tables)
- Diagnoses and medical conditions (look for diagnosis/condition tables)
- Procedures and treatments (look for procedure tables)
- Medications (look for medication/drug tables)
- Lab results and vital signs (look for laboratory/vital tables)
- Billing information (look for billing/financial tables)

Use LEFT JOINs to ensure all patient data is retrieved even if some tables have no matching records.
CRITICAL: Use ONLY the exact table names from the schema provided above.

SPECIAL NOTE: If any table name is a SQL reserved word (like order, user, group, table, etc.), wrap it in double quotes like "order" not 'order' and never use backslashes or forward slashes.

{base_requirements}

Generate the SQL query now using the actual table names from the schema.
"""
        
        elif query_type == "clinical":
            prompt = f"""
You are a healthcare database expert. Generate a clinical-focused SQL query for patient ID '{escaped_patient_id}'.

{schema_info}

Patient ID: {escaped_patient_id}

Focus on clinical data using ONLY the table names from the schema above:
- Patient demographics (look for patient-related tables in the schema)
- Diagnoses and medical conditions (look for diagnosis/condition tables)
- Procedures and treatments (look for procedure tables)
- Medications and prescriptions (look for medication tables)
- Lab results and vital signs (look for laboratory/vital tables)
- Clinical assessments (look for clinical/assessment tables)

CRITICAL: Use ONLY the exact table names from the schema provided above.
SPECIAL NOTE: If any table name is a SQL reserved word (like order, user, group, table, etc.), wrap it in double quotes like "order" not 'order' and never use backslashes or forward slashes.

{base_requirements}
"""
        
        elif query_type == "billing":
            prompt = f"""
You are a healthcare database expert. Generate a billing-focused SQL query for patient ID '{escaped_patient_id}'.

{schema_info}

Patient ID: {escaped_patient_id}

Focus on financial/billing data using ONLY the table names from the schema above:
- Patient demographics (look for patient-related tables in the schema)
- Bills and charges (look for billing/charge tables)
- Insurance claims and payments (look for insurance/claim tables)
- Payment history (look for payment/financial tables)
- Financial transactions (look for transaction tables)

CRITICAL: Use ONLY the exact table names from the schema provided above.
SPECIAL NOTE: If any table name is a SQL reserved word (like order, user, group, table, etc.), wrap it in double quotes like "order" not 'order' and never use backslashes or forward slashes.

{base_requirements}
"""
        
        else:  # basic
            prompt = f"""
You are a healthcare database expert. Generate a basic SQL query for patient ID '{escaped_patient_id}'.

{schema_info}

Patient ID: {escaped_patient_id}

Focus on essential patient information using ONLY the table names from the schema above:
- Basic patient demographics and identifiers
- Contact information
- Essential medical record information

CRITICAL: Use ONLY the exact table names from the schema provided above.
SPECIAL NOTE: If any table name is a SQL reserved word (like order, user, group, table, etc.), wrap it in double quotes like "order" not 'order' and never use backslashes or forward slashes.

{base_requirements}
"""
        
        return prompt
    
    def _create_mongodb_prompt(
        self, 
        schema_dict: Dict, 
        patient_id: str, 
        query_type: str
    ) -> str:
        """Create MongoDB-specific prompts based on query type."""
        
        # Escape patient ID for MongoDB safety
        escaped_patient_id = patient_id.replace("'", "\\'")
        
        # Extract schema information for MongoDB
        schema_info = self._extract_mongodb_schema_info(schema_dict)
        
        base_requirements = """
Requirements:
- CRITICAL: Use ONLY the exact collection names provided in the schema above
- Return a valid MongoDB query (aggregation pipeline or find query)
- Use proper MongoDB syntax and operators
- Return the query as valid JSON format
- Only return the MongoDB query, nothing else - no explanations or markdown
- Handle patient IDs properly in MongoDB queries
- Use efficient MongoDB query patterns with proper indexing considerations
- VERIFY: All collection names in your query must exist in the schema provided above
- For ObjectId fields, use ObjectId("...") syntax if needed
- For string patient IDs, use regular string matching
"""
        
        if query_type == "comprehensive":
            prompt = f"""
You are a MongoDB expert working with healthcare data. Generate a comprehensive MongoDB query to extract ALL medical information for patient ID '{escaped_patient_id}'.

{schema_info}

Patient ID: {escaped_patient_id}

Generate a MongoDB aggregation pipeline that includes ALL relevant patient data from the collections listed above.
Look for collections that likely contain:
- Patient demographics (look for collections with patient information)
- Medical encounters/visits (look for encounter/visit collections)
- Diagnoses and medical conditions (look for diagnosis/condition collections)
- Procedures and treatments (look for procedure collections)
- Medications (look for medication/drug collections)
- Lab results and vital signs (look for laboratory/vital collections)
- Billing information (look for billing/financial collections)

Use $lookup stages to join related collections and ensure all patient data is retrieved.
CRITICAL: Use ONLY the exact collection names from the schema provided above.

{base_requirements}

Generate the MongoDB aggregation pipeline now using the actual collection names from the schema.
"""
        
        elif query_type == "clinical":
            prompt = f"""
You are a MongoDB expert working with healthcare data. Generate a clinical-focused MongoDB query for patient ID '{escaped_patient_id}'.

{schema_info}

Patient ID: {escaped_patient_id}

Focus on clinical data using ONLY the collection names from the schema above:
- Patient demographics (look for patient-related collections in the schema)
- Diagnoses and medical conditions (look for diagnosis/condition collections)
- Procedures and treatments (look for procedure collections)
- Medications and prescriptions (look for medication collections)
- Lab results and vital signs (look for laboratory/vital collections)
- Clinical assessments (look for clinical/assessment collections)

CRITICAL: Use ONLY the exact collection names from the schema provided above.

{base_requirements}
"""
        
        elif query_type == "billing":
            prompt = f"""
You are a MongoDB expert working with healthcare data. Generate a billing-focused MongoDB query for patient ID '{escaped_patient_id}'.

{schema_info}

Patient ID: {escaped_patient_id}

Focus on financial/billing data using ONLY the collection names from the schema above:
- Patient demographics (look for patient-related collections in the schema)
- Bills and charges (look for billing/charge collections)
- Insurance claims and payments (look for insurance/claim collections)
- Payment history (look for payment/financial collections)
- Financial transactions (look for transaction collections)

CRITICAL: Use ONLY the exact collection names from the schema provided above.

{base_requirements}
"""
        
        else:  # basic
            prompt = f"""
You are a MongoDB expert working with healthcare data. Generate a basic MongoDB query for patient ID '{escaped_patient_id}'.

{schema_info}

Patient ID: {escaped_patient_id}

Focus on essential patient information using ONLY the collection names from the schema above:
- Basic patient demographics and identifiers
- Contact information
- Essential medical record information

CRITICAL: Use ONLY the exact collection names from the schema provided above.

{base_requirements}
"""
        
        return prompt
    
    def _extract_schema_info(self, schema_dict: Dict) -> str:
        """Extract and format schema information for the prompt with detailed column information."""
        if "unified_schema" in schema_dict:
            # Handle unified schema format
            unified = schema_dict["unified_schema"]
            tables_info = []
            foreign_key_info = []
            
            if "tables" in unified:
                # Use ALL actual tables from the database
                for table in unified["tables"]:
                    table_name = table.get("name", "")
                    columns = table.get("columns", [])
                    
                    # Get ALL columns with their types and constraints
                    column_details = []
                    primary_keys = []
                    foreign_key_candidates = []
                    
                    for col in columns:
                        col_name = col.get('name')
                        col_type = col.get('type')
                        col_info = f"{col_name} ({col_type})"
                        
                        if col.get('primary_key'):
                            col_info += " PK"
                            primary_keys.append(col_name)
                        
                        if col.get('nullable') == False:
                            col_info += " NOT NULL"
                        
                        # Identify potential foreign keys by name pattern
                        if col_name.endswith('_id') and col_name != 'patient_id':
                            foreign_key_candidates.append(col_name)
                        
                        column_details.append(col_info)
                    
                    # Format table information
                    tables_info.append(f"""
TABLE: {table_name}
  Columns: {', '.join(column_details)}
  Primary Key(s): {', '.join(primary_keys) if primary_keys else 'None identified'}
  Potential Foreign Keys: {', '.join(foreign_key_candidates) if foreign_key_candidates else 'None identified'}""")
            
            # Get database type for proper quoting rules
            db_type = unified.get('database_info', {}).get('type', 'postgresql').lower()
            quoting_rules = self._get_quoting_rules(db_type)
            
            schema_info = f"""
Database Type: {db_type}
QUOTING RULES FOR THIS DATABASE:
{quoting_rules}

Database: {unified.get('database_info', {}).get('name', 'unknown')}
Total Tables: {len(unified.get('tables', []))}

🔍 DETAILED TABLE SCHEMA (verify column names before creating JOINs):
{chr(10).join(tables_info)}

🚨 IMPORTANT JOIN VALIDATION RULES:
- Before creating any JOIN between tables, verify that BOTH the foreign key column and primary key column exist in the schema above
- Common patterns: If table A has 'patient_id', it can JOIN to a 'patient' table's 'patient_id' primary key
- If table B has 'encounter_id', it can JOIN to an 'encounter' table's 'encounter_id' primary key  
- DO NOT assume column names - use only the exact column names listed above
- If a foreign key relationship cannot be verified from the schema above, skip that JOIN

🔗 JOIN CONSTRUCTION RULES:
- Order JOINs logically: define each table alias before using it in subsequent JOIN conditions
- Use correct foreign key relationships (primary key to foreign key matches based on actual column names)
- Each JOIN must use the correct relationship columns from the schema provided above
- Use LEFT JOIN to ensure all patient data is retrieved even if related tables have no matching records
"""
        else:
            # Handle raw schema format
            schema_info = f"""
Database Schema:
{str(schema_dict)[:4000]}  # Show more schema context
"""
        
        return schema_info

    def _get_quoting_rules(self, db_type: str) -> str:
        """Get database-specific quoting rules."""
        db_type_lower = db_type.lower()
        if 'mysql' in db_type_lower or 'mariadb' in db_type_lower:
            return "MySQL/MariaDB: Use backticks for reserved keywords: `order`, `user`, `table`\nExample: SELECT p.patient_id, o.`order_id` FROM patients p LEFT JOIN `order` o"
        elif 'sql server' in db_type_lower or 'mssql' in db_type_lower:
            return "SQL Server: Use brackets for reserved keywords: [order], [user], [table]\nExample: SELECT p.patient_id, o.[order_id] FROM patients p LEFT JOIN [order] o"
        else:  # PostgreSQL default
            return "PostgreSQL: Use double quotes for reserved keywords: \"order\", \"user\", \"table\"\nExample: SELECT p.patient_id, o.\"order_id\" FROM patients p LEFT JOIN \"order\" o"
    
    def _extract_mongodb_schema_info(self, schema_dict: Dict) -> str:
        """Extract and format MongoDB schema information for the prompt."""
        if "unified_schema" in schema_dict:
            # Handle unified schema format for MongoDB
            unified = schema_dict["unified_schema"]
            collections_info = []
            
            if "tables" in unified:  # MongoDB collections are stored as "tables" in unified schema
                # Use ALL actual collections from the database
                for collection in unified["tables"]:
                    collection_name = collection.get("name", "")
                    fields = collection.get("columns", [])  # MongoDB fields are stored as "columns"
                    
                    # Get key fields
                    key_fields = []
                    for field in fields[:15]:  # Show more fields for better context
                        field_info = f"{field.get('name')} ({field.get('type')})"
                        if field.get('primary_key') or field.get('name') == '_id':
                            field_info += " ID"
                        key_fields.append(field_info)
                    
                    collections_info.append(f"- {collection_name}: {', '.join(key_fields)}")
            
            # Use ONLY actual database collections
            schema_info = f"""
MongoDB Database Schema:
Database: {unified.get('database_info', {}).get('name', 'unknown')}
Total Collections: {len(unified.get('tables', []))}

ACTUAL DATABASE COLLECTIONS (use these exact collection names):
{chr(10).join(collections_info)}

IMPORTANT: Use ONLY the collection names listed above. Do NOT use any other collection names.
"""
        else:
            # Handle raw schema format
            schema_info = f"""
MongoDB Database Schema:
{str(schema_dict)[:3000]}  # Increased limit for more context
"""
        
        return schema_info
    
    def _clean_mongodb_query(self, query: str) -> str:
        """Clean and format the generated MongoDB query."""
        # Remove line breaks and extra spaces while preserving JSON structure
        query = query.strip()
        
        # Remove any markdown code block formatting
        if query.startswith('```json'):
            query = query.replace('```json', '').replace('```', '').strip()
        elif query.startswith('```javascript'):
            query = query.replace('```javascript', '').replace('```', '').strip()
        elif query.startswith('```'):
            query = query.replace('```', '').strip()
        
        # Try to parse and reformat as valid JSON
        try:
            import json
            # If it's valid JSON, pretty format it
            parsed = json.loads(query)
            query = json.dumps(parsed, indent=2)
        except json.JSONDecodeError:
            # If not valid JSON, just clean up whitespace
            import re
            query = re.sub(r'\s+', ' ', query).strip()
        
        return query
    
    def _count_collections(self, schema_dict: Dict) -> int:
        """Count the number of collections in the MongoDB schema."""
        if "unified_schema" in schema_dict:
            return len(schema_dict["unified_schema"].get("tables", []))  # Collections stored as "tables"
        elif "tables" in schema_dict:
            return len(schema_dict["tables"])
        elif "collections" in schema_dict:
            return len(schema_dict["collections"])
        else:
            return 0
    
    def _clean_query(self, query: str) -> str:
        """Ultra-aggressive cleaning to eliminate all escape characters."""
        import re
        
        # NUCLEAR APPROACH: Remove ALL backslashes first
        query = query.replace('\\', '')
        
        # Method 1: Character-by-character filtering to remove any remaining backslashes
        query = ''.join(char for char in query if char != '\\')
        
        # Method 2: Multiple replacement passes (in case some escape sequences remain)
        for _ in range(5):  # Multiple passes to catch nested escapes
            query = query.replace('\\', '')
            query = query.replace('\\"', '"')  # Fix escaped quotes
            query = query.replace("\\'", "'")  # Fix escaped single quotes
            query = query.replace('\\`', '`')   # Fix escaped backticks (MySQL)
            query = query.replace('\\[', '[')   # Fix escaped brackets (SQL Server)
            query = query.replace('\\]', ']')
        
        # Method 3: Regex nuclear cleaning
        query = re.sub(r'\\+', '', query)  # Remove any remaining backslashes
        query = re.sub(r'\\"', '"', query)  # Fix any remaining escaped quotes
        
        # Target the specific \"order\" pattern that keeps appearing
        query = re.sub(r'\\"order\\"', '"order"', query, flags=re.IGNORECASE)
        query = re.sub(r'\\"([a-zA-Z_][a-zA-Z0-9_]*)\\"', r'"\1"', query)  # \"word\" -> "word"
        
        # Standard cleanup
        query = query.replace('\n', ' ').replace('\r', ' ')
        query = re.sub(r'\s+', ' ', query).strip()
        
        # Remove markdown formatting
        if query.startswith('```sql'):
            query = query.replace('```sql', '').replace('```', '').strip()
        elif query.startswith('```'):
            query = query.replace('```', '').strip()
        
        # Final safety net - remove any character that could be a backslash
        query = ''.join(char for char in query if ord(char) != 92)  # ASCII 92 is backslash
        
        return query
    
    def _count_tables(self, schema_dict: Dict) -> int:
        """Count the number of tables in the schema."""
        if "unified_schema" in schema_dict:
            return len(schema_dict["unified_schema"].get("tables", []))
        elif "tables" in schema_dict:
            return len(schema_dict["tables"])
        else:
            return 0
