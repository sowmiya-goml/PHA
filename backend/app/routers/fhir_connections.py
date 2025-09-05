"""FHIR connection API routes."""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.models.fhir_app import store_fhir_app_details, fhir_apps_collection

router = APIRouter(
    prefix="/fhir-app",
    tags=["FHIR Connections"],
    responses={404: {"description": "Not found"}}
)


class FHIRAppDetails(BaseModel):
    user_id: str
    password: str
    client_id: str
    client_secret: str
    redirect_uri: str


@router.post("/")
def create_fhir_app(details: FHIRAppDetails):
    """Create a new FHIR application configuration."""
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
