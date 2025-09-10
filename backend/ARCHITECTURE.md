# AWS Health PHI Report Generator - Architecture Documentation

## 🏗️ System Architecture Overview

The AWS Health PHI Report Generator is a secure, AI-powered system that connects to client databases, extracts schemas, and generates personalized health reports using AWS Bedrock without storing any PHI data.

```
┌─────────────────────────────────────────────────────────┐
│                Doctor/Healthcare User                    │
│         "Extract details for patient P1234"            │
└─────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────┐
│                 FastAPI Backend (EC2)                   │
│            • Fixed Elastic IP (Whitelisted)            │
│            • Natural Language Processing                │
│            • Connection Management                      │
└─────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────┐
│              MongoDB Atlas (Metadata Only)              │
│            • Connection Configurations                  │
│            • Extracted Database Schemas                │
│            • NO PHI Data Stored                        │
└─────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────┐
│              AWS Bedrock (Anthropic Claude)             │
│            • Natural Language → SQL/NoSQL              │
│            • Query Generation & Validation             │
│            • Health Report Generation                  │
└─────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────┐
│              Client Databases (Live Query)              │
│          [Hospital PostgreSQL] [Clinic MySQL]          │
│          [Healthcare MongoDB] [Other Systems]           │
└─────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────┐
│              Secure Report Delivery                     │
│          • PDF/CSV Generation                          │
│          • S3 Temporary Storage (Expiring URLs)       │
│          • Direct Download                             │
└─────────────────────────────────────────────────────────┘
```

---

## � **Complete System Flow**

### **Step 1: Database Registration**
- Healthcare clients register their databases with connection details
- Credentials stored securely in MongoDB (encrypted)
- No PHI data stored - only connection metadata

### **Step 2: Secure Connection Setup**
- Backend runs on EC2 with fixed Elastic IP
- Clients whitelist our IP for secure access
- On-demand connections established using stored credentials

### **Step 3: Schema Extraction**
- Custom Python scripts extract database schemas
- SQL: INFORMATION_SCHEMA queries
- NoSQL: Collection structure sampling
- Schemas stored in MongoDB for query generation

### **Step 4: Natural Language Processing**
- Doctor inputs plain English request: *"Extract patient P1234 details"*
- System retrieves stored schema for target database
- Request prepared for AI processing

### **Step 5: AI Query Generation**
- Natural language + schema sent to AWS Bedrock
- Anthropic Claude generates safe, parameterized queries
- Queries validated against schema and security rules

### **Step 6: Live Database Query**
- Generated query executed directly on client database
- Real-time data retrieval (no intermediate storage)
- Only requested patient data fetched

### **Step 7: Health Report Generation**
- Patient data processed by second Bedrock agent
- Structured Personal Health Report created
- Output formats: PDF, CSV with visualizations

### **Step 8: Secure Delivery**
- Reports generated in-memory only
- Temporary S3 storage with expiring URLs
- Direct download or secure link delivery

---

## 📦 **Component Architecture**

### 1. **FastAPI Backend** (`app/main.py`)

**Responsibilities:**
- Natural language request processing
- Database connection management
- AI integration with AWS Bedrock
- Secure report generation

**Key Features:**
```python
# FastAPI Application
app = FastAPI(
    title="AWS Health PHI Report Generator",
    version="2.0.0",
    description="AI-powered health report generator with secure PHI processing",
    docs_url="/docs",
    redoc_url="/redoc"
)
```

### 2. **Router Layer** 

**Core Endpoints:**
```python
# Database Management
@router.post("/connections", response_model=ConnectionResponse)
@router.get("/connections", response_model=List[ConnectionResponse])
@router.get("/connections/{id}/schema", response_model=SchemaResponse)

# AI Query & Report Generation
@router.post("/connections/{id}/query", response_model=QueryResponse)
@router.post("/connections/{id}/report", response_model=ReportResponse)
@router.get("/reports/{id}/download", response_model=DownloadResponse)
```

### 3. **Service Layer**

**Core Services:**
```python
class ConnectionService:
    async def register_database(self, config: DatabaseConfig) -> str
    async def extract_schema(self, connection_id: str) -> Dict
    async def test_connection(self, connection_id: str) -> bool

class BedrockService:
    async def generate_query(self, schema: Dict, request: str) -> str
    async def generate_report(self, data: Dict) -> bytes

class ReportService:
    async def create_pdf_report(self, data: Dict) -> bytes
    async def create_csv_report(self, data: Dict) -> bytes
    async def upload_to_s3(self, content: bytes) -> str
```

### 4. **Data Models** (`app/models/`)

**Core Models:**
```python
class DatabaseConfig:
    connection_name: str
    database_type: str  # PostgreSQL, MySQL, MongoDB
    host: str
    port: int
    database_name: str
    username: str
    password: str  # Encrypted in MongoDB
    
class QueryRequest:
    natural_language_query: str
    connection_id: str
    format: str  # pdf, csv, json
    
class HealthReport:
    patient_id: str
    report_type: str
    generated_at: datetime
    data: Dict[str, Any]
    
class ReportResponse:
    report_id: str
    download_url: str
    expires_at: datetime
```

### 5. **Security & Compliance Layer**

**Key Features:**
- **No PHI Storage**: All patient data processed in-memory only
- **Encryption**: All credentials and data encrypted in transit/rest
- **IP Whitelisting**: Client databases restrict access to our Elastic IP
- **Audit Logging**: All queries and report generations logged
- **Query Validation**: Prevent destructive operations (DROP, DELETE, etc.)

**Security Implementation:**
```python
class SecurityManager:
    @staticmethod
    def validate_query(query: str, schema: Dict) -> bool:
        # Prevent SQL injection and destructive operations
        
    @staticmethod
    def encrypt_credentials(credentials: str) -> str:
        # Encrypt database credentials before storage
        
    @staticmethod
    def audit_log(action: str, user_id: str, details: Dict):
        # Log all PHI access for compliance
```

---

## 🔄 **AI-Powered Query Flow**

### 1. **Natural Language to Query Flow**

```
Doctor Input → Schema Lookup → Bedrock Processing → Query Generation → Validation → Execution
     ↓              ↓               ↓                  ↓               ↓           ↓
"Patient P1234" → DB Schema → AI Analysis → SQL/NoSQL Query → Security Check → Live DB Query
```

**Example:**
```python
# Input: "Extract patient P1234's last 6 months visits"
# Schema: {patients: {id, name}, visits: {patient_id, date, diagnosis}}
# Generated Query: SELECT * FROM visits WHERE patient_id = $1 AND date >= $2
# Parameters: {patient_id: "P1234", date: "2024-03-01"}
```

### 2. **Report Generation Flow**

```
Query Results → Data Processing → Bedrock Report Agent → Format Selection → Secure Delivery
     ↓              ↓                    ↓                   ↓               ↓
Patient Data → Structured JSON → AI Report Generation → PDF/CSV → S3 + Expiring URL
```

**Report Types:**
- **Summary Report**: Key vitals, recent visits, medications
- **Detailed Report**: Complete medical history with visualizations
- **Custom Reports**: Based on specific doctor requirements

### 3. **Security & Compliance Flow**

```
Every Request → Authentication → Authorization → Audit Logging → PHI Processing → Secure Cleanup
     ↓              ↓               ↓               ↓               ↓              ↓
User Login → Role Check → Permission Verify → Log Access → Process Data → Memory Clear
```

---

## 🗃️ **Database Architecture**

### **MongoDB Atlas (Metadata Store)**
**Purpose**: Store connection configs and schemas (NO PHI data)

**Collections:**
```json
// database_connections
{
  "_id": ObjectId("..."),
  "connection_name": "City Hospital Main DB",
  "database_type": "PostgreSQL",
  "host": "hospital-db.amazonaws.com",
  "port": 5432,
  "database_name": "patient_records",
  "username_encrypted": "...",
  "password_encrypted": "...",
  "elastic_ip_whitelisted": true,
  "created_at": ISODate("..."),
  "last_schema_update": ISODate("...")
}

// database_schemas  
{
  "_id": ObjectId("..."),
  "connection_id": ObjectId("..."),
  "schema": {
    "tables": {
      "patients": {
        "columns": ["patient_id", "first_name", "last_name", "dob"],
        "primary_key": "patient_id"
      },
      "visits": {
        "columns": ["visit_id", "patient_id", "visit_date", "diagnosis"],
        "foreign_keys": {"patient_id": "patients.patient_id"}
      }
    }
  },
  "extracted_at": ISODate("...")
}

// audit_logs (Compliance)
{
  "user_id": "dr_smith_123",
  "action": "generate_report",
  "connection_id": ObjectId("..."),
  "patient_id": "P1234",  // Anonymized in logs
  "timestamp": ISODate("..."),
  "query_generated": "SELECT * FROM visits WHERE...",
  "rows_returned": 15,
  "report_format": "pdf"
}
```

### **Client Databases (Live Query Targets)**
**Purpose**: Healthcare databases containing actual PHI

**Supported Types:**
- **PostgreSQL**: Hospital management systems
- **MySQL**: Clinic databases  
- **MongoDB**: Modern healthcare platforms
- **SQL Server**: Legacy hospital systems (future)

---

## ☁️ **AWS Services Architecture**

### **Essential AWS Services**

| Service | Purpose | Usage | Monthly Cost Est. |
|---------|---------|-------|-------------------|
| **EC2** | FastAPI hosting with Elastic IP | t3.medium instance | $24-40 |
| **Bedrock** | AI query + report generation | Claude Sonnet API calls | $30-100 |
| **S3** | Temporary report storage | PDF/CSV with TTL | $1-5 |
| **MongoDB Atlas** | Metadata storage | Shared cluster | $9-25 |

### **Optional Enhancements**

| Service | Purpose | When Needed |
|---------|---------|-------------|
| **CloudWatch** | Monitoring & logging | Production deployment |
| **KMS** | Credential encryption | Enhanced security |
| **CloudTrail** | Compliance auditing | Regulatory requirements |

---

## 🔐 **Security Architecture**

### 1. **Network Security**
```python
# IP Whitelisting Configuration
ALLOWED_CLIENT_IPS = [
    "hospital-1.amazonaws.com",  # City Hospital
    "clinic-db.azure.com",      # Medical Clinic
    "healthcare-mongo.gcp.com"  # Health System
]

# Elastic IP Configuration  
EC2_ELASTIC_IP = "52.123.45.67"  # Fixed IP for client whitelisting
```

### 2. **Data Protection**
- **Encryption at Rest**: All MongoDB data encrypted with AES-256
- **Encryption in Transit**: TLS 1.3 for all connections
- **Credential Security**: Database passwords encrypted with AWS KMS
- **No PHI Storage**: Patient data never persisted to disk

### 3. **Access Control**
```python
class SecurityValidator:
    @staticmethod 
    def validate_query_safety(query: str) -> bool:
        """Prevent destructive operations"""
        forbidden = ['DROP', 'DELETE', 'UPDATE', 'INSERT', 'ALTER']
        return not any(word in query.upper() for word in forbidden)
    
    @staticmethod
    def sanitize_patient_data(data: Dict) -> Dict:
        """Remove sensitive fields from logs"""
        sensitive_fields = ['ssn', 'phone', 'address', 'email']
        return {k: v for k, v in data.items() if k not in sensitive_fields}
```

---

## ⚡ **Performance Architecture**

### 1. **AI Processing Optimization**
```python
# Optimized Bedrock calls
async def generate_query_and_report(schema: Dict, request: str) -> Dict:
    """Single Bedrock call for both query generation and report template"""
    
    # Combine operations to reduce API calls
    prompt = f"""
    Schema: {schema}
    Request: {request}
    
    Generate:
    1. Safe SQL/NoSQL query
    2. Report structure template
    3. Data processing instructions
    """
    
    # Single API call instead of multiple
    return await bedrock_client.invoke_model(prompt)
```

### 2. **Database Performance** 
- **Connection Pooling**: Reuse client database connections
- **Query Timeout**: 30-second maximum execution time
- **Result Limiting**: Maximum 10,000 rows per query
- **Parallel Processing**: Handle multiple requests simultaneously

### 3. **Memory Management**
- **Streaming Processing**: Large datasets processed in chunks
- **Automatic Cleanup**: PHI data cleared from memory after processing
- **Resource Limits**: Maximum 512MB memory per request
- **Garbage Collection**: Aggressive cleanup of temporary objects

### 4. **Caching Strategy**
```python
# Schema caching to avoid repeated extraction
@cache(expire=3600)  # 1 hour cache
async def get_database_schema(connection_id: str) -> Dict:
    """Cache schemas to improve response time"""
    return await extract_fresh_schema(connection_id)

# Query result caching for identical requests
@cache(expire=300)   # 5 minute cache for identical queries
async def execute_patient_query(query_hash: str) -> Dict:
    """Cache non-PHI query results temporarily"""
    return await execute_database_query(query_hash)
```

---

## 🔧 **Configuration Architecture**

### 1. **Environment Configuration**
```python
class Settings:
    # Application
    APP_NAME: str = "AWS Health PHI Report Generator"
    VERSION: str = "2.0.0"
    
    # AWS Configuration
    AWS_REGION: str = os.getenv("AWS_REGION", "us-east-1")
    BEDROCK_MODEL_ID: str = os.getenv("BEDROCK_MODEL_ID", "anthropic.claude-3-sonnet-20240229-v1:0")
    S3_REPORT_BUCKET: str = os.getenv("S3_REPORT_BUCKET")
    
    # Database Configuration
    MONGODB_URL: str = os.getenv("MONGODB_URL")
    DATABASE_NAME: str = os.getenv("DATABASE_NAME", "pha_metadata")
    
    # Security Configuration
    ELASTIC_IP: str = os.getenv("ELASTIC_IP")
    ENCRYPTION_KEY: str = os.getenv("ENCRYPTION_KEY")
    JWT_SECRET: str = os.getenv("JWT_SECRET")
    
    # Performance Configuration
    QUERY_TIMEOUT_SECONDS: int = int(os.getenv("QUERY_TIMEOUT_SECONDS", "30"))
    MAX_ROWS_PER_QUERY: int = int(os.getenv("MAX_ROWS_PER_QUERY", "10000"))
    REPORT_EXPIRY_MINUTES: int = int(os.getenv("REPORT_EXPIRY_MINUTES", "5"))
```

### 2. **Service Dependencies**
```python
# Dependency injection for services
async def get_bedrock_service() -> BedrockService:
    return BedrockService(
        model_id=settings.BEDROCK_MODEL_ID,
        region=settings.AWS_REGION
    )

async def get_connection_service() -> ConnectionService:
    return ConnectionService(
        db_manager=get_database_manager(),
        encryption_key=settings.ENCRYPTION_KEY
    )

async def get_report_service() -> ReportService:
    return ReportService(
        s3_bucket=settings.S3_REPORT_BUCKET,
        expiry_minutes=settings.REPORT_EXPIRY_MINUTES
    )
```

---

## 📊 **Monitoring & Compliance**

### 1. **Health Monitoring**
```python
@app.get("/health")
async def comprehensive_health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "services": {
            "mongodb": await db_manager.is_connected(),
            "bedrock": await bedrock_service.test_connection(),
            "s3": await s3_service.test_bucket_access()
        },
        "elastic_ip": settings.ELASTIC_IP,
        "active_connections": await get_active_client_connections()
    }
```

### 2. **Compliance Logging**
```python
class ComplianceLogger:
    async def log_phi_access(self, event_data: Dict):
        """HIPAA-compliant audit logging"""
        audit_record = {
            "timestamp": datetime.utcnow().isoformat(),
            "user_id": event_data["user_id"],
            "action": event_data["action"],  # "query_generated", "report_created"
            "connection_id": event_data["connection_id"],
            "patient_id_hash": hashlib.sha256(event_data["patient_id"].encode()).hexdigest(),
            "query_type": event_data.get("query_type"),
            "rows_affected": event_data.get("rows_affected"),
            "success": event_data["success"],
            "error_message": event_data.get("error_message")
        }
        
        # Store in separate audit collection
        await audit_collection.insert_one(audit_record)
        
        # Also send to CloudWatch for monitoring
        if settings.CLOUDWATCH_ENABLED:
            await cloudwatch_client.put_log_events(audit_record)
```

### 3. **Performance Metrics**
- **AI Processing Time**: Bedrock API response times
- **Database Query Performance**: Client database response times  
- **Report Generation Speed**: PDF/CSV creation duration
- **Memory Usage**: PHI data processing memory consumption
- **Error Rates**: Failed queries, timeouts, validation errors

---

## 🚀 **Scalability Architecture**

### 1. **Horizontal Scaling**
- **Stateless Design**: No server-side session storage
- **Load Balancer Ready**: Multiple EC2 instances behind ALB
- **Auto Scaling**: Based on CPU and memory usage
- **Database Connections**: Pooled and distributed

### 2. **AI Processing Scaling**
```python
# Bedrock rate limiting and queue management
class BedrockQueueManager:
    def __init__(self, max_concurrent_requests: int = 10):
        self.semaphore = asyncio.Semaphore(max_concurrent_requests)
    
    async def process_query(self, schema: Dict, request: str):
        async with self.semaphore:
            # Prevent overwhelming Bedrock API
            return await bedrock_client.generate_query(schema, request)
```

### 3. **Cost Optimization**
- **Smart Caching**: Reduce duplicate Bedrock API calls
- **Efficient Queries**: Limit data retrieval to necessary fields only
- **S3 Lifecycle**: Automatic deletion of expired reports
- **Connection Reuse**: Maintain persistent client database connections

---

## 🔄 **Extension Architecture**

### 1. **Adding New Database Types**
```python
# Extensible database support
class DatabaseConnector:
    async def connect_oracle(self, config: DatabaseConfig):
        """Oracle database support"""
        import cx_Oracle
        return cx_Oracle.connect(config.connection_string)
    
    async def connect_sqlserver(self, config: DatabaseConfig):
        """SQL Server support"""
        import pyodbc
        return pyodbc.connect(config.connection_string)
    
    async def extract_oracle_schema(self, connection):
        """Oracle-specific schema extraction"""
        query = """
        SELECT table_name, column_name, data_type 
        FROM user_tab_columns 
        ORDER BY table_name, column_id
        """
        return await connection.execute(query)
```

### 2. **Future Enhancements**
- **Multi-format Reports**: Excel, Word, PowerPoint
- **Real-time Dashboards**: Live patient monitoring
- **Mobile App Integration**: React Native companion app
- **Voice Processing**: "Alexa, generate patient P1234 report"
- **FHIR Integration**: HL7 FHIR standard support
- **Blockchain Audit**: Immutable compliance logging

---

## 📋 **Testing Strategy**

### 1. **Test Coverage**
```
tests/
├── unit/
│   ├── test_bedrock_service.py    # AI query generation tests
│   ├── test_security_validator.py # Security validation tests
│   ├── test_report_generator.py   # Report creation tests
├── integration/
│   ├── test_end_to_end_flow.py   # Complete flow testing
│   ├── test_database_connections.py # Client DB connectivity
├── security/
│   ├── test_sql_injection.py     # Security penetration tests
│   ├── test_phi_compliance.py    # PHI handling compliance
└── performance/
    ├── test_load_testing.py      # High-volume request testing
    └── test_memory_usage.py      # PHI memory cleanup testing
```

### 2. **Compliance Testing**
- **HIPAA Validation**: Ensure no PHI storage or logging
- **Security Audits**: Regular penetration testing
- **Performance Testing**: Handle 1000+ concurrent requests
- **Disaster Recovery**: Database failover testing

---

## 💰 **Cost Analysis**

### **Monthly Operating Costs**
| Component | Usage | Cost Range |
|-----------|-------|------------|
| **EC2 t3.medium** | 24/7 with Elastic IP | $30-45 |
| **Bedrock API** | 10,000 queries/month | $50-150 |
| **S3 Storage** | Temporary reports | $1-3 |
| **MongoDB Atlas** | M10 cluster | $57 |
| **Data Transfer** | Client DB connections | $10-25 |
| **CloudWatch** | Monitoring & logs | $5-15 |
| **Total Estimated** | | **$153-295/month** |

### **Scaling Costs**
- **High Volume**: +$200-500/month (50,000+ queries)
- **Enterprise**: +$500-1000/month (multi-tenant, 24/7 support)

---

**System Overview**: Secure, AI-powered PHI report generation without data storage  
**Last Updated**: September 2025  
**Architecture Version**: 2.0.0  
**Compliance Level**: HIPAA Ready
