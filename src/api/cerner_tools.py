from fastapi import APIRouter, Query, HTTPException
from db.auth import get_organization, get_cerner_credentials
from fastapi.responses import RedirectResponse, JSONResponse
from connector_fhir.cerner import generate_cerner_authorization_url, exchange_code_for_cerner_tokens, refresh_cerner_access_token, authorize_cerner
router = APIRouter()


@router.post("/CERNER/save-credentials", tags=["TEST"])
async def save_credentials(
    client_id: str = Query(...),
    client_secret: str = Query(...),
    redirect_uri: str = Query(...),
    aud: str = Query(...),
    state: str = Query(...),
    organization: str = Query(...),
    password: str = Query(...)
):
    creds = {
            "CERNER_CLIENT_ID": client_id,
        "CERNER_CLIENT_SECRET": client_secret,
        "CERNER_REDIRECT_URI": redirect_uri,
        "CERNER_AUD": aud,
        "CERNER_STATE": state,
        "CERNER_PASSWORD": password,
        "CERNER_ORG_NAME": organization

    }
    authorize_cerner(creds)

    return {
        "message": "Credentials saved successfully",
        "organization": organization
    }

@router.get("/CERNER/authorize", tags=["TEST"])
async def cerner_authorize(organization: str = Query(...)):
    url=generate_cerner_authorization_url(organization)
    return {"authorization_url": url}

# @router.get("/CERNER/callback", tags=["TEST"])
# def cerner_callback(code: str,state: str):
#     """
#     Step 2: Exchange the authorization code for tokens.
#     """
#     organization = get_organization(state)
#     print("organizationn", organization)
#     cerner_tokens = exchange_code_for_cerner_tokens(code,organization)
#     return {"message": "Authorization successful", "tokens": cerner_tokens}

@router.get("/CERNER/callback", tags=["TEST"])
def cerner_callback(code: str, state: str):
    try:
        organization = get_organization(state)
        print("organizationn", organization)

        cerner_tokens = exchange_code_for_cerner_tokens(code, organization)

        if cerner_tokens:
            redirect_url = "https://0rf47nqb-3000.inc1.devtunnels.ms/login"
            return RedirectResponse(url=redirect_url)
        else:
            return JSONResponse(
                status_code=400,
                content={"error": "Failed to retrieve tokens from Cerner."}
            )

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Internal server error: {str(e)}"}
        )



@router.get("/CERNER/refresh", tags=["TEST"])
def cerner_refresh(organization: str = Query(...)):
    """
    Step 3: Refresh the access token using the refresh token.
    """
    print("organization", organization)
    cerner_tokens = refresh_cerner_access_token(organization)
    return {"message": "Access token refreshed", "tokens": cerner_tokens}
 

@router.post("/CERNER/login", tags=["TEST"])
async def cerner_login(
    organization_name: str = Query(...),
    password: str = Query(...)
):
    result = get_cerner_credentials(organization_name)

    if result["status"] == "error":
        raise HTTPException(status_code=404, detail=result["message"])

    credentials = result["data"]

    # Fallback for different password key names
    stored_password = credentials.get("CERNER_PASSWORD") or credentials.get("password")

    if stored_password != password:
        raise HTTPException(status_code=401, detail="Invalid password")

    return {
        "message": "Login successful",
        "organization": organization_name,
    }

