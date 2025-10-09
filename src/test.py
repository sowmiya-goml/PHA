from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Dict, Any
from schemas.custom_query import CustomQueryRequest, CustomQueryResponse
from services.custom_query_service import CustomQueryService
from services.bedrock_service import BedrockService
from services.database_operation_service import DatabaseOperationService
from db.session import get_database_manager, DatabaseManager
from schemas.database_operations import QueryExecutionResponse
from schemas.schema import PatientSummary, PatientRequest
from services.agent_services import PatientService
from api.dashboard import PatientDashboardService
from tools import custom_query, patient_service, patient_dashboard_service, generate_patient_observ, generate_vitals_summary_endpoint
from api.agents import get_patient_service

router = APIRouter(
    prefix="/test-custom-query",
    tags=["Test Custom Query Agent"],
    responses={404: {"description": "Not found"}}
)

@router.get("/health")
async def health_check():
    """Simple health check endpoint to verify router is working"""
    return {"status": "healthy", "message": "Test router is working"}

@router.post("/process-test", response_model=CustomQueryResponse)
async def process_custom_query_test(
    request: CustomQueryRequest,
    service: CustomQueryService = Depends(custom_query)
):
    """Process a custom database query with natural language input."""
    try:
        result = await service.process_custom_query(
            connection_id=request.connection_id,
            user_query=request.user_query
        )
        
        return CustomQueryResponse(**result)
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing custom query: {str(e)}"
        )

@router.get("/test-patient", response_model=QueryExecutionResponse)
async def get_patient_info(
    connection_id: str = Query(..., description="Database connection ID"),
    patient_id: str = Query(..., description="Patient ID"),
    patient_service: PatientService = Depends(patient_service)
):
    """Test endpoint for patient service"""
    return await patient_service.get_patient_info(connection_id, patient_id)

@router.get("/test-patient-dashboard")
async def get_patient_dashboard_data(
    patient_id: str = Query(..., description="Patient ID to fetch all dashboard data"),
    connection_id: str = Query(..., description="Database connection ID to use for fetching data"),
    dashboard_service: PatientDashboardService = Depends(patient_dashboard_service)
):
    """Test endpoint for patient dashboard service from tools.py."""
    try:
        result = await dashboard_service.get_all_patient_data(patient_id, connection_id)
        
        return {
            "status": "success",
            "patient_id": patient_id,
            "connection_id": connection_id,
            "data": result,
            "message": f"Successfully fetched all dashboard data for patient {patient_id}"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching patient dashboard data: {str(e)}"
        )

@router.get("/test-epic-patient-agent/{organization}/{patient_id}", response_model=PatientSummary)
async def test_generate_patient_observ(patient_id: str,organization: str):
    print(patient_id,organization)
    return await generate_patient_observ(patient_id, organization)

@router.get("/test-cerner-vitals-agent/{organization}/{patient_id}")
async def test_generate_vitals_summary_endpoint(patient_id: str, organization: str):
    return await generate_vitals_summary_endpoint(patient_id, organization)

