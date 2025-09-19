"""Patient dashboard service for MongoDB operations."""

from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from bson import ObjectId

from pha.models.dashboard import (
    Patient, HeartRate, BloodPressure, BMI, SpO2, 
    Temperature, BloodSugar, RecoveryTracker
)
from pha.schemas.dashboard import (
    HeartRateResponse, BloodPressureResponse, BMIResponse,
    SpO2Response, TemperatureResponse, BloodSugarResponse,
    RecoveryTrackerResponse, RecoveryDataPoint,
)
from pha.services.connection_service import ConnectionService
from pha.services.database_operation_service import DatabaseOperationService


class DashboardService:
    """Service for patient dashboard operations using database connections."""
    
    def __init__(self, db_manager):
        self.db_manager = db_manager
        self.connection_service = ConnectionService(db_manager)
        self.db_operation_service = DatabaseOperationService(db_manager)
    
    def _auto_detect_database_type(self, connection_string: str) -> str:
        """Auto-detect database type from connection string."""
        connection_string_lower = connection_string.lower()
        
        if connection_string_lower.startswith('postgresql://') or connection_string_lower.startswith('postgres://'):
            return 'postgresql'
        elif connection_string_lower.startswith('mysql://'):
            return 'mysql'  
        elif connection_string_lower.startswith('mongodb://') or connection_string_lower.startswith('mongodb+srv://'):
            return 'mongodb'
        elif connection_string_lower.startswith('snowflake://'):
            return 'snowflake'
        elif connection_string_lower.startswith('oracle://'):
            return 'oracle'
        elif 'server=' in connection_string_lower and ('database=' in connection_string_lower or 'initial catalog=' in connection_string_lower):
            return 'sqlserver'
        else:
            # If we can't detect, return None
            return None
    
    def _is_supported_db_type(self, db_type: str) -> bool:
        """Check if database type is supported."""
        supported_types = [
            'mysql', 'postgresql', 'aurora-mysql', 'aurora-postgresql', 
            'sql-server', 'mssql', 'sqlserver', 'snowflake', 'mongodb'
        ]
        return db_type.lower() in supported_types
    
    def _get_effective_database_type(self, connection) -> str:
        """Get the effective database type, auto-detecting if necessary."""
        db_type = connection.database_type.lower()
        
        # Auto-detect database type if it's generic or unsupported
        if db_type in ['sql', 'database', 'db'] or not self._is_supported_db_type(db_type):
            detected_type = self._auto_detect_database_type(connection.connection_string)
            if detected_type:
                return detected_type
        
        return db_type

    async def validate_connection_and_patient(self, connection_id: str, patient_id: str) -> Dict[str, Any]:
        """Validate connection exists and get connection info."""
        try:
            # Get connection details
            connection = await self.connection_service.get_connection_by_id(connection_id)
            if not connection:
                raise ValueError(f"Connection with ID {connection_id} not found")
            
            # Test connection
            test_result = await self.connection_service.test_connection(connection_id)
            if test_result.status != "success":
                raise ValueError(f"Connection {connection_id} is not accessible: {test_result.message}")
            
            return {
                "connection": connection,
                "connection_info": test_result
            }
        except Exception as e:
            raise ValueError(f"Failed to validate connection {connection_id}: {str(e)}")
    
    async def get_heart_rate(self, patient_id: str, connection_id: str) -> HeartRateResponse:
        """Get latest heart rate for a patient from specified connection."""
        try:
            # Validate connection
            conn_info = await self.validate_connection_and_patient(connection_id, patient_id)
            connection = conn_info["connection"]
            
            # Get effective database type (with auto-detection)
            db_type = self._get_effective_database_type(connection)
            
            # Build query for heart rate data
            if db_type in ['mysql', 'postgresql', 'aurora-mysql', 'aurora-postgresql', 'sql-server', 'mssql', 'sqlserver', 'snowflake']:
                # SQL databases
                query = f"""
                SELECT heart_rate, status, timestamp, created_at
                FROM heart_rate 
                WHERE patient_id = '{patient_id}' 
                ORDER BY timestamp DESC 
                LIMIT 1
                """
            elif db_type == 'mongodb':
                # MongoDB
                query = {
                    "collection": "heart_rate",
                    "operation": "find",
                    "filter": {"patient_id": patient_id},
                    "sort": {"timestamp": -1},
                    "limit": 1
                }
            else:
                raise ValueError(f"Unsupported database type: {db_type}")
            
            # Execute query
            result = await self.db_operation_service.execute_query(
                connection_id=connection_id,
                query=query
            )
            
            if result.success and result.data and len(result.data) > 0:
                row = result.data[0]
                return HeartRateResponse(
                    heart_rate=row.get('heart_rate', 0),
                    status=row.get('status', 'unknown'),
                    timestamp=row.get('timestamp', datetime.utcnow())
                )
            else:
                # No data found - return error instead of mock data
                raise ValueError(f"No heart rate data found for patient {patient_id}")
                
        except Exception as e:
            raise ValueError(f"Error retrieving heart rate data: {str(e)}")
    
    async def get_blood_pressure(self, patient_id: str, connection_id: str) -> BloodPressureResponse:
        """Get latest blood pressure for a patient from specified connection."""
        try:
            # Validate connection
            conn_info = await self.validate_connection_and_patient(connection_id, patient_id)
            connection = conn_info["connection"]
            
            # Get effective database type (with auto-detection)
            db_type = self._get_effective_database_type(connection)
            
            # Build query for blood pressure data
            if db_type in ['mysql', 'postgresql', 'aurora-mysql', 'aurora-postgresql', 'sql-server', 'mssql', 'sqlserver', 'snowflake']:
                # SQL databases
                query = f"""
                SELECT systolic, diastolic, status, timestamp, created_at
                FROM blood_pressure 
                WHERE patient_id = '{patient_id}' 
                ORDER BY timestamp DESC 
                LIMIT 1
                """
            elif db_type == 'mongodb':
                # MongoDB
                query = {
                    "collection": "blood_pressure",
                    "operation": "find",
                    "filter": {"patient_id": patient_id},
                    "sort": {"timestamp": -1},
                    "limit": 1
                }
            else:
                raise ValueError(f"Unsupported database type: {db_type}")
            
            # Execute query
            result = await self.db_operation_service.execute_query(
                connection_id=connection_id,
                query=query
            )
            
            if result.success and result.data and len(result.data) > 0:
                row = result.data[0]
                return BloodPressureResponse(
                    systolic=row.get('systolic', 0),
                    diastolic=row.get('diastolic', 0),
                    status=row.get('status', 'unknown'),
                    timestamp=row.get('timestamp', datetime.utcnow())
                )
            else:
                # No data found - return error instead of mock data
                raise ValueError(f"No blood pressure data found for patient {patient_id}")
                
        except Exception as e:
            raise ValueError(f"Error retrieving blood pressure data: {str(e)}")
    
    async def get_bmi(self, patient_id: str, connection_id: str) -> BMIResponse:
        """Get latest BMI for a patient from specified connection."""
        try:
            # Validate connection
            conn_info = await self.validate_connection_and_patient(connection_id, patient_id)
            connection = conn_info["connection"]
            
            # Get effective database type (with auto-detection)
            db_type = self._get_effective_database_type(connection)
            
            # Build query for BMI data
            if db_type in ['mysql', 'postgresql', 'aurora-mysql', 'aurora-postgresql', 'sql-server', 'mssql', 'sqlserver', 'snowflake']:
                # SQL databases
                query = f"""
                SELECT bmi_value, trend, timestamp, weight, height, created_at
                FROM bmi 
                WHERE patient_id = '{patient_id}' 
                ORDER BY timestamp DESC 
                LIMIT 1
                """
            elif db_type == 'mongodb':
                # MongoDB
                query = {
                    "collection": "bmi",
                    "operation": "find",
                    "filter": {"patient_id": patient_id},
                    "sort": {"timestamp": -1},
                    "limit": 1
                }
            else:
                raise ValueError(f"Unsupported database type: {db_type}")
            
            # Execute query
            result = await self.db_operation_service.execute_query(
                connection_id=connection_id,
                query=query
            )
            
            if result.success and result.data and len(result.data) > 0:
                row = result.data[0]
                return BMIResponse(
                    bmi_value=row.get('bmi_value', 0.0),
                    trend=row.get('trend', 'stable'),
                    timestamp=row.get('timestamp', datetime.utcnow()),
                    weight=row.get('weight'),
                    height=row.get('height')
                )
            else:
                # No data found - return error instead of mock data
                raise ValueError(f"No BMI data found for patient {patient_id}")
                
        except Exception as e:
            raise ValueError(f"Error retrieving BMI data: {str(e)}")
    
    async def get_spo2(self, patient_id: str, connection_id: str) -> SpO2Response:
        """Get latest SpO2 for a patient from specified connection."""
        try:
            # Validate connection
            conn_info = await self.validate_connection_and_patient(connection_id, patient_id)
            connection = conn_info["connection"]
            
            # Get effective database type (with auto-detection)
            db_type = self._get_effective_database_type(connection)
            
            # Build query for SpO2 data
            if db_type in ['mysql', 'postgresql', 'aurora-mysql', 'aurora-postgresql', 'sql-server', 'mssql', 'sqlserver', 'snowflake']:
                # SQL databases
                query = f"""
                SELECT oxygen_saturation, status, timestamp, created_at
                FROM spo2 
                WHERE patient_id = '{patient_id}' 
                ORDER BY timestamp DESC 
                LIMIT 1
                """
            elif db_type == 'mongodb':
                # MongoDB
                query = {
                    "collection": "spo2",
                    "operation": "find",
                    "filter": {"patient_id": patient_id},
                    "sort": {"timestamp": -1},
                    "limit": 1
                }
            else:
                raise ValueError(f"Unsupported database type: {db_type}")
            
            # Execute query
            result = await self.db_operation_service.execute_query(
                connection_id=connection_id,
                query=query
            )
            
            if result.success and result.data and len(result.data) > 0:
                row = result.data[0]
                return SpO2Response(
                    oxygen_saturation=row.get('oxygen_saturation', 0.0),
                    status=row.get('status', 'unknown'),
                    timestamp=row.get('timestamp', datetime.utcnow())
                )
            else:
                # No data found - return error instead of mock data
                raise ValueError(f"No SpO2 data found for patient {patient_id}")
                
        except Exception as e:
            raise ValueError(f"Error retrieving SpO2 data: {str(e)}")
    
    async def get_temperature(self, patient_id: str, connection_id: str) -> TemperatureResponse:
        """Get latest temperature for a patient from specified connection."""
        try:
            # Validate connection
            conn_info = await self.validate_connection_and_patient(connection_id, patient_id)
            connection = conn_info["connection"]
            
            # Get effective database type (with auto-detection)
            db_type = self._get_effective_database_type(connection)
            
            # Build query for temperature data
            if db_type in ['mysql', 'postgresql', 'aurora-mysql', 'aurora-postgresql', 'sql-server', 'mssql', 'sqlserver', 'snowflake']:
                # SQL databases
                query = f"""
                SELECT temperature_f, temperature_c, status, timestamp, created_at
                FROM temperature 
                WHERE patient_id = '{patient_id}' 
                ORDER BY timestamp DESC 
                LIMIT 1
                """
            elif db_type == 'mongodb':
                # MongoDB
                query = {
                    "collection": "temperature",
                    "operation": "find",
                    "filter": {"patient_id": patient_id},
                    "sort": {"timestamp": -1},
                    "limit": 1
                }
            else:
                raise ValueError(f"Unsupported database type: {db_type}")
            
            # Execute query
            result = await self.db_operation_service.execute_query(
                connection_id=connection_id,
                query=query
            )
            
            if result.success and result.data and len(result.data) > 0:
                row = result.data[0]
                return TemperatureResponse(
                    temperature_f=row.get('temperature_f', 0.0),
                    temperature_c=row.get('temperature_c', 0.0),
                    status=row.get('status', 'unknown'),
                    timestamp=row.get('timestamp', datetime.utcnow())
                )
            else:
                # No data found - return error instead of mock data
                raise ValueError(f"No temperature data found for patient {patient_id}")
                
        except Exception as e:
            raise ValueError(f"Error retrieving temperature data: {str(e)}")
    
    async def get_blood_sugar(self, patient_id: str, connection_id: str) -> BloodSugarResponse:
        """Get latest blood sugar for a patient from specified connection."""
        try:
            # Validate connection
            conn_info = await self.validate_connection_and_patient(connection_id, patient_id)
            connection = conn_info["connection"]
            
            # Get effective database type (with auto-detection)
            db_type = self._get_effective_database_type(connection)
            
            # Build query for blood sugar data
            if db_type in ['mysql', 'postgresql', 'aurora-mysql', 'aurora-postgresql', 'sql-server', 'mssql', 'sqlserver', 'snowflake']:
                # SQL databases
                query = f"""
                SELECT glucose_level, trend, timestamp, measurement_type, created_at
                FROM blood_sugar 
                WHERE patient_id = '{patient_id}' 
                ORDER BY timestamp DESC 
                LIMIT 1
                """
            elif db_type == 'mongodb':
                # MongoDB
                query = {
                    "collection": "blood_sugar",
                    "operation": "find",
                    "filter": {"patient_id": patient_id},
                    "sort": {"timestamp": -1},
                    "limit": 1
                }
            else:
                raise ValueError(f"Unsupported database type: {db_type}")
            
            # Execute query
            result = await self.db_operation_service.execute_query(
                connection_id=connection_id,
                query=query
            )
            
            if result.success and result.data and len(result.data) > 0:
                row = result.data[0]
                return BloodSugarResponse(
                    glucose_level=row.get('glucose_level', 0.0),
                    trend=row.get('trend', 'stable'),
                    timestamp=row.get('timestamp', datetime.utcnow()),
                    measurement_type=row.get('measurement_type')
                )
            else:
                # No data found - return error instead of mock data
                raise ValueError(f"No blood sugar data found for patient {patient_id}")
                
        except Exception as e:
            raise ValueError(f"Error retrieving blood sugar data: {str(e)}")
    
    async def get_recovery_tracker(self, patient_id: str, connection_id: str, days: int = 30) -> RecoveryTrackerResponse:
        """Get recovery tracker data for a patient from specified connection."""
        try:
            # Validate connection
            conn_info = await self.validate_connection_and_patient(connection_id, patient_id)
            connection = conn_info["connection"]
            
            # Get effective database type (with auto-detection)
            db_type = self._get_effective_database_type(connection)
            
            # Calculate date range
            start_date = datetime.utcnow() - timedelta(days=days)
            
            # Build query for recovery tracker data
            if db_type in ['mysql', 'postgresql', 'aurora-mysql', 'aurora-postgresql', 'sql-server', 'mssql', 'sqlserver', 'snowflake']:
                # SQL databases
                query = f"""
                SELECT recovery_score, date, notes, recovery_type, created_at
                FROM recovery_tracker 
                WHERE patient_id = '{patient_id}' 
                AND date >= '{start_date.strftime('%Y-%m-%d %H:%M:%S')}'
                ORDER BY date ASC
                """
            elif db_type == 'mongodb':
                # MongoDB
                query = {
                    "collection": "recovery_tracker",
                    "operation": "find",
                    "filter": {
                        "patient_id": patient_id,
                        "date": {"$gte": start_date}
                    },
                    "sort": {"date": 1}
                }
            else:
                raise ValueError(f"Unsupported database type: {db_type}")
            
            # Execute query
            result = await self.db_operation_service.execute_query(
                connection_id=connection_id,
                query=query
            )
            
            if result.success and result.data and len(result.data) > 0:
                recovery_data = []
                for row in result.data:
                    recovery_data.append(RecoveryDataPoint(
                        date=row.get('date', datetime.utcnow()),
                        recovery_score=row.get('recovery_score', 0.0),
                        notes=row.get('notes'),
                        recovery_type=row.get('recovery_type')
                    ))
                
                # Calculate trend and latest score
                latest_score = recovery_data[-1].recovery_score if recovery_data else None
                trend = self._calculate_recovery_trend(recovery_data)
                
                return RecoveryTrackerResponse(
                    patient_id=patient_id,
                    recovery_data=recovery_data,
                    latest_score=latest_score,
                    trend=trend
                )
            else:
                # No data found - return error instead of mock data
                raise ValueError(f"No recovery tracker data found for patient {patient_id}")
                
        except Exception as e:
            raise ValueError(f"Error retrieving recovery tracker data: {str(e)}")
    
    def _calculate_recovery_trend(self, recovery_data: List[RecoveryDataPoint]) -> str:
        """Calculate recovery trend from data points."""
        if len(recovery_data) < 2:
            return "stable"
        
        # Compare latest score to average of previous scores
        latest_score = recovery_data[-1].recovery_score
        previous_scores = [point.recovery_score for point in recovery_data[:-1]]
        avg_previous = sum(previous_scores) / len(previous_scores)
        
        if latest_score > avg_previous + 5:
            return "improving"
        elif latest_score < avg_previous - 5:
            return "declining"
        else:
            return "stable"