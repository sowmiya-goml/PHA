"""Main FastAPI application entry point."""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.routers import connections
from app.routers import mongodb_schema_fixed as mongodb_schema
from app.routers import query_generator
from app.routers import healthcare_query
from app.utils.helpers import setup_logging
from app.db.session import db_manager

# Setup logging
setup_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan context manager for startup/shutdown events."""
    # Startup
    try:
        # Attempt to connect to MongoDB asynchronously
        await db_manager.connect()
    except Exception as e:
        print(f"Failed to initialize database connection: {e}")
        
    yield
    
    # Shutdown
    if db_manager.client:
        db_manager.close()


# Create FastAPI application with lifespan events
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
    description=settings.DESCRIPTION,
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(connections.router, prefix="/api/v1")
app.include_router(mongodb_schema.router, prefix="/api/v1")
app.include_router(query_generator.router, prefix="/api/v1")
app.include_router(healthcare_query.router, prefix="/api/v1")


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": f"{settings.APP_NAME} is running",
        "version": settings.VERSION,
        "docs_url": "/docs",
        "status": "healthy"
    }


@app.post("/database/reconnect")
async def reconnect_database():
    """Manually trigger database reconnection."""
    try:
        success = await db_manager.connect()
        if success:
            return {"status": "success", "message": "Database reconnected successfully"}
        else:
            return {"status": "failed", "message": "Failed to reconnect to database"}
    except Exception as e:
        return {"status": "error", "message": f"Reconnection error: {str(e)}"}


@app.get("/database/status")
async def database_status():
    """Get detailed database connection status."""
    return {
        "connected": db_manager.is_connected(),
        "mongodb_url": settings.MONGODB_URL[:50] + "..." if len(settings.MONGODB_URL) > 50 else settings.MONGODB_URL,
        "database_name": settings.DATABASE_NAME,
        "connection_timeout_ms": settings.DB_CONNECTION_TIMEOUT_MS,
        "server_selection_timeout_ms": settings.DB_SERVER_SELECTION_TIMEOUT_MS
    }


@app.get("/health")
async def health_check():
    """Health check endpoint with database status."""
    database_status = "connected" if db_manager.is_connected() else "disconnected"
    
    return {
        "status": "healthy",
        "timestamp": "2025-08-29T00:00:00Z",
        "database": database_status,
        "services": {
            "api": "running",
            "mongodb": database_status
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=True
    )
