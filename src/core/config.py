"""Core configuration settings for the Health Foundary PHA."""

import os
from pathlib import Path
from dotenv import load_dotenv

# Get the project root directory (go up from src/core/config.py to project root)
PROJECT_ROOT = Path(__file__).parent.parent.parent

# Try multiple .env file locations
env_paths = [
    PROJECT_ROOT / ".env",                    # Project root
    PROJECT_ROOT / "config" / ".env",         # Config folder
    Path.cwd() / ".env",                      # Current working directory
]

# Load environment variables from the first .env file found
env_loaded = False
for env_path in env_paths:
    if env_path.exists():
        load_dotenv(env_path)
        print(f"✅ Environment variables loaded from: {env_path}")
        env_loaded = True
        break

if not env_loaded:
    print(f"⚠️  No .env file found. Searched in:")
    for path in env_paths:
        print(f"   - {path}")
    print("Using environment variables from system/shell")


class Settings:
    """Application settings configuration."""
    
    # App metadata
    APP_NAME: str = "Health Foundary PHA"
    VERSION: str = "2.0.0"
    DESCRIPTION: str = "AI-powered healthcare platform for secure healthcare data processing and analytics"
    
    # MongoDB configuration - Load from environment
    MONGODB_URL: str = os.getenv("MONGODB_URL", "")
    DATABASE_NAME: str = os.getenv("DATABASE_NAME", "pha_connections")
    
    # AWS Configuration
    AWS_ACCESS_KEY_ID: str = os.getenv("AWS_ACCESS_KEY_ID", "")
    AWS_SECRET_ACCESS_KEY: str = os.getenv("AWS_SECRET_ACCESS_KEY", "")
    AWS_DEFAULT_REGION: str = os.getenv("AWS_DEFAULT_REGION", "us-east-1")
    AWS_REGION: str = os.getenv("AWS_REGION", os.getenv("AWS_DEFAULT_REGION", "us-east-1"))  # Fallback compatibility
    BEDROCK_MODEL_ID: str = os.getenv("BEDROCK_MODEL_ID", "anthropic.claude-3-5-sonnet-20241022-v2:0")
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
    
    def validate_mongodb_config(self) -> dict:
        """Validate MongoDB configuration."""
        return {
            "mongodb_url_present": bool(self.MONGODB_URL),
            "mongodb_url_length": len(self.MONGODB_URL) if self.MONGODB_URL else 0,
            "database_name": self.DATABASE_NAME,
            "connection_timeout_ms": self.DB_CONNECTION_TIMEOUT_MS,
            "server_selection_timeout_ms": self.DB_SERVER_SELECTION_TIMEOUT_MS
        }
    
    def validate_aws_credentials(self) -> dict:
        """Validate AWS credentials are properly loaded."""
        return {
            "aws_access_key_present": bool(self.AWS_ACCESS_KEY_ID),
            "aws_access_key_length": len(self.AWS_ACCESS_KEY_ID) if self.AWS_ACCESS_KEY_ID else 0,
            "aws_secret_key_present": bool(self.AWS_SECRET_ACCESS_KEY),
            "aws_secret_key_length": len(self.AWS_SECRET_ACCESS_KEY) if self.AWS_SECRET_ACCESS_KEY else 0,
            "aws_region": self.AWS_DEFAULT_REGION,
            "bedrock_model_id": self.BEDROCK_MODEL_ID
        }
    
    def get_config_summary(self) -> dict:
        """Get a summary of all configuration settings (safe for logging)."""
        return {
            "app": {
                "name": self.APP_NAME,
                "version": self.VERSION,
                "host": self.HOST,
                "port": self.PORT
            },
            "mongodb": self.validate_mongodb_config(),
            "aws": self.validate_aws_credentials(),
            "env_file_loaded": env_loaded,
            "env_paths_searched": [str(p) for p in env_paths]
        }
    
    class Config:
        case_sensitive = True


# Create a global settings instance
settings = Settings()

# Print configuration summary on import (for debugging)
if __name__ == "__main__" or os.getenv("DEBUG_CONFIG"):
    import json
    print("=== Configuration Summary ===")
    print(json.dumps(settings.get_config_summary(), indent=2))