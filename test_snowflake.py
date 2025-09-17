"""Test Snowflake integration with the new schema extraction functionality."""

import asyncio
import json
from pha.models.connection import DatabaseConnection
from pha.services.schema_extraction_service import DatabaseSchemaExtractor


async def test_snowflake_schema():
    """Test Snowflake schema extraction."""
    
    # Create a test connection object
    connection = DatabaseConnection(
        connection_name="snowflake_mumbai",
        database_type="snowflake",
        connection_string="snowflake://sowmiya:Sowmiya22112004@qgkxkwg-mr95865.ap-south-1.aws.snowflakecomputing.com/pha/my_schema?warehouse=COMPUTE_WH&role=SYSADMIN",
        additional_notes="Snowflake account in AWS Mumbai (ap-south-1). Database set to pha.",
        host="qgkxkwg-mr95865.ap-south-1.aws.snowflakecomputing.com",
        port=443,
        database_name="pha",
        username="sowmiya",
        password="Sowmiya22112004"
    )
    
    # Test schema extraction
    extractor = DatabaseSchemaExtractor()
    print("🔄 Testing Snowflake schema extraction...")
    
    try:
        result = await extractor.extract_schema(connection)
        
        print(f"Status: {result.status}")
        print(f"Message: {result.message}")
        print(f"Database Type: {result.database_type}")
        print(f"Database Name: {result.database_name}")
        
        if result.tables:
            print(f"Tables found: {len(result.tables)}")
            for table in result.tables[:3]:  # Show first 3 tables
                print(f"  - {table.name} ({table.type}) - {table.row_count} rows")
        
        if result.unified_schema:
            print("✅ Unified schema generated successfully!")
            # Print summary
            summary = result.unified_schema.get('summary', {})
            print(f"Total tables: {summary.get('total_tables', 0)}")
            print(f"Total columns: {summary.get('total_columns', 0)}")
        
        return result
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return None


if __name__ == "__main__":
    asyncio.run(test_snowflake_schema())