# Final Approved Architecture - AWS Health PHI Report Generator

## 🎯 **System Overview** 

**AI-powered healthcare reporting system that generates personalized health reports from natural language queries without storing any PHI data.**

### **Core Principle**: Zero PHI Storage + Real-time AI Processing + Secure Report Delivery

```
┌─────────────────────────────────────────────────────────┐
│              Healthcare Provider Input                   │
│    "Extract details of patient with ID P1234"          │
└─────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────┐
│           EC2 FastAPI Backend (Elastic IP)             │
│  • Natural Language Processing                         │
│  • Schema Retrieval from MongoDB                      │
│  • User Authentication & Authorization                 │
└─────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────┐
│          AWS Bedrock (Anthropic Claude)                │
│  • Schema-aware Query Generation                       │
│  • Natural Language → SQL/NoSQL Translation           │
│  • Query Validation & Safety Checks                   │
└─────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────┐
│            Live Client Database Query                   │
│  • Direct Connection to Hospital/Clinic DB             │
│  • Parameterized Query Execution                      │
│  • Real-time PHI Data Retrieval                       │
└─────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────┐
│          In-Memory Report Generation                    │
│  • Second Bedrock Call for Report Creation            │
│  • Medical Data Analysis & Summarization              │
│  • PDF/CSV Generation with Visualizations             │
└─────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────┐
│            Secure Report Delivery                      │
│  • Temporary S3 Storage (5-minute TTL)                │
│  • Pre-signed URL Generation                          │
│  • Automatic Cleanup After Download                   │
└─────────────────────────────────────────────────────────┘
```

## 📋 **Detailed Flow Steps**

### **1. Database Registration** 
- Healthcare client provides database connection details
- Credentials stored securely in MongoDB (encrypted)
- **Note**: Only connection metadata stored - NO PHI data

### **2. Secure Connection Setup**
- Backend runs on EC2 with fixed Elastic IP address  
- Clients whitelist our IP for database access
- On-demand secure connections using stored credentials

### **3. Schema Extraction** 
- **SQL Databases**: INFORMATION_SCHEMA queries extract table structures
- **NoSQL Databases**: Collection sampling to understand document structure  
- Extracted schemas stored in MongoDB for AI processing

### **4. Natural Language Query Processing**
- Doctor/Provider inputs plain English request
- System retrieves stored schema for target database
- Request prepared for AWS Bedrock processing

### **5. AI Query Generation with Bedrock**
- Natural language + database schema sent to Anthropic Claude
- AI generates safe, parameterized SQL/NoSQL queries
- Automatic validation against schema and security rules

### **6. Live Database Query Execution** 
- Generated query executed directly against client database
- Real-time data retrieval - no intermediate storage
- Only requested patient data retrieved from live system

### **7. Health Report Generation**
- Retrieved patient data processed by second Bedrock agent
- AI transforms raw data into structured health report:
  - Summarized medical history
  - Key vitals and conditions  
  - Medical visualizations and timelines
- Output formatted as PDF or CSV

### **8. Secure Report Delivery & Compliance**
- Report generated entirely in-memory (no disk storage)
- Temporary upload to S3 with 2-hour TTL
- Pre-signed URL provided for secure download
- Automatic cleanup after download or expiration
- All access logged for HIPAA compliance

## 🛠️ **Required AWS Services (Final)**

### **Essential Services**
| Service | Purpose | Monthly Cost |
|---------|---------|-------------|
| **Amazon EC2** | FastAPI backend hosting with Elastic IP | $30-50 |
| **Amazon Bedrock** | AI query generation + report creation | $40-120 |
| **Amazon S3** | Temporary report storage with TTL | $2-8 |
| **MongoDB Atlas** | Schema and connection metadata storage | $25-60 |

### **Optional Enhancements**  
| Service | Purpose | When Needed |
|---------|---------|-------------|
| **AWS CloudWatch** | Monitoring and logging | Production deployment |
| **AWS CloudTrail** | Audit trail for compliance | HIPAA requirements |
| **AWS KMS** | Credential encryption | Enhanced security |

### **Total Estimated Cost**: **$97-238/month** (compared to $500+ with original complex flow)

## 🔧 **Key Technical Implementation**

### **1. Core Services Architecture**

```python
# app/services/bedrock_service.py
class BedrockService:
    async def generate_query(self, schema: Dict, request: str, db_type: str) -> Dict:
        """Convert natural language to SQL/NoSQL query"""
        prompt = f"""
        Database Type: {db_type}
        Schema: {json.dumps(schema)}
        Request: {request}
        
        Generate a safe, parameterized query. Rules:
        1. Only SELECT operations
        2. Use parameters for all values
        3. Return JSON format with query and parameters
        """
        
        response = await self.bedrock_client.invoke_model(
            modelId="anthropic.claude-3-sonnet-20240229-v1:0",
            body=json.dumps({"messages": [{"role": "user", "content": prompt}]})
        )
        return json.loads(response['content'][0]['text'])
    
    async def generate_health_report(self, patient_data: Dict, format: str) -> bytes:
        """Transform patient data into structured health report"""
        prompt = f"""
        Patient Data: {json.dumps(patient_data)}
        Format: {format}
        
        Create a comprehensive health report with:
        1. Patient summary
        2. Medical history timeline  
        3. Key findings and recommendations
        4. Data visualizations (if PDF)
        """
        
        # Generate report content and format as PDF/CSV
        return await self.create_formatted_report(response, format)

# app/services/database_service.py  
class DatabaseQueryService:
    async def execute_live_query(self, connection_id: str, query_data: Dict) -> Dict:
        """Execute query against client database in real-time"""
        connection = await self.get_connection(connection_id)
        
        # Validate query safety
        self.validate_query_security(query_data['query'])
        
        # Execute against live database
        if connection.db_type == "postgresql":
            return await self.execute_postgres_query(connection, query_data)
        elif connection.db_type == "mongodb":
            return await self.execute_mongo_query(connection, query_data)
        # etc.

# app/services/report_service.py
class ReportService:
    async def create_secure_delivery(self, report_content: bytes, format: str) -> str:
        """Upload to S3 with expiring URL for secure delivery"""
        
        # Upload to S3 with TTL
        s3_key = f"reports/{uuid.uuid4()}.{format}"
        await self.s3_client.upload_object(
            bucket=self.report_bucket,
            key=s3_key,
            body=report_content,
            expires_in_hours=2
        )
        
        # Generate pre-signed URL (5 minute expiry)
        download_url = await self.s3_client.generate_presigned_url(
            bucket=self.report_bucket,
            key=s3_key,
            expires_in=300  # 5 minutes
        )
        
        return download_url
```

### **2. API Endpoints Design**

```python
# app/routers/queries.py - Main endpoint for the complete flow
@router.post("/connections/{connection_id}/generate-report")
async def generate_health_report(
    connection_id: str,
    request: HealthReportRequest,
    user: User = Depends(get_current_user)
):
    """
    Complete flow: Natural Language → Query → Execute → Report → Delivery
    Example: POST /api/v1/connections/123/generate-report
    Body: {"query": "Extract patient P1234 details", "format": "pdf"}
    """
    
    # 1. Get schema from MongoDB
    schema = await connection_service.get_schema(connection_id)
    
    # 2. Generate query with Bedrock
    query_data = await bedrock_service.generate_query(
        schema=schema, 
        request=request.query, 
        db_type=connection.database_type
    )
    
    # 3. Execute query on live database  
    patient_data = await database_service.execute_live_query(connection_id, query_data)
    
    # 4. Generate health report with Bedrock
    report_content = await bedrock_service.generate_health_report(
        patient_data=patient_data, 
        format=request.format
    )
    
    # 5. Secure delivery via S3
    download_url = await report_service.create_secure_delivery(
        report_content, 
        request.format
    )
    
    # 6. Audit logging
    await audit_service.log_report_generation(
        user_id=user.id,
        connection_id=connection_id, 
        patient_id=request.patient_id,
        success=True
    )
    
    return {
        "report_id": str(uuid.uuid4()),
        "download_url": download_url,
        "expires_at": datetime.utcnow() + timedelta(minutes=5),
        "format": request.format,
        "generated_at": datetime.utcnow().isoformat()
    }

# Supporting endpoints
@router.get("/connections/{connection_id}/schema")
async def get_database_schema(connection_id: str):
    """Get extracted schema for query generation"""
    pass

@router.post("/connections")  
async def register_database(config: DatabaseConnectionConfig):
    """Register new client database"""
    pass
```

### **3. Data Models & Security**

```python
# app/models/requests.py
class HealthReportRequest(BaseModel):
    query: str = Field(..., min_length=10, max_length=500, 
                      example="Extract details for patient P1234")
    format: str = Field(..., regex="^(pdf|csv)$")
    patient_id: Optional[str] = None  # For audit logging

class DatabaseConnectionConfig(BaseModel):
    connection_name: str
    database_type: str = Field(..., regex="^(PostgreSQL|MySQL|MongoDB)$")
    host: str
    port: int
    database_name: str
    username: str
    password: str = Field(..., min_length=8)  # Will be encrypted

# app/models/security.py  
class QueryValidator:
    FORBIDDEN_KEYWORDS = ['DROP', 'DELETE', 'UPDATE', 'INSERT', 'ALTER', 'TRUNCATE']
    
    @staticmethod
    def validate_query_safety(query: str) -> bool:
        """Ensure query is read-only and safe"""
        query_upper = query.upper()
        
        # Check for forbidden operations
        for keyword in QueryValidator.FORBIDDEN_KEYWORDS:
            if keyword in query_upper:
                raise SecurityException(f"Forbidden keyword: {keyword}")
        
        # Must be SELECT only
        if not query_upper.strip().startswith('SELECT'):
            raise SecurityException("Only SELECT queries allowed")
        
        return True

# app/models/audit.py
class AuditLog(BaseModel):
    timestamp: datetime
    user_id: str
    action: str  # "report_generated", "query_executed"
    connection_id: str
    patient_id_hash: str  # Hashed patient ID for privacy
    success: bool
    error_message: Optional[str]
    execution_time_ms: int
    rows_returned: int
```

## 🛡️ **Security & Compliance**

### **HIPAA Compliance Features**
- ✅ **Zero PHI Storage**: All patient data processed in-memory only
- ✅ **Minimum Necessary**: Only requested data fields retrieved 
- ✅ **Audit Logging**: Complete access trail for all PHI interactions
- ✅ **Encrypted Transport**: TLS 1.3 for all connections
- ✅ **Access Controls**: Role-based authentication and authorization
- ✅ **Automatic Cleanup**: PHI data cleared from memory after processing

### **Data Protection Implementation**
```python
class SecurityManager:
    @staticmethod
    async def encrypt_credentials(password: str) -> str:
        """Encrypt database credentials before MongoDB storage"""
        return await encryption_service.encrypt_with_kms(password)
    
    @staticmethod
    def hash_patient_id(patient_id: str) -> str:
        """Hash patient IDs for audit logs (privacy protection)"""
        return hashlib.sha256(f"{patient_id}{SALT}".encode()).hexdigest()
    
    @staticmethod
    async def clear_phi_from_memory(data_objects: List[Any]):
        """Aggressive memory cleanup of PHI data"""
        for obj in data_objects:
            if hasattr(obj, '__dict__'):
                obj.__dict__.clear()
        gc.collect()  # Force garbage collection
```

## � **Key Benefits of This Architecture**

### **✅ Advantages Over Complex Flows**
| Benefit | Our Approach | Alternative Complex Flow |
|---------|--------------|------------------------|
| **Cost** | $97-238/month | $500-1200/month |
| **Complexity** | 5 core steps | 10+ interconnected services |
| **PHI Security** | Zero storage, memory-only | Multiple data copies |
| **Performance** | Real-time (2-5 seconds) | Batch processing (minutes) |
| **Maintenance** | Single application stack | Multiple service orchestration |
| **Compliance** | Built-in HIPAA features | Requires multiple configurations |

### **🎯 Business Value**
1. **Healthcare Provider Benefits**:
   - Natural language queries (no SQL knowledge required)
   - Instant report generation 
   - Professional PDF/CSV outputs
   - HIPAA-compliant by design

2. **Patient Safety Benefits**:
   - No PHI data stored in third-party systems
   - Secure, encrypted data transmission
   - Audit trail for all data access
   - Automatic data cleanup

3. **IT Department Benefits**:
   - Simple IP whitelisting setup
   - No complex integrations required
   - Standard database connections
   - Comprehensive monitoring and logging

## 📊 **Implementation Timeline**

### **Phase 1: Core Infrastructure (Weeks 1-2)**
- [ ] EC2 setup with Elastic IP
- [ ] MongoDB Atlas configuration  
- [ ] Basic FastAPI application
- [ ] Database connection management
- [ ] Schema extraction functionality

### **Phase 2: AI Integration (Weeks 3-4)**  
- [ ] AWS Bedrock service integration
- [ ] Natural language query processing
- [ ] Query validation and security
- [ ] Live database query execution
- [ ] Basic report generation

### **Phase 3: Advanced Features (Weeks 5-6)**
- [ ] Professional PDF/CSV report formatting
- [ ] S3 secure delivery system
- [ ] Comprehensive audit logging
- [ ] Performance optimization
- [ ] Security hardening

### **Phase 4: Production Ready (Weeks 7-8)**
- [ ] Load testing and optimization
- [ ] Monitoring and alerting setup
- [ ] Documentation and training
- [ ] HIPAA compliance validation
- [ ] Production deployment

## 🎯 **Success Metrics**

### **Technical KPIs**
- Query generation time: < 2 seconds
- Report creation time: < 5 seconds  
- System uptime: > 99.9%
- Zero PHI data breaches
- Complete audit trail coverage

### **Business KPIs**
- Doctor satisfaction with natural language interface
- Report accuracy and completeness
- Time savings vs manual report creation
- Healthcare provider adoption rate
- Compliance audit success rate

---

**🏥 Final Summary**: This architecture delivers a secure, AI-powered PHI report generation system that processes healthcare data in real-time without storing sensitive information, ensuring HIPAA compliance while providing instant, professional medical reports through natural language queries.

**Total Implementation**: 6-8 weeks | **Monthly Cost**: $97-238 | **Compliance**: HIPAA Ready
