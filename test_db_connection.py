#!/usr/bin/env python3
"""Test database connection directly."""

import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from pha.db.session import db_manager
from pha.services.connection_service import ConnectionService
import asyncio

async def test_db_connection():
    """Test database connection."""
    try:
        print("Testing database connection...")
        
        # Try to connect to the database
        connected = await db_manager.connect()
        print(f"Database connected: {connected}")
        print(f"Is connected: {db_manager.is_connected()}")
        
        if db_manager.is_connected():
            print("Creating connection service...")
            connection_service = ConnectionService(db_manager)
            
            print("Testing connection ID...")
            connection = await connection_service.get_connection_by_id("68c8ea1dcee430be497cee25")
            print(f"Connection found: {connection is not None}")
            if connection:
                print(f"Connection name: {connection.connection_name}")
                print(f"Database type: {connection.database_type}")
                
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_db_connection())