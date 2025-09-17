#!/usr/bin/env python3
"""Quick MongoDB Atlas connection test."""

import asyncio
from pymongo import MongoClient
import time

# Your exact connection string
MONGODB_URL = "mongodb+srv://22cs027_db_user:SathyaPainter@pha.o1mtvpd.mongodb.net/?retryWrites=true&w=majority&appName=PHA"

def test_mongodb_connection():
    """Test MongoDB Atlas connection with optimized settings."""
    print("🧪 Testing MongoDB Atlas connection...")
    print(f"📍 Target: {MONGODB_URL.split('@')[1].split('?')[0]}")
    
    try:
        start_time = time.time()
        
        # Create client with optimized settings
        client = MongoClient(
            MONGODB_URL,
            serverSelectionTimeoutMS=5000,  # 5 seconds
            connectTimeoutMS=10000,         # 10 seconds
            socketTimeoutMS=10000,          # 10 seconds
            retryWrites=True,
            retryReads=True,
            directConnection=False,
            heartbeatFrequencyMS=5000
        )
        
        # Test connection
        print("⏳ Attempting connection...")
        result = client.admin.command('ping')
        connection_time = time.time() - start_time
        
        print(f"✅ SUCCESS! Connected in {connection_time:.2f} seconds")
        print(f"📊 Ping result: {result}")
        
        # Test database access
        db = client['pha_connections']
        collections = db.list_collection_names()
        print(f"📂 Available collections: {collections}")
        
        client.close()
        return True
        
    except Exception as e:
        connection_time = time.time() - start_time
        print(f"❌ FAILED after {connection_time:.2f} seconds")
        print(f"🔍 Error: {e}")
        print(f"🔍 Error type: {type(e).__name__}")
        return False

if __name__ == "__main__":
    success = test_mongodb_connection()
    if success:
        print("\n🎉 MongoDB Atlas connection is working correctly!")
    else:
        print("\n⚠️  MongoDB Atlas connection failed. Check network/credentials.")