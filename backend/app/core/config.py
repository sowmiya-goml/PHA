"""Core configuration settings for the PHA Database Connection Manager."""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Settings:
    """Application settings configuration."""
    
    # App metadata
    APP_NAME: str = "PHA Database Connection Manager"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "API for managing database connections"
    
    # MongoDB configuration
    MONGODB_URL: str = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
    DATABASE_NAME: str = os.getenv("DATABASE_NAME", "pha_connections")
    
    # Server configuration
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    
    # Security settings
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-here")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    
    # Database connection timeout
    DB_CONNECTION_TIMEOUT_MS: int = int(os.getenv("DB_CONNECTION_TIMEOUT_MS", "5000"))
    
    class Config:
        case_sensitive = True


# Create a global settings instance
settings = Settings()
