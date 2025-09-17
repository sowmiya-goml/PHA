# 🏥 AWS Health PHI Report Generator - Final Approved Flow

## 🎯 **System Overview**

**AI-powered healthcare reporting system that generates personalized health reports from natural language queries without storing any PHI data.**

---

## 🔹 **Detailed Flow – AWS Health PHI Report Generator**

### **1. Database Registration**
- Healthcare client (hospital, clinic, etc.) registers their database with our application
- **They provide:**
  - Database type (SQL/NoSQL) 
  - URI & credentials
  - Connection details
- **Storage:** Credentials stored securely in MongoDB (our central metadata store)
- **⚠️ Important:** No PHI data is stored in MongoDB — only connection configs and extracted schemas

### **2. Secure Connection Setup**
- Our backend runs on **EC2 instance with fixed Elastic IP**
- **Clients whitelist this IP** so only our service can connect to their databases
- Using registered credentials, backend establishes **on-demand connections** to client databases

### **3. Schema Extraction**
- Once connected, custom Python script extracts the schema:
  - **For SQL DBs** → INFORMATION_SCHEMA queries
  - **For NoSQL DBs** → Collection structure sampling
- **The extracted schema is stored in MongoDB**, associated with client's connection record

### **4. Natural Language Query (Doctor's Request)**
- Doctor (or authorized user) asks a question in plain English:
  - *"Extract the details of patient with ID P1234"*
  - *"Show me patient P1234's visits from last 6 months"*
  - *"Generate summary report for patient P1234"*
- System retrieves the **stored schema** for that client database

### **5. Query Generation with Bedrock**
- **Natural language request + schema** sent to Anthropic model on AWS Bedrock
- **Bedrock generates** a safe, parameterized query compatible with client's database type
- Query validated for security (no destructive operations)

### **6. Query Execution**
- Generated query is **validated** (checked against schema, blocked from destructive ops)
- Once validated, query is **executed directly** against client's live database
- **Only the requested patient's data** is retrieved

### **7. Health Report Generation**
- Fetched patient data passed into **another Bedrock agent**
- Agent transforms raw data into **structured Personal Health Report:**
  - Summarized medical history
  - Key vitals and conditions
  - Visualizations (optional)
- Report formatted as **PDF/CSV** and delivered securely (direct download or expiring S3 link)

### **8. Compliance & Security**
- **No PHI stored** in our system; flows in-memory only during processing
- MongoDB contains **only connection metadata and schema** (no patient data)
- Logs capture **metadata only** (request ID, execution time, query type)
- All traffic **encrypted (TLS)**, access restricted by Elastic IP whitelisting

---

## 🔹 **Summary (One-Liner)**

**Our system securely connects to client databases, extracts schemas, uses AWS Bedrock to generate safe queries from natural language requests, executes them in real time, and produces PHI reports — without ever storing sensitive patient data.**

---

## ⚡ **Technical Architecture**

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Healthcare    │───▶│    AWS Bedrock   │───▶│   Client DB     │
│   Provider      │    │   (AI Queries)   │    │  (Live PHI)     │
│  Natural Lang.  │    │ Claude Sonnet 3  │    │   PostgreSQL    │
│    Request      │    │                  │    │   MySQL/Mongo   │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                        │                       │
         ▼                        ▼                       ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│  FastAPI (EC2)  │───▶│  MongoDB Atlas   │    │  Report Gen     │
│ Fixed Elastic IP│    │ (Schema Only)    │    │  (PDF/CSV)      │
│ IP: 52.x.x.x    │    │  NO PHI Data     │    │   + S3 TTL      │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

---

## 💰 **AWS Services Required**

### **Essential Services (Final List)**
| Service | Purpose | Monthly Cost |
|---------|---------|-------------|
| **Amazon EC2** | FastAPI hosting with Elastic IP | $30-50 |
| **Amazon Bedrock** | AI query + report generation | $40-120 |
| **Amazon S3** | Temporary report storage with TTL | $2-8 |
| **MongoDB Atlas** | Schema metadata storage | $25-60 |
| **Total** | | **$97-238/month** |

### **Optional Enhancements**
- **AWS CloudWatch** - Monitoring ($5-15/month)
- **AWS CloudTrail** - HIPAA audit trail ($2-10/month)  
- **AWS KMS** - Enhanced encryption ($1-5/month)

---

## 🛡️ **Security & Compliance**

### **HIPAA Compliance Features**
✅ **Zero PHI Storage** - All patient data processed in-memory only  
✅ **Encrypted Transit** - TLS 1.3 for all connections  
✅ **IP Whitelisting** - Client databases restrict access to our Elastic IP  
✅ **Audit Logging** - Complete trail of all PHI access  
✅ **Query Validation** - Prevent destructive SQL operations  
✅ **Automatic Cleanup** - PHI data cleared from memory after processing  

### **Data Flow Security**
```
Request → Authentication → Schema Lookup → AI Processing → 
Live Query → In-Memory Processing → Report Generation → 
Secure S3 Upload → Expiring URL → Memory Cleanup
```

---

## 🚀 **Key Benefits**

### **For Healthcare Providers**
- 🗣️ **Natural Language Interface** - No SQL knowledge required
- ⚡ **Instant Reports** - 2-5 second generation time
- 📄 **Professional Output** - PDF reports with medical visualizations  
- 🔒 **HIPAA Compliant** - Built-in compliance features

### **For Patients**  
- 🛡️ **Data Security** - No PHI stored in third-party systems
- 🔐 **Privacy Protection** - Encrypted transmission and processing
- 📋 **Complete Audit Trail** - All data access logged

### **For IT Departments**
- 🔌 **Simple Integration** - Standard database connections + IP whitelisting
- 📊 **Easy Monitoring** - Comprehensive logging and health checks
- 💰 **Cost Effective** - $97-238/month vs $500+ complex alternatives

---

## 📊 **Performance Metrics**

### **Target Performance**
- **Query Generation:** < 2 seconds
- **Database Execution:** < 3 seconds  
- **Report Creation:** < 5 seconds
- **Total Response Time:** < 10 seconds
- **System Uptime:** > 99.9%
- **Security:** Zero PHI data breaches

---

## 🔄 **Implementation Timeline**

### **Phase 1: Foundation (Weeks 1-2)**
- EC2 setup with Elastic IP
- MongoDB Atlas configuration
- Basic database connection management
- Schema extraction functionality

### **Phase 2: AI Integration (Weeks 3-4)**  
- AWS Bedrock integration
- Natural language processing
- Live query execution
- Basic report generation

### **Phase 3: Production Ready (Weeks 5-6)**
- Professional PDF/CSV formatting
- S3 secure delivery system
- Comprehensive security & audit logging
- Performance optimization & testing

---

## 📋 **Example Usage**

### **Input:**
```json
{
  "connection_id": "hospital_main_db_123",
  "query": "Extract details for patient with ID P1234",
  "format": "pdf"
}
```

### **Processing Flow:**
1. Retrieve schema for `hospital_main_db_123`
2. Send to Bedrock: `"Patient P1234 details" + database_schema`
3. Bedrock returns: `SELECT * FROM patients p JOIN visits v ON p.id = v.patient_id WHERE p.patient_id = 'P1234'`
4. Execute query on live hospital database
5. Get patient data: `{name: "John Doe", visits: [...], medications: [...]}`
6. Send to Bedrock for report: Generate professional medical summary
7. Create PDF report with patient timeline and key findings
8. Upload to S3 with 5-minute expiring URL

### **Output:**
```json
{
  "report_id": "rpt_xyz789",
  "download_url": "https://s3.aws.com/reports/xyz789.pdf?expires=300",
  "expires_at": "2024-09-10T15:45:00Z",
  "format": "pdf",
  "generated_at": "2024-09-10T15:40:00Z"
}
```

---

**🎯 Final Result:** Healthcare providers can generate comprehensive, HIPAA-compliant patient reports in seconds using natural language queries, without any PHI data leaving their secure environment or being stored in third-party systems.
