from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from services.cerner import generate_cerner_diagnosis_summary, generate_cerner_medication_summary, generate_cerner_patient_summary, generate_cerner_lab_summary, generate_cerner_followup_summary, generate_procedure_summary, generate_allergy_summary, generate_upcoming_cappointment_summary, generate_nutrition_summary, get_diet, risk, generate_aftercare_summary, generate_vitals_summary
from schemas.schema import PatientSummary
router = APIRouter()

@router.get("/Patient-agent/{organization}/{patient_id}", response_model=PatientSummary, tags=["CERNER"])
async def generate_summary_patient(patient_id: str,organization: str):
    return await generate_cerner_patient_summary(patient_id,organization)

@router.get("/medications-agent/{organization}/{patient_id}",  tags=["CERNER"])
async def generate_summary_medication(patient_id: str,organization: str):
    return await generate_cerner_medication_summary(patient_id,organization)

@router.get("/conditions-agent/{organization}/{patient_id}", response_model=PatientSummary, tags=["CERNER"])
async def generate_summary_diagnosis(patient_id: str,organization: str):
    return await generate_cerner_diagnosis_summary(patient_id,organization)

@router.get("/follow-up-agent/{organization}/{patient_id}", response_model=PatientSummary, tags=["CERNER"])
async def generate_summary_followup(patient_id: str,organization: str):
    return await generate_cerner_followup_summary(patient_id,organization)

@router.get("/labresult-agent/{organization}/{patient_id}", response_model=PatientSummary, tags=["CERNER"])
async def generate_summary_lab(patient_id: str,organization: str):
    print(patient_id)
    return await generate_cerner_lab_summary(patient_id,organization)

@router.get("/Procedure-agent/{organization}/{patient_id}", response_model=PatientSummary, tags=["CERNER"])
async def generate_Procedure_summary(patient_id: str,organization: str):
    return await generate_procedure_summary(patient_id,organization)

@router.get("/Allergy-agent/{organization}/{patient_id}", response_model=PatientSummary, tags=["CERNER"])
async def generate_allergy(patient_id: str,organization: str):
    return await generate_allergy_summary(patient_id,organization)
@router.get("/upcoming-appointment/{organization}/{patient_id}", response_model=PatientSummary, tags=["CERNER"])
async def generate_agent_Response_followup(patient_id: str,organization: str):
    return await generate_upcoming_cappointment_summary(patient_id, organization)
@router.get("/nutrition/{organization}/{patient_id}", response_model=PatientSummary, tags=["CERNER"])
async def generate_agent_Response_nutrition(patient_id: str,organization: str):
    return await generate_nutrition_summary(patient_id, organization)
@router.get("/Diet/{organization}/{patient_id}", tags=["CERNER"])
async def get_diet_data(patient_id: str,organization: str):
    return await get_diet(patient_id, organization)
@router.get("/Risk/{organization}/{patient_id}", tags=["CERNER"])
async def riskpanel(patient_id: str,organization: str):
    return await risk(patient_id, organization)
@router.get("/aftercare/{organization}/{patient_id}", tags=["CERNER"])
async def aftercare(patient_id: str,organization: str):
    return await generate_aftercare_summary(patient_id, organization)
@router.get("/cerner-vitals-agent/{organization}/{patient_id}", tags=["CERNER"])
async def generate_vitals_summary_endpoint(patient_id: str, organization: str):
    return await generate_vitals_summary(patient_id, organization)
