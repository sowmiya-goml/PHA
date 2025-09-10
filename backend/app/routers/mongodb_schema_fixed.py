"""MongoDB schema analysis and webhook management API routes."""

from fastapi import APIRouter, HTTPException, Depends, Request
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime
import hashlib
import json
import logging
from bson import ObjectId

from app.services.connection_service import ConnectionService
from app.db.session import get_database_manager, DatabaseManager


def convert_objectid_to_str(data):
    """Convert ObjectId objects to strings for JSON serialization."""
    if isinstance(data, ObjectId):
        return str(data)
    elif isinstance(data, dict):
        return {key: convert_objectid_to_str(value) for key, value in data.items()}
    elif isinstance(data, list):
        return [convert_objectid_to_str(item) for item in data]
    return data


router = APIRouter(
    prefix="/mongodb-schema",
    tags=["MongoDB Schema"],
    responses={404: {"description": "Not found"}}
)

logger = logging.getLogger(__name__)


# Pydantic models for MongoDB schema
class MongoField(BaseModel):
    """Schema for MongoDB field information."""
    name: str = Field(..., description="Field name")
    type: str = Field(..., description="Field data type")
    frequency: int = Field(..., description="Number of documents containing this field")
    percentage: float = Field(..., description="Percentage of documents containing this field")
    sample_values: List[Any] = Field(default=[], description="Sample values for this field")


class MongoCollection(BaseModel):
    """Schema for MongoDB collection information."""
    name: str = Field(..., description="Collection name")
    document_count: int = Field(..., description="Number of documents in collection")
    fields: Dict[str, MongoField] = Field(..., description="Fields found in the collection")
    indexes: List[Dict[str, Any]] = Field(default=[], description="Collection indexes")
    sample_documents: List[Dict[str, Any]] = Field(default=[], description="Sample documents")


class MongoSchemaResult(BaseModel):
    """Schema for MongoDB schema analysis result."""
    status: str = Field(..., description="Schema analysis status")
    message: str = Field(..., description="Status message")
    database_name: str = Field(..., description="Database name")
    collections: List[MongoCollection] = Field(..., description="Collections in the database")
    analysis_timestamp: datetime = Field(..., description="When the analysis was performed")
    schema_hash: str = Field(..., description="Hash of the current schema for change detection")


class WebhookConfig(BaseModel):
    """Schema for webhook configuration."""
    url: str = Field(..., description="Webhook URL to call on schema changes")
    secret: Optional[str] = Field(None, description="Secret for webhook authentication")
    events: List[str] = Field(default=["schema_change"], description="Events to trigger webhook")
    active: bool = Field(default=True, description="Whether webhook is active")


class WebhookConfigResponse(WebhookConfig):
    """Schema for webhook configuration response."""
    id: str = Field(..., description="Webhook configuration ID")
    connection_id: str = Field(..., description="Associated connection ID")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")


class SchemaChangeNotification(BaseModel):
    """Schema for schema change webhook notification."""
    event_type: str = Field(..., description="Type of event (schema_change, collection_added, etc.)")
    connection_id: str = Field(..., description="Database connection ID")
    database_name: str = Field(..., description="Database name")
    timestamp: datetime = Field(..., description="When the change occurred")
    changes: List[Dict[str, Any]] = Field(..., description="List of schema changes detected")
    old_schema_hash: Optional[str] = Field(None, description="Previous schema hash")
    new_schema_hash: str = Field(..., description="New schema hash")


class WebhookTestRequest(BaseModel):
    """Schema for webhook test request."""
    webhook_url: str = Field(..., description="Webhook URL to test")
    test_payload: Dict[str, Any] = Field(default_factory=dict, description="Test payload to send")


class DirectConnectionRequest(BaseModel):
    """Schema for direct MongoDB connection request."""
    host: str = Field(default="localhost", description="MongoDB host")
    port: int = Field(default=27017, description="MongoDB port")
    database_name: str = Field(..., description="Database name")
    username: Optional[str] = Field(None, description="Username")
    password: Optional[str] = Field(None, description="Password")
    sample_size: int = Field(default=10, description="Number of documents to sample")
    connection_string: Optional[str] = Field(None, description="Full MongoDB connection string (optional)")
    is_atlas: bool = Field(default=False, description="Whether this is a MongoDB Atlas connection")


def get_connection_service(db_manager: DatabaseManager = Depends(get_database_manager)) -> ConnectionService:
    """Dependency to get connection service."""
    return ConnectionService(db_manager)


@router.get("/test")
async def test_endpoint():
    """Test endpoint to verify the router is working."""
    return {"status": "success", "message": "MongoDB schema router is working"}


@router.post("/test-atlas-connection")
async def test_atlas_connection(request: dict):
    """Test Atlas connection with provided credentials."""
    try:
        from pymongo import MongoClient
        
        # Extract connection details
        host = request.get("host", "")
        username = request.get("username", "")
        password = request.get("password", "")
        database_name = request.get("database_name", "test")
        
        # Create Atlas connection string
        if username and password:
            connection_string = f"mongodb+srv://{username}:{password}@{host}/{database_name}?retryWrites=true&w=majority"
        else:
            connection_string = f"mongodb+srv://{host}/{database_name}?retryWrites=true&w=majority"
        
        logger.info(f"Testing Atlas connection to: {host}")
        
        try:
            client = MongoClient(
                connection_string,
                serverSelectionTimeoutMS=30000,
                connectTimeoutMS=30000,
                socketTimeoutMS=30000
            )
            
            # Test connection
            client.admin.command('ping')
            
            # Get database info
            db = client[database_name]
            collections = db.list_collection_names()
            
            client.close()
            
            return {
                "status": "success",
                "message": f"Successfully connected to Atlas",
                "database": database_name,
                "collections_count": len(collections),
                "collections": collections[:5]  # First 5 collections
            }
            
        except Exception as e:
            logger.error(f"Atlas connection failed: {str(e)}")
            return {
                "status": "error",
                "message": f"Failed to connect to Atlas: {str(e)}"
            }
            
    except Exception as e:
        logger.error(f"Error in Atlas test: {str(e)}")
        return {
            "status": "error",
            "message": f"Error: {str(e)}"
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


@router.get("/{connection_id}/analyze", response_model=MongoSchemaResult)
async def analyze_mongodb_schema(
    connection_id: str,
    sample_size: int = 100,
    service: ConnectionService = Depends(get_connection_service)
):
    """Analyze the schema of a MongoDB database using stored connection."""
    try:
        # Get connection details
        connection = await service.get_connection_by_id(connection_id)
        if not connection:
            raise HTTPException(status_code=404, detail="Connection not found")
        
        if connection.database_type.lower() != "mongodb":
            raise HTTPException(status_code=400, detail="Connection is not a MongoDB connection")
        
        # Use the direct analysis with connection details
        request_data = DirectConnectionRequest(
            host=connection.host,
            port=connection.port,
            database_name=connection.database_name,
            username=connection.username,
            password=connection.password,
            sample_size=sample_size
        )
        
        return await analyze_mongodb_direct(request_data)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error analyzing MongoDB schema: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to analyze schema: {str(e)}")


@router.post("/webhook/test")
async def test_webhook(webhook_test: WebhookTestRequest):
    """Test a webhook URL by sending a sample payload."""
    try:
        import httpx
        import re
        
        # Validate and fix URL
        webhook_url = webhook_test.webhook_url.strip()
        if not webhook_url.startswith(('http://', 'https://')):
            webhook_url = 'https://' + webhook_url
        
        # Basic URL validation
        url_pattern = re.compile(
            r'^https?://'  # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
            r'localhost|'  # localhost...
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
            r'(?::\d+)?'  # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        
        if not url_pattern.match(webhook_url):
            raise HTTPException(status_code=400, detail=f"Invalid webhook URL format: {webhook_url}")
        
        # Create a sample schema change notification
        test_payload = webhook_test.test_payload or {
            "event_type": "schema_change",
            "connection_id": "test_connection",
            "database_name": "test_db",
            "timestamp": datetime.utcnow().isoformat(),
            "changes": [
                {
                    "collection": "users",
                    "field": "email",
                    "change_type": "added",
                    "old_type": None,
                    "new_type": "string"
                }
            ],
            "old_schema_hash": "abc123",
            "new_schema_hash": "def456"
        }
        
        logger.info(f"Testing webhook URL: {webhook_url}")
        
        # Send test webhook with more specific error handling
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    webhook_url,
                    json=test_payload,
                    headers={"Content-Type": "application/json"}
                )
                
            logger.info(f"Webhook test sent to {webhook_url}, response: {response.status_code}")
            
            return {
                "status": "success",
                "message": "Webhook test completed successfully",
                "webhook_url": webhook_url,
                "response_status": response.status_code,
                "response_body": response.text[:500] if response.text else None,
                "test_payload": test_payload
            }
            
        except httpx.ConnectError as e:
            error_msg = f"Connection failed: Cannot reach {webhook_url}. Check if the URL is correct and accessible."
            logger.error(f"Webhook connection error: {str(e)}")
            return {
                "status": "error",
                "message": error_msg,
                "webhook_url": webhook_url,
                "error_type": "connection_error",
                "details": str(e)
            }
            
        except httpx.TimeoutException as e:
            error_msg = f"Request timeout: {webhook_url} took too long to respond."
            logger.error(f"Webhook timeout error: {str(e)}")
            return {
                "status": "error",
                "message": error_msg,
                "webhook_url": webhook_url,
                "error_type": "timeout_error"
            }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Webhook test failed: {str(e)}")
        return {
            "status": "error",
            "message": f"Webhook test failed: {str(e)}",
            "webhook_url": webhook_test.webhook_url,
            "error_type": "general_error"
        }


@router.post("/webhook/notify")
async def send_schema_change_notification(notification: SchemaChangeNotification, webhook_url: str):
    """Send a schema change notification to a webhook URL."""
    try:
        import httpx
        import re
        
        # Validate and fix URL
        webhook_url = webhook_url.strip()
        if not webhook_url.startswith(('http://', 'https://')):
            webhook_url = 'https://' + webhook_url
        
        # Basic URL validation
        url_pattern = re.compile(
            r'^https?://'  # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
            r'localhost|'  # localhost...
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
            r'(?::\d+)?'  # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        
        if not url_pattern.match(webhook_url):
            raise HTTPException(status_code=400, detail=f"Invalid webhook URL format: {webhook_url}")
        
        # Prepare the payload
        payload = notification.dict()
        payload["timestamp"] = payload["timestamp"].isoformat() if isinstance(payload["timestamp"], datetime) else payload["timestamp"]
        
        logger.info(f"Sending notification to webhook: {webhook_url}")
        
        # Send webhook notification with better error handling
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    webhook_url,
                    json=payload,
                    headers={"Content-Type": "application/json"}
                )
                
            logger.info(f"Schema change notification sent to {webhook_url}, response: {response.status_code}")
            
            return {
                "status": "success",
                "message": "Notification sent successfully",
                "webhook_url": webhook_url,
                "response_status": response.status_code,
                "notification_id": str(ObjectId())
            }
            
        except httpx.ConnectError as e:
            error_msg = f"Connection failed: Cannot reach {webhook_url}. Check if the URL is correct and accessible."
            logger.error(f"Webhook connection error: {str(e)}")
            return {
                "status": "error",
                "message": error_msg,
                "webhook_url": webhook_url,
                "error_type": "connection_error",
                "details": str(e)
            }
            
        except httpx.TimeoutException as e:
            error_msg = f"Request timeout: {webhook_url} took too long to respond."
            logger.error(f"Webhook timeout error: {str(e)}")
            return {
                "status": "error",
                "message": error_msg,
                "webhook_url": webhook_url,
                "error_type": "timeout_error"
            }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to send notification: {str(e)}")
        return {
            "status": "error",
            "message": f"Failed to send notification: {str(e)}",
            "webhook_url": webhook_url,
            "error_type": "general_error"
        }


@router.post("/schema/compare")
async def compare_schemas(
    request_data: DirectConnectionRequest,
    previous_schema_hash: Optional[str] = None
):
    """Compare current schema with a previous version and detect changes."""
    try:
        # Analyze current schema
        current_result = await analyze_mongodb_direct(request_data)
        
        # Handle both dict and Pydantic model responses
        if hasattr(current_result, 'dict'):
            # It's a Pydantic model
            schema_dict = current_result.dict()
        else:
            # It's already a dictionary
            schema_dict = current_result
        
        # Generate schema hash
        schema_content = json.dumps(schema_dict, sort_keys=True, default=str)
        current_hash = hashlib.sha256(schema_content.encode()).hexdigest()
        
        # If no previous hash provided, just return current schema with hash
        if not previous_schema_hash:
            return {
                "status": "success",
                "message": "Current schema analyzed",
                "schema_hash": current_hash,
                "schema": schema_dict,
                "changes_detected": False
            }
        
        # Compare hashes
        changes_detected = current_hash != previous_schema_hash
        
        result = {
            "status": "success",
            "message": "Schema comparison completed",
            "previous_hash": previous_schema_hash,
            "current_hash": current_hash,
            "changes_detected": changes_detected,
            "schema": schema_dict
        }
        
        if changes_detected:
            result["changes"] = [
                {
                    "type": "schema_modified",
                    "description": "Schema structure has changed",
                    "timestamp": datetime.utcnow().isoformat()
                }
            ]
            logger.info(f"Schema changes detected for database {request_data.database_name}")
        
        return result
        
    except Exception as e:
        logger.error(f"Schema comparison failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Schema comparison failed: {str(e)}")


@router.post("/webhook-receiver")
async def webhook_receiver(request: Request):
    """Webhook receiver endpoint for testing incoming webhook notifications."""
    try:
        content_type = request.headers.get("content-type", "")
        body = await request.body()
        
        if not body:
            return {"status": "received", "message": "Empty webhook received", "timestamp": datetime.utcnow()}
        
        if content_type.startswith("application/json"):
            payload = await request.json()
            logger.info(f"Webhook received: {payload}")
            
            # Process the webhook payload
            event_type = payload.get("event_type", "unknown")
            connection_id = payload.get("connection_id", "unknown")
            
            return {
                "status": "received", 
                "message": f"Webhook processed successfully for {event_type} on {connection_id}",
                "event_type": event_type,
                "connection_id": connection_id,
                "received_at": datetime.utcnow(),
                "payload": payload
            }
        else:
            body_text = body.decode('utf-8') if body else ""
            logger.info(f"Non-JSON webhook received: {body_text}")
            return {
                "status": "received", 
                "message": "Non-JSON webhook processed",
                "content_type": content_type,
                "body": body_text,
                "received_at": datetime.utcnow()
            }
        
    except Exception as e:
        logger.error(f"Webhook processing failed: {str(e)}")
        return {"status": "error", "message": f"Webhook processing failed: {str(e)}", "timestamp": datetime.utcnow()}
