"""Patient dashboard API controller with real database connections via Connection ID."""

import logging
import json
from typing import Optional, Dict, Any, List
from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends, Path, Query

from services.connection_service import ConnectionService
from services.database_operation_service import DatabaseOperationService  
from db.session import get_database_manager, DatabaseManager
from schemas.database_operations import DatabaseQueryResult

logger = logging.getLogger(__name__)


class PatientDashboardController:
    """Controller for patient dashboard endpoints using real database connections."""
    
    def __init__(self):
        """Initialize the patient dashboard controller."""
        self.router = APIRouter()
        self._setup_routes()
    
    def get_connection_service(self, db_manager: DatabaseManager = Depends(get_database_manager)) -> ConnectionService:
        """Dependency to get connection service."""
        return ConnectionService(db_manager)

    def get_database_operation_service(self, db_manager: DatabaseManager = Depends(get_database_manager)) -> DatabaseOperationService:
        """Dependency to get database operation service."""  
        return DatabaseOperationService(db_manager)
    
    def _setup_routes(self):
        """Setup routes for patient dashboard endpoints."""
        
        # Heart Rate endpoint
        @self.router.get("/patients/{patient_id}/heart-rate")
        async def get_patient_heart_rate(
            patient_id: str = Path(..., description="Patient ID to fetch heart rate data for"),
            connection_id: str = Query(..., description="Database connection ID to use for fetching data"),
            connection_service: ConnectionService = Depends(self.get_connection_service),
            db_operation_service: DatabaseOperationService = Depends(self.get_database_operation_service)
        ):
            """Get latest heart rate data for a patient from the specified database connection."""
            return await self._get_patient_vital_data(
                connection_service, db_operation_service, connection_id, patient_id, "heart_rate", 
                ["heart_rate", "status", "recorded_at", "device_id"]
            )
        
        # Blood Pressure endpoint 
         
        @self.router.get("/patients/{patient_id}/blood-pressure")
        async def get_patient_blood_pressure(
            patient_id: str = Path(..., description="Patient ID to fetch blood pressure data for"),
            connection_id: str = Query(..., description="Database connection ID to use for fetching data"),
            connection_service: ConnectionService = Depends(self.get_connection_service),
            db_operation_service: DatabaseOperationService = Depends(self.get_database_operation_service)
        ):
            """Get latest blood pressure data for a patient from the specified database connection."""
            return await self._get_patient_vital_data(
                connection_service, db_operation_service, connection_id, patient_id, "blood_pressure",
                ["systolic", "diastolic", "recorded_at", "device_id"]
            )
        
        # BMI endpoint
        @self.router.get("/patients/{patient_id}/bmi")
        async def get_patient_bmi(
            patient_id: str = Path(..., description="Patient ID to fetch BMI data for"),
            connection_id: str = Query(..., description="Database connection ID to use for fetching data"),
            connection_service: ConnectionService = Depends(self.get_connection_service),
            db_operation_service: DatabaseOperationService = Depends(self.get_database_operation_service)
        ):
            """Get latest BMI data for a patient from the specified database connection."""
            return await self._get_patient_vital_data(
                connection_service, db_operation_service, connection_id, patient_id, "bmi",
                ["bmi", "weight", "height", "recorded_at"]
            )
        
        # SpO2 endpoint
        @self.router.get("/patients/{patient_id}/spo2") 
        async def get_patient_spo2(
            patient_id: str = Path(..., description="Patient ID to fetch SpO2 data for"),
            connection_id: str = Query(..., description="Database connection ID to use for fetching data"),
            connection_service: ConnectionService = Depends(self.get_connection_service),
            db_operation_service: DatabaseOperationService = Depends(self.get_database_operation_service)
        ):
            """Get latest SpO2 data for a patient from the specified database connection."""
            return await self._get_patient_vital_data(
                connection_service, db_operation_service, connection_id, patient_id, "spo2",
                ["spo2_percentage", "recorded_at", "device_id"]
            )
        
        # Temperature endpoint
        @self.router.get("/patients/{patient_id}/temperature")
        async def get_patient_temperature(
            patient_id: str = Path(..., description="Patient ID to fetch temperature data for"),
            connection_id: str = Query(..., description="Database connection ID to use for fetching data"),
            connection_service: ConnectionService = Depends(self.get_connection_service),
            db_operation_service: DatabaseOperationService = Depends(self.get_database_operation_service)
        ):
            """Get latest temperature data for a patient from the specified database connection."""
            return await self._get_patient_vital_data(
                connection_service, db_operation_service, connection_id, patient_id, "temperature",
                ["temperature_celsius", "temperature_fahrenheit", "recorded_at", "device_id"]
            )
        
        # Blood Sugar endpoint
        @self.router.get("/patients/{patient_id}/blood-sugar")
        async def get_patient_blood_sugar(
            patient_id: str = Path(..., description="Patient ID to fetch blood sugar data for"),
            connection_id: str = Query(..., description="Database connection ID to use for fetching data"),
            connection_service: ConnectionService = Depends(self.get_connection_service),
            db_operation_service: DatabaseOperationService = Depends(self.get_database_operation_service)
        ):
            """Get latest blood sugar data for a patient from the specified database connection."""
            return await self._get_patient_vital_data(
                connection_service, db_operation_service, connection_id, patient_id, "blood_sugar",
                ["glucose_level", "test_type", "recorded_at"]
            )
        
        # Recovery Tracker endpoint
        @self.router.get("/patients/{patient_id}/recovery-tracker")
        async def get_patient_recovery_tracker(
            patient_id: str = Path(..., description="Patient ID to fetch recovery data for"),
            connection_id: str = Query(..., description="Database connection ID to use for fetching data"),
            connection_service: ConnectionService = Depends(self.get_connection_service),
            db_operation_service: DatabaseOperationService = Depends(self.get_database_operation_service)
        ):
            """Get latest recovery tracking data for a patient from the specified database connection."""
            return await self._get_patient_vital_data(
                connection_service, db_operation_service, connection_id, patient_id, "recovery_tracker",
                ["stage", "progress_percentage", "notes", "updated_at"]
            )

    async def _get_patient_vital_data(
        self, 
        connection_service: ConnectionService,
        db_operation_service: DatabaseOperationService,
        connection_id: str, 
        patient_id: str, 
        data_type: str,
        preferred_columns: list
    ) -> Dict[str, Any]:
        """Get patient vital data from the specified database connection using dynamic table discovery."""
        try:
            # Get the database connection configuration
            connection = await connection_service.get_connection_by_id(connection_id)
            if not connection:
                raise HTTPException(
                    status_code=404,
                    detail=f"Database connection with ID '{connection_id}' not found"
                )
            
            # Test the connection first
            test_result = await connection_service.test_connection(connection_id)
            if test_result.status != "success":
                raise HTTPException(
                    status_code=503,
                    detail=f"Database connection failed: {test_result.message}"
                )
            
            # Get database schema to discover available tables
            schema_result = await connection_service.get_database_schema(connection_id)
            if schema_result.status != "success":
                raise HTTPException(
                    status_code=500,
                    detail=f"Failed to retrieve database schema: {schema_result.message}"
                )
            
            # Find appropriate table for the requested data type
            table_name = await self._find_healthcare_table(schema_result, data_type)
            if not table_name:
                available_tables = [t.name for t in schema_result.tables] if schema_result.tables else []
                raise HTTPException(
                    status_code=404,
                    detail=f"No suitable table found for {data_type} data in the database. Available tables: {available_tables}"
                )
            
            # Get available columns for the found table  
            available_columns = await self._get_available_columns(schema_result, table_name, preferred_columns)
            if not available_columns:
                table_columns = []
                for table in schema_result.tables:
                    if table.name == table_name:
                        table_columns = [field.name for field in table.fields]
                        break
                raise HTTPException(
                    status_code=404,
                    detail=f"No matching columns found in table '{table_name}' for {data_type}. Available columns: {table_columns}"
                )
            
            # Generate appropriate query for the database type
            query = await self._build_patient_query(
                connection.database_type, table_name, available_columns, patient_id
            )
            
            # Execute the query using database operation service
            query_results: List[DatabaseQueryResult] = await db_operation_service.execute_query(
                connection_id=connection_id,
                query=query,
                limit=1  # Only get the latest record
            )
            
            if not query_results or not query_results[0].data:
                raise HTTPException(
                    status_code=404,
                    detail=f"No {data_type} data found for patient '{patient_id}' in table '{table_name}'"
                )
            
            # Extract the first record from the first result
            first_result = query_results[0]
            if first_result.data and len(first_result.data) > 0:
                patient_data = first_result.data[0]
                
                # Add metadata to the response
                patient_data.update({
                    "patient_id": patient_id,
                    "connection_id": connection_id,
                    "data_source": "database",
                    "timestamp": datetime.now().isoformat(),
                    "table_name": table_name,
                    "execution_time_ms": first_result.execution_time_ms,
                    "columns_found": available_columns
                })
                
                logger.info(f"Successfully fetched {data_type} data for patient {patient_id} from table '{table_name}' in connection {connection_id}")
                return patient_data
            else:
                raise HTTPException(
                    status_code=404,
                    detail=f"No data returned for patient '{patient_id}'"
                )
            
        except HTTPException:
            # Re-raise HTTP exceptions
            raise
        except Exception as e:
            logger.error(f"Error fetching {data_type} data for patient {patient_id}: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to fetch {data_type} data: {str(e)}"
            )

    async def _find_healthcare_table(self, schema_result, data_type: str) -> Optional[str]:
        """Find the most appropriate table for the requested healthcare data type."""
        if not schema_result.tables:
            return None
            
        # Healthcare table patterns for different data types
        table_patterns = {
            "heart_rate": ["heart_rate", "heartrate", "hr", "cardiac", "vitals", "vital_signs", "patient_vitals"],
            "blood_pressure": ["blood_pressure", "bloodpressure", "bp", "vitals", "vital_signs", "patient_vitals"], 
            "bmi": ["bmi", "body_mass_index", "weight", "anthropometric", "vitals", "vital_signs"],
            "spo2": ["spo2", "oxygen_saturation", "pulse_ox", "vitals", "vital_signs", "patient_vitals"],
            "temperature": ["temperature", "temp", "body_temp", "vitals", "vital_signs", "patient_vitals"],
            "blood_sugar": ["blood_sugar", "glucose", "blood_glucose", "lab_results", "laboratory"],
            "recovery_tracker": ["recovery", "recovery_tracker", "patient_progress", "treatment_progress"]
        }
        
        patterns = table_patterns.get(data_type, [data_type])
        
        # First try exact matches
        for pattern in patterns:
            for table in schema_result.tables:
                if table.name.lower() == pattern.lower():
                    logger.info(f"Found exact table match: {table.name} for {data_type}")
                    return table.name
        
        # Then try partial matches
        for pattern in patterns:
            for table in schema_result.tables:
                if pattern.lower() in table.name.lower():
                    logger.info(f"Found partial table match: {table.name} for {data_type} (pattern: {pattern})")
                    return table.name
        
        # If no specific match, try to find any table that might contain patient data
        patient_related_patterns = ["patient", "user", "person", "individual", "subject"]
        for table in schema_result.tables:
            table_lower = table.name.lower()
            for pattern in patient_related_patterns:
                if pattern in table_lower:
                    logger.info(f"Found patient-related table: {table.name} for {data_type}")
                    return table.name
        
        # Last resort - return the first table if any exists
        if schema_result.tables:
            logger.warning(f"No specific match found for {data_type}, using first available table: {schema_result.tables[0].name}")
            return schema_result.tables[0].name
            
        return None
    
    async def _get_available_columns(self, schema_result, table_name: str, preferred_columns: List[str]) -> List[str]:
        """Get available columns from the table that match the preferred columns or are relevant."""
        if not schema_result.tables:
            return []
        
        # Find the table
        target_table = None
        for table in schema_result.tables:
            if table.name == table_name:
                target_table = table
                break
                
        if not target_table:
            return []
            
        available_columns = [field.name for field in target_table.fields]
        matched_columns = []
        
        # First, try to match preferred columns exactly
        for preferred in preferred_columns:
            for available in available_columns:
                if preferred.lower() == available.lower():
                    matched_columns.append(available)
                    break
        
        # If no exact matches, try partial matches
        if not matched_columns:
            for preferred in preferred_columns:
                for available in available_columns:
                    if preferred.lower() in available.lower() or available.lower() in preferred.lower():
                        matched_columns.append(available)
                        break
        
        # If still no matches, include some common healthcare columns
        if not matched_columns:
            common_patterns = ["id", "patient", "value", "measurement", "result", "data", "time", "date", "created", "updated"]
            for pattern in common_patterns:
                for available in available_columns:
                    if pattern.lower() in available.lower() and available not in matched_columns:
                        matched_columns.append(available)
                        if len(matched_columns) >= 5:  # Limit to avoid too many columns
                            break
                if len(matched_columns) >= 5:
                    break
        
        # If still nothing, return first few columns
        if not matched_columns:
            matched_columns = available_columns[:5]  # Just take first 5 columns
            
        logger.info(f"Matched columns for table {table_name}: {matched_columns} (from available: {available_columns})")
        return matched_columns

    async def _build_patient_query(
        self, 
        database_type: str, 
        table_name: str, 
        columns: List[str], 
        patient_id: str
    ) -> str:
        """Build database-specific query for patient data."""
        db_type = database_type.lower()
        column_list = ", ".join(columns)
        
        # Find appropriate ordering columns from available columns
        time_columns = []
        for col in columns:
            col_lower = col.lower()
            if any(time_word in col_lower for time_word in ["time", "date", "created", "updated", "recorded", "modified"]):
                time_columns.append(col)
        
        # Build ORDER BY clause only with available columns
        order_clause = ""
        if time_columns:
            order_clause = f"ORDER BY {', '.join([f'{col} DESC' for col in time_columns])}"
        
        # Handle different database query syntax
        if db_type in ["mysql", "aurora-mysql"]:
            return f"""
            SELECT {column_list}
            FROM {table_name} 
            WHERE patient_id = '{patient_id}' 
            {order_clause}
            LIMIT 1
            """
        elif db_type in ["postgresql", "aurora-postgresql", "postgres"]:
            return f"""
            SELECT {column_list}
            FROM {table_name} 
            WHERE patient_id = '{patient_id}' 
            {order_clause}
            LIMIT 1
            """
        elif db_type in ["oracle", "oracle-db"]:
            return f"""
            SELECT * FROM (
                SELECT {column_list}
                FROM {table_name} 
                WHERE patient_id = '{patient_id}' 
                {order_clause}
            ) WHERE ROWNUM = 1
            """
        elif db_type in ["sqlserver", "sql-server", "mssql"]:
            return f"""
            SELECT TOP 1 {column_list}
            FROM {table_name} 
            WHERE patient_id = '{patient_id}' 
            {order_clause}
            """
        elif db_type == "mongodb":
            # For MongoDB, we need to construct a find query
            return json.dumps({
                "patient_id": patient_id
            })
        else:
            # Default to PostgreSQL syntax
            return f"""
            SELECT {column_list}
            FROM {table_name} 
            WHERE patient_id = '{patient_id}' 
            {order_clause}
            LIMIT 1
            """


# Create controller instance and get router
dashboard_controller = PatientDashboardController()
router = dashboard_controller.router