"""FHIR connection API routes."""

from fastapi import APIRouter, HTTPException, Query, Response, status
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
import requests
import uuid
import urllib.parse

from app.models.fhir_app import store_fhir_app_details, fhir_apps_collection

router = APIRouter(
    prefix="/fhir-app",
    tags=["FHIR Connections"],
    responses={404: {"description": "Not found"}}
)

#app.include_router(fhir_connections.router)


class FHIRAppDetails(BaseModel):
    user_id: str
    password: str
    client_id: str
    client_secret: str
    redirect_uri: str
    state: str
    scope: str = "openid"
    aud: str = "https://fhir.epic.com/interconnect-fhir-oauth/api/FHIR/R4"


@router.post("/")
def create_fhir_app(details: FHIRAppDetails):
    """Create a new FHIR application configuration and redirect to Epic FHIR OAuth authorize."""
    try:
        # Save details in DB
        result = store_fhir_app_details(
            fhir_apps_collection,
            user_id=details.user_id,
            password=details.password,
            client_id=details.client_id,
            client_secret=details.client_secret,
            redirect_uri=details.redirect_uri
        )

        result["_id"] = str(result["_id"])  # Convert ObjectId to string

        # Build Epic OAuth2 authorize URL (no PKCE)
        epic_auth_url = (
            "https://fhir.epic.com/Authorization/oauth2/authorize"
            f"?response_type=code"
            f"&client_id={details.client_id}"
            f"&redirect_uri={details.redirect_uri}"
            f"&scope=openid%20fhirUser%20patient/*.read"
            f"&state={details.state}"
            f"&aud=https://fhir.epic.com/interconnect-fhir-oauth/api/FHIR/R4"
        )

        # Redirect to Epic authorization page (303 = POST → GET)
        return RedirectResponse(url=epic_auth_url, status_code=302)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/callback")
async def fhir_app_callback(
    code: str = Query(...),
    state: str = Query(...),
    redirect_uri: str = Query(...)
):
    token_url = "https://fhir.epic.com/Authorization/oauth2/token"
    client_id = "50560479-b540-428a-9b34-a8c49f51f0c0"
    client_secret = "Wui9fco0ArmvIvR/p9DPhXTMhPhpRDl0H19ABUBWHGx0ZOJWFUX4QnAQuCIlyx6BGRGAmT2/TAK5R4c757k2xg=="
    payload = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": redirect_uri,
        "client_id": client_id,
        "client_secret": client_secret
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    resp = requests.post(token_url, data=payload, headers=headers)
    if resp.status_code == 200:
        return resp.json()
    return Response(content=resp.text, status_code=resp.status_code)


@router.post("/fhir-app/")
async def create_fhir_app(details: FHIRAppDetails):
    # Store details in MongoDB
    app_record = store_fhir_app_details(
        fhir_apps_collection,
        user_id=details.user_id,
        password=details.password,
        client_id=details.client_id,
        client_secret=details.client_secret,
        redirect_uri=details.redirect_uri
    )
    # Build Epic authorization URL
    state = str(uuid.uuid4())
    params = {
        "response_type": "code",
        "client_id": details.client_id,
        "redirect_uri": details.redirect_uri,
        "scope": details.scope,
        "state": state,
        "aud": details.aud
    }
    auth_url = "https://fhir.epic.com/Authorization/oauth2/authorize?" + urllib.parse.urlencode(params)
    # Return a redirect response
    return RedirectResponse(auth_url, status_code=status.HTTP_302_FOUND)



@router.get("/test-redirect")
def test_redirect():
    epic_auth_url = (
        "https://fhir.epic.com/interconnect-fhir-oauth/oauth2/authorize"
        "?response_type=code"
        "&client_id=57ec0583-7f79-41e0-850f-d7c9c7282178"
        "&redirect_uri=https%3A%2F%2F0nw197d5-8000.inc1.devtunnels.ms%2Fapi%2Fv1%2Ffhir%2Fcallback"
        "&scope=smart%20v1"
        "&state=xyz123"
        "&aud=https%3A%2F%2Ffhir.epic.com%2Finterconnect-fhir-oauth%2Fapi%2FFHIR%2FR4"
    )

    # Redirect browser to Epic authorization page
    return RedirectResponse(url=epic_auth_url, status_code=302)