# filepath: src/api/agents.py
"""Combined healthcare agents API router."""

from fastapi import APIRouter, Query, Depends
from services.agent_services import (
    PatientService, MedicationService, FollowupService, ConditionService,
    LabResultService, ProcedureService, AllergyService, AppointmentService, DietService
)
from schemas.healthcare import HealthcareQueryResponse
from typing import List, Dict, Any
from db.session import get_database_manager

# Dependency functions
def get_patient_service() -> PatientService:
    return PatientService(get_database_manager())

def get_medication_service() -> MedicationService:
    return MedicationService(get_database_manager())

def get_followup_service() -> FollowupService:
    return FollowupService(get_database_manager())

def get_condition_service() -> ConditionService:
    return ConditionService(get_database_manager())

def get_lab_result_service() -> LabResultService:
    return LabResultService(get_database_manager())

def get_procedure_service() -> ProcedureService:
    return ProcedureService(get_database_manager())

def get_allergy_service() -> AllergyService:
    return AllergyService(get_database_manager())

def get_appointment_service() -> AppointmentService:
    return AppointmentService(get_database_manager())

def get_diet_service() -> DietService:
    return DietService(get_database_manager())

router = APIRouter()

# Patient Agent
@router.get("/patient", response_model=List[Dict[str, Any]])
async def get_patient_info(
    connection_id: str = Query(..., description="Database connection ID"),
    patient_id: str = Query(..., description="Patient ID"),
    patient_service: PatientService = Depends(get_patient_service)
):
    """Get patient demographic and profile information."""
    result = await patient_service.process_query(connection_id, patient_id)
    if result.execution_results and len(result.execution_results) > 0:
        return result.execution_results[0].data
    return []

# Medication Agent
@router.get("/medication", response_model=List[Dict[str, Any]])
async def get_medication_info(
    connection_id: str = Query(..., description="Database connection ID"),
    patient_id: str = Query(..., description="Patient ID"),
    medication_service: MedicationService = Depends(get_medication_service)
):
    """Get medication history and interactions."""
    result = await medication_service.process_query(connection_id, patient_id)
    return result

# Follow-up Agent
@router.get("/followup", response_model=List[Dict[str, Any]])
async def get_followup_info(
    connection_id: str = Query(..., description="Database connection ID"),
    patient_id: str = Query(..., description="Patient ID"),
    followup_service: FollowupService = Depends(get_followup_service)
):
    """Get follow-up care and appointment information."""
    result = await followup_service.process_query(connection_id, patient_id)
    return result

# Condition Agent
@router.get("/condition", response_model=List[Dict[str, Any]])
async def get_condition_info(
    connection_id: str = Query(..., description="Database connection ID"),
    patient_id: str = Query(..., description="Patient ID"),
    condition_service: ConditionService = Depends(get_condition_service)
):
    """Get medical conditions and diagnoses."""
    result = await condition_service.process_query(connection_id, patient_id)
    return result

# Lab Results Agent
@router.get("/lab-results", response_model=List[Dict[str, Any]])
async def get_lab_results_info(
    connection_id: str = Query(..., description="Database connection ID"),
    patient_id: str = Query(..., description="Patient ID"),
    lab_result_service: LabResultService = Depends(get_lab_result_service)
):
    """Get laboratory test results."""
    result = await lab_result_service.process_query(connection_id, patient_id)
    return result

# Procedure Agent
@router.get("/procedure", response_model=List[Dict[str, Any]])
async def get_procedure_info(
    connection_id: str = Query(..., description="Database connection ID"),
    patient_id: str = Query(..., description="Patient ID"),
    procedure_service: ProcedureService = Depends(get_procedure_service)
):
    """Get medical procedures and surgeries."""
    result = await procedure_service.process_query(connection_id, patient_id)
    return result

# Allergy Agent
@router.get("/allergy", response_model=List[Dict[str, Any]])
async def get_allergy_info(
    connection_id: str = Query(..., description="Database connection ID"),
    patient_id: str = Query(..., description="Patient ID"),
    allergy_service: AllergyService = Depends(get_allergy_service)
):
    """Get allergies and sensitivities."""
    result = await allergy_service.process_query(connection_id, patient_id)
    return result

# Appointment Agent
@router.get("/appointment", response_model=List[Dict[str, Any]])
async def get_appointment_info(
    connection_id: str = Query(..., description="Database connection ID"),
    patient_id: str = Query(..., description="Patient ID"),
    appointment_service: AppointmentService = Depends(get_appointment_service)
):
    """Get appointment schedules and history."""
    result = await appointment_service.process_query(connection_id, patient_id)
    return result

# Diet Agent
@router.get("/diet", response_model=List[Dict[str, Any]])
async def get_diet_info(
    connection_id: str = Query(..., description="Database connection ID"),
    patient_id: str = Query(..., description="Patient ID"),
    diet_service: DietService = Depends(get_diet_service)
):
    """Get dietary information and plans."""
    result = await diet_service.process_query(connection_id, patient_id)
    return result