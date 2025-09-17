"""Core configuration settings for the Health Foundary PHA."""

import os
from pathlib import Path
from dotenv import load_dotenv
from pymongo import MongoClient

# Load environment variables from config directory
config_dir = Path(__file__).parent.parent.parent.parent / "config"
env_file = config_dir / ".env"

# Ensure the .env file exists
if not env_file.exists():
    print(f"Warning: .env file not found at {env_file}")
else:
    print(f"Loading environment variables from: {env_file}")

load_dotenv(env_file)


class Settings:
    """Application settings configuration."""
    
    # App metadata
    APP_NAME: str = "Health Foundary PHA"
    VERSION: str = "2.0.0"
    DESCRIPTION: str = "AI-powered healthcare platform for secure healthcare data processing and analytics"
    
    # MongoDB configuration - Direct Atlas connection
    MONGODB_URL: str = "mongodb+srv://22cs027_db_user:SathyaPainter@pha.o1mtvpd.mongodb.net/?retryWrites=true&w=majority&appName=PHA"
    DATABASE_NAME: str = os.getenv("DATABASE_NAME", "pha_connections")
    
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
    
    # Database connection timeout (working settings for MongoDB Atlas)
    DB_CONNECTION_TIMEOUT_MS: int = int(os.getenv("DB_CONNECTION_TIMEOUT_MS", "20000"))  # 20 seconds
    DB_SERVER_SELECTION_TIMEOUT_MS: int = int(os.getenv("DB_SERVER_SELECTION_TIMEOUT_MS", "10000"))  # 10 seconds
    
    # Store config directory for reference
    config_dir = config_dir
    
    def validate_aws_credentials(self) -> dict:
        """Validate AWS credentials are properly loaded."""
        aws_access_key = os.getenv("AWS_ACCESS_KEY_ID")
        aws_secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")
        aws_region = os.getenv("AWS_DEFAULT_REGION")
        
        return {
            "aws_access_key_present": bool(aws_access_key),
            "aws_access_key_length": len(aws_access_key) if aws_access_key else 0,
            "aws_secret_key_present": bool(aws_secret_key),
            "aws_secret_key_length": len(aws_secret_key) if aws_secret_key else 0,
            "aws_region": aws_region or "not_set",
            "config_file_loaded": env_file.exists()
        }
    
    class Config:
        case_sensitive = True


# Create a global settings instance
settings = Settings()

# Note: MongoDB connection is now handled in session.py with proper async startup
# This avoids blocking the application startup process
