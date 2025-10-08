"""Dashboard service for patient vitals with LLM-powered query generation."""

from typing import List, Dict, Any, Optional
from datetime import datetime
from services.bedrock_service import BedrockService
from services.database_operation_service import DatabaseOperationService
from services.connection_service import ConnectionService
from schemas.database_operations import DatabaseQueryResult
from prompt.prompts import DASHBOARD_VITALS_PROMPT
import json
import logging

logger = logging.getLogger(__name__)

class PatientDashboardService:
    """Service class for patient dashboard operations using LLM query generation."""
    
    def __init__(self, db_manager, bedrock_service: BedrockService, db_ops_service: DatabaseOperationService):
        self.db_manager = db_manager
        self.bedrock_service = bedrock_service
        self.db_ops_service = db_ops_service

    async def get_all_patient_data(self, patient_id: str, connection_id: str):
        """Get all vital data for a patient using LLM-generated queries."""
        data_types = {
            "heart_rate": "Get the latest heart rate measurements including heart rate value, status, recorded time, and device information",
            "blood_pressure": "Get the latest blood pressure readings including systolic, diastolic values, recorded time, and device information",
            "spo2": "Get the latest SpO2 measurements including oxygen saturation percentage, recorded time, and device information",
            "temperature": "Get the latest temperature readings including temperature in Celsius and Fahrenheit, recorded time, and device information",
            "blood_sugar": "Get the latest blood sugar/glucose measurements including glucose level, test type, and recorded time",
        }
        
        all_data = {}
        for data_type, description in data_types.items():
            try:
                result = await self._get_patient_vital_data(
                    connection_id, patient_id, data_type, description
                )
                all_data[data_type] = result
            except Exception as e:
                all_data[data_type] = {"error": str(e)}
        
        return all_data

    async def _get_patient_vital_data(
        self, 
        connection_id: str, 
        patient_id: str, 
        data_type: str,
        query_description: str
    ) -> Dict[str, Any]:
        """Get patient vital data using LLM-generated queries."""
        try:
            # Get schema and enhance context
            connection_service = ConnectionService(self.db_manager)
            schema_result = await connection_service.get_database_schema(connection_id)
            
            if not schema_result or schema_result.status != "success":
                raise Exception(f"Failed to get schema: {schema_result.message if schema_result else 'No schema result'}")

            # Get database connection info
            connection = await connection_service.get_connection_by_id(connection_id)
            if not connection:
                raise Exception(f"Database connection with ID '{connection_id}' not found")

            # Format schema context for the LLM
            schema_context = {
                "database_type": schema_result.database_type,
                "tables": schema_result.unified_schema.get("tables", []),
                "data_type": data_type
            }

            # Create user query with schema context
            formatted_prompt = DASHBOARD_VITALS_PROMPT.format(
                patient_id=patient_id,
                data_type=data_type,
                query_description=query_description,
                schema_info=schema_context
            )

            # Generate query using Bedrock
            query_result = await self.bedrock_service.generate_healthcare_query(
                connection_id=connection_id,
                query_request=formatted_prompt,
                patient_id=patient_id,
                schema_context=schema_context
            )

            if not query_result or "query" not in query_result:
                raise Exception(f"Failed to generate query for {data_type}")

            generated_query = query_result["query"]
            
            # Execute generated query
            db_results = await self.db_ops_service.execute_query(
                connection_id=connection_id,
                query=generated_query,
                params={"patient_id": patient_id}
            )

            if not db_results or len(db_results) == 0:
                return {
                    "status": "no_data",
                    "message": f"No {data_type} data found for patient {patient_id}",
                    "generated_query": generated_query,
                    "patient_id": patient_id,
                    "data_type": data_type
                }

            # Get the first result
            first_result = db_results[0]
            
            if first_result.data and len(first_result.data) > 0:
                patient_data = first_result.data[0]
                
                # Add metadata to the response
                result = {
                    "status": "success",
                    "data": patient_data,
                    "metadata": {
                        "patient_id": patient_id,
                        "connection_id": connection_id,
                        "data_type": data_type,
                        "timestamp": datetime.now().isoformat(),
                        "table_name": first_result.table_name,
                        "generated_query": generated_query,
                        "execution_time_ms": first_result.execution_time_ms,
                        "row_count": first_result.row_count
                    }
                }
                
                logger.info(f"Successfully fetched {data_type} data for patient {patient_id}")
                return result
            else:
                return {
                    "status": "no_data",
                    "message": f"No {data_type} data returned for patient {patient_id}",
                    "generated_query": generated_query,
                    "patient_id": patient_id,
                    "data_type": data_type
                }
            
        except Exception as e:
            logger.error(f"Error fetching {data_type} data for patient {patient_id}: {str(e)}")
            return {
                "status": "error",
                "message": str(e),
                "patient_id": patient_id,
                "data_type": data_type
            }
