"""
Simple CLI script to interact with the Database Connection API
"""
import requests
import json
from typing import Dict, Any

API_BASE_URL = "http://localhost:8000"

def create_connection(connection_data: Dict[str, Any]) -> Dict[str, Any]:
    """Create a new database connection"""
    response = requests.post(f"{API_BASE_URL}/connections", json=connection_data)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error creating connection: {response.text}")
        return {}

def get_all_connections() -> list:
    """Get all database connections"""
    response = requests.get(f"{API_BASE_URL}/connections")
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error getting connections: {response.text}")
        return []

def get_connection(connection_id: str) -> Dict[str, Any]:
    """Get a specific connection by ID"""
    response = requests.get(f"{API_BASE_URL}/connections/{connection_id}")
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error getting connection: {response.text}")
        return {}

def test_connection(connection_id: str) -> Dict[str, Any]:
    """Test a database connection"""
    response = requests.post(f"{API_BASE_URL}/connections/{connection_id}/test")
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error testing connection: {response.text}")
        return {}

def delete_connection(connection_id: str) -> Dict[str, Any]:
    """Delete a database connection"""
    response = requests.delete(f"{API_BASE_URL}/connections/{connection_id}")
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error deleting connection: {response.text}")
        return {}

def main():
    print("=== PHA Database Connection Manager CLI ===")
    
    while True:
        print("\nOptions:")
        print("1. Create a new connection")
        print("2. List all connections")
        print("3. Get specific connection")
        print("4. Test connection")
        print("5. Delete connection")
        print("6. Exit")
        
        choice = input("\nEnter your choice (1-6): ").strip()
        
        if choice == "1":
            print("\n--- Create New Connection ---")
            connection_name = input("Connection name: ")
            database_type = input("Database type (MySQL/PostgreSQL/MongoDB): ")
            host = input("Host: ")
            port = int(input("Port: "))
            database_name = input("Database name: ")
            username = input("Username: ")
            password = input("Password: ")
            additional_notes = input("Additional notes (optional): ")
            
            connection_data = {
                "connection_name": connection_name,
                "database_type": database_type,
                "host": host,
                "port": port,
                "database_name": database_name,
                "username": username,
                "password": password,
                "additional_notes": additional_notes if additional_notes else None
            }
            
            result = create_connection(connection_data)
            if result:
                print(f"✅ Connection created successfully! ID: {result['id']}")
            
        elif choice == "2":
            print("\n--- All Connections ---")
            connections = get_all_connections()
            if connections:
                for conn in connections:
                    print(f"ID: {conn['id']}")
                    print(f"Name: {conn['connection_name']}")
                    print(f"Type: {conn['database_type']}")
                    print(f"Host: {conn['host']}:{conn['port']}")
                    print(f"Database: {conn['database_name']}")
                    print(f"Username: {conn['username']}")
                    print("---")
            else:
                print("No connections found.")
        
        elif choice == "3":
            connection_id = input("Enter connection ID: ")
            connection = get_connection(connection_id)
            if connection:
                print(f"\n--- Connection Details ---")
                print(f"ID: {connection['id']}")
                print(f"Name: {connection['connection_name']}")
                print(f"Type: {connection['database_type']}")
                print(f"Host: {connection['host']}:{connection['port']}")
                print(f"Database: {connection['database_name']}")
                print(f"Username: {connection['username']}")
                print(f"Password: {connection['password']}")
                if connection['additional_notes']:
                    print(f"Notes: {connection['additional_notes']}")
                print(f"Created: {connection['created_at']}")
        
        elif choice == "4":
            connection_id = input("Enter connection ID to test: ")
            result = test_connection(connection_id)
            if result:
                print(f"\n--- Test Result ---")
                print(f"Status: {result['status']}")
                print(f"Message: {result['message']}")
        
        elif choice == "5":
            connection_id = input("Enter connection ID to delete: ")
            confirm = input("Are you sure? (yes/no): ")
            if confirm.lower() == "yes":
                result = delete_connection(connection_id)
                if result:
                    print("✅ Connection deleted successfully!")
        
        elif choice == "6":
            print("Goodbye!")
            break
        
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
