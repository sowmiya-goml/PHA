"""Healthcare query generation router with class-based structure."""

from fastapi import APIRouter, Query, HTTPException, Depends
import json

from pha.services.bedrock_service import BedrockService
from pha.db.session import get_database_manager
from pha.schemas.healthcare import HealthcareQueryResponse


class HealthcareQueryController:
    """Controller class for healthcare query generation endpoints."""
    
    def __init__(self):
        """Initialize the healthcare query controller."""
        self.router = APIRouter()
        self._setup_routes()
    
    def _setup_routes(self):
        """Setup routes for the healthcare query controller."""
        self.router.add_api_route(
            "/generate-query-by-connection",
            self.generate_query_by_connection,
            methods=["GET"],
            summary="Generate Query By Connection",
            description="Generate healthcare query using a database connection ID",
            response_model=HealthcareQueryResponse
        )
    
    async def generate_query_by_connection(
        self,
        connection_id: str = Query(..., description="Database connection ID"),
        patient_id: str = Query(..., description="Patient ID for data extraction"),
        query_type: str = Query("comprehensive", description="Type of query: comprehensive, clinical, billing, basic"),
        db_manager = Depends(get_database_manager)
    ):
        """
        Generate healthcare query using a database connection ID.
        
        This endpoint automatically fetches the schema from the specified database connection
        and generates the appropriate healthcare query. No need to manually provide the schema.
        
        Query Types:
        - comprehensive: Full patient profile across all healthcare domains
        - clinical: Medical data focused (diagnoses, procedures, medications, labs, vitals)
        - billing: Financial data focused (bills, claims, payments, insurance)
        - basic: Essential patient information only (demographics, contacts)
        
        Example Usage:
        GET /healthcare/generate-query-by-connection?connection_id=507f1f77bcf86cd799439011&patient_id=687b0aca-ca63-4926-800b-90d5e92e5a0a&query_type=comprehensive
        """
        try:
            # Import here to avoid circular dependency
            from pha.services.connection_service import ConnectionService
            
            connection_service = ConnectionService(db_manager)
            schema_result = await connection_service.get_database_schema(connection_id)
            
            if schema_result.status != "success":
                raise HTTPException(
                    status_code=400,
                    detail=f"Failed to retrieve schema: {schema_result.message}"
                )
            
            if not schema_result.unified_schema:
                raise HTTPException(
                    status_code=404,
                    detail="Unified schema not available for this database connection"
                )
            
            schema_dict = {
                "unified_schema": schema_result.unified_schema,
                "database_type": schema_result.database_type,
                "database_name": schema_result.database_name
            }
            
            bedrock_service = BedrockService(db_manager)
            result = bedrock_service.generate_healthcare_query(
                schema=schema_dict,
                patient_id=patient_id.strip(),
                query_type=query_type
            )
            
            if result.get("status") == "failed":
                raise HTTPException(status_code=500, detail=result.get("error"))
            
            result["connection_info"] = {
                "connection_id": connection_id,
                "database_type": schema_result.database_type,
                "database_name": schema_result.database_name,
                "total_tables": schema_result.unified_schema.get("summary", {}).get("total_tables", 0)
            }
            
            return result
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error generating query by connection: {str(e)}")


# Create controller instance and get router
healthcare_controller = HealthcareQueryController()
router = healthcare_controller.router
