"""Main FastAPI application entry point."""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from app.core.config import settings
from app.routers import connections
from app.utils.helpers import setup_logging
from app.models.fhir_app import store_fhir_app_details, fhir_apps_collection

# Setup logging
setup_logging()

# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
    description=settings.DESCRIPTION,
    docs_url="/docs",
    redoc_url="/redoc"
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


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": f"{settings.APP_NAME} is running",
        "version": settings.VERSION,
        "docs_url": "/docs",
        "status": "healthy"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "timestamp": "2025-08-29T00:00:00Z"}


class FHIRAppDetails(BaseModel):
    user_id: str
    password: str
    client_id: str
    client_secret: str
    redirect_uri: str


@app.post("/fhir-app/")
def create_fhir_app(details: FHIRAppDetails):
    try:
        result = store_fhir_app_details(
            fhir_apps_collection,
            user_id=details.user_id,
            password=details.password,
            client_id=details.client_id,
            client_secret=details.client_secret,
            redirect_uri=details.redirect_uri
        )
        result["_id"] = str(result["_id"])  # Convert ObjectId to string for JSON serialization
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=True
    )
