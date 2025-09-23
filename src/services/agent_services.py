# filepath: src/services/agent_services.py
"""Combined healthcare agent services."""

from services.bedrock_service import BedrockService
from services.database_operation_service import DatabaseOperationService
from schemas.database_operations import QueryExecutionResponse
from prompt.prompts import (
    PATIENT_AGENT_PROMPT, MEDICATION_AGENT_PROMPT, FOLLOWUP_AGENT_PROMPT,
    CONDITION_AGENT_PROMPT, LAB_RESULT_AGENT_PROMPT, PROCEDURE_AGENT_PROMPT,
    ALLERGY_AGENT_PROMPT, APPOINTMENT_AGENT_PROMPT, DIET_AGENT_PROMPT
)
from typing import List, Dict, Any

async def _generic_agent_flow(db_manager, bedrock_service, db_ops_service, connection_id: str, patient_id: str, default_query: str, query_type: str, agent_prompt: str) -> QueryExecutionResponse:
    """Generic flow for processing healthcare agent queries using Bedrock."""
    import time
    from src.services.connection_service import ConnectionService
    
    start_time = time.time()
    
    try:
        # Get connection info
        connection_service = ConnectionService(db_manager)
        schema_result = await connection_service.get_database_schema(connection_id)
        
        if schema_result.status != "success":
            return QueryExecutionResponse(
                generated_query="",
                patient_id=patient_id,
                query_type=query_type,
                model_used="anthropic.claude-3.5-sonnet",
                schema_tables_count=0,
                status="error",
                timestamp="",
                connection_info={
                    "connection_id": connection_id,
                    "database_type": "unknown",
                    "database_name": "unknown",
                    "total_tables": 0
                },
                query_executed=False,
                execution_errors=[f"Failed to retrieve schema: {schema_result.message}"]
            )
        
        # Use Bedrock to generate query with agent-specific prompt
        result = await bedrock_service.generate_healthcare_query(
            connection_id=connection_id,
            query_request=default_query,
            patient_id=patient_id,
            agent_prompt=agent_prompt  # Pass the specific prompt
        )
        
        if result.get("status") == "error":
            return QueryExecutionResponse(
                generated_query="",
                patient_id=patient_id,
                query_type=query_type,
                model_used="anthropic.claude-3.5-sonnet",
                schema_tables_count=schema_result.unified_schema.get("summary", {}).get("total_tables", 0) if schema_result.unified_schema else 0,
                status="error",
                timestamp=result.get("timestamp", ""),
                connection_info={
                    "connection_id": connection_id,
                    "database_type": schema_result.database_type,
                    "database_name": schema_result.database_name,
                    "total_tables": schema_result.unified_schema.get("summary", {}).get("total_tables", 0) if schema_result.unified_schema else 0
                },
                query_executed=False,
                execution_errors=[result.get("error", "Unknown error")]
            )
        
        generated_query = result["query"]
        
        # Execute the query
        execution_results = []
        execution_errors = []
        total_records = 0
        query_executed = False
        
        try:
            execution_results = await db_ops_service.execute_query(
                connection_id=connection_id,
                query=generated_query,
                limit=100
            )
            query_executed = True
            total_records = sum(result.row_count for result in execution_results)
        except Exception as e:
            execution_errors.append(f"Query execution failed: {str(e)}")
        
        total_execution_time = (time.time() - start_time) * 1000
        
        return QueryExecutionResponse(
            generated_query=generated_query,
            patient_id=patient_id,
            query_type=query_type,
            model_used=result.get("metadata", {}).get("model_id", "anthropic.claude-3.5-sonnet"),
            schema_tables_count=schema_result.unified_schema.get("summary", {}).get("total_tables", 0) if schema_result.unified_schema else 0,
            status="success" if not execution_errors else "partial_success",
            timestamp=result.get("timestamp", ""),
            connection_info={
                "connection_id": connection_id,
                "database_type": schema_result.database_type,
                "database_name": schema_result.database_name,
                "total_tables": schema_result.unified_schema.get("summary", {}).get("total_tables", 0) if schema_result.unified_schema else 0
            },
            query_executed=query_executed,
            execution_results=execution_results if execution_results else None,
            total_records_found=total_records if query_executed else None,
            total_execution_time_ms=total_execution_time,
            execution_errors=execution_errors if execution_errors else None
        )
        
    except Exception as e:
        return QueryExecutionResponse(
            generated_query="",
            patient_id=patient_id,
            query_type=query_type,
            model_used="anthropic.claude-3.5-sonnet",
            schema_tables_count=0,
            status="error",
            timestamp="",
            connection_info={
                "connection_id": connection_id,
                "database_type": "unknown",
                "database_name": "unknown",
                "total_tables": 0
            },
            query_executed=False,
            execution_errors=[f"Unexpected error: {str(e)}"]
        )

class PatientService:
    """Service for patient information queries."""

    def __init__(self, db_manager):
        """Initialize PatientService with database manager."""
        self.db_manager = db_manager
        self.bedrock_service = BedrockService(db_manager)
        self.db_ops_service = DatabaseOperationService(db_manager)

    async def process_query(self, connection_id: str, patient_id: str) -> QueryExecutionResponse:
        """Process a patient query using Bedrock and execute it."""
        # Default query for patient information
        default_query = f"Get basic demographic information for patient {patient_id}"
        
        # Parse query type
        query_type = self.bedrock_service._parse_query_type(default_query)
        
        return await _generic_agent_flow(self.db_manager, self.bedrock_service, self.db_ops_service, connection_id, patient_id, default_query, query_type, PATIENT_AGENT_PROMPT)

class MedicationService:
    """Service for medication queries."""

    def __init__(self, db_manager):
        """Initialize MedicationService with database manager."""
        self.db_manager = db_manager
        self.bedrock_service = BedrockService(db_manager)
        self.db_ops_service = DatabaseOperationService(db_manager)

    async def process_query(self, connection_id: str, patient_id: str) -> List[Dict[str, Any]]:
        """Process a medication query using Bedrock and execute it."""
        # Default query for medication information
        default_query = f"Get medication history, prescriptions, and drug interactions for patient {patient_id}"
        
        # Get the query execution result
        result = await _generic_agent_flow(self.db_manager, self.bedrock_service, self.db_ops_service, connection_id, patient_id, default_query, "medication", MEDICATION_AGENT_PROMPT)
        
        # Process results to extract unique medications
        medications = []
        seen_medications = set()
        
        if result.execution_results:
            for result_set in result.execution_results:
                if result_set.data:
                    for row in result_set.data:
                        # Extract medication information - handle different possible field names
                        med_name = None
                        med_desc = None
                        status = "Active"  # Default to active
                        
                        # Try different field names for medication name
                        for field in ['medication_name', 'drug_name', 'medication', 'medications_at_discharge', 'prescription_name']:
                            if field in row and row[field]:
                                med_name = str(row[field])
                                break
                        
                        # Try different field names for description
                        for field in ['dosage', 'frequency', 'instructions', 'medication_description', 'prescription_details']:
                            if field in row and row[field]:
                                med_desc = str(row[field])
                                break
                        
                        # Determine status
                        if 'is_active' in row:
                            status = "Active" if row['is_active'] else "Inactive"
                        elif 'status' in row:
                            status = str(row['status'])
                        elif 'prescription_status' in row:
                            status = str(row['prescription_status'])
                        
                        # Create unique key for deduplication
                        if med_name:
                            key = (med_name.lower(), med_desc or "")
                            if key not in seen_medications:
                                seen_medications.add(key)
                                medications.append({
                                    "medication_name": med_name,
                                    "medication_description": med_desc or f"Prescription for {med_name}",
                                    "status": status
                                })
        
        return medications

class FollowupService:
    """Service for follow-up care queries."""

    def __init__(self, db_manager):
        """Initialize FollowupService with database manager."""
        self.db_manager = db_manager
        self.bedrock_service = BedrockService(db_manager)
        self.db_ops_service = DatabaseOperationService(db_manager)

    async def process_query(self, connection_id: str, patient_id: str) -> List[Dict[str, Any]]:
        """Process a follow-up query using Bedrock and execute it."""
        # Default query for follow-up care information
        default_query = f"Get followup care, appointments, and care plan details for patient {patient_id}"
        
        # Get the query execution result
        result = await _generic_agent_flow(self.db_manager, self.bedrock_service, self.db_ops_service, connection_id, patient_id, default_query, "followup", FOLLOWUP_AGENT_PROMPT)
        
        # Process results to extract unique follow-up information
        followups = []
        seen_followups = set()
        
        if result.execution_results:
            for result_set in result.execution_results:
                if result_set.data:
                    for row in result_set.data:
                        # Extract follow-up information - handle different possible field names
                        followup_type = None
                        followup_desc = None
                        status = "Scheduled"  # Default
                        
                        # Try different field names for follow-up type
                        for field in ['followup_type', 'appointment_type', 'care_type', 'visit_type', 'encounter_type']:
                            if field in row and row[field]:
                                followup_type = str(row[field])
                                break
                        
                        # Try different field names for description
                        for field in ['followup_description', 'care_plan', 'appointment_notes', 'visit_notes', 'instructions', 'procedures_performed']:
                            if field in row and row[field]:
                                followup_desc = str(row[field])
                                break
                        
                        # Determine status
                        if 'status' in row:
                            status = str(row['status'])
                        elif 'appointment_status' in row:
                            status = str(row['appointment_status'])
                        elif 'followup_status' in row:
                            status = str(row['followup_status'])
                        
                        # Create unique key for deduplication
                        if followup_type:
                            key = (followup_type.lower(), followup_desc or "")
                            if key not in seen_followups:
                                seen_followups.add(key)
                                followups.append({
                                    "followup_type": followup_type,
                                    "followup_description": followup_desc or f"Follow-up care: {followup_type}",
                                    "status": status
                                })
        
        return followups

class ConditionService:
    """Service for medical condition queries."""

    def __init__(self, db_manager):
        """Initialize ConditionService with database manager."""
        self.db_manager = db_manager
        self.bedrock_service = BedrockService(db_manager)
        self.db_ops_service = DatabaseOperationService(db_manager)

    async def process_query(self, connection_id: str, patient_id: str) -> List[Dict[str, Any]]:
        """Process a condition query using Bedrock and execute it."""
        # Default query for medical condition information
        default_query = f"Get medical conditions, diagnoses, and health status for patient {patient_id}"
        
        # Get the query execution result
        result = await _generic_agent_flow(self.db_manager, self.bedrock_service, self.db_ops_service, connection_id, patient_id, default_query, "condition", CONDITION_AGENT_PROMPT)
        
        # Process results to extract unique conditions
        conditions = []
        seen_conditions = set()
        
        if result.execution_results:
            for result_set in result.execution_results:
                if result_set.data:
                    for row in result_set.data:
                        # Extract condition information - handle different possible field names
                        condition_name = None
                        condition_desc = None
                        status = "Active"  # Default
                        
                        # Try different field names for condition name
                        for field in ['condition_name', 'diagnosis', 'medical_condition', 'diagnosis_description', 'primary_diagnosis']:
                            if field in row and row[field]:
                                condition_name = str(row[field])
                                break
                        
                        # Try different field names for description
                        for field in ['condition_description', 'diagnosis_details', 'severity', 'condition_notes']:
                            if field in row and row[field]:
                                condition_desc = str(row[field])
                                break
                        
                        # Determine status
                        if 'status' in row:
                            status = str(row['status'])
                        elif 'condition_status' in row:
                            status = str(row['condition_status'])
                        elif 'is_active' in row:
                            status = "Active" if row['is_active'] else "Inactive"
                        
                        # Create unique key for deduplication
                        if condition_name:
                            key = (condition_name.lower(), condition_desc or "")
                            if key not in seen_conditions:
                                seen_conditions.add(key)
                                conditions.append({
                                    "condition_name": condition_name,
                                    "condition_description": condition_desc or f"Diagnosis: {condition_name}",
                                    "status": status
                                })
        
        return conditions

class LabResultService:
    """Service for lab result queries."""

    def __init__(self, db_manager):
        """Initialize LabResultService with database manager."""
        self.db_manager = db_manager
        self.bedrock_service = BedrockService(db_manager)
        self.db_ops_service = DatabaseOperationService(db_manager)

    async def process_query(self, connection_id: str, patient_id: str) -> List[Dict[str, Any]]:
        """Process a lab result query using Bedrock and execute it."""
        # Default query for lab result information
        default_query = f"Get laboratory test results, blood work, and diagnostic tests for patient {patient_id}"
        
        # Get the query execution result
        result = await _generic_agent_flow(self.db_manager, self.bedrock_service, self.db_ops_service, connection_id, patient_id, default_query, "lab_result", LAB_RESULT_AGENT_PROMPT)
        
        # Process results to extract unique lab results
        lab_results = []
        seen_results = set()
        
        if result.execution_results:
            for result_set in result.execution_results:
                if result_set.data:
                    for row in result_set.data:
                        # Extract lab result information - handle different possible field names
                        test_name = None
                        test_result = None
                        status = "Completed"  # Default
                        
                        # Try different field names for test name
                        for field in ['test_name', 'lab_test', 'test_type', 'procedure_name']:
                            if field in row and row[field]:
                                test_name = str(row[field])
                                break
                        
                        # Try different field names for result
                        for field in ['result', 'test_result', 'value', 'lab_result', 'result_value']:
                            if field in row and row[field]:
                                test_result = str(row[field])
                                break
                        
                        # Try different field names for status
                        for field in ['status', 'test_status', 'result_status']:
                            if field in row and row[field]:
                                status = str(row[field])
                                break
                        
                        # Create unique key for deduplication
                        if test_name and test_result:
                            key = (test_name.lower(), test_result.lower())
                            if key not in seen_results:
                                seen_results.add(key)
                                lab_results.append({
                                    "test_name": test_name,
                                    "test_result": test_result,
                                    "status": status
                                })
        
        return lab_results

class ProcedureService:
    """Service for procedure queries."""

    def __init__(self, db_manager):
        """Initialize ProcedureService with database manager."""
        self.db_manager = db_manager
        self.bedrock_service = BedrockService(db_manager)
        self.db_ops_service = DatabaseOperationService(db_manager)

    async def process_query(self, connection_id: str, patient_id: str) -> List[Dict[str, Any]]:
        """Process a procedure query using Bedrock and execute it."""
        # Default query for procedure information
        default_query = f"Get medical procedures, surgeries, and treatments performed for patient {patient_id}"
        
        # Get the query execution result
        result = await _generic_agent_flow(self.db_manager, self.bedrock_service, self.db_ops_service, connection_id, patient_id, default_query, "procedure", PROCEDURE_AGENT_PROMPT)
        
        # Process results to extract unique procedures
        procedures = []
        seen_procedures = set()
        
        if result.execution_results:
            for result_set in result.execution_results:
                if result_set.data:
                    for row in result_set.data:
                        # Extract procedure information - handle different possible field names
                        procedure_name = None
                        procedure_desc = None
                        status = "Completed"  # Default
                        
                        # Try different field names for procedure name
                        for field in ['procedure_name', 'surgery_name', 'treatment_name', 'procedure_type', 'procedures_performed']:
                            if field in row and row[field]:
                                procedure_name = str(row[field])
                                break
                        
                        # Try different field names for description
                        for field in ['procedure_description', 'surgery_details', 'treatment_details', 'procedure_notes', 'outcome']:
                            if field in row and row[field]:
                                procedure_desc = str(row[field])
                                break
                        
                        # Try different field names for status
                        for field in ['status', 'procedure_status', 'surgery_status']:
                            if field in row and row[field]:
                                status = str(row[field])
                                break
                        
                        # Create unique key for deduplication
                        if procedure_name:
                            key = (procedure_name.lower(), procedure_desc or "")
                            if key not in seen_procedures:
                                seen_procedures.add(key)
                                procedures.append({
                                    "procedure_name": procedure_name,
                                    "procedure_description": procedure_desc or f"Medical procedure: {procedure_name}",
                                    "status": status
                                })
        
        return procedures

class AllergyService:
    """Service for allergy queries."""

    def __init__(self, db_manager):
        """Initialize AllergyService with database manager."""
        self.db_manager = db_manager
        self.bedrock_service = BedrockService(db_manager)
        self.db_ops_service = DatabaseOperationService(db_manager)

    async def process_query(self, connection_id: str, patient_id: str) -> List[Dict[str, Any]]:
        """Process an allergy query using Bedrock and execute it."""
        # Default query for allergy information
        default_query = f"Get allergies, adverse reactions, and sensitivities for patient {patient_id}"
        
        # Get the query execution result
        result = await _generic_agent_flow(self.db_manager, self.bedrock_service, self.db_ops_service, connection_id, patient_id, default_query, "allergy", ALLERGY_AGENT_PROMPT)
        
        # Process results to extract unique allergies
        allergies = []
        seen_allergies = set()
        
        if result.execution_results:
            for result_set in result.execution_results:
                if result_set.data:
                    for row in result_set.data:
                        # Extract allergy information - handle different possible field names
                        allergen_name = None
                        reaction_desc = None
                        status = "Active"  # Default
                        
                        # Try different field names for allergen name
                        for field in ['allergen_name', 'allergy_name', 'allergen', 'allergy']:
                            if field in row and row[field]:
                                allergen_name = str(row[field])
                                break
                        
                        # Try different field names for reaction
                        for field in ['reaction_type', 'reaction', 'severity', 'allergy_reaction', 'adverse_reaction']:
                            if field in row and row[field]:
                                reaction_desc = str(row[field])
                                break
                        
                        # Try different field names for status
                        for field in ['status', 'allergy_status']:
                            if field in row and row[field]:
                                status = str(row[field])
                                break
                        
                        # Create unique key for deduplication
                        if allergen_name:
                            key = (allergen_name.lower(), reaction_desc or "")
                            if key not in seen_allergies:
                                seen_allergies.add(key)
                                allergies.append({
                                    "allergen_name": allergen_name,
                                    "reaction_description": reaction_desc or f"Allergic reaction to {allergen_name}",
                                    "status": status
                                })
        
        return allergies

class AppointmentService:
    """Service for appointment queries."""

    def __init__(self, db_manager):
        """Initialize AppointmentService with database manager."""
        self.db_manager = db_manager
        self.bedrock_service = BedrockService(db_manager)
        self.db_ops_service = DatabaseOperationService(db_manager)

    async def process_query(self, connection_id: str, patient_id: str) -> List[Dict[str, Any]]:
        """Process an appointment query using Bedrock and execute it."""
        # Default query for appointment information
        default_query = f"Get scheduled appointments, visit history, and healthcare encounters for patient {patient_id}"
        
        # Get the query execution result
        result = await _generic_agent_flow(self.db_manager, self.bedrock_service, self.db_ops_service, connection_id, patient_id, default_query, "appointment", APPOINTMENT_AGENT_PROMPT)
        
        # Process results to extract unique appointments
        appointments = []
        seen_appointments = set()
        
        if result.execution_results:
            for result_set in result.execution_results:
                if result_set.data:
                    for row in result_set.data:
                        # Extract appointment information - handle different possible field names
                        appointment_type = None
                        appointment_desc = None
                        status = "Scheduled"  # Default
                        
                        # Try different field names for appointment type
                        for field in ['appointment_type', 'visit_type', 'encounter_type', 'appointment_reason']:
                            if field in row and row[field]:
                                appointment_type = str(row[field])
                                break
                        
                        # Try different field names for description
                        for field in ['appointment_description', 'visit_notes', 'encounter_notes', 'appointment_details']:
                            if field in row and row[field]:
                                appointment_desc = str(row[field])
                                break
                        
                        # Try different field names for status
                        for field in ['status', 'appointment_status', 'visit_status']:
                            if field in row and row[field]:
                                status = str(row[field])
                                break
                        
                        # Create unique key for deduplication
                        if appointment_type:
                            key = (appointment_type.lower(), appointment_desc or "")
                            if key not in seen_appointments:
                                seen_appointments.add(key)
                                appointments.append({
                                    "appointment_type": appointment_type,
                                    "appointment_description": appointment_desc or f"Healthcare appointment: {appointment_type}",
                                    "status": status
                                })
        
        return appointments

class DietService:
    """Service for diet and nutrition queries."""

    def __init__(self, db_manager):
        """Initialize DietService with database manager."""
        self.db_manager = db_manager
        self.bedrock_service = BedrockService(db_manager)
        self.db_ops_service = DatabaseOperationService(db_manager)

    async def process_query(self, connection_id: str, patient_id: str) -> List[Dict[str, Any]]:
        """Process a diet query using Bedrock and execute it."""
        # Default query for diet and nutrition information
        default_query = f"Get dietary information, nutritional assessments, and diet plans for patient {patient_id}"
        
        # Get the query execution result
        result = await _generic_agent_flow(self.db_manager, self.bedrock_service, self.db_ops_service, connection_id, patient_id, default_query, "diet", DIET_AGENT_PROMPT)
        
        # Process results to extract unique diet information
        diets = []
        seen_diets = set()
        
        if result.execution_results:
            for result_set in result.execution_results:
                if result_set.data:
                    for row in result_set.data:
                        # Extract diet information - handle different possible field names
                        diet_type = None
                        diet_desc = None
                        status = "Active"  # Default
                        
                        # Try different field names for diet type
                        for field in ['diet_type', 'nutrition_plan', 'dietary_restriction', 'diet_plan']:
                            if field in row and row[field]:
                                diet_type = str(row[field])
                                break
                        
                        # Try different field names for description
                        for field in ['diet_description', 'nutrition_details', 'dietary_notes', 'nutritional_assessment']:
                            if field in row and row[field]:
                                diet_desc = str(row[field])
                                break
                        
                        # Try different field names for status
                        for field in ['status', 'diet_status', 'plan_status']:
                            if field in row and row[field]:
                                status = str(row[field])
                                break
                        
                        # Create unique key for deduplication
                        if diet_type:
                            key = (diet_type.lower(), diet_desc or "")
                            if key not in seen_diets:
                                seen_diets.add(key)
                                diets.append({
                                    "diet_type": diet_type,
                                    "diet_description": diet_desc or f"Dietary plan: {diet_type}",
                                    "status": status
                                })
        
        return diets