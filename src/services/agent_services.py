"""Combined healthcare agent services with personalized report generation."""

from typing import List, Dict, Any
from datetime import datetime
from services.bedrock_service import BedrockService
from services.database_operation_service import DatabaseOperationService
from services.connection_service import ConnectionService
from schemas.database_operations import QueryExecutionResponse
from prompt.prompts import (
    PATIENT_AGENT_PROMPT, MEDICATION_AGENT_PROMPT, FOLLOWUP_AGENT_PROMPT,
    CONDITION_AGENT_PROMPT, LAB_RESULT_AGENT_PROMPT, PROCEDURE_AGENT_PROMPT,
    ALLERGY_AGENT_PROMPT, APPOINTMENT_AGENT_PROMPT, DIET_AGENT_PROMPT,
    PATIENT_REPORT_PROMPT, MEDICATION_REPORT_PROMPT, FOLLOWUP_REPORT_PROMPT,
    CONDITION_REPORT_PROMPT, LAB_RESULT_REPORT_PROMPT, PROCEDURE_REPORT_PROMPT,
    ALLERGY_REPORT_PROMPT, APPOINTMENT_REPORT_PROMPT, DIET_REPORT_PROMPT
)
import json

async def _generate_health_report(
    bedrock_service: BedrockService,
    patient_id: str,
    executed_query: str,
    data: List[Dict],
    report_prompt: str
) -> str:
    """Generate personalized health report using LLM."""
    try:
        # Format the data for the LLM
        formatted_data = json.dumps(data, indent=2, default=str) if data else "No data available"
        
        # Create the report generation prompt
        report_request = report_prompt.format(
            patient_id=patient_id,
            executed_query=executed_query,
            **{
                'patient_data': formatted_data,
                'medication_data': formatted_data,
                'followup_data': formatted_data,
                'condition_data': formatted_data,
                'lab_data': formatted_data,
                'procedure_data': formatted_data,
                'allergy_data': formatted_data,
                'appointment_data': formatted_data,
                'diet_data': formatted_data
            }
        )
        
        # Call Bedrock to generate the report
        report_response = await bedrock_service._call_bedrock_api(report_request)
        
        if report_response.get("status") == "success":
            # Extract the report text from the response
            content = report_response.get("raw_response", {}).get('content', [])
            if content:
                return content[0].get('text', 'Unable to generate report')
            
        return "Unable to generate personalized report"
        
    except Exception as e:
        return f"Error generating report: {str(e)}"

async def _generic_agent_flow(
    db_manager, 
    bedrock_service: BedrockService, 
    db_ops_service: DatabaseOperationService,
    connection_id: str,
    patient_id: str,
    default_query: str,
    query_type: str,
    agent_prompt: str,
    report_prompt: str
) -> QueryExecutionResponse:
    """Generic flow for processing healthcare agent queries using Bedrock with report generation."""
    try:
        # Get schema and enhance context
        connection_service = ConnectionService(db_manager)
        schema_result = await connection_service.get_database_schema(connection_id)
        
        if not schema_result or schema_result.status != "success":
            raise Exception(f"Failed to get schema: {schema_result.message if schema_result else 'No schema result'}")

        # Format schema context for the LLM
        schema_context = {
            "database_type": schema_result.database_type,
            "tables": schema_result.unified_schema.get("tables", []),
            "agent_type": query_type
        }

        # Create user query with schema context
        formatted_prompt = agent_prompt.format(
            patient_id=patient_id,
            user_query=default_query,
            schema_info=schema_context
        )

        # Generate query using Bedrock
        query_result = await bedrock_service.generate_healthcare_query(
            connection_id=connection_id,
            query_request=formatted_prompt,
            patient_id=patient_id,
            schema_context=schema_context
        )

        if not query_result or "query" not in query_result:
            raise Exception("Failed to generate query from Bedrock")

        generated_query = query_result["query"]
        
        # Execute generated query - this returns List[DatabaseQueryResult]
        db_results = await db_ops_service.execute_query(
            connection_id=connection_id,
            query=generated_query,
            params={"patient_id": patient_id}
        )

        if not db_results or len(db_results) == 0:
            return QueryExecutionResponse(
                generated_query=generated_query,
                patient_id=patient_id,
                query_type=query_type,
                model_used="bedrock-claude",
                schema_tables_count=len(schema_context.get("tables", [])),
                status="success",
                timestamp=datetime.now().isoformat(),
                connection_info={
                    "connection_id": connection_id,
                    "database_type": schema_result.database_type,
                    "database_name": schema_result.database_name
                },
                query_executed=True,
                execution_results=[],
                total_records_found=0,
                total_execution_time_ms=0,
                execution_errors=None
            )

        # Get the first result (database_operation_service returns List[DatabaseQueryResult])
        first_result = db_results[0]
        
        # Generate personalized health report using the retrieved data
        health_report = await _generate_health_report(
            bedrock_service=bedrock_service,
            patient_id=patient_id,
            executed_query=generated_query,
            data=first_result.data,
            report_prompt=report_prompt
        )
        
        # Convert the DatabaseQueryResult to the format expected by execution_results
        db_query_result = {
            "table_name": first_result.table_name,
            "query": first_result.query,
            "row_count": first_result.row_count,
            "data": first_result.data,
            "execution_time_ms": first_result.execution_time_ms,
            "personalized_health_report": health_report  # Add the generated report
        }
        
        # Return QueryExecutionResponse with actual data and health report
        return QueryExecutionResponse(
            generated_query=generated_query,
            patient_id=patient_id,
            query_type=query_type,
            model_used="bedrock-claude",
            schema_tables_count=len(schema_context.get("tables", [])),
            status="success",
            timestamp=datetime.now().isoformat(),
            connection_info={
                "connection_id": connection_id,
                "database_type": schema_result.database_type,
                "database_name": schema_result.database_name
            },
            query_executed=True,
            execution_results=[db_query_result],  # This contains the actual data + report
            total_records_found=first_result.row_count,
            total_execution_time_ms=first_result.execution_time_ms,
            execution_errors=None
        )

    except Exception as e:
        # Return error response with all required fields
        return QueryExecutionResponse(
            generated_query="",
            patient_id=patient_id,
            query_type=query_type,
            model_used="bedrock-claude",
            schema_tables_count=0,
            status="error",
            timestamp=datetime.now().isoformat(),
            connection_info={
                "connection_id": connection_id,
                "database_type": "unknown"
            },
            query_executed=False,
            execution_results=None,
            total_records_found=0,
            total_execution_time_ms=0,
            execution_errors=[str(e)]
        )

class PatientService:
    """Patient information service with personalized health reports."""
    
    def __init__(self, db_manager, bedrock_service: BedrockService, db_ops_service: DatabaseOperationService):
        self.db_manager = db_manager
        self.bedrock_service = bedrock_service
        self.db_ops_service = db_ops_service

    async def get_patient_info(self, connection_id: str, patient_id: str) -> QueryExecutionResponse:
        try:
            if not connection_id:
                raise ValueError("connection_id is required")
            if not patient_id:
                raise ValueError("patient_id is required")

            default_query = "SELECT demographic information FROM patient WHERE patient_id = :patient_id"
            result = await _generic_agent_flow(
                self.db_manager,
                self.bedrock_service,
                self.db_ops_service,
                connection_id,
                patient_id,
                default_query,
                "patient",
                PATIENT_AGENT_PROMPT,
                PATIENT_REPORT_PROMPT
            )
            return result

        except Exception as e:
            return QueryExecutionResponse(
                generated_query="",
                patient_id=patient_id,
                query_type="patient",
                model_used="bedrock-claude",
                schema_tables_count=0,
                status="error",
                timestamp=datetime.now().isoformat(),
                connection_info={"connection_id": connection_id, "database_type": "unknown"},
                query_executed=False,
                execution_results=None,
                total_records_found=0,
                total_execution_time_ms=0,
                execution_errors=[f"Patient service error: {str(e)}"]
            )

class MedicationService:
    """Medication service with personalized health reports."""
    
    def __init__(self, db_manager, bedrock_service: BedrockService, db_ops_service: DatabaseOperationService):
        self.db_manager = db_manager
        self.bedrock_service = bedrock_service
        self.db_ops_service = db_ops_service

    async def get_medications(self, connection_id: str, patient_id: str) -> QueryExecutionResponse:
        try:
            if not connection_id:
                raise ValueError("connection_id is required")
            if not patient_id:
                raise ValueError("patient_id is required")

            default_query = "SELECT medication details FROM medications WHERE patient_id = :patient_id"
            result = await _generic_agent_flow(
                self.db_manager,
                self.bedrock_service,
                self.db_ops_service,
                connection_id,
                patient_id,
                default_query,
                "medication",
                MEDICATION_AGENT_PROMPT,
                MEDICATION_REPORT_PROMPT
            )
            return result

        except Exception as e:
            return QueryExecutionResponse(
                generated_query="",
                patient_id=patient_id,
                query_type="medication",
                model_used="bedrock-claude",
                schema_tables_count=0,
                status="error",
                timestamp=datetime.now().isoformat(),
                connection_info={"connection_id": connection_id, "database_type": "unknown"},
                query_executed=False,
                execution_results=None,
                total_records_found=0,
                total_execution_time_ms=0,
                execution_errors=[f"Medication service error: {str(e)}"]
            )

class FollowupService:
    """Follow-up service with personalized health reports."""
    
    def __init__(self, db_manager, bedrock_service: BedrockService, db_ops_service: DatabaseOperationService):
        self.db_manager = db_manager
        self.bedrock_service = bedrock_service
        self.db_ops_service = db_ops_service

    async def get_followups(self, connection_id: str, patient_id: str) -> QueryExecutionResponse:
        try:
            default_query = "SELECT followup details FROM followups WHERE patient_id = :patient_id"
            return await _generic_agent_flow(
                self.db_manager, self.bedrock_service, self.db_ops_service,
                connection_id, patient_id, default_query, "followup", 
                FOLLOWUP_AGENT_PROMPT, FOLLOWUP_REPORT_PROMPT
            )
        except Exception as e:
            return QueryExecutionResponse(
                generated_query="", patient_id=patient_id, query_type="followup", 
                model_used="bedrock-claude", schema_tables_count=0, status="error",
                timestamp=datetime.now().isoformat(),
                connection_info={"connection_id": connection_id, "database_type": "unknown"},
                query_executed=False, execution_results=None, total_records_found=0,
                total_execution_time_ms=0, execution_errors=[f"Followup service error: {str(e)}"]
            )

class ConditionService:
    """Medical conditions service with personalized health reports."""
    
    def __init__(self, db_manager, bedrock_service: BedrockService, db_ops_service: DatabaseOperationService):
        self.db_manager = db_manager
        self.bedrock_service = bedrock_service
        self.db_ops_service = db_ops_service

    async def get_conditions(self, connection_id: str, patient_id: str) -> QueryExecutionResponse:
        try:
            default_query = "SELECT condition details FROM conditions WHERE patient_id = :patient_id"
            return await _generic_agent_flow(
                self.db_manager, self.bedrock_service, self.db_ops_service,
                connection_id, patient_id, default_query, "condition", 
                CONDITION_AGENT_PROMPT, CONDITION_REPORT_PROMPT
            )
        except Exception as e:
            return QueryExecutionResponse(
                generated_query="", patient_id=patient_id, query_type="condition", 
                model_used="bedrock-claude", schema_tables_count=0, status="error",
                timestamp=datetime.now().isoformat(),
                connection_info={"connection_id": connection_id, "database_type": "unknown"},
                query_executed=False, execution_results=None, total_records_found=0,
                total_execution_time_ms=0, execution_errors=[f"Condition service error: {str(e)}"]
            )

class LabResultService:
    """Laboratory results service with personalized health reports."""
    
    def __init__(self, db_manager, bedrock_service: BedrockService, db_ops_service: DatabaseOperationService):
        self.db_manager = db_manager
        self.bedrock_service = bedrock_service
        self.db_ops_service = db_ops_service

    async def get_lab_results(self, connection_id: str, patient_id: str) -> QueryExecutionResponse:
        try:
            default_query = "SELECT lab results FROM lab_results WHERE patient_id = :patient_id"
            return await _generic_agent_flow(
                self.db_manager, self.bedrock_service, self.db_ops_service,
                connection_id, patient_id, default_query, "lab_result", 
                LAB_RESULT_AGENT_PROMPT, LAB_RESULT_REPORT_PROMPT
            )
        except Exception as e:
            return QueryExecutionResponse(
                generated_query="", patient_id=patient_id, query_type="lab_result", 
                model_used="bedrock-claude", schema_tables_count=0, status="error",
                timestamp=datetime.now().isoformat(),
                connection_info={"connection_id": connection_id, "database_type": "unknown"},
                query_executed=False, execution_results=None, total_records_found=0,
                total_execution_time_ms=0, execution_errors=[f"Lab result service error: {str(e)}"]
            )

class ProcedureService:
    """Medical procedures service with personalized health reports."""
    
    def __init__(self, db_manager, bedrock_service: BedrockService, db_ops_service: DatabaseOperationService):
        self.db_manager = db_manager
        self.bedrock_service = bedrock_service
        self.db_ops_service = db_ops_service

    async def get_procedures(self, connection_id: str, patient_id: str) -> QueryExecutionResponse:
        try:
            default_query = "SELECT procedure details FROM procedures WHERE patient_id = :patient_id"
            return await _generic_agent_flow(
                self.db_manager, self.bedrock_service, self.db_ops_service,
                connection_id, patient_id, default_query, "procedure", 
                PROCEDURE_AGENT_PROMPT, PROCEDURE_REPORT_PROMPT
            )
        except Exception as e:
            return QueryExecutionResponse(
                generated_query="", patient_id=patient_id, query_type="procedure", 
                model_used="bedrock-claude", schema_tables_count=0, status="error",
                timestamp=datetime.now().isoformat(),
                connection_info={"connection_id": connection_id, "database_type": "unknown"},
                query_executed=False, execution_results=None, total_records_found=0,
                total_execution_time_ms=0, execution_errors=[f"Procedure service error: {str(e)}"]
            )

class AllergyService:
    """Allergy information service with personalized health reports."""
    
    def __init__(self, db_manager, bedrock_service: BedrockService, db_ops_service: DatabaseOperationService):
        self.db_manager = db_manager
        self.bedrock_service = bedrock_service
        self.db_ops_service = db_ops_service

    async def get_allergies(self, connection_id: str, patient_id: str) -> QueryExecutionResponse:
        try:
            default_query = "SELECT allergy details FROM allergies WHERE patient_id = :patient_id"
            return await _generic_agent_flow(
                self.db_manager, self.bedrock_service, self.db_ops_service,
                connection_id, patient_id, default_query, "allergy", 
                ALLERGY_AGENT_PROMPT, ALLERGY_REPORT_PROMPT
            )
        except Exception as e:
            return QueryExecutionResponse(
                generated_query="", patient_id=patient_id, query_type="allergy", 
                model_used="bedrock-claude", schema_tables_count=0, status="error",
                timestamp=datetime.now().isoformat(),
                connection_info={"connection_id": connection_id, "database_type": "unknown"},
                query_executed=False, execution_results=None, total_records_found=0,
                total_execution_time_ms=0, execution_errors=[f"Allergy service error: {str(e)}"]
            )

class AppointmentService:
    """Appointment management service with personalized health reports."""
    
    def __init__(self, db_manager, bedrock_service: BedrockService, db_ops_service: DatabaseOperationService):
        self.db_manager = db_manager
        self.bedrock_service = bedrock_service
        self.db_ops_service = db_ops_service

    async def get_appointments(self, connection_id: str, patient_id: str) -> QueryExecutionResponse:
        try:
            default_query = "SELECT appointment details FROM appointments WHERE patient_id = :patient_id"
            return await _generic_agent_flow(
                self.db_manager, self.bedrock_service, self.db_ops_service,
                connection_id, patient_id, default_query, "appointment", 
                APPOINTMENT_AGENT_PROMPT, APPOINTMENT_REPORT_PROMPT
            )
        except Exception as e:
            return QueryExecutionResponse(
                generated_query="", patient_id=patient_id, query_type="appointment", 
                model_used="bedrock-claude", schema_tables_count=0, status="error",
                timestamp=datetime.now().isoformat(),
                connection_info={"connection_id": connection_id, "database_type": "unknown"},
                query_executed=False, execution_results=None, total_records_found=0,
                total_execution_time_ms=0, execution_errors=[f"Appointment service error: {str(e)}"]
            )

class DietService:
    """Dietary information service with personalized health reports."""
    
    def __init__(self, db_manager, bedrock_service: BedrockService, db_ops_service: DatabaseOperationService):
        self.db_manager = db_manager
        self.bedrock_service = bedrock_service
        self.db_ops_service = db_ops_service

    async def get_diet_info(self, connection_id: str, patient_id: str) -> QueryExecutionResponse:
        try:
            default_query = "SELECT diet details FROM diet_plans WHERE patient_id = :patient_id"
            return await _generic_agent_flow(
                self.db_manager, self.bedrock_service, self.db_ops_service,
                connection_id, patient_id, default_query, "diet", 
                DIET_AGENT_PROMPT, DIET_REPORT_PROMPT
            )
        except Exception as e:
            return QueryExecutionResponse(
                generated_query="", patient_id=patient_id, query_type="diet", 
                model_used="bedrock-claude", schema_tables_count=0, status="error",
                timestamp=datetime.now().isoformat(),
                connection_info={"connection_id": connection_id, "database_type": "unknown"},
                query_executed=False, execution_results=None, total_records_found=0,
                total_execution_time_ms=0, execution_errors=[f"Diet service error: {str(e)}"]
            )

# Export all services
__all__ = [
    'PatientService',
    'MedicationService',
    'FollowupService',
    'ConditionService',
    'LabResultService',
    'ProcedureService',
    'AllergyService',
    'AppointmentService',
    'DietService'
]