"""Debug Snowflake databases and schemas to understand the structure."""

import asyncio
import snowflake.connector
from urllib.parse import urlparse, parse_qs


async def debug_snowflake_structure():
    """Debug what databases, schemas, and tables are available in Snowflake."""
    
    print("🔍 Debugging Snowflake Database Structure")
    print("=" * 50)
    
    # Connection string from our working connection
    connection_string = "snowflake://sowmiya:Sowmiya22112004@qgkxkwg-mr95865.ap-south-1.aws.snowflakecomputing.com/pha/my_schema?warehouse=COMPUTE_WH&role=SYSADMIN"
    
    try:
        # Parse connection string with the same logic as our service
        parsed = urlparse(connection_string)
        hostname = parsed.hostname
        account = hostname.replace('.snowflakecomputing.com', '')
        
        # Use account without region (same logic as connection service)
        if '.ap-south-1.aws' in account:
            account = account.replace('.ap-south-1.aws', '')
        
        # Path components
        path_parts = [p for p in parsed.path.split('/') if p]
        database = path_parts[0] if len(path_parts) > 0 else 'PHA'
        schema = path_parts[1] if len(path_parts) > 1 else 'PUBLIC'
        
        # Parse query parameters
        query_params = parse_qs(parsed.query)
        warehouse = query_params.get('warehouse', [''])[0]
        role = query_params.get('role', [''])[0]
        
        conn_params = {
            'user': parsed.username,
            'password': parsed.password,
            'account': account,
            'database': database,
            'schema': schema,
            'warehouse': warehouse,
            'role': role
        }
        
        print("🔗 Connection Parameters:")
        for key, value in conn_params.items():
            if key == 'password':
                print(f"  {key}: {'*' * len(value)}")
            else:
                print(f"  {key}: {value}")
        print()
        
        # Connect to Snowflake
        print("🔌 Connecting to Snowflake...")
        conn = snowflake.connector.connect(**conn_params)
        cursor = conn.cursor()
        
        # Check current context
        print("📍 Current Context:")
        cursor.execute("SELECT CURRENT_DATABASE(), CURRENT_SCHEMA(), CURRENT_WAREHOUSE(), CURRENT_ROLE()")
        context = cursor.fetchone()
        print(f"  Database: {context[0]}")
        print(f"  Schema: {context[1]}")
        print(f"  Warehouse: {context[2]}")
        print(f"  Role: {context[3]}")
        print()
        
        # List all databases
        print("🗄️ Available Databases:")
        cursor.execute("SHOW DATABASES")
        databases = cursor.fetchall()
        for db in databases[:10]:  # Show first 10
            print(f"  - {db[1]} (created: {db[0]})")
        if len(databases) > 10:
            print(f"  ... and {len(databases) - 10} more")
        print()
        
        # List schemas in current database
        print(f"📂 Schemas in Database '{context[0]}':")
        cursor.execute(f"SHOW SCHEMAS IN DATABASE {context[0]}")
        schemas = cursor.fetchall()
        for schema_info in schemas[:10]:  # Show first 10
            print(f"  - {schema_info[1]} (created: {schema_info[0]})")
        if len(schemas) > 10:
            print(f"  ... and {len(schemas) - 10} more")
        print()
        
        # List tables in current schema
        print(f"📋 Tables in Schema '{context[0]}.{context[1]}':")
        cursor.execute(f"SHOW TABLES IN SCHEMA {context[0]}.{context[1]}")
        tables = cursor.fetchall()
        if tables:
            for table in tables:
                print(f"  - {table[1]} (type: {table[3]}, rows: {table[4]})")
        else:
            print("  No tables found in current schema")
        print()
        
        # Try information_schema query directly
        print("📊 Trying INFORMATION_SCHEMA query:")
        try:
            cursor.execute(f"""
                SELECT 
                    TABLE_NAME,
                    TABLE_TYPE,
                    ROW_COUNT
                FROM INFORMATION_SCHEMA.TABLES 
                WHERE TABLE_SCHEMA = '{context[1]}'
                    AND TABLE_CATALOG = '{context[0]}'
                ORDER BY TABLE_NAME
            """)
            info_tables = cursor.fetchall()
            print(f"  Found {len(info_tables)} tables via INFORMATION_SCHEMA")
            for table in info_tables:
                print(f"    - {table[0]} (type: {table[1]}, rows: {table[2]})")
        except Exception as e:
            print(f"  ❌ INFORMATION_SCHEMA query failed: {e}")
        print()
        
        # Try different schemas that might have data
        test_schemas = ['PUBLIC', 'INFORMATION_SCHEMA', schema.upper(), 'MY_SCHEMA']
        for test_schema in test_schemas:
            if test_schema != context[1]:  # Skip current schema, already checked
                print(f"🔍 Checking schema '{test_schema}':")
                try:
                    cursor.execute(f"SHOW TABLES IN SCHEMA {context[0]}.{test_schema}")
                    test_tables = cursor.fetchall()
                    if test_tables:
                        print(f"  Found {len(test_tables)} tables:")
                        for table in test_tables[:5]:  # Show first 5
                            print(f"    - {table[1]} (type: {table[3]})")
                        if len(test_tables) > 5:
                            print(f"    ... and {len(test_tables) - 5} more")
                    else:
                        print("  No tables found")
                except Exception as e:
                    print(f"  ❌ Error accessing schema: {e}")
                print()
        
        # Close connection
        cursor.close()
        conn.close()
        
        print("✅ Debug completed!")
        
    except Exception as e:
        print(f"❌ Error during debugging: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(debug_snowflake_structure())