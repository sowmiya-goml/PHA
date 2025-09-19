"""Patient dashboard API routes."""

from fastapi import APIRouter, HTTPException, Depends

from pha.schemas.dashboard import (
    HeartRateResponse, BloodPressureResponse, BMIResponse,
    SpO2Response, TemperatureResponse, BloodSugarResponse,
    RecoveryTrackerResponse, DashboardErrorResponse, PatientNotFoundResponse
)
from pha.services.dashboard_service import DashboardService
from pha.db.session import get_database_manager, DatabaseManager
from datetime import datetime

router = APIRouter(
    prefix="/patients",
    tags=["Dashboard"],
    responses={404: {"description": "Patient not found"}}
)


def get_dashboard_service(db_manager: DatabaseManager = Depends(get_database_manager)) -> DashboardService:
    """Dependency to get dashboard service."""
    if not db_manager.is_connected():
        raise HTTPException(
            status_code=503,
            detail="Database service unavailable. Please check MongoDB connection."
        )
    return DashboardService(db_manager)


@router.get(
    "/{patient_id}/heart-rate",
    response_model=HeartRateResponse,
    summary="Get patient heart rate",
    description="Returns the latest heart rate measurement for a patient from specified database connection."
)
async def get_patient_heart_rate(
    patient_id: str,
    connection_id: str,
    service: DashboardService = Depends(get_dashboard_service)
):
    """Get latest heart rate for a patient."""
    try:
        result = await service.get_heart_rate(patient_id, connection_id)
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving heart rate data: {str(e)}"
        )


@router.get(
    "/{patient_id}/blood-pressure",
    response_model=BloodPressureResponse,
    summary="Get patient blood pressure",
    description="Returns the latest blood pressure measurement for a patient from specified database connection."
)
async def get_patient_blood_pressure(
    patient_id: str,
    connection_id: str,
    service: DashboardService = Depends(get_dashboard_service)
):
    """Get latest blood pressure for a patient."""
    try:
        result = await service.get_blood_pressure(patient_id, connection_id)
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving blood pressure data: {str(e)}"
        )


@router.get(
    "/{patient_id}/bmi",
    response_model=BMIResponse,
    summary="Get patient BMI",
    description="Returns the latest BMI measurement for a patient from specified database connection."
)
async def get_patient_bmi(
    patient_id: str,
    connection_id: str,
    service: DashboardService = Depends(get_dashboard_service)
):
    """Get latest BMI for a patient."""
    try:
        result = await service.get_bmi(patient_id, connection_id)
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving BMI data: {str(e)}"
        )


@router.get(
    "/{patient_id}/spo2",
    response_model=SpO2Response,
    summary="Get patient oxygen saturation",
    description="Returns the latest SpO2 measurement for a patient from specified database connection."
)
async def get_patient_spo2(
    patient_id: str,
    connection_id: str,
    service: DashboardService = Depends(get_dashboard_service)
):
    """Get latest oxygen saturation for a patient."""
    try:
        result = await service.get_spo2(patient_id, connection_id)
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving SpO2 data: {str(e)}"
        )


@router.get(
    "/{patient_id}/temperature",
    response_model=TemperatureResponse,
    summary="Get patient temperature",
    description="Returns the latest temperature measurement for a patient from specified database connection in both Fahrenheit and Celsius."
)
async def get_patient_temperature(
    patient_id: str,
    connection_id: str,
    service: DashboardService = Depends(get_dashboard_service)
):
    """Get latest temperature for a patient."""
    try:
        result = await service.get_temperature(patient_id, connection_id)
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving temperature data: {str(e)}"
        )


@router.get(
    "/{patient_id}/blood-sugar",
    response_model=BloodSugarResponse,
    summary="Get patient blood sugar",
    description="Returns the latest blood glucose measurement for a patient from specified database connection."
)
async def get_patient_blood_sugar(
    patient_id: str,
    connection_id: str,
    service: DashboardService = Depends(get_dashboard_service)
):
    """Get latest blood sugar for a patient."""
    try:
        result = await service.get_blood_sugar(patient_id, connection_id)
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving blood sugar data: {str(e)}"
        )


@router.get(
    "/{patient_id}/recovery-tracker",
    response_model=RecoveryTrackerResponse,
    summary="Get patient recovery tracker",
    description="Returns timeseries recovery data for a patient from specified database connection over the specified number of days (default 30)."
)
async def get_patient_recovery_tracker(
    patient_id: str,
    connection_id: str,
    days: int = 30,
    service: DashboardService = Depends(get_dashboard_service)
):
    """Get recovery tracker data for a patient."""
    try:
        if days < 1 or days > 365:
            raise HTTPException(
                status_code=400,
                detail="Days parameter must be between 1 and 365"
            )
        
        result = await service.get_recovery_tracker(patient_id, connection_id, days)
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving recovery tracker data: {str(e)}"
        )


# Additional utility endpoints for dashboard
@router.get(
    "/{patient_id}/dashboard/status",
    summary="Get dashboard data availability",
    description="Check what dashboard data is available for a patient in the specified database connection"
)
async def get_dashboard_status(
    patient_id: str,
    connection_id: str,
    service: DashboardService = Depends(get_dashboard_service)
):
    """Get dashboard data availability status for a patient."""
    try:
        # Validate connection first
        conn_info = await service.validate_connection_and_patient(connection_id, patient_id)
        connection = conn_info["connection"]
        
        # Check data availability for each vital
        collections_status = {}
        vitals = ["heart_rate", "blood_pressure", "bmi", "spo2", "temperature", "blood_sugar", "recovery_tracker"]
        
        for vital in vitals:
            try:
                if connection.database_type.lower() in ['mysql', 'postgresql', 'aurora-mysql', 'aurora-postgresql', 'sql-server', 'mssql', 'sqlserver', 'snowflake']:
                    # SQL databases - check if table exists and has data
                    query = f"SELECT COUNT(*) as count FROM {vital} WHERE patient_id = '{patient_id}' LIMIT 1"
                elif connection.database_type.lower() == 'mongodb':
                    # MongoDB - check if collection has data
                    query = {
                        "collection": vital,
                        "operation": "count",
                        "filter": {"patient_id": patient_id}
                    }
                else:
                    collections_status[vital] = False
                    continue
                
                result = await service.db_operation_service.execute_query(
                    connection_id=connection_id,
                    query=query
                )
                
                if result.success and result.data:
                    if connection.database_type.lower() == 'mongodb':
                        collections_status[vital] = result.data > 0
                    else:
                        collections_status[vital] = result.data[0].get('count', 0) > 0
                else:
                    collections_status[vital] = False
                    
            except Exception:
                collections_status[vital] = False
        
        return {
            "patient_id": patient_id,
            "connection_id": connection_id,
            "database_type": connection.database_type,
            "connection_accessible": True,
            "data_availability": collections_status,
            "has_real_data": any(collections_status.values()),
            "mock_data_used": not any(collections_status.values()),
            "timestamp": datetime.utcnow()
        }
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error checking dashboard status: {str(e)}"
        )