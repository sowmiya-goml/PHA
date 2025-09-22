from fastapi import APIRouter
from db.session import db_manager
from core.config import settings
router = APIRouter()

@router.post("/reconnect")
async def reconnect_database():
    """Manually trigger database reconnection."""
    try:
        success = await db_manager.connect()
        return {
            "status": "success" if success else "failed",
            "message": "Database reconnected successfully" if success else "Failed to reconnect",
        }
    except Exception as e:
        return {"status": "error", "message": f"Reconnection error: {str(e)}"}


@router.get("/status")
async def database_status():
    """Get detailed database connection status."""
    return {
        "connected": db_manager.is_connected(),
        "mongodb_url": (
            settings.MONGODB_URL[:50] + "..."
            if len(settings.MONGODB_URL) > 50
            else settings.MONGODB_URL
        ),
        "database_name": settings.DATABASE_NAME,
        "connection_timeout_ms": settings.DB_CONNECTION_TIMEOUT_MS,
        "server_selection_timeout_ms": settings.DB_SERVER_SELECTION_TIMEOUT_MS,
    }
