"""Debug and fix Snowflake connection issues."""

import asyncio
from urllib.parse import urlparse, parse_qs


def analyze_snowflake_connection():
    """Analyze the Snowflake connection string for potential issues."""
    
    # Your original connection string
    connection_string = "snowflake://sowmiya:Sowmiya22112004@qgkxkwg-mr95865.ap-south-1.aws.snowflakecomputing.com/pha/my_schema?warehouse=COMPUTE_WH&role=SYSADMIN"
    
    print("🔍 Analyzing Snowflake connection string...")
    print(f"Original: {connection_string}")
    print()
    
    # Parse the connection string
    parsed = urlparse(connection_string)
    
    print("📋 Parsed components:")
    print(f"Username: {parsed.username}")
    print(f"Password: {'*' * len(parsed.password) if parsed.password else 'None'}")
    print(f"Hostname: {parsed.hostname}")
    print(f"Path: {parsed.path}")
    print(f"Query: {parsed.query}")
    print()
    
    # Extract account identifier
    account_from_hostname = parsed.hostname.replace('.snowflakecomputing.com', '')
    print(f"🏢 Account identifier extracted: {account_from_hostname}")
    
    # Parse path components
    path_parts = [p for p in parsed.path.split('/') if p]
    database = path_parts[0] if len(path_parts) > 0 else 'PHA'
    schema = path_parts[1] if len(path_parts) > 1 else 'PUBLIC'
    
    print(f"🗄️ Database: {database}")
    print(f"📊 Schema: {schema}")
    
    # Parse query parameters
    query_params = parse_qs(parsed.query)
    warehouse = query_params.get('warehouse', [''])[0]
    role = query_params.get('role', [''])[0]
    
    print(f"🏭 Warehouse: {warehouse}")
    print(f"👤 Role: {role}")
    print()
    
    # Common issues and fixes
    print("🚨 Potential Issues & Fixes:")
    print()
    
    # Issue 1: Account identifier format
    print("1. Account Identifier Format:")
    print(f"   Current: {account_from_hostname}")
    
    # Snowflake account identifiers can have different formats:
    # - Legacy: account_name (e.g., "xy12345")
    # - Modern: orgname-account_name (e.g., "myorg-myaccount")
    # - With region: account_name.region (e.g., "xy12345.ap-south-1.aws")
    
    if '.ap-south-1.aws' in account_from_hostname:
        # Extract just the account part
        account_only = account_from_hostname.replace('.ap-south-1.aws', '')
        print(f"   ✅ Region included in account. Try account only: {account_only}")
        suggested_account = account_only
    else:
        suggested_account = account_from_hostname
        print(f"   💡 Try with region: {account_from_hostname}.ap-south-1.aws")
    
    print()
    
    # Issue 2: Connection parameters for Snowflake
    print("2. Suggested Connection Parameters:")
    
    # Method 1: Without region in account (Snowflake auto-detects)
    params_v1 = {
        'user': parsed.username,
        'password': parsed.password,
        'account': suggested_account,
        'database': database,
        'schema': schema,
        'warehouse': warehouse,
        'role': role
    }
    
    # Method 2: With explicit region
    params_v2 = {
        'user': parsed.username,
        'password': parsed.password,
        'account': f"{suggested_account}.ap-south-1.aws",
        'database': database,
        'schema': schema,
        'warehouse': warehouse,
        'role': role
    }
    
    print("   Method 1 (Auto-detect region):")
    for key, value in params_v1.items():
        if key == 'password':
            print(f"     {key}: {'*' * len(value)}")
        else:
            print(f"     {key}: {value}")
    
    print()
    print("   Method 2 (Explicit region):")
    for key, value in params_v2.items():
        if key == 'password':
            print(f"     {key}: {'*' * len(value)}")
        else:
            print(f"     {key}: {value}")
    
    print()
    
    # Issue 3: Alternative connection strings
    print("3. Alternative Connection String Formats:")
    
    # Format 1: Simple account
    conn_str_1 = f"snowflake://{parsed.username}:{parsed.password}@{suggested_account}/pha/my_schema?warehouse=COMPUTE_WH&role=SYSADMIN"
    
    # Format 2: Account with region
    conn_str_2 = f"snowflake://{parsed.username}:{parsed.password}@{suggested_account}.ap-south-1.aws/pha/my_schema?warehouse=COMPUTE_WH&role=SYSADMIN"
    
    # Format 3: Legacy format with full hostname
    conn_str_3 = f"snowflake://{parsed.username}:{parsed.password}@{suggested_account}.ap-south-1.aws.snowflakecomputing.com/pha/my_schema?warehouse=COMPUTE_WH&role=SYSADMIN"
    
    print("   Option 1:")
    print(f"     {conn_str_1}")
    print()
    print("   Option 2:")
    print(f"     {conn_str_2}")
    print()
    print("   Option 3:")
    print(f"     {conn_str_3}")
    
    print()
    print("🔧 Debugging Steps:")
    print("1. Verify account identifier in Snowflake console")
    print("2. Check if account is in correct region (ap-south-1)")
    print("3. Verify user has access to specified warehouse and role")
    print("4. Test connection with Snowflake web interface first")
    print("5. Try different connection string formats above")
    
    return params_v1, params_v2


if __name__ == "__main__":
    analyze_snowflake_connection()