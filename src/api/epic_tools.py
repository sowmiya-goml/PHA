from fastapi import APIRouter
from fastapi.responses import RedirectResponse, JSONResponse
from connector_fhir.epic import exchange_code_for_tokens, extract_organization_from_state, refresh_access_token, generate_epic_authorization_url, authorize_epic, validate_user_credentials
from schemas.schema import Credentials
from fastapi import APIRouter, HTTPException
from typing import Optional, Dict
from schemas.schema import LoginRequest

from pydantic import BaseModel

class LoginResponse(BaseModel):
    authenticated: bool
    organization: str
 


router = APIRouter()

@router.post("/epic/credentials", tags=["TEST"])
async def epic_authorize(credentials: Credentials):
    """
    Endpoint to authorize Epic API credentials and store them in MongoDB
    """
    response = authorize_epic(credentials)
    return response

@router.get("/internal/authorize", tags=["TEST"])
async def authorize(organization: str):

    # Step 1: Redirect user to Epic's authorization page.
    print(organization)
    auth_url = generate_epic_authorization_url(organization)
    return {"authorization_url": auth_url}


@router.get("/callback", tags=["TEST"])
async def callback(
    code: str,
    state: Optional[str] = None,
    organization: Optional[str] = None,
    error: Optional[str] = None,
    error_description: Optional[str] = None
):
    """
    Callback endpoint for Epic OAuth flow with redirect on success
    """
    if error:
        raise HTTPException(
            status_code=400,
            detail=f"Authorization failed: {error} - {error_description}"
        )

    if not organization and state:
        organization = extract_organization_from_state(state)
        if not organization:
            raise HTTPException(
                status_code=422,
                detail=[{
                    "type": "missing",
                    "loc": ["query", "organization"],
                    "msg": "Field required",
                    "input": None
                }]
            )

    try:
        tokens = exchange_code_for_tokens(code, organization)

        if tokens:
            redirect_url = f"https://0rf47nqb-3000.inc1.devtunnels.ms/login"
            return RedirectResponse(url=redirect_url)
        else:
            return JSONResponse(
                status_code=400,
                content={"error": "Token exchange failed. Please try again."}
            )

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    


@router.get("/internal/refresh",tags=["TEST"])
def refresh(organization: str):
    tokens = refresh_access_token(organization)
    return {"message": "Access token refreshed", "tokens": tokens}


@router.post("/epic/login", response_model=LoginResponse, tags=["TEST"])
def login_user(login_request: LoginRequest):
    is_valid = validate_user_credentials(
        organization=login_request.organization_name,
        password=login_request.password
    )
    if is_valid:
        return LoginResponse(
            authenticated=True,
            organization=login_request.organization_name
        )
    else:
        raise HTTPException(status_code=401, detail="Invalid credentials")
 