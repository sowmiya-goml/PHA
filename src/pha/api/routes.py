"""API routes aggregator for v1 endpoints."""

from fastapi import APIRouter

from pha.api.v1 import connections, healthcare, dashboard

# Create main API router
api_router = APIRouter()

# Include all v1 routes
api_router.include_router(connections.router, prefix="/connections", tags=["Database Connections"])
api_router.include_router(healthcare.router, prefix="/healthcare", tags=["Healthcare Queries"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["Patient Dashboard"])