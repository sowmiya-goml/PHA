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


@router.post("/{connection_id}/webhooks", response_model=WebhookConfigResponse)
async def create_webhook(
    connection_id: str,
    webhook_config: WebhookConfig,
    service: ConnectionService = Depends(get_connection_service)
):
    """Create a webhook configuration for schema change notifications."""
    try:
        # Verify connection exists
        connection = await service.get_connection_by_id(connection_id)
        if not connection:
            raise HTTPException(status_code=404, detail="Connection not found")
        
        if connection.database_type.lower() != "mongodb":
            raise HTTPException(status_code=400, detail="Connection is not a MongoDB connection")
        
        # For now, just return a mock response
        webhook_id = str(ObjectId())
        webhook_response = WebhookConfigResponse(
            id=webhook_id,
            connection_id=connection_id,
            url=webhook_config.url,
            secret=webhook_config.secret,
            events=webhook_config.events,
            active=webhook_config.active,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        logger.info(f"Created webhook {webhook_id} for connection {connection_id}")
        return webhook_response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating webhook: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to create webhook: {str(e)}")


@router.get("/{connection_id}/webhooks", response_model=List[WebhookConfigResponse])
async def list_webhooks(
    connection_id: str,
    service: ConnectionService = Depends(get_connection_service)
):
    """List all webhook configurations for a connection."""
    try:
        # Verify connection exists
        connection = await service.get_connection_by_id(connection_id)
        if not connection:
            raise HTTPException(status_code=404, detail="Connection not found")
        
        # For now, return empty list
        return []
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error listing webhooks: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to list webhooks: {str(e)}")


@router.post("/webhook-receiver")
async def webhook_receiver(request: Request):
    """Sample webhook receiver endpoint for testing."""
    try:
        payload = await request.json()
        logger.info(f"Received webhook: {payload}")
        
        return {"status": "received", "message": "Webhook processed successfully"}
        
    except Exception as e:
        logger.error(f"Error processing webhook: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to process webhook")
