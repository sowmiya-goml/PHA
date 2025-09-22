"""Database connection and session management."""

import asyncio
from pymongo import MongoClient
from pymongo.database import Database
from pymongo.collection import Collection
from core.config import settings
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class DatabaseManager:
    """MongoDB database connection manager with async support."""
    
    def __init__(self):
        self.client: Optional[MongoClient] = None
        self.db: Optional[Database] = None
        self.connections_collection: Optional[Collection] = None
        self._connection_retries = 0
        self._max_retries = 3
        
    async def connect(self):
        """Establish connection to MongoDB with retry logic."""
        # Validate connection string format
        if not settings.MONGODB_URL.startswith("mongodb+srv://"):
            logger.error("❌ Invalid MongoDB connection string format. Expected mongodb+srv:// format")
            return False
            
        logger.info(f"🔗 Connecting to MongoDB Atlas cluster: {settings.MONGODB_URL.split('@')[1].split('?')[0]}")
        logger.debug(f"🔍 Full connection string: {settings.MONGODB_URL[:50]}...")
        
        for attempt in range(self._max_retries):
            try:
                logger.info(f"Attempting to connect to MongoDB (attempt {attempt + 1}/{self._max_retries})")
                
                self.client = MongoClient(
                    settings.MONGODB_URL,
                    serverSelectionTimeoutMS=settings.DB_SERVER_SELECTION_TIMEOUT_MS,
                    connectTimeoutMS=settings.DB_CONNECTION_TIMEOUT_MS,
                    socketTimeoutMS=settings.DB_CONNECTION_TIMEOUT_MS,
                    retryWrites=True,
                    retryReads=True,
                    maxPoolSize=50,
                    minPoolSize=5
                )
                
                # Test connection with timeout
                self.client.admin.command('ping')
                
                self.db = self.client[settings.DATABASE_NAME]
                self.connections_collection = self.db.database_connections
                
                logger.info(f"✅ Connected to MongoDB at {settings.MONGODB_URL}")
                self._connection_retries = 0
                return True
                
            except Exception as e:
                error_msg = str(e)
                if "DNS" in error_msg or "resolution" in error_msg:
                    logger.warning(f"⚠️  DNS resolution failed on attempt {attempt + 1}: Network/DNS issue")
                elif "timeout" in error_msg.lower():
                    logger.warning(f"⚠️  Connection timeout on attempt {attempt + 1}: MongoDB Atlas may be slow")
                else:
                    logger.warning(f"⚠️  MongoDB connection attempt {attempt + 1} failed: {error_msg}")
                
                self._connection_retries += 1
                
                if attempt < self._max_retries - 1:
                    wait_time = 1 + attempt  # Linear backoff: 1s, 2s, 3s (faster)
                    logger.info(f"Retrying in {wait_time} seconds...")
                    await asyncio.sleep(wait_time)
                else:
                    logger.error("❌ All MongoDB connection attempts failed")
                    logger.error("💡 Possible solutions:")
                    logger.error("   - Check your internet connection")
                    logger.error("   - Verify MongoDB Atlas cluster is running")
                    logger.error("   - Check firewall/proxy settings")
                    logger.warning("🚀 Starting server without database connection...")
                    self.client = None
                    self.db = None
                    self.connections_collection = None
                    return False
        return False
                
    def _connect_sync(self):
        """Synchronous connection method for backward compatibility."""
        try:
            self.client = MongoClient(
                settings.MONGODB_URL,
                serverSelectionTimeoutMS=settings.DB_SERVER_SELECTION_TIMEOUT_MS,
                connectTimeoutMS=settings.DB_CONNECTION_TIMEOUT_MS
            )
            self.db = self.client[settings.DATABASE_NAME]
            self.connections_collection = self.db.database_connections
            
            # Test connection
            self.client.admin.command('ping')
            logger.info("✅ Connected to MongoDB successfully")
            
        except Exception as e:
            logger.error(f"⚠️  MongoDB connection failed: {e}")
            logger.warning("Starting without database connection...")
            self.client = None
            self.db = None
            self.connections_collection = None
    
    def get_connections_collection(self) -> Collection:
        """Get the database connections collection."""
        if self.connections_collection is None:
            raise RuntimeError("Database not available")
        return self.connections_collection
    
    def get_database(self) -> Database:
        """Get the database instance."""
        if self.db is None:
            raise RuntimeError("Database not available")
        return self.db
    
    def is_connected(self) -> bool:
        """Check if database is connected."""
        return self.connections_collection is not None
    
    def close(self):
        """Close database connection."""
        if self.client:
            self.client.close()


# Global database manager instance - will be connected during app startup
db_manager = DatabaseManager()


def get_database_manager() -> DatabaseManager:
    """Dependency to get database manager."""
    return db_manager
