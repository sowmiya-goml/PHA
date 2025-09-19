"""Check available database connections."""

import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

# Set environment variables from config
config_file = Path(__file__).parent / 'config' / '.env'
if config_file.exists():
    with open(config_file, 'r') as f:
        for line in f:
            if line.strip() and '=' in line and not line.startswith('#'):
                key, value = line.strip().split('=', 1)
                os.environ[key] = value

from pha.db.session import DatabaseManager


def check_connections():
    """Check what database connections are available."""
    
    print("🔍 Checking Available Database Connections")
    print("=" * 50)
    
    try:
        # Initialize database
        db_manager = DatabaseManager()
        db_manager.connect_sync()  # Use synchronous connection
        
        collection = db_manager.get_connections_collection()
        connections = list(collection.find({}))
        
        print(f"Found {len(connections)} connection(s):")
        
        for conn in connections:
            conn_id = str(conn.get('_id', 'Unknown'))
            conn_name = conn.get('connection_name', 'Unknown')
            db_type = conn.get('database_type', 'Unknown')
            
            print(f"  - ID: {conn_id}")
            print(f"    Name: {conn_name}")
            print(f"    Type: {db_type}")
            print()
            
        if connections:
            print("You can use any of these connection IDs to test the API endpoint.")
        else:
            print("No connections found. You may need to create a connection first.")
        
    except Exception as e:
        print(f"❌ Error checking connections: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    check_connections()