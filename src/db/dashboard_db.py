"""Async SQLAlchemy database setup and connection management for dashboard functionality."""

import os
import logging
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from typing import AsyncGenerator
from contextlib import asynccontextmanager
from models.dashboard import Base

logger = logging.getLogger(__name__)

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/health_db")

# Handle different database URL formats for async
if DATABASE_URL.startswith("postgresql://"):
    ASYNC_DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)
elif DATABASE_URL.startswith("sqlite://"):
    ASYNC_DATABASE_URL = DATABASE_URL.replace("sqlite://", "sqlite+aiosqlite://", 1)
else:
    ASYNC_DATABASE_URL = DATABASE_URL

# Create async engine
async_engine = create_async_engine(
    ASYNC_DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=300,
    echo=False
)

# Async session maker
AsyncSessionLocal = async_sessionmaker(
    bind=async_engine, 
    class_=AsyncSession, 
    expire_on_commit=False
)


class DatabaseSetup:
    """Database setup and connection testing utilities."""
    
    @staticmethod
    async def create_tables():
        """Create all tables in the database."""
        try:
            logger.info("Creating database tables...")
            async with async_engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            logger.info("✅ Database tables created successfully")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to create database tables: {e}")
            return False
    
    @staticmethod
    async def test_connection() -> bool:
        """Test database connection at startup."""
        try:
            logger.info("Testing database connection...")
            async with async_engine.begin() as connection:
                result = await connection.execute(text("SELECT 1"))
                await result.fetchone()
                logger.info("✅ Database connection successful")
                return True
        except Exception as e:
            logger.error(f"❌ Database connection failed: {e}")
            logger.error("💡 Make sure DATABASE_URL is set correctly")
            logger.error(f"💡 Current DATABASE_URL: {ASYNC_DATABASE_URL}")
            return False


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency to get async database session.
    Use this with FastAPI Depends() for async endpoints.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


@asynccontextmanager
async def get_db_session() -> AsyncSession:
    """
    Context manager to get async database session.
    Use this for manual session management.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_database():
    """Initialize database on application startup."""
    logger.info("🔧 Initializing database...")
    
    # Test connection first
    if not await DatabaseSetup.test_connection():
        logger.error("❌ Database connection failed")
        return False
    
    # Create tables
    if not await DatabaseSetup.create_tables():
        logger.error("❌ Failed to create tables")
        return False
    
    logger.info("✅ Database initialization completed")
    return True