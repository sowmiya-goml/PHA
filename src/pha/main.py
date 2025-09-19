"""Main FastAPI application entry point."""

import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from pha.core.config import settings
from pha.api.routes import api_router
from pha.utils.helpers import setup_logging
from pha.db.session import db_manager

# Setup logging
setup_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan context manager for startup/shutdown events."""
    # Startup
    try:
        # Attempt to connect to MongoDB asynchronously
        await db_manager.connect()
        print("✅ PHA Server ready - Dashboard endpoints use real database connections only!")
    except Exception as e:
        print(f"Failed to initialize database connection: {e}")
        
    yield
    
    # Shutdown
    try:
        if db_manager.client:
            db_manager.close()
    except Exception as e:
        print(f"Error during shutdown: {e}")


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
# Include API routes
app.include_router(api_router, prefix="/api/v1")


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
    try:
        mongodb_status = "connected" if db_manager.is_connected() else "disconnected"
    except Exception:
        mongodb_status = "error"
    
    return {
        "status": "healthy",
        "timestamp": "2025-09-19T00:00:00Z",
        "databases": {
            "mongodb": mongodb_status
        },
        "services": {
            "api": "running",
            "mongodb": mongodb_status,
            "dashboard": "real_database_only"
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
