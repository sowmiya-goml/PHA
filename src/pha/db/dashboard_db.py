"""SQLAlchemy database setup and connection management for dashboard functionality."""

import os
import logging
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from typing import Generator, AsyncGenerator
from contextlib import asynccontextmanager
from pha.models.dashboard import Base
from pha.core.config import settings

logger = logging.getLogger(__name__)

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/health_db")

# Handle different database URL formats
if DATABASE_URL.startswith("postgresql://"):
    ASYNC_DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)
elif DATABASE_URL.startswith("sqlite://"):
    ASYNC_DATABASE_URL = DATABASE_URL.replace("sqlite://", "sqlite+aiosqlite://", 1)
else:
    ASYNC_DATABASE_URL = DATABASE_URL

# Create engines
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=300,
    echo=False  # Set to True for SQL debugging
)

async_engine = create_async_engine(
    ASYNC_DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=300,
    echo=False
)

# Session makers
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
AsyncSessionLocal = async_sessionmaker(
    bind=async_engine, 
    class_=AsyncSession, 
    expire_on_commit=False
)


class DatabaseSetup:
    """Database setup and connection testing utilities."""
    
    @staticmethod
    def create_tables():
        """Create all tables in the database."""
        try:
            logger.info("Creating database tables...")
            Base.metadata.create_all(bind=engine)
            logger.info("✅ Database tables created successfully")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to create database tables: {e}")
            return False
    
    @staticmethod
    def test_connection() -> bool:
        """Test database connection at startup."""
        try:
            logger.info("Testing database connection...")
            with engine.connect() as connection:
                # Test basic connectivity
                result = connection.execute(text("SELECT 1"))
                result.fetchone()
                logger.info("✅ Database connection successful")
                return True
        except Exception as e:
            logger.error(f"❌ Database connection failed: {e}")
            logger.error("💡 Make sure DATABASE_URL is set correctly")
            logger.error(f"💡 Current DATABASE_URL: {DATABASE_URL}")
            return False
    
    @staticmethod
    async def test_async_connection() -> bool:
        """Test async database connection."""
        try:
            logger.info("Testing async database connection...")
            async with async_engine.begin() as connection:
                result = await connection.execute(text("SELECT 1"))
                await result.fetchone()
                logger.info("✅ Async database connection successful")
                return True
        except Exception as e:
            logger.error(f"❌ Async database connection failed: {e}")
            return False


def get_db() -> Generator[Session, None, None]:
    """
    Dependency to get database session for synchronous operations.
    Use this with FastAPI Depends().
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def get_async_db() -> AsyncGenerator[AsyncSession, None]:
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
async def get_async_db_session() -> AsyncSession:
    """
    Context manager to get async database session.
    Use this for manual session management.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


def init_database():
    """Initialize database on application startup."""
    logger.info("🔧 Initializing database...")
    
    # Test connection first
    if not DatabaseSetup.test_connection():
        logger.warning("⚠️  Database connection failed, but continuing startup...")
        logger.warning("⚠️  Dashboard endpoints will return mock data")
        return False
    
    # Create tables
    if not DatabaseSetup.create_tables():
        logger.warning("⚠️  Failed to create tables, but continuing startup...")
        return False
    
    logger.info("✅ Database initialization completed")
    return True


async def init_async_database():
    """Initialize async database components."""
    logger.info("🔧 Initializing async database...")
    
    if not await DatabaseSetup.test_async_connection():
        logger.warning("⚠️  Async database connection failed")
        return False
    
    logger.info("✅ Async database initialization completed")
    return True


# Mock data generators for fallback when database is unavailable
class MockDataGenerator:
    """Generate mock patient data when database is unavailable."""
    
    @staticmethod
    def get_mock_heart_rate(patient_id: str):
        """Generate mock heart rate data."""
        import random
        from datetime import datetime, timedelta
        
        base_hr = 72 + (hash(patient_id) % 20)  # Deterministic but varied
        return {
            "heart_rate": base_hr,
            "status": "resting" if base_hr < 80 else "elevated",
            "timestamp": (datetime.utcnow() - timedelta(minutes=random.randint(1, 60))).isoformat(),
            "patient_id": patient_id
        }
    
    @staticmethod
    def get_mock_blood_pressure(patient_id: str):
        """Generate mock blood pressure data."""
        import random
        from datetime import datetime, timedelta
        
        systolic = 120 + (hash(patient_id) % 30)
        diastolic = 80 + (hash(patient_id) % 20)
        
        return {
            "systolic": systolic,
            "diastolic": diastolic,
            "status": "normal" if systolic < 140 and diastolic < 90 else "elevated",
            "timestamp": (datetime.utcnow() - timedelta(minutes=random.randint(1, 60))).isoformat(),
            "patient_id": patient_id
        }
    
    @staticmethod
    def get_mock_bmi(patient_id: str):
        """Generate mock BMI data."""
        from datetime import datetime, timedelta
        
        bmi = 22.5 + ((hash(patient_id) % 100) / 10.0)  # BMI between 22.5 and 32.5
        
        return {
            "bmi": round(bmi, 1),
            "trend": "stable",
            "timestamp": (datetime.utcnow() - timedelta(hours=1)).isoformat(),
            "patient_id": patient_id
        }
    
    @staticmethod
    def get_mock_spo2(patient_id: str):
        """Generate mock SpO2 data."""
        from datetime import datetime, timedelta
        
        spo2 = 96 + (hash(patient_id) % 5)  # SpO2 between 96-100%
        
        return {
            "spo2_percentage": spo2,
            "status": "normal" if spo2 >= 95 else "low",
            "timestamp": (datetime.utcnow() - timedelta(minutes=30)).isoformat(),
            "patient_id": patient_id
        }
    
    @staticmethod
    def get_mock_temperature(patient_id: str):
        """Generate mock temperature data."""
        from datetime import datetime, timedelta
        
        temp_c = 36.5 + ((hash(patient_id) % 20) / 10.0)  # 36.5-38.5°C
        temp_f = (temp_c * 9/5) + 32
        
        return {
            "temperature_celsius": round(temp_c, 1),
            "temperature_fahrenheit": round(temp_f, 1),
            "status": "normal" if temp_c < 37.5 else "fever",
            "timestamp": (datetime.utcnow() - timedelta(minutes=15)).isoformat(),
            "patient_id": patient_id
        }
    
    @staticmethod
    def get_mock_blood_sugar(patient_id: str):
        """Generate mock blood sugar data."""
        from datetime import datetime, timedelta
        
        glucose = 90 + (hash(patient_id) % 60)  # 90-150 mg/dL
        
        return {
            "glucose_level": glucose,
            "trend": "stable",
            "timestamp": (datetime.utcnow() - timedelta(hours=2)).isoformat(),
            "patient_id": patient_id
        }
    
    @staticmethod
    def get_mock_recovery_tracker(patient_id: str):
        """Generate mock recovery tracker data."""
        import random
        from datetime import datetime, timedelta
        
        # Generate 7 days of recovery data
        data = []
        base_score = 70 + (hash(patient_id) % 20)
        
        for i in range(7):
            score_variation = random.randint(-5, 8) if i > 0 else 0
            recovery_score = max(0, min(100, base_score + score_variation))
            
            data.append({
                "date": (datetime.utcnow() - timedelta(days=6-i)).strftime("%Y-%m-%d"),
                "recovery_score": recovery_score,
                "mobility_score": recovery_score - 5 + random.randint(0, 10),
                "pain_level": max(0, 10 - (recovery_score // 10)),
                "activity_level": "high" if recovery_score > 80 else "moderate" if recovery_score > 50 else "low"
            })
        
        return {
            "patient_id": patient_id,
            "recovery_data": data,
            "current_stage": "recovery" if base_score > 60 else "acute",
            "timestamp": datetime.utcnow().isoformat()
        }