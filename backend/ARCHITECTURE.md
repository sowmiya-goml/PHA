# PHA Database Connection Manager - Architecture Documentation

## 🏗️ System Architecture Overview

The PHA Database Connection Manager follows a **layered architecture pattern** with clear separation of concerns, ensuring maintainability, scalability, and testability.

```
┌─────────────────────────────────────────────────────────┐
│                    Client Layer                          │
│  (Web Browser, Mobile App, API Clients, Swagger UI)    │
└─────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────┐
│                   API Gateway Layer                     │
│            (FastAPI + Uvicorn ASGI Server)             │
│  • CORS Middleware     • Request/Response Validation    │
│  • Error Handling      • Auto Documentation            │
└─────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────┐
│                   Router Layer                          │
│                (app/routers/connections.py)             │
│  • REST Endpoints      • HTTP Status Codes             │
│  • Path Parameters     • Dependency Injection          │
└─────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────┐
│                  Service Layer                          │
│              (app/services/connection_service.py)       │
│  • Business Logic      • Schema Analysis               │
│  • Database Testing    • Connection Management         │
└─────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────┐
│                   Model Layer                           │
│               (app/models/connection.py)                │
│  • Data Models         • MongoDB Mapping               │
│  • Serialization      • Type Definitions               │
└─────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────┐
│                  Database Layer                         │
│                 (app/db/session.py)                     │
│  • Connection Pooling  • Session Management            │
│  • Error Handling     • Health Checks                  │
└─────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────┐
│                External Databases                       │
│  [MongoDB Atlas] [PostgreSQL/Neon] [MySQL] [Others]   │
└─────────────────────────────────────────────────────────┘
```

---

## 📦 Component Architecture

### 1. **API Gateway Layer** (`app/main.py`)

**Responsibilities:**
- HTTP request/response handling
- CORS configuration
- Middleware management
- Application startup/shutdown
- Route registration

**Key Features:**
```python
# FastAPI Application
app = FastAPI(
    title="PHA Database Connection Manager",
    version="1.0.0",
    description="API for managing database connections with schema extraction",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)
```

### 2. **Router Layer** (`app/routers/connections.py`)

**Responsibilities:**
- Define REST API endpoints
- Handle HTTP methods and status codes
- Parameter validation and extraction
- Response formatting

**Endpoint Architecture:**
```python
@router.post("/", response_model=DatabaseConnectionResponse, status_code=201)
@router.get("/", response_model=List[DatabaseConnectionResponse])
@router.get("/{connection_id}", response_model=DatabaseConnectionResponse)
@router.put("/{connection_id}", response_model=DatabaseConnectionResponse)
@router.delete("/{connection_id}")
@router.post("/test", response_model=ConnectionTestResult)
@router.get("/{connection_id}/schema", response_model=DatabaseSchemaResult)
@router.get("/{connection_id}/databases")
```

### 3. **Service Layer** (`app/services/connection_service.py`)

**Responsibilities:**
- Core business logic implementation
- Database connection testing
- Schema extraction and analysis
- Data transformation and processing

**Key Components:**
```python
class ConnectionService:
    # CRUD Operations
    async def create_connection(self, connection_data: DatabaseConnectionCreate)
    async def get_all_connections(self) -> List[DatabaseConnectionResponse]
    async def get_connection_by_id(self, connection_id: str)
    async def update_connection(self, connection_id: str, update_data)
    async def delete_connection(self, connection_id: str) -> bool
    
    # Testing & Analysis
    async def test_connection(self, connection_id: str) -> ConnectionTestResult
    async def get_database_schema(self, connection_id: str) -> DatabaseSchemaResult
    async def discover_databases(self, connection_id: str)
    
    # Database-Specific Methods
    async def _get_mongodb_schema(self, connection: DatabaseConnection)
    async def _get_postgresql_schema(self, connection: DatabaseConnection)
    async def _get_mysql_schema(self, connection: DatabaseConnection)
```

### 4. **Model Layer** (`app/models/connection.py`)

**Responsibilities:**
- Define data structures
- MongoDB document mapping
- Serialization/deserialization
- Data validation

**Model Structure:**
```python
class DatabaseConnection:
    def __init__(self, connection_name, database_type, host, port, 
                 database_name, username, password, additional_notes=None):
        self._id = None
        self.connection_name = connection_name
        self.database_type = database_type
        # ... other fields
        
    def to_dict(self) -> Dict[str, Any]:
        # Convert to MongoDB document
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DatabaseConnection":
        # Create from MongoDB document
```

### 5. **Database Layer** (`app/db/session.py`)

**Responsibilities:**
- MongoDB connection management
- Connection pooling
- Health checks and monitoring
- Error handling

**Connection Management:**
```python
class DatabaseManager:
    def __init__(self):
        self.client: MongoClient = None
        self.db: Database = None
        self.connections_collection: Collection = None
        self._connect()
    
    def _connect(self):
        # Establish MongoDB connection with error handling
        
    def get_connections_collection(self) -> Collection:
        # Return connection collection with availability check
        
    def is_connected(self) -> bool:
        # Health check method
```

---

## 🔄 Data Flow Architecture

### 1. **Connection Creation Flow**

```
Client Request → Router Validation → Service Logic → Model Creation → Database Storage
     ↓              ↓                   ↓               ↓               ↓
JSON Payload → Pydantic Schema → Business Rules → MongoDB Doc → Collection Insert
```

**Detailed Steps:**
1. **Client** sends POST request with connection data
2. **Router** validates request using Pydantic schema
3. **Service** applies business logic and validation
4. **Model** converts to MongoDB document format
5. **Database** stores document and returns ID
6. **Response** returns created connection with metadata

### 2. **Schema Extraction Flow**

```
Client Request → Connection Lookup → Database Connection → Schema Analysis → Response
     ↓                ↓                     ↓                   ↓             ↓
GET /schema → Find Connection → Connect to Target DB → Analyze Structure → JSON Result
```

**MongoDB Schema Analysis:**
```python
# 1. Connect to Atlas cluster
client = MongoClient(atlas_uri)

# 2. Discover databases
available_dbs = client.list_database_names()

# 3. Auto-select database
target_db = smart_database_selection(available_dbs, specified_db)

# 4. Analyze collections
for collection in db.list_collection_names():
    # Sample documents
    samples = collection.aggregate([{"$sample": {"size": 20}}])
    
    # Analyze field types
    field_analysis = analyze_document_fields(samples)
    
    # Calculate statistics
    field_frequency = calculate_field_presence(samples)
```

### 3. **Error Handling Flow**

```
Error Occurrence → Service Handling → Router Catching → Response Formatting → Client
       ↓               ↓                 ↓                    ↓               ↓
Database Error → Try/Catch Block → HTTP Exception → JSON Error → Error Display
```

---

## 🗃️ Database Architecture

### Primary Database (MongoDB Atlas)
**Purpose**: Store connection metadata and configurations

**Collections:**
- `database_connections`: Store connection configurations

**Document Structure:**
```json
{
  "_id": ObjectId("..."),
  "connection_name": "string",
  "database_type": "string",
  "host": "string",
  "port": number,
  "database_name": "string",
  "username": "string",
  "password": "string",
  "additional_notes": "string",
  "created_at": ISODate("..."),
  "updated_at": ISODate("...")
}
```

### Target Databases (Analysis Targets)
**Purpose**: Databases being analyzed for schema extraction

**Supported Types:**
- **MongoDB Atlas**: Collections and document analysis
- **PostgreSQL**: Tables, views, and column analysis
- **MySQL**: Tables and column analysis

---

## 🔐 Security Architecture

### 1. **Input Validation**
```python
# Pydantic schema validation
class DatabaseConnectionCreate(BaseModel):
    connection_name: str = Field(..., min_length=1, max_length=100)
    database_type: str = Field(..., regex="^(MongoDB|PostgreSQL|MySQL)$")
    host: str = Field(..., min_length=1)
    port: int = Field(..., ge=1, le=65535)
    # ... other validations
```

### 2. **Connection Security**
- SSL support for PostgreSQL (Neon)
- SRV connections for MongoDB Atlas
- Connection timeouts to prevent hanging
- Error message sanitization

### 3. **Data Protection**
- Environment variable configuration
- No hardcoded credentials
- Secure connection string handling
- Input sanitization

---

## ⚡ Performance Architecture

### 1. **Async/Await Pattern**
```python
# Non-blocking operations throughout
async def get_database_schema(self, connection_id: str):
    # Async database operations
    doc = await self.collection.find_one({"_id": ObjectId(connection_id)})
    return await self._analyze_schema(doc)
```

### 2. **Connection Management**
- MongoDB connection pooling
- Configurable timeouts
- Connection reuse
- Health check monitoring

### 3. **Schema Analysis Optimization**
- Document sampling (max 20 docs per collection)
- Nested analysis depth limiting (3 levels)
- Smart database selection
- Efficient field type inference

### 4. **Memory Management**
- Streaming document analysis
- Limited sample sizes
- Connection cleanup
- Garbage collection friendly

---

## 🔧 Configuration Architecture

### 1. **Environment-Based Configuration**
```python
class Settings:
    # App Configuration
    APP_NAME: str = "PHA Database Connection Manager"
    VERSION: str = "1.0.0"
    
    # Database Configuration
    MONGODB_URL: str = os.getenv("MONGODB_URL")
    DATABASE_NAME: str = os.getenv("DATABASE_NAME", "pha_connections")
    
    # Server Configuration
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    
    # Performance Configuration
    DB_CONNECTION_TIMEOUT_MS: int = int(os.getenv("DB_CONNECTION_TIMEOUT_MS", "10000"))
```

### 2. **Dependency Injection**
```python
def get_database_manager() -> DatabaseManager:
    return db_manager

def get_connection_service(db_manager: DatabaseManager = Depends(get_database_manager)):
    return ConnectionService(db_manager)
```

---

## 📊 Monitoring Architecture

### 1. **Health Checks**
```python
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "database": db_manager.is_connected()
    }
```

### 2. **Logging Strategy**
- Structured logging with timestamps
- Error tracking and alerting
- Performance monitoring
- Debug information for development

### 3. **Metrics Collection** (Future Enhancement)
- Request/response times
- Database connection statistics
- Schema extraction performance
- Error rates and types

---

## 🚀 Scalability Architecture

### 1. **Horizontal Scaling**
- Stateless application design
- Load balancer compatibility
- Database connection pooling
- Session-independent operations

### 2. **Caching Strategy** (Future Enhancement)
```python
# Redis caching for schema results
@cache(expire=3600)  # Cache for 1 hour
async def get_database_schema(connection_id: str):
    # Expensive schema analysis
    pass
```

### 3. **Database Scaling**
- MongoDB Atlas auto-scaling
- Connection pool sizing
- Query optimization
- Index usage

---

## 🔄 Extension Architecture

### 1. **Adding New Database Types**
```python
# Extend service with new database type
async def _get_oracle_schema(self, connection: DatabaseConnection):
    # Oracle-specific schema extraction
    pass

# Register in main schema method
if db_type == "oracle":
    return await self._get_oracle_schema(connection)
```

### 2. **Plugin Architecture** (Future Enhancement)
- Database driver plugins
- Custom schema analyzers
- Authentication providers
- Export format plugins

---

## 📋 Testing Architecture

### 1. **Test Structure**
```
tests/
├── conftest.py              # Test configuration and fixtures
├── test_connections.py      # API endpoint tests
├── test_services.py         # Service layer tests
├── test_models.py          # Model layer tests
└── test_database.py        # Database layer tests
```

### 2. **Test Types**
- **Unit Tests**: Individual component testing
- **Integration Tests**: Database and service interaction
- **API Tests**: Full endpoint testing
- **Performance Tests**: Load and stress testing

---

**Last Updated**: September 2025  
**Architecture Version**: 1.0.0  
**Documentation Status**: Complete
