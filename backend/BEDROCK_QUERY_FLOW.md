# Bedrock Query Generation → Direct DB Query Flow

## 🔄 **Complete Technical Flow**

```
User Request → Schema Lookup → Bedrock Prompt → Generated Query → 
Query Validation → Parameterization → DB Execution → Results → HealthLake
```

---

## 1️⃣ **Step 1: Bedrock Query Generation**

### **Input to Bedrock:**
```python
# app/services/bedrock_service.py
class BedrockService:
    async def generate_query(self, schema: dict, user_request: str, db_type: str) -> dict:
        bedrock_client = boto3.client('bedrock-runtime', region_name='us-east-1')
        
        # Construct the prompt with schema context
        prompt = f"""
        You are a database query expert. Generate a safe, parameterized query based on this schema and request.
        
        Database Type: {db_type}
        Schema: {json.dumps(schema, indent=2)}
        User Request: {user_request}
        
        Rules:
        1. Only SELECT queries (no INSERT, UPDATE, DELETE)
        2. Use parameterized queries with placeholders
        3. Return response in this exact JSON format:
        {{
            "query_type": "sql|mongodb",
            "query": "SELECT * FROM patients WHERE patient_id = $1",
            "parameters": {{"patient_id": "P1234"}},
            "explanation": "This query fetches patient data for ID P1234",
            "estimated_rows": 50,
            "tables_accessed": ["patients", "visits"]
        }}
        
        Generate the query now:
        """
        
        response = bedrock_client.invoke_model(
            modelId="anthropic.claude-3-sonnet-20240229-v1:0",
            body=json.dumps({
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 1000,
                "messages": [{"role": "user", "content": prompt}]
            })
        )
        
        result = json.loads(response['body'].read())
        bedrock_response = json.loads(result['content'][0]['text'])
        
        return bedrock_response
```

### **Example Bedrock Response:**
```json
{
    "query_type": "sql",
    "query": "SELECT p.patient_id, p.first_name, p.last_name, v.visit_date, v.diagnosis_code FROM patients p JOIN visits v ON p.patient_id = v.patient_id WHERE p.patient_id = $1 AND v.visit_date >= $2",
    "parameters": {
        "patient_id": "P1234",
        "start_date": "2024-03-01"
    },
    "explanation": "Fetches patient details and visits for patient P1234 from March 2024 onwards",
    "estimated_rows": 15,
    "tables_accessed": ["patients", "visits"]
}
```

---

## 2️⃣ **Step 2: Query Validation & Security**

```python
# app/utils/query_validator.py
class QueryValidator:
    
    DANGEROUS_KEYWORDS = [
        'DROP', 'DELETE', 'UPDATE', 'INSERT', 'ALTER', 'CREATE', 
        'TRUNCATE', 'EXEC', 'EXECUTE', 'UNION', 'SCRIPT', 'DECLARE'
    ]
    
    @staticmethod
    def validate_sql_query(query: str, schema: dict) -> bool:
        """Validate SQL query for security and schema compliance"""
        
        # 1. Check for dangerous keywords
        query_upper = query.upper()
        for keyword in QueryValidator.DANGEROUS_KEYWORDS:
            if keyword in query_upper:
                raise ValueError(f"Dangerous keyword '{keyword}' not allowed")
        
        # 2. Ensure only SELECT queries
        if not query_upper.strip().startswith('SELECT'):
            raise ValueError("Only SELECT queries are allowed")
        
        # 3. Validate table names against schema
        tables_in_query = QueryValidator._extract_table_names(query)
        schema_tables = schema.get('tables', {}).keys()
        
        for table in tables_in_query:
            if table not in schema_tables:
                raise ValueError(f"Table '{table}' not found in schema")
        
        # 4. Check for SQL injection patterns
        injection_patterns = [r"';", r"--", r"/\*", r"\*/", r"0x", r"char\("]
        for pattern in injection_patterns:
            if re.search(pattern, query, re.IGNORECASE):
                raise ValueError("Potential SQL injection detected")
        
        return True
    
    @staticmethod
    def validate_mongodb_query(query: dict, schema: dict) -> bool:
        """Validate MongoDB query"""
        # Check for dangerous operations
        dangerous_ops = ['$eval', '$where', 'mapReduce', 'drop', 'deleteMany']
        
        def check_dangerous_ops(obj):
            if isinstance(obj, dict):
                for key, value in obj.items():
                    if key in dangerous_ops:
                        raise ValueError(f"Dangerous operation '{key}' not allowed")
                    check_dangerous_ops(value)
            elif isinstance(obj, list):
                for item in obj:
                    check_dangerous_ops(item)
        
        check_dangerous_ops(query)
        return True
    
    @staticmethod
    def _extract_table_names(sql: str) -> list:
        """Extract table names from SQL query"""
        # Simple regex to extract table names (can be enhanced)
        pattern = r'FROM\s+(\w+)|JOIN\s+(\w+)'
        matches = re.findall(pattern, sql, re.IGNORECASE)
        tables = [match[0] or match[1] for match in matches]
        return [t.lower() for t in tables if t]
```

---

## 3️⃣ **Step 3: Database Connection & Query Execution**

```python
# app/services/database_query_service.py
class DatabaseQueryService:
    
    async def execute_query(self, connection_id: str, bedrock_response: dict) -> dict:
        """Execute the validated query against client database"""
        
        # 1. Get connection details
        connection = await self.connection_service.get_connection_by_id(connection_id)
        
        # 2. Validate query
        if connection.database_type == "PostgreSQL":
            QueryValidator.validate_sql_query(bedrock_response['query'], connection.schema)
            return await self._execute_postgres_query(connection, bedrock_response)
        
        elif connection.database_type == "MySQL":
            QueryValidator.validate_sql_query(bedrock_response['query'], connection.schema)
            return await self._execute_mysql_query(connection, bedrock_response)
        
        elif connection.database_type == "MongoDB":
            QueryValidator.validate_mongodb_query(bedrock_response['query'], connection.schema)
            return await self._execute_mongodb_query(connection, bedrock_response)
        
        else:
            raise ValueError(f"Unsupported database type: {connection.database_type}")
    
    async def _execute_postgres_query(self, connection: DatabaseConnection, bedrock_response: dict) -> dict:
        """Execute PostgreSQL query with parameters"""
        
        import asyncpg
        
        # Create secure connection
        conn = await asyncpg.connect(
            host=connection.host,
            port=connection.port,
            user=connection.username,
            password=connection.password,
            database=connection.database_name,
            ssl='require'  # Force SSL
        )
        
        try:
            # Convert parameters to proper format
            query = bedrock_response['query']
            params = bedrock_response['parameters']
            
            # Replace $1, $2 style parameters
            param_values = list(params.values())
            
            # Execute query with timeout
            rows = await asyncio.wait_for(
                conn.fetch(query, *param_values),
                timeout=30.0  # 30 second timeout
            )
            
            # Convert to dict format
            results = [dict(row) for row in rows]
            
            return {
                "success": True,
                "row_count": len(results),
                "data": results,
                "execution_time": time.time() - start_time,
                "query_info": bedrock_response
            }
            
        except asyncio.TimeoutError:
            raise HTTPException(status_code=408, detail="Query execution timeout")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Query execution failed: {str(e)}")
        finally:
            await conn.close()
    
    async def _execute_mysql_query(self, connection: DatabaseConnection, bedrock_response: dict) -> dict:
        """Execute MySQL query with parameters"""
        
        import aiomysql
        
        conn = await aiomysql.connect(
            host=connection.host,
            port=connection.port,
            user=connection.username,
            password=connection.password,
            db=connection.database_name,
            ssl={'ssl_ca': None}  # Configure SSL properly
        )
        
        try:
            cursor = await conn.cursor(aiomysql.DictCursor)
            
            # Convert parameters
            query = bedrock_response['query'].replace('$1', '%s').replace('$2', '%s')  # Convert to MySQL format
            param_values = list(bedrock_response['parameters'].values())
            
            await cursor.execute(query, param_values)
            rows = await cursor.fetchall()
            
            return {
                "success": True,
                "row_count": len(rows),
                "data": rows,
                "execution_time": time.time() - start_time,
                "query_info": bedrock_response
            }
            
        finally:
            await conn.ensure_closed()
    
    async def _execute_mongodb_query(self, connection: DatabaseConnection, bedrock_response: dict) -> dict:
        """Execute MongoDB query"""
        
        from motor.motor_asyncio import AsyncIOMotorClient
        
        # Create connection string
        if connection.username and connection.password:
            uri = f"mongodb://{connection.username}:{connection.password}@{connection.host}:{connection.port}/{connection.database_name}"
        else:
            uri = f"mongodb://{connection.host}:{connection.port}/{connection.database_name}"
        
        client = AsyncIOMotorClient(uri)
        db = client[connection.database_name]
        
        try:
            # Extract collection and query from Bedrock response
            collection_name = bedrock_response['collection']
            query = bedrock_response['query']
            
            collection = db[collection_name]
            
            # Execute query
            cursor = collection.find(query)
            results = await cursor.to_list(length=1000)  # Limit results
            
            # Convert ObjectId to string
            for result in results:
                if '_id' in result:
                    result['_id'] = str(result['_id'])
            
            return {
                "success": True,
                "row_count": len(results),
                "data": results,
                "execution_time": time.time() - start_time,
                "query_info": bedrock_response
            }
            
        finally:
            client.close()
```

---

## 4️⃣ **Step 4: Complete FastAPI Endpoint**

```python
# app/routers/reports.py
@router.post("/connections/{connection_id}/query")
async def execute_ai_query(
    connection_id: str,
    request: QueryRequest,
    db_service: DatabaseQueryService = Depends(get_db_service),
    bedrock_service: BedrockService = Depends(get_bedrock_service)
):
    """
    Main endpoint: Natural language → SQL/NoSQL → Execute → Results
    """
    
    try:
        # 1. Get connection and schema
        connection = await db_service.get_connection_by_id(connection_id)
        schema = connection.schema  # Previously extracted schema
        
        # 2. Generate query with Bedrock
        bedrock_response = await bedrock_service.generate_query(
            schema=schema,
            user_request=request.natural_language_query,
            db_type=connection.database_type
        )
        
        # 3. Execute query against client database
        query_results = await db_service.execute_query(connection_id, bedrock_response)
        
        # 4. Log for compliance
        await audit_logger.log_phi_access(
            user_id=request.user_id,
            connection_id=connection_id,
            query=bedrock_response['query'],
            row_count=query_results['row_count']
        )
        
        return {
            "query_id": str(uuid.uuid4()),
            "generated_query": bedrock_response['query'],
            "explanation": bedrock_response['explanation'],
            "results": query_results['data'],
            "row_count": query_results['row_count'],
            "execution_time": query_results['execution_time']
        }
        
    except Exception as e:
        logger.error(f"Query execution failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
```

---

## 5️⃣ **Step 5: Request/Response Models**

```python
# app/schemas/query.py
class QueryRequest(BaseModel):
    natural_language_query: str = Field(..., min_length=10, max_length=500)
    format: Optional[str] = Field(default="json", regex="^(json|pdf|csv)$")
    limit: Optional[int] = Field(default=100, ge=1, le=1000)
    
    class Config:
        schema_extra = {
            "example": {
                "natural_language_query": "Show me all visits for patient P1234 in the last 6 months",
                "format": "json",
                "limit": 100
            }
        }

class QueryResponse(BaseModel):
    query_id: str
    generated_query: str
    explanation: str
    results: List[Dict[str, Any]]
    row_count: int
    execution_time: float
    
class BedrockQueryResponse(BaseModel):
    query_type: str
    query: str
    parameters: Dict[str, Any]
    explanation: str
    estimated_rows: int
    tables_accessed: List[str]
```

---

## 🛡️ **Security Measures Summary**

1. **Query Validation**: Block dangerous SQL keywords
2. **Parameterized Queries**: Prevent SQL injection
3. **Connection Security**: SSL/TLS required
4. **Timeout Protection**: Prevent long-running queries
5. **Result Limiting**: Max 1000 rows per query
6. **Audit Logging**: Track all database access
7. **Schema Validation**: Only query existing tables/collections

---

## 📊 **Example End-to-End Flow**

### **Input:**
```json
{
    "natural_language_query": "Get patient P1234's visits from last 3 months",
    "format": "json",
    "limit": 50
}
```

### **Bedrock Generated Query:**
```sql
SELECT 
    p.patient_id, 
    p.first_name, 
    p.last_name,
    v.visit_date,
    v.diagnosis_code,
    v.treatment_notes
FROM patients p 
JOIN visits v ON p.patient_id = v.patient_id 
WHERE p.patient_id = $1 
    AND v.visit_date >= $2
ORDER BY v.visit_date DESC
LIMIT $3
```

### **Parameters:**
```json
{
    "patient_id": "P1234",
    "start_date": "2024-06-01",
    "limit": 50
}
```

### **Final Output:**
```json
{
    "query_id": "qry_12345",
    "generated_query": "SELECT p.patient_id...",
    "explanation": "This query fetches patient P1234's visits from the last 3 months",
    "results": [
        {
            "patient_id": "P1234",
            "first_name": "John",
            "last_name": "Doe",
            "visit_date": "2024-08-15",
            "diagnosis_code": "Z00.00",
            "treatment_notes": "Routine checkup"
        }
    ],
    "row_count": 3,
    "execution_time": 0.245
}
```

This is exactly how the "Direct DB Query" works - Bedrock generates safe, parameterized queries that get executed directly against your client databases! 🚀
