from typing import Dict, Any
from pymongo.collection import Collection
from pymongo import MongoClient
from datetime import datetime

from app.core.config import db  # or from wherever your shared db is defined

fhir_apps_collection = db["fhir_apps"]

def store_fhir_app_details(
    collection: Collection,
    user_id: str,
    password: str,
    client_id: str,
    client_secret: str,
    redirect_uri: str
) -> Dict[str, Any]:
    """Store FHIR app details in the MongoDB collection."""
    fhir_app_data = {
        "user_id": user_id,
        "password": password,
        "client_id": client_id,
        "client_secret": client_secret,
        "redirect_uri": redirect_uri,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    result = collection.insert_one(fhir_app_data)
    fhir_app_data["_id"] = result.inserted_id
    return fhir_app_data

# app_details = store_fhir_app_details(
#     fhir_apps_collection,
#     user_id="your_user_id",
#     password="your_password",
#     client_id="your_client_id",
#     client_secret="your_client_secret",
#     redirect_uri="your_redirect_uri"
# )
# print(app_details)