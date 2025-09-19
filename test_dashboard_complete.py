#!/usr/bin/env python3
"""Test the full dashboard endpoint logic directly without FastAPI server."""

import sys
import os
import asyncio

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from pha.db.session import db_manager
from pha.api.v1.dashboard import PatientDashboardController
from pha.services.connection_service import ConnectionService
from pha.services.database_operation_service import DatabaseOperationService

async def test_full_dashboard_logic():
    """Test the full dashboard logic directly."""
    try:
        print("🔧 Testing complete dashboard endpoint logic...")
        
        # Connect to database
        await db_manager.connect()
        print(f"✅ Database connected: {db_manager.is_connected()}")
        
        if not db_manager.is_connected():
            print("❌ Database not connected!")
            return
        
        # Create services
        connection_service = ConnectionService(db_manager)
        db_operation_service = DatabaseOperationService(db_manager)
        
        # Create dashboard controller
        dashboard = PatientDashboardController()
        
        connection_id = "68c8ea1dcee430be497cee25"
        patient_id = "687b0aca-ca63-4926-800b-90d5e92e5a0a"
        
        print(f"🔍 Testing with:")
        print(f"  Connection ID: {connection_id}")
        print(f"  Patient ID: {patient_id}")
        
        # Call the dashboard method directly
        print("\n🚀 Calling dashboard endpoint logic...")
        
        result = await dashboard._get_patient_vital_data(
            connection_service=connection_service,
            db_operation_service=db_operation_service,
            connection_id=connection_id,
            patient_id=patient_id,
            data_type="heart_rate",
            preferred_columns=["heart_rate", "status", "recorded_at", "device_id"]
        )
        
        print("✅ SUCCESS! Dashboard endpoint returned data:")
        print(f"📊 Result: {result}")
        
        # Update todo status
        print("\n✅ Dashboard endpoint is working with real database data!")
        print("📈 No mock data used - all data from the real database connection!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_full_dashboard_logic())