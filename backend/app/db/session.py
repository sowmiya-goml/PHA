"""Database connection and session management."""

from pymongo import MongoClient
from pymongo.database import Database
from pymongo.collection import Collection
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)


class DatabaseManager:
    """MongoDB database connection manager."""
    
    def __init__(self):
        self.client: MongoClient = None
        self.db: Database = None
        self.connections_collection: Collection = None
        self._connect()
    
    def _connect(self):
        """Establish connection to MongoDB."""
        try:
            self.client = MongoClient(
                settings.MONGODB_URL,
                serverSelectionTimeoutMS=settings.DB_CONNECTION_TIMEOUT_MS
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


# Global database manager instance
db_manager = DatabaseManager()


def get_database_manager() -> DatabaseManager:
    """Dependency to get database manager."""
    return db_manager
