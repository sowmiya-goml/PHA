# 🏥 Enhanced Healthcare Query System - Implementation Reference

## 📋 **Overview**
This system extends the original query generation functionality to include actual database execution, providing both AI-generated queries AND real patient data in a single API call.

---

## 🏗️ **System Architecture**

### **Component Stack**
```
┌─────────────────────────────────────────────────────────┐
│                   API Layer                             │
│  /generate-and-execute-query endpoint                   │
└─────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────┐
│              Query Generation Service                    │
│  AWS Bedrock + Claude 3.5 Sonnet                       │
└─────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────┐
│              Query Execution Service                     │
│  Multi-database support + Safety validation             │
└─────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────┐
│              Database Connections                        │
│  PostgreSQL | MySQL | MongoDB | Oracle | SQL Server    │
└─────────────────────────────────────────────────────────┘
```

---

## 🔄 **Complete Request Flow**

### **Step 1: API Request**
```http
GET /api/v1/healthcare/generate-and-execute-query
Parameters:
  - connection_id: "507f1f77bcf86cd799439011"
  - patient_id: "687b0aca-ca63-4926-800b-90d5e92e5a0a"
  - query_type: "comprehensive" | "clinical" | "billing" | "basic"
  - limit: 100 (optional, default safety limit)
```

### **Step 2: Schema Retrieval**
```python
# Fetch database schema from connection metadata
connection_service = ConnectionService(db_manager)
schema_result = await connection_service.get_database_schema(connection_id)

# Extract unified schema structure
schema_dict = {
    "unified_schema": schema_result.unified_schema,
    "database_type": schema_result.database_type,
    "database_name": schema_result.database_name
}
```

### **Step 3: AI Query Generation**
```python
# Generate healthcare-specific query using AWS Bedrock
bedrock_service = BedrockService(db_manager)
query_result = bedrock_service.generate_healthcare_query(
    schema=schema_dict,
    patient_id=patient_id.strip(),
    query_type=query_type
)

# Example generated query:
# "SELECT p.*, d.diagnosis_code, m.medication_name 
#  FROM patients p 
#  LEFT JOIN diagnoses d ON p.patient_id = d.patient_id 
#  LEFT JOIN medications m ON p.patient_id = m.patient_id 
#  WHERE p.patient_id = '687b0aca-ca63-4926-800b-90d5e92e5a0a'"
```

### **Step 4: Query Safety Validation**
```python
# Multi-layer security validation
validation_result = db_operation_service.validate_query_safety(
    query=generated_query,
    database_type=database_type
)

# Security checks:
✅ Read-only operations only (SELECT/FIND)
✅ No SQL injection patterns
✅ No destructive operations (DROP/DELETE/UPDATE)
✅ Query complexity assessment
✅ Safety score calculation (0.0 - 1.0)
```

### **Step 5: Database-Specific Execution**
```python
# Route to appropriate database driver
if database_type == "postgresql":
    results = await _execute_postgresql_query(connection, query, limit)
elif database_type == "mysql":
    results = await _execute_mysql_query(connection, query, limit)
elif database_type == "mongodb":
    results = await _execute_mongodb_query(connection, query, limit)
# ... etc for Oracle, SQL Server
```

### **Step 6: Results Processing**
```python
# Convert database results to standardized format
execution_results = [
    DatabaseQueryResult(
        table_name="patients",
        query="SELECT * FROM patients WHERE...",
        row_count=5,
        data=[
            {"patient_id": "P001", "name": "John Doe", "age": 45},
            {"patient_id": "P002", "name": "Jane Smith", "age": 32},
            # ... actual patient records
        ],
        execution_time_ms=45.2
    )
]
```

### **Step 7: Comprehensive Response**
```json
{
  "generated_query": "SELECT p.*, d.diagnosis_code FROM patients p...",
  "patient_id": "687b0aca-ca63-4926-800b-90d5e92e5a0a",
  "query_type": "comprehensive",
  "model_used": "anthropic.claude-3-5-sonnet-20240620-v1:0",
  "schema_tables_count": 12,
  "status": "success",
  "timestamp": "2025-09-17T12:34:56.789Z",
  
  "connection_info": {
    "connection_id": "507f1f77bcf86cd799439011",
    "database_type": "postgresql",
    "database_name": "healthcare_db",
    "total_tables": 12
  },
  
  "query_executed": true,
  "execution_results": [
    {
      "table_name": "patients",
      "query": "SELECT * FROM patients WHERE patient_id = $1",
      "row_count": 5,
      "data": [
        {
          "patient_id": "687b0aca-ca63-4926-800b-90d5e92e5a0a",
          "first_name": "John",
          "last_name": "Doe",
          "date_of_birth": "1978-03-15",
          "email": "john.doe@email.com"
        }
      ],
      "execution_time_ms": 45.2
    }
  ],
  "total_records_found": 5,
  "total_execution_time_ms": 1247.8,
  "execution_errors": null
}
```

---

## 🛡️ **Security & Safety Features**

### **Query Validation Rules**
```python
# Blocked patterns (case-insensitive)
DANGEROUS_PATTERNS = [
    r'\b(DROP|DELETE|UPDATE|INSERT|CREATE|ALTER|TRUNCATE)\b',  # Write operations
    r'\b(EXEC|EXECUTE)\b',                                      # Command execution
    r';\s*--',                                                  # SQL comments
    r'/\*.*\*/',                                               # Block comments
    r'\bUNION\s+SELECT\b',                                     # Union injection
    r'\bINTO\s+OUTFILE\b',                                     # File operations
    r'\bLOAD_FILE\b',                                          # File loading
    r'\bxp_cmdshell\b'                                         # Command shell
]

# Safety scoring
safety_score = 1.0
if dangerous_pattern_found: safety_score -= 0.3
if not_read_only: safety_score -= 0.5
if high_complexity: safety_score -= 0.1
```

### **Automatic Query Limits**
```python
# Database-specific limit application
PostgreSQL: "SELECT ... LIMIT {limit}"
MySQL:      "SELECT ... LIMIT {limit}"
MongoDB:    collection.find().limit(limit)
Oracle:     "SELECT * FROM (query) WHERE ROWNUM <= {limit}"
SQL Server: "SELECT TOP {limit} ..."
```

---

## 🔌 **Database Driver Support**

### **Currently Supported**
```python
✅ PostgreSQL  → psycopg2
✅ MySQL       → mysql.connector
✅ MongoDB     → pymongo
🔧 Oracle      → oracledb (optional install)
🔧 SQL Server  → pyodbc (optional install)
```

### **Connection Methods**
```python
# Method 1: Connection string (preferred)
connection_string = "postgresql://user:pass@host:5432/dbname"

# Method 2: Individual parameters
host = "localhost"
port = 5432
database_name = "healthcare_db"
username = "admin"
password = "secure_password"
```

---

## 📊 **Query Types & Examples**

### **1. Comprehensive Query**
```sql
-- Generates queries across ALL healthcare domains
SELECT 
    p.patient_id, p.first_name, p.last_name, p.date_of_birth,
    d.diagnosis_code, d.diagnosis_description,
    m.medication_name, m.dosage,
    v.visit_date, v.visit_type,
    l.test_name, l.result_value
FROM patients p
LEFT JOIN diagnoses d ON p.patient_id = d.patient_id
LEFT JOIN medications m ON p.patient_id = m.patient_id
LEFT JOIN visits v ON p.patient_id = v.patient_id
LEFT JOIN lab_results l ON p.patient_id = l.patient_id
WHERE p.patient_id = ?
```

### **2. Clinical Query**
```sql
-- Focuses on medical data only
SELECT 
    p.patient_id, p.first_name, p.last_name,
    d.diagnosis_code, d.diagnosis_description, d.diagnosis_date,
    pr.procedure_code, pr.procedure_description,
    m.medication_name, m.dosage, m.start_date,
    v.vital_signs, v.measurement_date
FROM patients p
LEFT JOIN diagnoses d ON p.patient_id = d.patient_id
LEFT JOIN procedures pr ON p.patient_id = pr.patient_id
LEFT JOIN medications m ON p.patient_id = m.patient_id
LEFT JOIN vitals v ON p.patient_id = v.patient_id
WHERE p.patient_id = ?
```

### **3. Billing Query**
```sql
-- Focuses on financial/billing data
SELECT 
    p.patient_id, p.first_name, p.last_name,
    b.bill_id, b.total_amount, b.bill_date,
    c.claim_id, c.claim_amount, c.claim_status,
    pay.payment_amount, pay.payment_date,
    ins.insurance_provider, ins.policy_number
FROM patients p
LEFT JOIN bills b ON p.patient_id = b.patient_id
LEFT JOIN claims c ON p.patient_id = c.patient_id
LEFT JOIN payments pay ON p.patient_id = pay.patient_id
LEFT JOIN insurance ins ON p.patient_id = ins.patient_id
WHERE p.patient_id = ?
```

### **4. Basic Query**
```sql
-- Essential patient information only
SELECT 
    patient_id, first_name, last_name, date_of_birth,
    email, phone, address, emergency_contact
FROM patients
WHERE patient_id = ?
```

---

## ⚡ **Performance Considerations**

### **Execution Time Tracking**
```python
start_time = time.time()
# ... execute query ...
execution_time_ms = (time.time() - start_time) * 1000

# Response includes:
# - Individual query execution time
# - Total operation time (generation + execution)
# - Row count per table
# - Total records found
```

### **Resource Limits**
```python
DEFAULT_LIMIT = 100          # Max records per query
MAX_EXECUTION_TIME = 30      # Seconds timeout
MAX_RESPONSE_SIZE = "10MB"   # Prevent memory issues
CONNECTION_TIMEOUT = 10      # Database connection timeout
```

---

## 🚨 **Error Handling Strategy**

### **Graceful Degradation**
```python
# Scenario 1: Query generation fails
→ Return error immediately, no execution attempted

# Scenario 2: Query validation fails
→ Block execution, return validation errors + generated query

# Scenario 3: Database connection fails
→ Return connection error, keep generated query for manual use

# Scenario 4: Query execution fails
→ Return partial success with query + error details

# Scenario 5: Partial table failures
→ Return successful tables + error list for failed ones
```

### **Error Response Format**
```json
{
  "generated_query": "SELECT * FROM patients...",
  "query_executed": false,
  "execution_results": null,
  "execution_errors": [
    "Database connection timeout",
    "Table 'medications' not found"
  ],
  "status": "partial_success"
}
```

---

## 🔧 **Configuration & Environment**

### **Required Environment Variables**
```env
# AWS Bedrock Configuration
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_DEFAULT_REGION=us-east-1

# Database Operations
DATABASE_QUERY_TIMEOUT=30
MAX_QUERY_RESULTS=100
ENABLE_QUERY_LOGGING=true
```

### **Optional Dependencies**
```bash
# Core dependencies (required)
pip install psycopg2-binary mysql-connector-python pymongo

# Optional database support
pip install oracledb      # For Oracle databases
pip install pyodbc         # For SQL Server databases
pip install sqlalchemy     # For advanced SQL operations
```

---

## 📝 **API Endpoints Comparison**

### **Original Endpoint** (Query Generation Only)
```http
GET /api/v1/healthcare/generate-query-by-connection
→ Returns: Generated query + metadata (no execution)
```

### **Enhanced Endpoint** (Generation + Execution)
```http
GET /api/v1/healthcare/generate-and-execute-query
→ Returns: Generated query + metadata + actual patient data
```

### **Key Differences**
| Feature | Original | Enhanced |
|---------|----------|----------|
| Query Generation | ✅ | ✅ |
| Query Validation | ❌ | ✅ |
| Database Execution | ❌ | ✅ |
| Real Patient Data | ❌ | ✅ |
| Safety Checks | ❌ | ✅ |
| Performance Metrics | ❌ | ✅ |
| Error Recovery | Basic | Advanced |

---

## 🎯 **Use Cases**

### **1. Healthcare Reports**
- Generate comprehensive patient reports with real data
- Perfect for PHI extraction and health summaries

### **2. Data Validation**
- Verify AI-generated queries against actual database structure
- Test query accuracy with live data

### **3. Real-time Analytics**
- Execute complex healthcare queries on-demand
- Get immediate insights from patient databases

### **4. Integration Testing**
- Validate database connectivity and query performance
- Test different query types across database platforms

---

## 🔮 **Future Enhancements**

### **Planned Features**
```python
# 1. Connection Pooling
connection_pool = DatabaseConnectionPool(max_connections=50)

# 2. Query Caching
@cache(ttl=300)  # 5-minute cache for identical queries
async def execute_cached_query(query_hash, connection_id):

# 3. Async Batch Processing
async def execute_multiple_patients(patient_ids: List[str]):

# 4. Query Optimization Suggestions
def suggest_query_improvements(query: str) -> List[str]:

# 5. Real-time Streaming
async def stream_large_results(query: str) -> AsyncIterator[dict]:
```

---

## 📚 **File Structure Reference**

```
src/pha/
├── api/v1/healthcare.py                    # Enhanced API endpoints
├── services/
│   ├── bedrock_service.py                  # AI query generation
│   ├── database_operation_service.py       # NEW: Query execution
│   └── connection_service.py               # Database connections
└── schemas/
    ├── healthcare.py                       # Original query schemas
    └── database_operations.py              # NEW: Execution schemas
```

---

This reference document provides a complete overview of the enhanced healthcare query system architecture, implementation details, and usage patterns. Keep this for future development and troubleshooting! 🚀