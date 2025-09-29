from fastapi import HTTPException
import requests
from datetime import datetime, timezone

FHIR_BASE_URL = "https://fhir.epic.com/interconnect-fhir-oauth/api/FHIR/R4"

async def get_patient_info(client, headers, patient_id):
    resp = await client.get(f"{FHIR_BASE_URL}/Patient/{patient_id}", headers=headers)
    if resp.status_code != 200:
        raise HTTPException(status_code=400, detail="Failed to fetch patient info")
    return resp.json()


async def get_observations(client, headers, patient_id, category="vital-signs"):
    url = f"{FHIR_BASE_URL}/Observation?patient={patient_id}"
    if category:
        url += f"&category={category}"
    resp = await client.get(url, headers=headers)
    if resp.status_code != 200:
        raise HTTPException(status_code=400, detail="Failed to fetch observations")
    return resp.json().get("entry", [])


async def get_diagnostics(client, headers, patient_id):
    resp = await client.get(
        f"{FHIR_BASE_URL}/DiagnosticReport?patient={patient_id}&_count=50",
        headers=headers
    )
    if resp.status_code != 200:
        return []
    return resp.json().get("entry", [])

async def get_medications(client, headers, patient_id):
    url = f"https://fhir.epic.com/interconnect-fhir-oauth/api/FHIR/R4/MedicationRequest?patient={patient_id}"
    response = await client.get(url, headers=headers)
    
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail="Failed to fetch medications")
    
    return response.json().get("entry", [])

async def get_diagnostic_reports(client, headers, patient_id):
    url = f"https://fhir.epic.com/interconnect-fhir-oauth/api/FHIR/R4/DiagnosticReport?patient={patient_id}"
    response = await client.get(url, headers=headers)
    
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail="Failed to fetch diagnostic reports")
    
    return response.json().get("entry", [])


FHIR_BASE_URL_APP = "https://fhir.epic.com/interconnect-fhir-oauth/api/FHIR/R4/Appointment"

async def get_appointments(client, headers, patient_id: str) -> dict:
    current_date = datetime.now(timezone.utc).isoformat()

    before_url = (
        f"{FHIR_BASE_URL_APP}?patient={patient_id}&date=lt{current_date}"
        f"&_sort=-date&_count=3"
    )
    after_url = (
        f"{FHIR_BASE_URL_APP}?patient={patient_id}&date=gt{current_date}"
        f"&_sort=date&_count=1"
    )
    goal_url=f"https://fhir.epic.com/interconnect-fhir-oauth/api/FHIR/R4/Goal?patient=Patient/{patient_id}"
    goal_resp = await client.get(goal_url, headers=headers)
    before_resp = await client.get(before_url, headers=headers)
    after_resp = await client.get(after_url, headers=headers)
    if before_resp.status_code != 200 or after_resp.status_code != 200 or goal_resp.status_code != 200:
        raise HTTPException(status_code=500, detail="Failed to fetch appointments")

    before_data = before_resp.json().get("entry", [])
    after_data = after_resp.json().get("entry", [])
    goal_data = goal_resp.json().get("entry", [])

    before_appointments = [entry.get("resource", {}) for entry in before_data]
    after_appointment = after_data[0].get("resource", {}) if after_data else {
    }
    goal = goal_data[0].get("resource", {}) if goal_data else {}

    return {
        "before_appointments": before_appointments, 
        "after_appointment": after_appointment,
        "goal": goal     
    }
async def get_upcoming_appointments(client, headers, patient_id: str) -> dict:
    current_date = datetime.now(timezone.utc).isoformat()
    current_date='2025-05-01T07:56:05.486238+00:00'
    after_url = (
        f"{FHIR_BASE_URL_APP}?patient={patient_id}&date=gt{current_date}"
        f"&_sort=date"
    )
    after_resp = await client.get(after_url, headers=headers)
    after_data = after_resp.json().get("entry", [])
    after_appointment = after_data[0].get("resource", {}) if after_data else {
    }
    print(after_appointment)
    return {
        # "before_appointments": before_appointments, 
        "after_appointment": after_appointment,
        # "goal": goal     
    }

    
async def get_current_conditions(client, headers, patient_id: str):
    url = f"https://fhir.epic.com/interconnect-fhir-oauth/api/FHIR/R4/Condition?patient={patient_id}&clinical-status=active"

    response = await client.get(url, headers=headers)

    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail="Failed to fetch conditions")

    conditions = response.json().get("entry", [])
    
    return [entry.get("resource", {}) for entry in conditions]

async def get_lab_results(client, headers, patient_id: str):
    diagnostic_report_url = f"https://fhir.epic.com/interconnect-fhir-oauth/api/FHIR/R4/DiagnosticReport?patient={patient_id}&category=laboratory"
    diagnostic_report_response = await client.get(diagnostic_report_url, headers=headers)
    
    if diagnostic_report_response.status_code != 200:
        raise HTTPException(status_code=diagnostic_report_response.status_code, detail="Failed to fetch diagnostic reports")
    
    diagnostic_reports = diagnostic_report_response.json().get("entry", [])
    
    observation_url = f"https://fhir.epic.com/interconnect-fhir-oauth/api/FHIR/R4/Observation?patient={patient_id}&category=laboratory"
    observation_response = await client.get(observation_url, headers=headers)
    
    if observation_response.status_code != 200:
        raise HTTPException(status_code=observation_response.status_code, detail="Failed to fetch observations")
    
    observations = observation_response.json().get("entry", [])

    return {
        "diagnostic_reports": [entry.get("resource", {}) for entry in diagnostic_reports],
        "observations": [entry.get("resource", {}) for entry in observations]
    }

async def get_procedure(client, headers, patient_id: str):
    url = f"https://fhir.epic.com/interconnect-fhir-oauth/api/FHIR/R4/Procedure?patient={patient_id}"

    response = await client.get(url, headers=headers)

    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail="Failed to fetch conditions")

    conditions = response.json().get("entry", [])
    
    return [entry.get("resource", {}) for entry in conditions]


async def get_allergy(client, headers, patient_id: str):
    allergy_url = f"https://fhir.epic.com/interconnect-fhir-oauth/api/FHIR/R4/AllergyIntolerance?patient={patient_id}"

    response = await client.get(allergy_url, headers=headers)

    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail="Failed to fetch conditions")

    allergy = response.json().get("entry", [])
    immun_url = f"https://fhir.epic.com/interconnect-fhir-oauth/api/FHIR/R4/Immunization?patient={patient_id}"

    response = await client.get(immun_url, headers=headers)

    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail="Failed to fetch conditions")

    immunization = response.json().get("entry", [])
    
    return {"allergy":[entry.get("resource", {}) for entry in allergy], "immunization":[entry.get("resource", {}) for entry in immunization]}

async def get_nutrition(client, headers, patient_id: str):
    url = f"https://fhir.epic.com/interconnect-fhir-oauth/api/FHIR/R4/NutritionOrder?patient={patient_id}"

    response = await client.get(url, headers=headers)

    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail="Failed to fetch conditions")

    nutrition = response.json().get("entry", [])
    
    return [entry.get("resource", {}) for entry in nutrition]