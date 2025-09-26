from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError

mongo_uri = 'mongodb+srv://22cs027_db_user:SathyaPainter@pha.o1mtvpd.mongodb.net/?retryWrites=true&w=majority&appName=PHA'

def get_mongo_client():
    """Create MongoDB client with timeout settings"""
    try:
        client = MongoClient(
            mongo_uri,
            serverSelectionTimeoutMS=100000, 
            connectTimeoutMS=100000,
        )
        # Verify connection
        client.admin.command('ping')
        return client
    except (ConnectionFailure, ServerSelectionTimeoutError) as e:
        raise ConnectionError(f"Failed to connect to MongoDB: {str(e)}")
    
def get_epic_credentials(organization_name: str):
    """
    Retrieve Epic credentials for a given organization from MongoDB.
    """
    try:
        client = get_mongo_client()
        db = client["epic"]
        
        credentials = db.credentials.find_one(
            {"organization_name": organization_name},
            {"_id": 0}  # Exclude MongoDB _id field from result
        )
        client.close()
        if credentials:
            return {"status": "success", "data": credentials}
        return {"status": "error", "message": "Organization not found"}
        
    except ConnectionError as e:
        return {"status": "error", "message": "Database connection failed", "details": str(e)}
    except Exception as e:
        return {"status": "error", "message": "Failed to fetch credentials", "details": str(e)}
    
    
def get_cerner_credentials(organization_name: str):
    """
    Retrieve Epic credentials for a given organization from MongoDB.
    """
    print(organization_name, "🎉🎉🎉🎉🎉🎉")
    try:
        client = get_mongo_client()
        db = client["cerner"]
        credentials = db.credentials.find_one(
            {"organization_name": organization_name},
            {"_id": 0}  # Exclude MongoDB _id field from result
        )
        client.close()
        print(credentials, "💕💕💕💕💕💕")
        
        if credentials:
            return {"status": "success", "data": credentials}
        return {"status": "error", "message": "Organization not found"}
        
    except ConnectionError as e:
        return {"status": "error", "message": "Database connection failed", "details": str(e)}
    except Exception as e:
        return {"status": "error", "message": "Failed to fetch credentials", "details": str(e)}
    
def get_organization(state: str):
    """
    Retrieve the organization name from the state parameter.
    """
    try:
        client = get_mongo_client()
        db = client['cerner']
        
        result = db.credentials.find_one({"state": state}, {"organization_name": 1, "_id": 0})
        print("result", result)
        return result.get("organization_name") if result else None

    except Exception as e:
        print(f"Error retrieving organization name: {e}")
        return None
    
    
def save_tokens_db(tokens: dict,organization_name: str):
    """
    Save tokens to MongoDB for a given organization.
    """
    try:
        # print(tokens,organization_name)
        client = get_mongo_client()
        db = client["cerner"]
        
        result = db.credentials.update_one(
            {"organization_name": organization_name},
            {"$set": {"tokens": tokens}},
            upsert=True
        )
        client.close()
        print(result)
        
        if result.matched_count > 0:
            print("success")
            return {"status": "success", "message": "Tokens updated successfully"}
        return {"status": "success", "message": "Tokens saved successfully"}
        
    except ConnectionError as e:
        return {"status": "error", "message": "Database connection failed", "details": str(e)}
    except Exception as e:
        return {"status": "error", "message": "Failed to save tokens", "details": str(e)}
    
def load_cerner_tokens_db(organization_name: str):
    """
    Load tokens from MongoDB for a given organization.
    """
    print(organization_name)
    try:
        client = get_mongo_client()
        db = client["cerner"]
        
        tokens = db.credentials.find_one(
            {"organization_name": organization_name},
            {"tokens": 1, "_id": 0}  # Exclude MongoDB _id field from result
        )
        client.close()
        
        if tokens:
            return {"status": "success", "data": tokens.get("tokens")}
        return {"status": "error", "message": "Tokens not found"}
        
    except ConnectionError as e:
        return {"status": "error", "message": "Database connection failed", "details": str(e)}
    except Exception as e:
        return {"status": "error", "message": "Failed to load tokens", "details": str(e)}
    
def update_cerner_access_token_db(access_token: str, organization_name: str):
    """
    Update the access token in MongoDB for a given organization.
    """
    print(access_token)
    try:
        client = get_mongo_client()
        db = client["cerner"]
        
        result = db.credentials.update_one(
            {"organization_name": organization_name},
            {"$set": {"tokens.access_token": access_token['access_token']}},
            upsert=True
        )
        client.close()
        print(result)
        
        if result.matched_count > 0:
            return {"status": "success", "message": "Access token updated successfully"}
        return {"status": "error", "message": "Organization not found"}
        
    except ConnectionError as e:
        return {"status": "error", "message": "Database connection failed", "details": str(e)}
    except Exception as e:
        return {"status": "error", "message": "Failed to update access token", "details": str(e)}
