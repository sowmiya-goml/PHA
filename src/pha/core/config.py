"""Core configuration settings for the Health Foundary PHA."""

import os
from dotenv import load_dotenv
from pymongo import MongoClient

# Load environment variables
load_dotenv()


class Settings:
    """Application settings configuration."""
    
    # App metadata
    APP_NAME: str = "Health Foundary PHA"
    VERSION: str = "2.0.0"
    DESCRIPTION: str = "AI-powered healthcare platform for secure healthcare data processing and analytics"
    
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
    
    # Database connection timeout (increased for MongoDB Atlas)
    DB_CONNECTION_TIMEOUT_MS: int = int(os.getenv("DB_CONNECTION_TIMEOUT_MS", "30000"))  # 30 seconds
    DB_SERVER_SELECTION_TIMEOUT_MS: int = int(os.getenv("DB_SERVER_SELECTION_TIMEOUT_MS", "30000"))  # 30 seconds
    
    class Config:
        case_sensitive = True


# Create a global settings instance
settings = Settings()

# Note: MongoDB connection is now handled in session.py with proper async startup
# This avoids blocking the application startup process
