"""Patient dashboard API controller with LLM-powered query generation."""

import logging
from typing import Dict, Any
from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends, Path, Query

from services.dashboard_service import PatientDashboardService
from services.bedrock_service import BedrockService
from services.database_operation_service import DatabaseOperationService
from db.session import get_database_manager, DatabaseManager

logger = logging.getLogger(__name__)


class PatientDashboardController:
    """Controller for patient dashboard endpoints using LLM-generated queries."""
    
    def __init__(self):
        """Initialize the patient dashboard controller."""
        self.router = APIRouter()
        self._setup_routes()
    
    def get_dashboard_service(self, db_manager: DatabaseManager = Depends(get_database_manager)) -> PatientDashboardService:
        """Dependency to get dashboard service with LLM capabilities."""
        bedrock_service = BedrockService(db_manager)
        db_ops_service = DatabaseOperationService(db_manager)
        return PatientDashboardService(db_manager, bedrock_service, db_ops_service)
    
    def _setup_routes(self):
        """Setup routes for patient dashboard endpoints."""
        
        @self.router.get("/patients_dashboard/{patient_id}/all")
        async def get_patient_all_data(
            patient_id: str = Path(..., description="Patient ID to fetch all vital data"),
            connection_id: str = Query(..., description="Database connection ID to use for fetching data"),
            dashboard_service: PatientDashboardService = Depends(self.get_dashboard_service)
        ):
            """
            Get all vital signs data for a patient using LLM-generated queries.
            
            This endpoint:
            1. Gets database schema for the connection
            2. Uses LLM to generate appropriate queries for each vital sign type
            3. Executes the queries and returns structured data
            """
            try:
                result = await dashboard_service.get_all_patient_data(patient_id, connection_id)
                
                return {
                    "status": "success",
                    "patient_id": patient_id,
                    "connection_id": connection_id,
                    "timestamp": datetime.now().isoformat(),
                    "data": result,
                    "message": f"Successfully retrieved all vital data for patient {patient_id}"
                }
                
            except Exception as e:
                logger.error(f"Error in get_patient_all_data: {str(e)}")
                raise HTTPException(
                    status_code=500,
                    detail=f"Failed to fetch patient data: {str(e)}"
                )

# Create controller instance and get router
dashboard_controller = PatientDashboardController()
router = dashboard_controller.router