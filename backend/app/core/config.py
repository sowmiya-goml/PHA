"""Core configuration settings for the AWS Health PHI Report Generator."""

import os
from dotenv import load_dotenv
from pymongo import MongoClient

# Load environment variables
load_dotenv()


class Settings:
    """Application settings configuration."""
    
    # App metadata
    APP_NAME: str = "AWS Health PHI Report Generator"
    VERSION: str = "2.0.0"
    DESCRIPTION: str = "AI-powered healthcare report generation system with secure PHI processing"
    
    # MongoDB configuration  
    MONGODB_URL: str = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
    DATABASE_NAME: str = os.getenv("DATABASE_NAME", "pha_metadata")
    
    # AWS Configuration
    AWS_REGION: str = os.getenv("AWS_REGION", "us-east-1")
    BEDROCK_MODEL_ID: str = os.getenv("BEDROCK_MODEL_ID", "anthropic.claude-3-sonnet-20240229-v1:0")
    S3_REPORT_BUCKET: str = os.getenv("S3_REPORT_BUCKET", "pha-health-reports")
    
    # Server configuration
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    ELASTIC_IP: str = os.getenv("ELASTIC_IP", "")  # Fixed IP for client whitelisting
    
    # Security settings
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-here")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    ENCRYPTION_KEY: str = os.getenv("ENCRYPTION_KEY", "")  # For database credential encryption
    
    # Performance settings
    QUERY_TIMEOUT_SECONDS: int = int(os.getenv("QUERY_TIMEOUT_SECONDS", "30"))
    MAX_ROWS_PER_QUERY: int = int(os.getenv("MAX_ROWS_PER_QUERY", "10000"))
    REPORT_EXPIRY_MINUTES: int = int(os.getenv("REPORT_EXPIRY_MINUTES", "5"))
    
    # Database connection timeout
    DB_CONNECTION_TIMEOUT_MS: int = int(os.getenv("DB_CONNECTION_TIMEOUT_MS", "5000"))
    
    class Config:
        case_sensitive = True


# Create a global settings instance
settings = Settings()

# Initialize MongoDB connection with better error handling
try:
    client = MongoClient(
        settings.MONGODB_URL,
        serverSelectionTimeoutMS=settings.DB_CONNECTION_TIMEOUT_MS
    )
    # Test the connection
    client.admin.command('ping')
    db = client[settings.DATABASE_NAME]
    print(f"✅ Connected to MongoDB at {settings.MONGODB_URL}")
except Exception as e:
    print(f"⚠️ MongoDB connection failed: {e}")
    print("🔄 Using in-memory storage for testing")
    # Create a dummy db object for testing
    client = None
    db = None

# Collections for the new AWS Health PHI Report Generator
connections_collection = db["database_connections"] if db is not None else None
schemas_collection = db["database_schemas"] if db is not None else None
audit_logs_collection = db["audit_logs"] if db is not None else None
