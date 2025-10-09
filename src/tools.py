from services.dashboard_service import PatientDashboardService
from db.session import get_database_manager, DatabaseManager
from fastapi import Depends
from services.bedrock_service import BedrockService
from services.database_operation_service import DatabaseOperationService
from services.agent_services import AllergyService, AppointmentService, ConditionService, DietService, FollowupService, LabResultService, MedicationService, PatientService, ProcedureService
from services.custom_query_service import CustomQueryService
from api.dashboard import dashboard_controller
from services.epic import generate_patient_summary, generate_Followup_summary, generate_medication_summary, generate_condition_summary, generate_lab_summary, generate_procedure_summary, generate_allergy_summary, generate_upcoming_appointment_summary, generate_nutrition_summary, get_diet, risk, generate_aftercare_summary, fetch_epic_observations, generate_vitals_summary
from services.cerner import generate_cerner_diagnosis_summary, generate_cerner_medication_summary, generate_cerner_patient_summary, generate_cerner_lab_summary, generate_cerner_followup_summary, generate_procedure_summary, generate_allergy_summary, generate_upcoming_cappointment_summary, generate_nutrition_summary, get_diet, risk, generate_aftercare_summary, generate_vitals_summary


def custom_query(db_manager: DatabaseManager = Depends(get_database_manager)):
    bedrock_service = BedrockService(db_manager)
    db_ops_service = DatabaseOperationService(db_manager)
    return CustomQueryService(db_manager, bedrock_service, db_ops_service)

def patient_service(db_manager: DatabaseManager = Depends(get_database_manager)):
    bedrock_service = BedrockService(db_manager)
    db_ops_service = DatabaseOperationService(db_manager)
    return PatientService(db_manager, bedrock_service, db_ops_service)

def medication_service(db_manager: DatabaseManager = Depends(get_database_manager)):
    bedrock_service = BedrockService(db_manager)
    db_ops_service = DatabaseOperationService(db_manager)
    return MedicationService(db_manager, bedrock_service, db_ops_service)

def followup_service(db_manager: DatabaseManager = Depends(get_database_manager)):
    bedrock_service = BedrockService(db_manager)
    db_ops_service = DatabaseOperationService(db_manager)
    return FollowupService(db_manager, bedrock_service, db_ops_service)

def condition_service(db_manager: DatabaseManager = Depends(get_database_manager)):
    bedrock_service = BedrockService(db_manager)
    db_ops_service = DatabaseOperationService(db_manager)
    return ConditionService(db_manager, bedrock_service, db_ops_service)

def lab_service(db_manager: DatabaseManager = Depends(get_database_manager)):
    bedrock_service = BedrockService(db_manager)
    db_ops_service = DatabaseOperationService(db_manager)
    return LabResultService(db_manager, bedrock_service, db_ops_service)

def procedure_service(db_manager: DatabaseManager = Depends(get_database_manager)):
    bedrock_service = BedrockService(db_manager)
    db_ops_service = DatabaseOperationService(db_manager)
    return ProcedureService(db_manager, bedrock_service, db_ops_service)

def allergy_service(db_manager: DatabaseManager = Depends(get_database_manager)):
    bedrock_service = BedrockService(db_manager)
    db_ops_service = DatabaseOperationService(db_manager)
    return AllergyService(db_manager, bedrock_service, db_ops_service)

def appointment_service(db_manager: DatabaseManager = Depends(get_database_manager)):
    bedrock_service = BedrockService(db_manager)
    db_ops_service = DatabaseOperationService(db_manager)
    return AppointmentService(db_manager, bedrock_service, db_ops_service)

def diet_service(db_manager: DatabaseManager = Depends(get_database_manager)):
    bedrock_service = BedrockService(db_manager)
    db_ops_service = DatabaseOperationService(db_manager)
    return DietService(db_manager, bedrock_service, db_ops_service)

def patient_dashboard_service(db_manager: DatabaseManager = Depends(get_database_manager)):
    bedrock_service = BedrockService(db_manager)
    db_ops_service = DatabaseOperationService(db_manager)
    return PatientDashboardService(db_manager, bedrock_service, db_ops_service)

#epic
async def generate_patient_observ(patient_id: str,organization: str):
    print(patient_id,organization)
    return await generate_patient_summary(patient_id, organization)

async def generate_medication(patient_id: str,organization: str):
    return await generate_medication_summary(patient_id, organization)

async def generate_agent_Response_followup(patient_id: str,organization: str):
    return await generate_Followup_summary(patient_id, organization)

async def generate_condition(patient_id: str,organization: str):
    return await generate_condition_summary(patient_id, organization)

async def generate_lab(patient_id: str,organization: str):
    return await generate_lab_summary(patient_id, organization)

async def generate_procedure(patient_id: str,organization: str):
    return await generate_procedure_summary(patient_id, organization)

async def generate_allergy(patient_id: str,organization: str):
    return await generate_allergy_summary(patient_id, organization)

async def generate_agent_Response_upcoming(patient_id: str,organization: str):
    return await generate_upcoming_appointment_summary(patient_id, organization)

async def generate_agent_Response_nutrition(patient_id: str,organization: str):
    return await generate_nutrition_summary(patient_id, organization)

async def get_diet_data(patient_id: str,organization: str):
    return await get_diet(patient_id, organization)

async def riskpanel(patient_id: str,organization: str):
    return await risk(patient_id, organization)

async def aftercare(patient_id: str,organization: str):
    return await generate_aftercare_summary(patient_id, organization)

async def get_patient_vitals(patient_id: str, organization: str):
    return await generate_vitals_summary(patient_id, organization)

#cerner
async def generate_summary_patient(patient_id: str,organization: str):
    return await generate_cerner_patient_summary(patient_id,organization)

async def generate_summary_medication(patient_id: str,organization: str):
    return await generate_cerner_medication_summary(patient_id,organization)

async def generate_summary_diagnosis(patient_id: str,organization: str):
    return await generate_cerner_diagnosis_summary(patient_id,organization)

async def generate_summary_followup(patient_id: str,organization: str):
    return await generate_cerner_followup_summary(patient_id,organization)

async def generate_summary_lab(patient_id: str,organization: str):
    print(patient_id)
    return await generate_cerner_lab_summary(patient_id,organization)

async def generate_Procedure_summary(patient_id: str,organization: str):
    return await generate_procedure_summary(patient_id,organization)

async def generate_allergy(patient_id: str,organization: str):
    return await generate_allergy_summary(patient_id,organization)

async def generate_agent_Response_followup(patient_id: str,organization: str):
    return await generate_upcoming_cappointment_summary(patient_id, organization)

async def generate_agent_Response_nutrition(patient_id: str,organization: str):
    return await generate_nutrition_summary(patient_id, organization)

async def get_diet_data(patient_id: str,organization: str):
    return await get_diet(patient_id, organization)

async def riskpanel(patient_id: str,organization: str):
    return await risk(patient_id, organization)

async def aftercare(patient_id: str,organization: str):
    return await generate_aftercare_summary(patient_id, organization)

async def generate_vitals_summary_endpoint(patient_id: str, organization: str):
    return await generate_vitals_summary(patient_id, organization)


