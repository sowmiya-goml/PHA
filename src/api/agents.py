"""Combined healthcare agents API router."""

from fastapi import APIRouter, Query, Depends
from services.agent_services import (
    PatientService, MedicationService, FollowupService, ConditionService,
    LabResultService, ProcedureService, AllergyService, AppointmentService, DietService
)
from services.bedrock_service import BedrockService
from services.database_operation_service import DatabaseOperationService
from schemas.healthcare import HealthcareQueryResponse
from typing import List, Dict, Any
from schemas.database_operations import QueryExecutionResponse
from db.session import get_database_manager

# Base service dependencies
def get_bedrock_service(db_manager=Depends(get_database_manager)) -> BedrockService:
    return BedrockService(db_manager)

def get_db_ops_service(db_manager=Depends(get_database_manager)) -> DatabaseOperationService:
    return DatabaseOperationService(db_manager)

# Healthcare service dependencies
def get_patient_service(
    db_manager=Depends(get_database_manager),
    bedrock_service=Depends(get_bedrock_service),
    db_ops_service=Depends(get_db_ops_service)
) -> PatientService:
    return PatientService(db_manager, bedrock_service, db_ops_service)

def get_medication_service(
    db_manager=Depends(get_database_manager),
    bedrock_service=Depends(get_bedrock_service),
    db_ops_service=Depends(get_db_ops_service)
) -> MedicationService:
    return MedicationService(db_manager, bedrock_service, db_ops_service)

def get_followup_service(
    db_manager=Depends(get_database_manager),
    bedrock_service=Depends(get_bedrock_service),
    db_ops_service=Depends(get_db_ops_service)
) -> FollowupService:
    return FollowupService(db_manager, bedrock_service, db_ops_service)

def get_condition_service(
    db_manager=Depends(get_database_manager),
    bedrock_service=Depends(get_bedrock_service),
    db_ops_service=Depends(get_db_ops_service)
) -> ConditionService:
    return ConditionService(db_manager, bedrock_service, db_ops_service)

def get_lab_result_service(
    db_manager=Depends(get_database_manager),
    bedrock_service=Depends(get_bedrock_service),
    db_ops_service=Depends(get_db_ops_service)
) -> LabResultService:
    return LabResultService(db_manager, bedrock_service, db_ops_service)

def get_procedure_service(
    db_manager=Depends(get_database_manager),
    bedrock_service=Depends(get_bedrock_service),
    db_ops_service=Depends(get_db_ops_service)
) -> ProcedureService:
    return ProcedureService(db_manager, bedrock_service, db_ops_service)

def get_allergy_service(
    db_manager=Depends(get_database_manager),
    bedrock_service=Depends(get_bedrock_service),
    db_ops_service=Depends(get_db_ops_service)
) -> AllergyService:
    return AllergyService(db_manager, bedrock_service, db_ops_service)

def get_appointment_service(
    db_manager=Depends(get_database_manager),
    bedrock_service=Depends(get_bedrock_service),
    db_ops_service=Depends(get_db_ops_service)
) -> AppointmentService:
    return AppointmentService(db_manager, bedrock_service, db_ops_service)

def get_diet_service(
    db_manager=Depends(get_database_manager),
    bedrock_service=Depends(get_bedrock_service),
    db_ops_service=Depends(get_db_ops_service)
) -> DietService:
    return DietService(db_manager, bedrock_service, db_ops_service)

router = APIRouter()

# API endpoints
@router.get("/patient", response_model=QueryExecutionResponse)
async def get_patient_info(
    connection_id: str = Query(..., description="Database connection ID"),
    patient_id: str = Query(..., description="Patient ID"),
    patient_service: PatientService = Depends(get_patient_service)
):
    """Get patient demographic information."""
    return await patient_service.get_patient_info(connection_id, patient_id)

@router.get("/medication", response_model=QueryExecutionResponse)
async def get_medication_info(
    connection_id: str = Query(..., description="Database connection ID"),
    patient_id: str = Query(..., description="Patient ID"),
    medication_service: MedicationService = Depends(get_medication_service)
):
    """Get medication history and interactions."""
    return await medication_service.get_medications(connection_id, patient_id)

@router.get("/followup", response_model=QueryExecutionResponse)
async def get_followup_info(
    connection_id: str = Query(..., description="Database connection ID"),
    patient_id: str = Query(..., description="Patient ID"),
    followup_service: FollowupService = Depends(get_followup_service)
):
    """Get follow-up appointments and care plans."""
    return await followup_service.get_followups(connection_id, patient_id)

@router.get("/condition", response_model=QueryExecutionResponse)
async def get_condition_info(
    connection_id: str = Query(..., description="Database connection ID"),
    patient_id: str = Query(..., description="Patient ID"),
    condition_service: ConditionService = Depends(get_condition_service)
):
    """Get medical conditions and diagnoses."""
    return await condition_service.get_conditions(connection_id, patient_id)

@router.get("/lab-results", response_model=QueryExecutionResponse)
async def get_lab_result_info(
    connection_id: str = Query(..., description="Database connection ID"),
    patient_id: str = Query(..., description="Patient ID"),
    lab_result_service: LabResultService = Depends(get_lab_result_service)
):
    """Get laboratory test results."""
    return await lab_result_service.get_lab_results(connection_id, patient_id)

@router.get("/procedure", response_model=QueryExecutionResponse)
async def get_procedure_info(
    connection_id: str = Query(..., description="Database connection ID"),
    patient_id: str = Query(..., description="Patient ID"),
    procedure_service: ProcedureService = Depends(get_procedure_service)
):
    """Get medical procedures history."""
    return await procedure_service.get_procedures(connection_id, patient_id)

@router.get("/allergy", response_model=QueryExecutionResponse)
async def get_allergy_info(
    connection_id: str = Query(..., description="Database connection ID"),
    patient_id: str = Query(..., description="Patient ID"),
    allergy_service: AllergyService = Depends(get_allergy_service)
):
    """Get allergy information."""
    return await allergy_service.get_allergies(connection_id, patient_id)

@router.get("/appointment", response_model=QueryExecutionResponse)
async def get_appointment_info(
    connection_id: str = Query(..., description="Database connection ID"),
    patient_id: str = Query(..., description="Patient ID"),
    appointment_service: AppointmentService = Depends(get_appointment_service)
):
    """Get appointment schedule."""
    return await appointment_service.get_appointments(connection_id, patient_id)

@router.get("/diet", response_model=QueryExecutionResponse)
async def get_diet_info(
    connection_id: str = Query(..., description="Database connection ID"),
    patient_id: str = Query(..., description="Patient ID"),
    diet_service: DietService = Depends(get_diet_service)
):
    """Get dietary information and restrictions."""
    return await diet_service.get_diet_info(connection_id, patient_id)