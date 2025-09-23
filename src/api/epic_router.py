from fastapi import APIRouter
from schemas.schema import PatientSummary, PatientRequest
from services.epic import generate_patient_summary, generate_Followup_summary, generate_medication_summary, generate_condition_summary, generate_lab_summary, generate_procedure_summary, generate_allergy_summary, generate_upcoming_appointment_summary, generate_nutrition_summary, get_diet, risk, generate_aftercare_summary
router = APIRouter()
@router.get("/patient-agent/{organization}/{patient_id}", response_model=PatientSummary, tags=["EPIC"])
async def generate_patient_observ(patient_id: str,organization: str):
    print(patient_id,organization)
    return await generate_patient_summary(patient_id, organization)

@router.get("/medication-agent/{organization}/{patient_id}", response_model=PatientSummary, tags=["EPIC"])
async def generate_medication(patient_id: str,organization: str):
    return await generate_medication_summary(patient_id, organization)

@router.get("/followup-agent/{organization}/{patient_id}", response_model=PatientSummary, tags=["EPIC"])
async def generate_agent_Response_followup(patient_id: str,organization: str):
    return await generate_Followup_summary(patient_id, organization)

@router.get("/condition-agent/{organization}/{patient_id}", response_model=PatientSummary, tags=["EPIC"])
async def generate_condition(patient_id: str,organization: str):
    return await generate_condition_summary(patient_id, organization)

@router.get("/lab-result-agent/{organization}/{patient_id}", response_model=PatientSummary, tags=["EPIC"])
async def generate_lab(patient_id: str,organization: str):
    return await generate_lab_summary(patient_id, organization)

@router.get("/procedure-agent/{organization}/{patient_id}", response_model=PatientSummary, tags=["EPIC"])
async def generate_procedure(patient_id: str,organization: str):
    return await generate_procedure_summary(patient_id, organization)

@router.get("/allergy-agent/{organization}/{patient_id}", response_model=PatientSummary, tags=["EPIC"])
async def generate_allergy(patient_id: str,organization: str):
    return await generate_allergy_summary(patient_id, organization)

@router.get("/upcoming-epic-appointment/{organization}/{patient_id}", response_model=PatientSummary, tags=["EPIC"])
async def generate_agent_Response_upcoming(patient_id: str,organization: str):
    return await generate_upcoming_appointment_summary(patient_id, organization)

@router.get("/epic_nutrition/{organization}/{patient_id}", response_model=PatientSummary, tags=["EPIC"])
async def generate_agent_Response_nutrition(patient_id: str,organization: str):
    return await generate_nutrition_summary(patient_id, organization)

@router.get("/Epic-Diet/{organization}/{patient_id}", tags=["EPIC"])
async def get_diet_data(patient_id: str,organization: str):
    return await get_diet(patient_id, organization)


@router.get("/Epic-Risk/{organization}/{patient_id}", tags=["EPIC"])
async def riskpanel(patient_id: str,organization: str):
    return await risk(patient_id, organization)

@router.get("/Epic-aftercare/{organization}/{patient_id}", tags=["EPIC"])
async def aftercare(patient_id: str,organization: str):
    return await generate_aftercare_summary(patient_id, organization)