from api.dashboard import PatientDashboardService
from db.session import get_database_manager, DatabaseManager
from fastapi import Depends
from services.bedrock_service import BedrockService
from services.database_operation_service import DatabaseOperationService
from services.agent_services import AllergyService, AppointmentService, ConditionService, DietService, FollowupService, LabResultService, MedicationService, PatientService, ProcedureService
from services.custom_query_service import CustomQueryService
from api.dashboard import dashboard_controller
from services.connection_service import ConnectionService

'''def custom_query(db_manager: DatabaseManager = Depends(get_database_manager)):
    return get_custom_query_service(db_manager)'''

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
    connection_service = ConnectionService(db_manager)
    db_ops_service = DatabaseOperationService(db_manager)
    return PatientDashboardService(db_manager, connection_service, db_ops_service)
