"""Healthcare-specific query generation router."""

from fastapi import APIRouter, Query, HTTPException, Depends
from typing import Union, Optional
import json

from app.services.bedrock_service import BedrockService
from app.db.session import get_database_manager

router = APIRouter()

@router.get("/healthcare/generate-query-by-connection")
async def generate_query_by_connection(
    connection_id: str = Query(..., description="Database connection ID"),
    patient_id: str = Query(..., description="Patient ID for data extraction"),
    query_type: str = Query("comprehensive", description="Type of query: comprehensive, clinical, billing, basic"),
    db_manager = Depends(get_database_manager)
):
    """
    Generate healthcare query using a database connection ID.
    
    This endpoint automatically fetches the schema from the specified database connection
    and generates the appropriate healthcare query. No need to manually provide the schema.
    
    **Query Types:**
    - **comprehensive**: Full patient profile across all healthcare domains
    - **clinical**: Medical data focused (diagnoses, procedures, medications, labs, vitals)
    - **billing**: Financial data focused (bills, claims, payments, insurance)
    - **basic**: Essential patient information only (demographics, contacts)
    
    **Example Usage:**
    ```
    GET /healthcare/generate-query-by-connection?connection_id=507f1f77bcf86cd799439011&patient_id=687b0aca-ca63-4926-800b-90d5e92e5a0a&query_type=comprehensive
    ```
    """
    try:
        # Import here to avoid circular dependency
        from app.services.connection_service import ConnectionService
        
        # Get the database schema
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
        
        # Create the schema format expected by bedrock service
        schema_dict = {
            "unified_schema": schema_result.unified_schema,
            "database_type": schema_result.database_type,
            "database_name": schema_result.database_name
        }
        
        # Generate the healthcare query
        bedrock_service = BedrockService(db_manager)
        result = bedrock_service.generate_healthcare_query(
            schema=schema_dict,
            patient_id=patient_id.strip(),
            query_type=query_type
        )
        
        if result.get("status") == "failed":
            raise HTTPException(status_code=500, detail=result.get("error"))
        
        # Add connection information to the result
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


@router.get("/healthcare/generate-mongodb-query")
async def generate_mongodb_query(
    connection_id: str = Query(..., description="MongoDB connection ID"),
    patient_id: str = Query(..., description="Patient ID for data extraction"),
    query_type: str = Query("comprehensive", description="Type of query: comprehensive, clinical, billing, basic"),
    db_manager = Depends(get_database_manager)
):
    """
    Generate MongoDB query using a database connection ID.
    
    This endpoint automatically fetches the schema from the specified MongoDB connection
    and generates the appropriate MongoDB aggregation pipeline or find queries.
    
    **Query Types:**
    - **comprehensive**: Full patient profile across all healthcare collections
    - **clinical**: Medical data focused (diagnoses, procedures, medications, labs, vitals)
    - **billing**: Financial data focused (bills, claims, payments, insurance)
    - **basic**: Essential patient information only (demographics, contacts)
    
    **Example Usage:**
    ```
    GET /healthcare/generate-mongodb-query?connection_id=507f1f77bcf86cd799439011&patient_id=687b0aca-ca63-4926-800b-90d5e92e5a0a&query_type=comprehensive
    ```
    """
    try:
        # Validate query type
        if query_type not in ["comprehensive", "clinical", "billing", "basic"]:
            raise HTTPException(
                status_code=400, 
                detail="Query type must be one of: comprehensive, clinical, billing, basic"
            )
        
        # Import here to avoid circular dependency
        from app.services.connection_service import ConnectionService
        
        # Get the database schema
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
        
        # Verify it's a MongoDB connection
        db_type_lower = schema_result.database_type.lower()
        mongodb_types = ["mongodb", "mongo", "mongodb atlas", "mongo atlas", "atlas"]
        
        if db_type_lower not in mongodb_types:
            raise HTTPException(
                status_code=400,
                detail=f"This endpoint is for MongoDB connections only. Connection type: {schema_result.database_type}"
            )
        
        # Create the schema format expected by bedrock service
        schema_dict = {
            "unified_schema": schema_result.unified_schema,
            "database_type": schema_result.database_type,
            "database_name": schema_result.database_name
        }
        
        # Generate the MongoDB query using a new MongoDB-specific method
        bedrock_service = BedrockService(db_manager)
        result = bedrock_service.generate_mongodb_query(
            schema=schema_dict,
            patient_id=patient_id.strip(),
            query_type=query_type
        )
        
        if result.get("status") == "failed":
            raise HTTPException(status_code=500, detail=result.get("error"))
        
        # Add connection information to the result
        result["connection_info"] = {
            "connection_id": connection_id,
            "database_type": schema_result.database_type,
            "database_name": schema_result.database_name,
            "total_collections": schema_result.unified_schema.get("summary", {}).get("total_collections", 0)
        }
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating MongoDB query: {str(e)}")


@router.get("/healthcare/generate-query")
async def generate_healthcare_query(
    schema: str = Query(..., description="Healthcare database schema (JSON format)"),
    patient_id: str = Query(..., description="Patient ID (UUID, string, or integer)"),
    query_type: str = Query(
        "comprehensive", 
        description="Query type: 'comprehensive', 'clinical', 'billing', or 'basic'"
    ),
    db_manager = Depends(get_database_manager)
):
    """
    Generate healthcare-specific SQL queries for patient data extraction.
    
    This endpoint is optimized for healthcare databases with tables like:
    - patients, encounters, diagnoses, procedures
    - medications, lab results, vital signs
    - billing, insurance claims, payments
    """
    try:
        # Validate parameters
        if not schema or not schema.strip():
            raise HTTPException(status_code=400, detail="Schema parameter is required")
        
        patient_id = patient_id.strip() if patient_id else ""
        if not patient_id:
            raise HTTPException(status_code=400, detail="Patient ID is required")
        
        if query_type not in ["comprehensive", "clinical", "billing", "basic"]:
            raise HTTPException(
                status_code=400, 
                detail="Query type must be one of: comprehensive, clinical, billing, basic"
            )
        
        # Initialize Bedrock service
        bedrock_service = BedrockService(db_manager)
        
        # Generate healthcare query
        result = bedrock_service.generate_healthcare_query(
            schema=schema,
            patient_id=patient_id,
            query_type=query_type
        )
        
        if result.get("status") == "failed":
            raise HTTPException(status_code=500, detail=result.get("error", "Query generation failed"))
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")


@router.get("/healthcare/generate-comprehensive")
async def generate_comprehensive_patient_query(
    schema: str = Query(..., description="Healthcare database schema (JSON format)"),
    patient_id: str = Query(..., description="Patient ID to extract comprehensive data for"),
    db_manager = Depends(get_database_manager)
):
    """
    Generate a comprehensive query that retrieves ALL patient medical information.
    
    Includes: demographics, encounters, diagnoses, procedures, medications,
    lab results, vital signs, billing information, and more.
    """
    try:
        bedrock_service = BedrockService(db_manager)
        result = bedrock_service.generate_healthcare_query(
            schema=schema,
            patient_id=patient_id.strip(),
            query_type="comprehensive"
        )
        
        if result.get("status") == "failed":
            raise HTTPException(status_code=500, detail=result.get("error"))
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating comprehensive query: {str(e)}")


@router.get("/healthcare/generate-clinical")
async def generate_clinical_query(
    schema: str = Query(..., description="Healthcare database schema (JSON format)"),
    patient_id: str = Query(..., description="Patient ID for clinical data extraction"),
    db_manager = Depends(get_database_manager)
):
    """
    Generate a clinical-focused query for patient medical data.
    
    Focuses on: diagnoses, procedures, medications, lab results, vital signs,
    and clinical assessments while excluding billing information.
    """
    try:
        bedrock_service = BedrockService(db_manager)
        result = bedrock_service.generate_healthcare_query(
            schema=schema,
            patient_id=patient_id.strip(),
            query_type="clinical"
        )
        
        if result.get("status") == "failed":
            raise HTTPException(status_code=500, detail=result.get("error"))
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating clinical query: {str(e)}")


@router.get("/healthcare/generate-billing")
async def generate_billing_query(
    schema: str = Query(..., description="Healthcare database schema (JSON format)"),
    patient_id: str = Query(..., description="Patient ID for billing data extraction"),
    db_manager = Depends(get_database_manager)
):
    """
    Generate a billing-focused query for patient financial information.
    
    Focuses on: patient bills, insurance claims, payments, outstanding balances,
    and financial history while including basic demographics.
    """
    try:
        bedrock_service = BedrockService(db_manager)
        result = bedrock_service.generate_healthcare_query(
            schema=schema,
            patient_id=patient_id.strip(),
            query_type="billing"
        )
        
        if result.get("status") == "failed":
            raise HTTPException(status_code=500, detail=result.get("error"))
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating billing query: {str(e)}")


@router.get("/healthcare/schema-analysis")
async def analyze_healthcare_schema(
    schema: str = Query(..., description="Healthcare database schema to analyze"),
    db_manager = Depends(get_database_manager)
):
    """
    Analyze the provided healthcare schema and return insights.
    
    Returns information about tables, relationships, and healthcare-specific
    data structures found in the schema.
    """
    try:
        # Parse schema
        try:
            schema_dict = json.loads(schema)
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="Schema must be valid JSON")
        
        analysis = {
            "schema_type": "unknown",
            "total_tables": 0,
            "healthcare_tables": [],
            "patient_related_tables": [],
            "billing_tables": [],
            "clinical_tables": [],
            "administrative_tables": []
        }
        
        # Analyze unified schema format
        if "unified_schema" in schema_dict:
            unified = schema_dict["unified_schema"]
            analysis["schema_type"] = "unified_healthcare_schema"
            
            if "tables" in unified:
                tables = unified["tables"]
                analysis["total_tables"] = len(tables)
                
                # Categorize tables by healthcare domain
                for table in tables:
                    table_name = table.get("name", "").lower()
                    
                    if any(keyword in table_name for keyword in ["patient", "person", "demographic"]):
                        analysis["patient_related_tables"].append(table["name"])
                    
                    if any(keyword in table_name for keyword in ["bill", "payment", "insurance", "claim", "charge"]):
                        analysis["billing_tables"].append(table["name"])
                    
                    if any(keyword in table_name for keyword in ["diagnosis", "procedure", "medication", "lab", "vital", "clinical", "treatment"]):
                        analysis["clinical_tables"].append(table["name"])
                    
                    if any(keyword in table_name for keyword in ["department", "provider", "staff", "unit", "bed"]):
                        analysis["administrative_tables"].append(table["name"])
                
                analysis["healthcare_tables"] = [table["name"] for table in tables]
        
        # Add database info if available
        if "unified_schema" in schema_dict and "database_info" in schema_dict["unified_schema"]:
            db_info = schema_dict["unified_schema"]["database_info"]
            analysis["database_info"] = {
                "name": db_info.get("name"),
                "type": db_info.get("type"),
                "version": db_info.get("version"),
                "total_rows": schema_dict["unified_schema"].get("summary", {}).get("total_rows")
            }
        
        return {
            "schema_analysis": analysis,
            "recommendations": {
                "query_types_supported": ["comprehensive", "clinical", "billing", "basic"],
                "optimal_query_type": "comprehensive" if analysis["total_tables"] > 30 else "clinical",
                "patient_id_fields": ["patient_id", "mrn", "person_id"],
                "key_relationships": "Most tables likely link via patient_id (UUID format)"
            },
            "status": "success"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Schema analysis failed: {str(e)}")


@router.get("/healthcare/test-with-sample")
async def test_with_sample_data(
    db_manager = Depends(get_database_manager)
):
    """
    Test the healthcare query generator with sample schema and patient ID.
    Use this endpoint to verify the system works before using your real data.
    """
    try:
        # Sample healthcare schema
        sample_schema = {
            "unified_schema": {
                "database_info": {
                    "name": "sample_healthcare_db",
                    "type": "postgresql"
                },
                "tables": [
                    {
                        "name": "patients",
                        "columns": [
                            {"name": "patient_id", "type": "uuid", "primary_key": True},
                            {"name": "mrn", "type": "varchar(50)"},
                            {"name": "first_name", "type": "varchar(128)"},
                            {"name": "last_name", "type": "varchar(128)"},
                            {"name": "date_of_birth", "type": "date"},
                            {"name": "gender", "type": "varchar(20)"}
                        ]
                    },
                    {
                        "name": "encounters",
                        "columns": [
                            {"name": "encounter_id", "type": "uuid", "primary_key": True},
                            {"name": "patient_id", "type": "uuid"},
                            {"name": "encounter_type", "type": "varchar(100)"},
                            {"name": "admission_datetime", "type": "timestamp"}
                        ]
                    },
                    {
                        "name": "diagnoses",
                        "columns": [
                            {"name": "diagnosis_id", "type": "uuid", "primary_key": True},
                            {"name": "patient_id", "type": "uuid"},
                            {"name": "diagnosis_code", "type": "varchar(20)"},
                            {"name": "diagnosis_description", "type": "varchar(500)"}
                        ]
                    }
                ]
            }
        }
        
        sample_patient_id = "12345678-1234-1234-1234-123456789012"
        
        bedrock_service = BedrockService(db_manager)
        result = bedrock_service.generate_healthcare_query(
            schema=sample_schema,
            patient_id=sample_patient_id,
            query_type="comprehensive"
        )
        
        return {
            "test_result": result,
            "sample_schema_used": sample_schema,
            "sample_patient_id_used": sample_patient_id,
            "message": "This was a test with sample data. Replace with your actual schema and patient ID.",
            "status": "success"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Test failed: {str(e)}")
