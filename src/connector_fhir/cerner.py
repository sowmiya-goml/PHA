import requests
import json
from pathlib import Path
from dotenv import load_dotenv
import os
import httpx
import base64
from db.auth import get_mongo_client,get_cerner_credentials, save_tokens_db, load_cerner_tokens_db, update_cerner_access_token_db
from pymongo import ASCENDING
from pymongo.errors import DuplicateKeyError
load_dotenv()

TOKEN_URL = os.getenv("CERNER_TOKEN_URL")
CERNER_AUTH_URL=os.getenv("CERNER_AUTHORIZATION_URL")
SCOPES = (
    "user/Condition.read user/Condition.write "
    "user/Appointment.read user/Appointment.write "
    "user/Practitioner.read user/Practitioner.write "
    "user/Patient.read user/Patient.write "
    "user/MedicationRequest.read user/MedicationRequest.write "
    "user/AllergyIntolerance.read user/AllergyIntolerance.write "
    "user/Procedure.read user/Procedure.write "
    "user/FamilyMemberHistory.read user/FamilyMemberHistory.write "
    "user/Immunization.read user/Immunization.write "
    "user/Encounter.read  user/Encounter.write "
    "user/DiagnosticReport.read user/DiagnosticReport.write "
    "user/Observation.read user/Observation.write "
    "user/DocumentReference.read user/DocumentReference.write "
    "user/CarePlan.read user/CarePlan.write offline_access"
    
)
CERNER_TOKENS_FILE = Path("tokens/tokens.json")

CREDENTIALS_FILE = Path("C:/Users/Sharath Prasaath/PHA/goML-PHA_connector/api/tokens/credentials.json")

def authorize_cerner(credentials: dict):
    """
    Authorize the user with Epic API using the provided credentials.
    Organization name is used as the primary key.
    """
    try:
        credentials_dict = {
    "client_id": credentials.get("CERNER_CLIENT_ID"),
    "client_secret": credentials.get("CERNER_CLIENT_SECRET"),
    "redirect_uri": credentials.get("CERNER_REDIRECT_URI"),
    "organization_name": credentials.get("CERNER_ORG_NAME"),
    "password": credentials.get("CERNER_PASSWORD"),
    "aud": credentials.get("CERNER_AUD"),
    "state": credentials.get("CERNER_STATE")
    }
        print("Credentials to be saved:", credentials_dict)
        client = get_mongo_client()
        db = client["cerner"]
        print(db)
        
        db.credentials.create_index([("organization_name", ASCENDING)], unique=True)
    
        result = db.credentials.update_one(
            {"organization_name": credentials.get("organization_name")},
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

def generate_cerner_authorization_url(organization: str):
    CERNER_AUTH_URL=os.getenv("CERNER_AUTHORIZATION_URL")
    credentials = get_cerner_credentials(organization)
    if credentials["status"] == "error":
        return {"error": "Failed to fetch credentials", "details": credentials["message"]}
    
    creds = credentials['data']
    url = (
        f"{CERNER_AUTH_URL}?response_type=code"
        f"&client_id={creds['client_id']}"
        f"&redirect_uri={creds['redirect_uri']}"
        f"&scope={SCOPES}"
        f"&aud={creds['aud']}"
        f"&state={creds['state']}"
        )
    
    return {
        "authorization_url": url,
    }    
    
        
def get_organizations(state: str) -> str | None:
    with open(CREDENTIALS_FILE,"r") as f:
        all_credentials = json.load(f)
    for organization, creds in all_credentials.items():
        if creds.get("CERNER_STATE") == state:
            return organization
    return None

def exchange_code_for_cerner_tokens(code: str,organization: str) -> dict:
    credentials = get_cerner_credentials(organization)
    if credentials["status"] == "error":
        return {"error": "Failed to fetch credentials", "details": credentials["message"]}
    creds = credentials['data']
    print(code,organization)
    client_id = creds.get("client_id")
    redirect_uri = creds.get("redirect_uri")
    client_secret = creds.get("client_secret")
    credential = f"{client_id}:{client_secret}"
    encoded_credentials = base64.b64encode(credential.encode()).decode()
    
    data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": redirect_uri
    }
    headers = {
        "Authorization": f"Basic {encoded_credentials}",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    with httpx.Client() as client:
        response = client.post(TOKEN_URL, data=data, headers=headers)
    if response.status_code == 200:
        tokens = response.json()
        save_tokens_db(tokens,organization)
        return tokens
    else:
        raise Exception(f"Token exchange failed: {response.status_code} - {response.text}")
    

def update_access_token(new_access_token,organization):
    try:
        if os.path.exists(CERNER_TOKENS_FILE):
            with open(CERNER_TOKENS_FILE, 'r') as file:
                data = json.load(file)
        else:
            data = {}

        if organization in data:
            data[organization]['access_token'] = new_access_token['access_token']
        else:
            print(f"Integration ID '{organization}' not found.")
            return

        with open(CERNER_TOKENS_FILE, 'w') as file:
            json.dump(data, file, indent=4)

    except Exception as e:
        print(f"Error updating access token for '{organization}': {e}")
        
        
        
def refresh_cerner_access_token(organization) -> dict:
    tokens = load_cerner_tokens_db(organization)
    refresh_token = tokens['data'].get("refresh_token")
    print("Refresh token",refresh_token)
    credentials = get_cerner_credentials(organization)
    if credentials["status"] == "error":
        return {"error": "Failed to fetch credentials", "details": credentials["message"]}
    creds = credentials['data']
    print(creds)
    client_id = creds.get("client_id")
    token_url = creds.get("token_url")
    client_secret = creds.get("client_secret")

    if not refresh_token:
        raise Exception("No refresh token found in stored tokens")
    credentials = f"{client_id}:{client_secret}"
    encoded_credentials = base64.b64encode(credentials.encode()).decode()
    headers = {
    "Authorization": f"Basic {encoded_credentials}",
    "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {
    "grant_type": "refresh_token",
    "refresh_token": refresh_token,
    }

    response = requests.post(TOKEN_URL, data=data, headers=headers)
    print(response.status_code)
    if response.status_code == 200:
        new_tokens = response.json()
        update_cerner_access_token_db(new_tokens,organization)
        return new_tokens
    else:
        raise Exception(f"Refresh token failed: {response.status_code} - {response.text}")

