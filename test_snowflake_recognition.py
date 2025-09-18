"""Test that Snowflake is now recognized as a supported database type."""

import asyncio
from pha.models.connection import DatabaseConnection
from pha.services.schema_extraction_service import DatabaseSchemaExtractor


async def test_snowflake_recognition():
    """Test that Snowflake is recognized as a supported database type."""
    
    # Create a test connection with invalid credentials to test recognition only
    connection = DatabaseConnection(
        connection_name="test_snowflake",
        database_type="snowflake",
        connection_string="snowflake://test:test@invalid-account/test/test",
        host="invalid-account.snowflakecomputing.com",
        port=443,
        database_name="test",
        username="test",
        password="test"
    )
    
    # Test schema extraction
    extractor = DatabaseSchemaExtractor()
    print("🔄 Testing Snowflake type recognition...")
    
    # Test the normalization first
    normalized_type = extractor._normalize_db_type("snowflake")
    print(f"Normalized type: {normalized_type}")
    
    try:
        result = await extractor.extract_schema(connection)
        
        print(f"Status: {result.status}")
        print(f"Message: {result.message}")
        
        # Check if we get the old "Unsupported database type" error
        if "Unsupported database type" in result.message:
            print("❌ Still getting 'Unsupported database type' error!")
            return False
        elif "snowflake-connector-python package is not installed" in result.message:
            print("❌ Package not found error (but type is recognized)")
            return False
        elif "Failed to extract Snowflake schema" in result.message:
            print("✅ Snowflake is recognized! (Connection failed as expected with test credentials)")
            return True
        else:
            print(f"✅ Snowflake support working! Message: {result.message}")
            return True
        
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        return False


if __name__ == "__main__":
    success = asyncio.run(test_snowflake_recognition())
    if success:
        print("🎉 Snowflake support successfully added!")
    else:
        print("💥 Snowflake support still has issues!")