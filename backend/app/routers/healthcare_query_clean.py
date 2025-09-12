"""
Healthcare Query Router - Connection-Based Approach Only

This router provides healthcare-specific SQL query generation using database connections.
All endpoints automatically fetch schemas from database connections - no manual schema required.
"""

from fastapi import APIRouter, Query, Depends, HTTPException
from app.services.bedrock_service import BedrockService
from app.db.session import get_database_manager

router = APIRouter()


@router.get("/healthcare/generate-query")
async def generate_healthcare_query(
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
    GET /healthcare/generate-query?connection_id=507f1f77bcf86cd799439011&patient_id=687b0aca-ca63-4926-800b-90d5e92e5a0a&query_type=comprehensive
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
        raise HTTPException(status_code=500, detail=f"Error generating healthcare query: {str(e)}")


@router.get("/healthcare/generate-comprehensive")
async def generate_comprehensive_query(
    connection_id: str = Query(..., description="Database connection ID"),
    patient_id: str = Query(..., description="Patient ID for comprehensive data extraction"),
    db_manager = Depends(get_database_manager)
):
    """
    Generate a comprehensive query for complete patient health records.
    
    Includes: demographics, encounters, diagnoses, procedures, medications,
    lab results, vital signs, billing, insurance, and all related data.
    """
    return await generate_healthcare_query(
        connection_id=connection_id,
        patient_id=patient_id,
        query_type="comprehensive",
        db_manager=db_manager
    )


@router.get("/healthcare/generate-clinical")
async def generate_clinical_query(
    connection_id: str = Query(..., description="Database connection ID"),
    patient_id: str = Query(..., description="Patient ID for clinical data extraction"),
    db_manager = Depends(get_database_manager)
):
    """
    Generate a clinical-focused query for patient medical data.
    
    Focuses on: diagnoses, procedures, medications, lab results, vital signs,
    and clinical assessments while excluding billing information.
    """
    return await generate_healthcare_query(
        connection_id=connection_id,
        patient_id=patient_id,
        query_type="clinical",
        db_manager=db_manager
    )


@router.get("/healthcare/generate-billing")
async def generate_billing_query(
    connection_id: str = Query(..., description="Database connection ID"),
    patient_id: str = Query(..., description="Patient ID for billing data extraction"),
    db_manager = Depends(get_database_manager)
):
    """
    Generate a billing-focused query for patient financial data.
    
    Focuses on: billing records, insurance claims, payments, charges,
    and financial transactions while including basic patient demographics.
    """
    return await generate_healthcare_query(
        connection_id=connection_id,
        patient_id=patient_id,
        query_type="billing",
        db_manager=db_manager
    )


@router.get("/healthcare/generate-basic")
async def generate_basic_query(
    connection_id: str = Query(..., description="Database connection ID"),
    patient_id: str = Query(..., description="Patient ID for basic data extraction"),
    db_manager = Depends(get_database_manager)
):
    """
    Generate a basic query for essential patient information.
    
    Focuses on: patient demographics, contact information, and basic identifiers.
    """
    return await generate_healthcare_query(
        connection_id=connection_id,
        patient_id=patient_id,
        query_type="basic",
        db_manager=db_manager
    )


@router.get("/healthcare/schema-analysis")
async def analyze_healthcare_schema(
    connection_id: str = Query(..., description="Database connection ID"),
    db_manager = Depends(get_database_manager)
):
    """
    Analyze database schema for healthcare-specific table identification.
    
    Returns information about detected healthcare tables and their relationships.
    """
    try:
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
        
        # Analyze healthcare tables
        unified = schema_result.unified_schema
        tables = unified.get("tables", [])
        
        # Identify healthcare table categories
        healthcare_tables = {
            "patient_related": [],
            "clinical": [],
            "billing": [],
            "administrative": [],
            "other": []
        }
        
        for table in tables:
            table_name = table.get("name", "").lower()
            
            if any(keyword in table_name for keyword in ["patient", "person", "individual"]):
                healthcare_tables["patient_related"].append(table["name"])
            elif any(keyword in table_name for keyword in ["diagnosis", "procedure", "medication", "lab", "vital", "encounter", "visit"]):
                healthcare_tables["clinical"].append(table["name"])
            elif any(keyword in table_name for keyword in ["bill", "claim", "payment", "insurance", "charge"]):
                healthcare_tables["billing"].append(table["name"])
            elif any(keyword in table_name for keyword in ["provider", "facility", "department", "staff", "user"]):
                healthcare_tables["administrative"].append(table["name"])
            else:
                healthcare_tables["other"].append(table["name"])
        
        return {
            "status": "success",
            "message": "Healthcare schema analysis completed",
            "connection_info": {
                "connection_id": connection_id,
                "database_type": schema_result.database_type,
                "database_name": schema_result.database_name
            },
            "schema_summary": {
                "total_tables": len(tables),
                "healthcare_coverage": {
                    "patient_tables": len(healthcare_tables["patient_related"]),
                    "clinical_tables": len(healthcare_tables["clinical"]),
                    "billing_tables": len(healthcare_tables["billing"]),
                    "administrative_tables": len(healthcare_tables["administrative"]),
                    "other_tables": len(healthcare_tables["other"])
                }
            },
            "healthcare_tables": healthcare_tables
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing healthcare schema: {str(e)}")
