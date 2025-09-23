import requests
from pathlib import Path
from pymongo import ASCENDING
from pymongo.errors import DuplicateKeyError
from schemas.schema import Credentials
from datetime import datetime
from db.auth import get_mongo_client, get_epic_credentials

# --- Static URLs ---
EPIC_AUTH_URL = "https://fhir.epic.com/interconnect-fhir-oauth/oauth2/authorize"
EPIC_TOKEN_URL = "https://fhir.epic.com/interconnect-fhir-oauth/oauth2/token"

# --- Token Storage in MongoDB ---

def save_tokens_to_db(organization: str, tokens: dict):
    client = get_mongo_client()
    try:
        db = client["epic"]
        db.credentials.update_one(
            {"organization_name": organization},
            {
                "$set": {
                    "tokens": tokens
                    # "last_updated": datetime.utcnow()
                }
            },
            upsert=True
        )
    finally:
        client.close()

def load_tokens_from_db(organization: str) -> dict:
    client = get_mongo_client()
    try:
        db = client["epic"]
        print(organization, "organization")
        record = db.credentials.find_one({"organization_name": organization})
        print(record, "recorddd")
        return record.get("tokens", {}) if record else {}
        # return record
    finally:
        client.close()


# --- Store credentials into MongoDB ---

def authorize_epic(credentials: Credentials):
    try:
        credentials_dict = {
            "client_id": credentials.client_id,
            "secret_id": credentials.secret_id,
            "redirect_uri": credentials.redirect_uri,
            "organization_name": credentials.organization_name,
            "password": credentials.password,
        }

        client = get_mongo_client()
        db = client["epic"]

        db.credentials.create_index([("organization_name", ASCENDING)], unique=True)

        result = db.credentials.update_one(
            {"organization_name": credentials.organization_name},
            {"$set": credentials_dict},
            upsert=True
        )
        client.close()

        if result.matched_count > 0:
            return {"message": "Authorization updated successfully"}
        return {"message": "Authorization successful"}

    except DuplicateKeyError:
        return {"error": "Organization already exists", "details": "This organization is already authorized"}
    except ConnectionError as e:
        return {"error": "Database connection failed", "details": str(e)}
    except Exception as e:
        return {"error": "Authorization failed", "details": str(e)}

# --- Generate authorization URL ---

def generate_epic_authorization_url(organization: str) -> dict:
    print("hi")
    credentials = get_epic_credentials(organization)
    print(credentials)
    if credentials["status"] == "error":
        return {"error": "Failed to fetch credentials", "details": credentials["message"]}
    print(credentials)
    creds = credentials["data"]

    state = f"org_{organization}"
    
    auth_url = (
        f"{EPIC_AUTH_URL}"
        f"?response_type=code"
        f"&client_id={creds['client_id']}"
        f"&redirect_uri={creds['redirect_uri']}"
        f"&scope=Patient.read offline_access"
        f"&state={state}" 
    )
    print(auth_url)
    return {"authorization_url": auth_url}

# --- Exchange code for token using static token URL ---

def exchange_code_for_tokens(code: str, organization: str) -> dict:
    credentials = get_epic_credentials(organization)
    if credentials["status"] == "error":
        raise Exception(f"Failed to fetch credentials: {credentials['message']}")

    creds = credentials['data']

    payload = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": creds["redirect_uri"],
        "client_id": creds["client_id"],
        "client_secret": creds["secret_id"]
    }

    response = requests.post(EPIC_TOKEN_URL, data=payload)
    if response.status_code == 200:
        tokens = response.json()
        save_tokens_to_db(organization, tokens)
        return tokens
    else:
        raise Exception(f"Token exchange failed: {response.status_code} - {response.text}")

# --- Extract organization from state parameter ---

def extract_organization_from_state(state: str) -> str:
    """Extract organization name from the state parameter"""
    if state and state.startswith("org_"):
        return state[4:]  # Remove 'org_' prefix
    return None

# --- Refresh token using MongoDB credentials and static token URL ---

def refresh_access_token(organization: str) -> dict:
    credentials = get_epic_credentials(organization)
    print(credentials, "credentials")
    if credentials["status"] == "error":
        raise Exception(f"Failed to fetch credentials: {credentials['message']}")

    creds = credentials['data']
    tokens = load_tokens_from_db(organization)
    refresh_token = tokens.get("refresh_token")
    if not refresh_token:
        raise Exception("No refresh token found for organization")

    payload = {
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
        "client_id": creds["client_id"],
        "client_secret": creds["secret_id"]
    }

    response = requests.post(EPIC_TOKEN_URL, data=payload)
    if response.status_code == 200:
        new_tokens = response.json()
        print("new token",new_tokens)
        save_tokens_to_db(organization, new_tokens)
        return new_tokens
    else:
        raise Exception(f"Refresh token failed: {response.status_code} - {response.text}")
    
def validate_user_credentials(organization: str, password: str) -> bool:
    """
    Check if the provided organization and password match the credentials stored in MongoDB.
    """
    client = get_mongo_client()
    try:
        db = client["epic"]
        record = db.credentials.find_one({"organization_name": organization})
        if record and record.get("password") == password:
            return True
        return False
    finally:
        client.close()
