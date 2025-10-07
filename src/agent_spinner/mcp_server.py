"""MCP Server for healthcare agents using FastMCP - Direct Database Access."""

from typing import Any, Dict, List
from fastmcp import FastMCP
import json
from datetime import datetime
import sys
import os
import asyncio
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - MCP Server - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stderr)]
)
logger = logging.getLogger(__name__)

# Add parent directory to path to import from src
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from db.session import DatabaseManager
from services.database_operation_service import DatabaseOperationService
from core.config import settings

# Initialize FastMCP server
mcp = FastMCP("Healthcare Agent Server")

# Initialize database manager and services
db_manager = None
db_ops_service = None
_services_initialized = False


async def ensure_services_initialized():
    """Ensure database connection and services are initialized."""
    global db_manager, db_ops_service, _services_initialized
    
    if not _services_initialized:
        try:
            logger.info("Initializing database connection...")
            db_manager = DatabaseManager(
                mongodb_url=settings.MONGODB_URL,
                database_name=settings.DATABASE_NAME
            )
            await db_manager.connect()
            db_ops_service = DatabaseOperationService(db_manager)
            _services_initialized = True
            logger.info("Database connection initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize services: {e}")
            raise


def format_data_response(data: List[Dict], query: str, record_count: int) -> Dict[str, Any]:
    """Format database query results for MCP tools."""
    if data:
        return {
            "status": "success",
            "data": data,
            "query_executed": query,
            "total_records": record_count,
            "message": f"Retrieved {record_count} record(s) successfully"
        }
    else:
        return {
            "status": "success",
            "data": [],
            "query_executed": query,
            "total_records": 0,
            "message": "No records found for the given criteria"
        }


@mcp.tool()
async def get_patient_demographics(
    connection_id: str,
    patient_id: str
) -> Dict[str, Any]:
    """
    Retrieve comprehensive patient demographic information.
    
    Args:
        connection_id: Database connection identifier
        patient_id: Patient unique identifier
        
    Returns:
        Patient demographics including personal details, contact info, and health profile
    """
    await ensure_services_initialized()
    try:
        logger.info(f"get_patient_demographics called: connection_id={connection_id}, patient_id={patient_id}")
        query = f"""
        SELECT patient_id, mrn, first_name, last_name, date_of_birth, 
               gender, blood_type, is_active
        FROM patients 
        WHERE patient_id = '{patient_id}'
        LIMIT 1
        """
        
        results = await db_ops_service.execute_query(
            connection_id=connection_id,
            query=query,
            params={}
        )
        
        if results and len(results) > 0:
            logger.info(f"Successfully retrieved demographics for patient {patient_id}")
            return format_data_response(results[0].data, query, results[0].row_count)
        logger.warning(f"No patient found with ID {patient_id}")
        return {"status": "error", "message": "No patient found", "data": []}
    except Exception as e:
        logger.error(f"Error in get_patient_demographics: {e}", exc_info=True)
        return {"status": "error", "error": str(e), "message": "Failed to retrieve demographics"}


@mcp.tool()
async def get_patient_medications(
    connection_id: str,
    patient_id: str
) -> Dict[str, Any]:
    """Retrieve patient medication history and current prescriptions."""
    await ensure_services_initialized()
    try:
        query = f"""
        SELECT medication_id, medication_name, dosage, frequency, start_date, end_date
        FROM medications 
        WHERE patient_id = '{patient_id}'
        ORDER BY start_date DESC
        LIMIT 50
        """
        
        results = await db_ops_service.execute_query(connection_id=connection_id, query=query, params={})
        if results and len(results) > 0:
            return format_data_response(results[0].data, query, results[0].row_count)
        return {"status": "success", "message": "No medications found", "data": [], "total_records": 0}
    except Exception as e:
        return {"status": "error", "error": str(e), "message": "Failed to retrieve medications"}


@mcp.tool()
async def get_patient_conditions(
    connection_id: str,
    patient_id: str
) -> Dict[str, Any]:
    """Retrieve patient medical conditions and diagnoses."""
    await ensure_services_initialized()
    try:
        query = f"""
        SELECT condition_id, condition_name, icd_code, onset_date, status
        FROM conditions 
        WHERE patient_id = '{patient_id}'
        ORDER BY onset_date DESC
        LIMIT 50
        """
        
        results = await db_ops_service.execute_query(connection_id=connection_id, query=query, params={})
        if results and len(results) > 0:
            return format_data_response(results[0].data, query, results[0].row_count)
        return {"status": "success", "message": "No conditions found", "data": [], "total_records": 0}
    except Exception as e:
        return {"status": "error", "error": str(e), "message": "Failed to retrieve conditions"}


@mcp.tool()
async def get_patient_lab_results(
    connection_id: str,
    patient_id: str
) -> Dict[str, Any]:
    """Retrieve patient laboratory test results."""
    await ensure_services_initialized()
    try:
        query = f"""
        SELECT lab_result_id, test_name, test_value, unit, reference_range, test_date
        FROM lab_results 
        WHERE patient_id = '{patient_id}'
        ORDER BY test_date DESC
        LIMIT 50
        """
        
        results = await db_ops_service.execute_query(connection_id=connection_id, query=query, params={})
        if results and len(results) > 0:
            return format_data_response(results[0].data, query, results[0].row_count)
        return {"status": "success", "message": "No lab results found", "data": [], "total_records": 0}
    except Exception as e:
        return {"status": "error", "error": str(e), "message": "Failed to retrieve lab results"}


@mcp.tool()
async def get_patient_procedures(
    connection_id: str,
    patient_id: str
) -> Dict[str, Any]:
    """Retrieve patient medical procedures history."""
    await ensure_services_initialized()
    try:
        query = f"""
        SELECT procedure_id, procedure_name, procedure_date, outcome
        FROM procedures 
        WHERE patient_id = '{patient_id}'
        ORDER BY procedure_date DESC
        LIMIT 50
        """
        
        results = await db_ops_service.execute_query(connection_id=connection_id, query=query, params={})
        if results and len(results) > 0:
            return format_data_response(results[0].data, query, results[0].row_count)
        return {"status": "success", "message": "No procedures found", "data": [], "total_records": 0}
    except Exception as e:
        return {"status": "error", "error": str(e), "message": "Failed to retrieve procedures"}


@mcp.tool()
async def get_patient_allergies(
    connection_id: str,
    patient_id: str
) -> Dict[str, Any]:
    """Retrieve patient allergy information."""
    await ensure_services_initialized()
    try:
        query = f"""
        SELECT allergy_id, allergen, severity, reaction, onset_date
        FROM allergies 
        WHERE patient_id = '{patient_id}'
        LIMIT 50
        """
        
        results = await db_ops_service.execute_query(connection_id=connection_id, query=query, params={})
        if results and len(results) > 0:
            return format_data_response(results[0].data, query, results[0].row_count)
        return {"status": "success", "message": "No allergies found", "data": [], "total_records": 0}
    except Exception as e:
        return {"status": "error", "error": str(e), "message": "Failed to retrieve allergies"}


@mcp.tool()
async def get_patient_appointments(
    connection_id: str,
    patient_id: str
) -> Dict[str, Any]:
    """Retrieve patient appointment schedule."""
    await ensure_services_initialized()
    try:
        query = f"""
        SELECT appointment_id, appointment_date, appointment_type, provider_name, status
        FROM appointments 
        WHERE patient_id = '{patient_id}'
        ORDER BY appointment_date DESC
        LIMIT 50
        """
        
        results = await db_ops_service.execute_query(connection_id=connection_id, query=query, params={})
        if results and len(results) > 0:
            return format_data_response(results[0].data, query, results[0].row_count)
        return {"status": "success", "message": "No appointments found", "data": [], "total_records": 0}
    except Exception as e:
        return {"status": "error", "error": str(e), "message": "Failed to retrieve appointments"}


@mcp.tool()
async def get_patient_followups(
    connection_id: str,
    patient_id: str
) -> Dict[str, Any]:
    """Retrieve patient follow-up appointments and care plans."""
    await ensure_services_initialized()
    try:
        query = f"""
        SELECT followup_id, followup_date, followup_type, notes
        FROM followups 
        WHERE patient_id = '{patient_id}'
        ORDER BY followup_date DESC
        LIMIT 50
        """
        
        results = await db_ops_service.execute_query(connection_id=connection_id, query=query, params={})
        if results and len(results) > 0:
            return format_data_response(results[0].data, query, results[0].row_count)
        return {"status": "success", "message": "No followups found", "data": [], "total_records": 0}
    except Exception as e:
        return {"status": "error", "error": str(e), "message": "Failed to retrieve followups"}


@mcp.tool()
async def get_patient_diet(
    connection_id: str,
    patient_id: str
) -> Dict[str, Any]:
    """Retrieve patient dietary information and restrictions."""
    await ensure_services_initialized()
    try:
        query = f"""
        SELECT diet_id, diet_type, restrictions, notes
        FROM diet_information 
        WHERE patient_id = '{patient_id}'
        LIMIT 50
        """
        
        results = await db_ops_service.execute_query(connection_id=connection_id, query=query, params={})
        if results and len(results) > 0:
            return format_data_response(results[0].data, query, results[0].row_count)
        return {"status": "success", "message": "No diet information found", "data": [], "total_records": 0}
    except Exception as e:
        return {"status": "error", "error": str(e), "message": "Failed to retrieve diet information"}


if __name__ == "__main__":
    # Run the MCP server - services will be initialized on first tool call
    logger.info("Starting MCP Healthcare Agent Server...")
    try:
        mcp.run()
    except Exception as e:
        logger.error(f"MCP server crashed: {e}", exc_info=True)
        raise
