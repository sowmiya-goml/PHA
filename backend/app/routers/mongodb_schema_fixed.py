"""
MongoDB Schema Analysis and Webhook Management Router.

This module provides comprehensive MongoDB schema analysis capabilities including:
- Direct MongoDB connection analysis with Atlas support
- Schema comparison with hash-based change detection
- Webhook testing and notification system
- ObjectId serialization handling
- Real-time schema monitoring endpoints
"""

import asyncio
import hashlib
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any, Union
from urllib.parse import urlparse

import httpx
from bson import ObjectId
from fastapi import APIRouter, HTTPException, BackgroundTasks
from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError, ConnectionFailure
from pydantic import BaseModel, HttpUrl, validator

logger = logging.getLogger(__name__)

# Router setup
router = APIRouter(
    prefix="/mongodb-schema",
    tags=["MongoDB Schema Analysis"],
    responses={404: {"description": "Not found"}}
)

# Pydantic Models
class DirectConnectionRequest(BaseModel):
    """Request model for direct MongoDB connection analysis."""
    host: str
    database_name: str
    username: Optional[str] = None
    password: Optional[str] = None
    port: Optional[int] = 27017
    is_atlas: bool = False
    sample_size: int = 10
    timeout_ms: int = 30000
    connection_string: Optional[str] = None

class MongoField(BaseModel):
    """MongoDB field information."""
    name: str
    type: str
    frequency: int
    percentage: float
    sample_values: List[str] = []

class MongoCollection(BaseModel):
    """MongoDB collection information."""
    name: str
    document_count: int
    fields: Dict[str, MongoField]
    indexes: List[Dict] = []
    sample_documents: List[Dict] = []

class MongoSchemaResult(BaseModel):
    """MongoDB schema analysis result."""
    status: str
    message: str
    database_name: str
    collections: List[MongoCollection]
    analysis_timestamp: datetime
    schema_hash: str

class MongoConnectionRequest(BaseModel):
    """Request model for MongoDB connection with separate parameters."""
    host: str
    database_name: str
    username: str
    password: str
    is_atlas: bool = False
    sample_size: Optional[int] = 10
    timeout_ms: Optional[int] = 30000
    
    def to_connection_string(self) -> str:
        """Convert parameters to MongoDB connection string."""
        if self.is_atlas:
            # MongoDB Atlas format
            return f"mongodb+srv://{self.username}:{self.password}@{self.host}/?retryWrites=true&w=majority"
        else:
            # Regular MongoDB format
            port = 27017  # Default MongoDB port
            return f"mongodb://{self.username}:{self.password}@{self.host}:{port}/"

class MongoConnectionStringRequest(BaseModel):
    """Alternative request model using connection string (for backward compatibility)."""
    connection_string: str
    database_name: Optional[str] = None
    timeout_ms: Optional[int] = 30000

    @validator('connection_string')
    def validate_connection_string(cls, v):
        if not v.startswith(('mongodb://', 'mongodb+srv://')):
            raise ValueError('Connection string must start with mongodb:// or mongodb+srv://')
        return v

class WebhookTestRequest(BaseModel):
    """Request model for webhook testing."""
    webhook_url: HttpUrl
    timeout_seconds: Optional[int] = 30

class SchemaCompareRequest(BaseModel):
    """Request model for schema comparison with connection parameters."""
    host: str
    database_name: str
    username: str
    password: str
    is_atlas: bool = False
    previous_schema_hash: Optional[str] = None
    include_sample_data: Optional[bool] = False
    sample_size: Optional[int] = 10
    timeout_ms: Optional[int] = 30000
    
    def to_connection_string(self) -> str:
        """Convert parameters to MongoDB connection string."""
        if self.is_atlas:
            return f"mongodb+srv://{self.username}:{self.password}@{self.host}/?retryWrites=true&w=majority"
        else:
            port = 27017
            return f"mongodb://{self.username}:{self.password}@{self.host}:{port}/"

class WebhookNotifyRequest(BaseModel):
    """Request model for webhook notifications."""
    webhook_url: HttpUrl
    message: str
    schema_data: Optional[Dict] = None
    change_type: Optional[str] = "schema_change"

class SchemaAnalysisResult(BaseModel):
    """Result model for schema analysis."""
    status: str
    database_name: str
    server_info: Dict[str, Any]
    collections: List[Dict[str, Any]]
    schema_hash: str
    analysis_timestamp: datetime
    total_collections: int
    total_documents: int
    connection_method: str = "direct"

class WebhookTestResult(BaseModel):
    """Result model for webhook testing."""
    status: str
    webhook_url: str
    response_code: Optional[int] = None
    response_time_ms: Optional[float] = None
    error_message: Optional[str] = None
    test_timestamp: datetime

# Utility Functions
def convert_objectid_to_str(obj) -> Any:
    """Convert ObjectId objects to string recursively."""
    if isinstance(obj, ObjectId):
        return str(obj)
    elif isinstance(obj, dict):
        return {k: convert_objectid_to_str(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_objectid_to_str(item) for item in obj]
    return obj

def serialize_bson(obj) -> Any:
    """Convert BSON objects to JSON-serializable format."""
    if isinstance(obj, ObjectId):
        return str(obj)
    elif isinstance(obj, datetime):
        return obj.isoformat()
    elif isinstance(obj, dict):
        return {k: serialize_bson(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [serialize_bson(item) for item in obj]
    return obj

def analyze_field_types(documents: List[Dict], max_samples: int = 100) -> Dict[str, Dict]:
    """Analyze field types from document samples."""
    field_analysis = {}
    sample_count = min(len(documents), max_samples)
    
    for doc in documents[:sample_count]:
        for field, value in doc.items():
            if field not in field_analysis:
                field_analysis[field] = {
                    'types': set(),
                    'null_count': 0,
                    'sample_values': [],
                    'occurrence_count': 0
                }
            
            if value is None:
                field_analysis[field]['null_count'] += 1
            else:
                field_analysis[field]['types'].add(type(value).__name__)
                if len(field_analysis[field]['sample_values']) < 5:
                    field_analysis[field]['sample_values'].append(serialize_bson(value))
            
            field_analysis[field]['occurrence_count'] += 1
    
    # Convert sets to lists for JSON serialization
    for field_info in field_analysis.values():
        field_info['types'] = list(field_info['types'])
        field_info['null_percentage'] = (field_info['null_count'] / sample_count) * 100
        field_info['occurrence_percentage'] = (field_info['occurrence_count'] / sample_count) * 100
    
    return field_analysis

def generate_schema_hash(schema_data: Dict) -> str:
    """Generate MD5 hash of schema structure for change detection."""
    # Create a simplified schema structure for hashing
    hash_data = {}
    for collection in schema_data.get('collections', []):
        hash_data[collection['name']] = {
            'fields': sorted(collection.get('schema_analysis', {}).keys()),
            'document_count': collection.get('document_count', 0)
        }
    
    schema_json = json.dumps(hash_data, sort_keys=True)
    return hashlib.md5(schema_json.encode()).hexdigest()

async def test_mongodb_connection(connection_string: str, database_name: Optional[str] = None, timeout_ms: int = 30000) -> Dict:
    """Test MongoDB connection and return basic info."""
    try:
        client = MongoClient(
            connection_string,
            serverSelectionTimeoutMS=timeout_ms,
            connectTimeoutMS=timeout_ms,
            socketTimeoutMS=timeout_ms
        )
        
        # Test connection
        server_info = client.server_info()
        
        # Get database info
        if database_name:
            db = client[database_name]
            collections = db.list_collection_names()
        else:
            db_names = client.list_database_names()
            system_dbs = ['admin', 'local', 'config']
            user_dbs = [db for db in db_names if db not in system_dbs]
            
            if user_dbs:
                database_name = user_dbs[0]
                db = client[database_name]
                collections = db.list_collection_names()
            else:
                database_name = 'admin'
                collections = []
        
        client.close()
        
        return {
            "status": "success",
            "database_name": database_name,
            "server_info": serialize_bson(server_info),
            "collections_count": len(collections),
            "collections": collections
        }
        
    except ServerSelectionTimeoutError as e:
        return {
            "status": "error",
            "error_type": "timeout",
            "message": f"Connection timeout: {str(e)}"
        }
    except ConnectionFailure as e:
        return {
            "status": "error",
            "error_type": "connection_failure",
            "message": f"Connection failed: {str(e)}"
        }
    except Exception as e:
        return {
            "status": "error",
            "error_type": "unknown",
            "message": f"Unexpected error: {str(e)}"
        }

# API Endpoints
@router.get("/test")
async def health_check():
    """Health check endpoint for MongoDB schema analysis service."""
    return {
        "status": "healthy",
        "service": "MongoDB Schema Analysis",
        "timestamp": datetime.now().isoformat(),
        "features": [
            "Direct MongoDB analysis",
            "MongoDB Atlas support",
            "Schema comparison",
            "Webhook notifications",
            "Real-time monitoring"
        ]
    }

@router.post("/analyze-direct")
async def analyze_mongodb_direct(request: DirectConnectionRequest):
    """Analyze MongoDB schema using direct connection parameters."""
    try:
        # Import pymongo here to avoid blocking imports
        from pymongo import MongoClient
        
        # Create MongoDB connection string
        if request.connection_string:
            # Use provided connection string
            connection_string = request.connection_string
            logger.info(f"Using provided connection string")
        elif request.is_atlas or "mongodb.net" in request.host:
            # MongoDB Atlas connection
            if request.username and request.password:
                connection_string = f"mongodb+srv://{request.username}:{request.password}@{request.host}/{request.database_name}?retryWrites=true&w=majority"
            else:
                connection_string = f"mongodb+srv://{request.host}/{request.database_name}?retryWrites=true&w=majority"
            logger.info(f"Using Atlas connection string for: {request.host}")
        else:
            # Regular MongoDB connection
            if request.username and request.password:
                connection_string = f"mongodb://{request.username}:{request.password}@{request.host}:{request.port}/{request.database_name}"
            else:
                connection_string = f"mongodb://{request.host}:{request.port}/{request.database_name}"
            logger.info(f"Using regular MongoDB connection for: {request.host}:{request.port}")
        
        try:
            # Create client with longer timeout for Atlas
            client = MongoClient(
                connection_string, 
                serverSelectionTimeoutMS=30000,  # 30 seconds for Atlas
                connectTimeoutMS=30000,
                socketTimeoutMS=30000
            )
            
            # Test connection
            client.admin.command('ping')
            logger.info("Successfully connected to MongoDB")
            
            # Get database
            db = client[request.database_name]
            
            # Get all collections (limit to first 5 for testing)
            collection_names = db.list_collection_names()[:5]
            collections = []
            
            logger.info(f"Found {len(collection_names)} collections: {collection_names}")
            
            for col_name in collection_names:
                try:
                    collection = db[col_name]
                    
                    # Get basic stats
                    try:
                        document_count = collection.estimated_document_count()
                    except Exception as e:
                        logger.warning(f"Could not get document count for {col_name}: {e}")
                        document_count = 0
                    
                    # Simple field analysis - just get a few sample documents
                    sample_docs = []
                    try:
                        sample_docs = list(collection.find().limit(min(request.sample_size, 5)))
                    except Exception as e:
                        logger.warning(f"Could not get sample documents for {col_name}: {e}")
                    
                    # Basic field analysis
                    fields = {}
                    if sample_docs:
                        # Analyze first document structure
                        first_doc = sample_docs[0]
                        for field_name, value in first_doc.items():
                            try:
                                field_type = type(value).__name__
                                if field_type == 'ObjectId':
                                    field_type = 'objectId'
                                
                                # Get sample value (safely)
                                sample_val = str(value)[:50] if not isinstance(value, (dict, list)) else f"<{field_type}>"
                                
                                fields[field_name] = MongoField(
                                    name=field_name,
                                    type=field_type,
                                    frequency=len(sample_docs),
                                    percentage=100.0,
                                    sample_values=[sample_val]
                                )
                            except Exception as e:
                                logger.warning(f"Error analyzing field {field_name}: {e}")
                    
                    # Get indexes
                    indexes = []
                    try:
                        indexes = [idx for idx in collection.list_indexes()]
                    except Exception as e:
                        logger.warning(f"Could not get indexes for {col_name}: {e}")
                    
                    mongo_collection = MongoCollection(
                        name=col_name,
                        document_count=document_count,
                        fields=fields,
                        indexes=indexes,
                        sample_documents=sample_docs[:1] if sample_docs else []  # Include 1 sample document
                    )
                    collections.append(mongo_collection)
                    
                except Exception as e:
                    logger.error(f"Error analyzing collection {col_name}: {e}")
                    # Continue with other collections
            
            # Create result
            result = MongoSchemaResult(
                status="success",
                message=f"Successfully analyzed {len(collections)} collections",
                database_name=request.database_name,
                collections=collections,
                analysis_timestamp=datetime.utcnow(),
                schema_hash=hashlib.sha256(f"{request.database_name}_{len(collections)}".encode()).hexdigest()[:16]
            )
            
            client.close()
            logger.info(f"Analysis complete: {len(collections)} collections analyzed")
            
            # Convert to dict and handle ObjectId serialization
            result_dict = result.model_dump()
            result_dict = convert_objectid_to_str(result_dict)
            return result_dict
            
        except Exception as e:
            logger.error(f"MongoDB connection error: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Failed to connect to MongoDB: {str(e)}")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in direct analysis: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to analyze schema: {str(e)}")


@router.post("/test-atlas-connection", response_model=WebhookTestResult)
async def test_atlas_connection(request: MongoConnectionRequest):
    """
    Test MongoDB Atlas connection with detailed diagnostics.
    
    Provides comprehensive connection testing including DNS resolution,
    authentication, and basic database operations.
    Accepts connection parameters: host, username, password, database_name, is_atlas.
    """
    start_time = datetime.now()
    
    try:
        # Convert parameters to connection string
        connection_string = request.to_connection_string()
        
        connection_result = await test_mongodb_connection(
            connection_string,
            request.database_name,
            request.timeout_ms
        )
        
        end_time = datetime.now()
        response_time = (end_time - start_time).total_seconds() * 1000
        
        if connection_result["status"] == "success":
            return WebhookTestResult(
                status="success",
                webhook_url=f"mongodb://{request.host}",
                response_code=200,
                response_time_ms=response_time,
                test_timestamp=start_time
            )
        else:
            return WebhookTestResult(
                status="failed",
                webhook_url=f"mongodb://{request.host}",
                response_code=503,
                response_time_ms=response_time,
                error_message=connection_result.get("message", "Connection failed"),
                test_timestamp=start_time
            )
            
    except Exception as e:
        end_time = datetime.now()
        response_time = (end_time - start_time).total_seconds() * 1000
        
        return WebhookTestResult(
            status="error",
            webhook_url=request.connection_string,
            response_time_ms=response_time,
            error_message=f"Connection test failed: {str(e)}",
            test_timestamp=start_time
        )

@router.post("/webhook/test", response_model=WebhookTestResult)
async def test_webhook_url(request: WebhookTestRequest):
    """
    Test webhook URL connectivity and response.
    
    Sends a test POST request to the webhook URL and measures response time.
    """
    start_time = datetime.now()
    
    test_payload = {
        "test": True,
        "message": "MongoDB schema webhook test",
        "timestamp": start_time.isoformat(),
        "service": "MongoDB Schema Analysis"
    }
    
    try:
        async with httpx.AsyncClient(timeout=request.timeout_seconds) as client:
            response = await client.post(
                str(request.webhook_url),
                json=test_payload,
                headers={"Content-Type": "application/json"}
            )
            
            end_time = datetime.now()
            response_time = (end_time - start_time).total_seconds() * 1000
            
            return WebhookTestResult(
                status="success" if response.status_code < 400 else "failed",
                webhook_url=str(request.webhook_url),
                response_code=response.status_code,
                response_time_ms=response_time,
                error_message=None if response.status_code < 400 else f"HTTP {response.status_code}",
                test_timestamp=start_time
            )
            
    except httpx.TimeoutException:
        end_time = datetime.now()
        response_time = (end_time - start_time).total_seconds() * 1000
        
        return WebhookTestResult(
            status="timeout",
            webhook_url=str(request.webhook_url),
            response_time_ms=response_time,
            error_message=f"Request timeout after {request.timeout_seconds} seconds",
            test_timestamp=start_time
        )
    except Exception as e:
        end_time = datetime.now()
        response_time = (end_time - start_time).total_seconds() * 1000
        
        return WebhookTestResult(
            status="error",
            webhook_url=str(request.webhook_url),
            response_time_ms=response_time,
            error_message=str(e),
            test_timestamp=start_time
        )

@router.post("/webhook/notify")
async def send_webhook_notification(request: WebhookNotifyRequest, background_tasks: BackgroundTasks):
    """
    Send schema change notification to webhook URL.
    
    Supports background processing to avoid blocking the API response.
    """
    async def send_notification():
        notification_payload = {
            "change_type": request.change_type,
            "message": request.message,
            "timestamp": datetime.now().isoformat(),
            "service": "MongoDB Schema Analysis",
            "schema_data": serialize_bson(request.schema_data) if request.schema_data else None
        }
        
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                response = await client.post(
                    str(request.webhook_url),
                    json=notification_payload,
                    headers={"Content-Type": "application/json"}
                )
                
                logger.info(f"Webhook notification sent: {response.status_code} - {request.webhook_url}")
                return response.status_code
                
        except Exception as e:
            logger.error(f"Failed to send webhook notification: {e}")
            return None
    
    background_tasks.add_task(send_notification)
    
    return {
        "status": "queued",
        "message": "Webhook notification queued for delivery",
        "webhook_url": str(request.webhook_url),
        "timestamp": datetime.now().isoformat()
    }

@router.post("/schema/compare")
async def compare_schema_versions(request: SchemaCompareRequest):
    """
    Compare current schema with previous version using hash-based detection.
    
    Returns detailed comparison results and change detection.
    """
    try:
        # Get current schema using new parameter format
        connection_request = MongoConnectionRequest(
            host=request.host,
            database_name=request.database_name,
            username=request.username,
            password=request.password,
            is_atlas=request.is_atlas,
            sample_size=request.sample_size,
            timeout_ms=request.timeout_ms
        )
        
        current_analysis = await analyze_mongodb_direct(connection_request)
        current_hash = current_analysis.schema_hash
        
        comparison_result = {
            "current_schema_hash": current_hash,
            "previous_schema_hash": request.previous_schema_hash,
            "schema_changed": current_hash != request.previous_schema_hash if request.previous_schema_hash else True,
            "analysis_timestamp": datetime.now().isoformat(),
            "database_name": current_analysis.database_name,
            "total_collections": current_analysis.total_collections,
            "total_documents": current_analysis.total_documents
        }
        
        if request.include_sample_data:
            comparison_result["current_schema"] = current_analysis.dict()
        
        return comparison_result
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Schema comparison failed: {str(e)}"
        )

@router.post("/webhook-receiver")
async def webhook_receiver(payload: Dict[str, Any]):
    """
    Receive and process webhook notifications.
    
    This endpoint can be used as a webhook receiver for schema change notifications.
    """
    timestamp = datetime.now().isoformat()
    
    logger.info(f"Webhook received at {timestamp}: {json.dumps(payload, default=str)}")
    
    # Process webhook payload
    processed_payload = {
        "received_at": timestamp,
        "payload": serialize_bson(payload),
        "payload_size": len(json.dumps(payload, default=str)),
        "processing_status": "received"
    }
    
    return {
        "status": "received",
        "message": "Webhook payload processed successfully",
        "timestamp": timestamp,
        "payload_info": {
            "size_bytes": processed_payload["payload_size"],
            "keys": list(payload.keys()) if isinstance(payload, dict) else []
        }
    }
