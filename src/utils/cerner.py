from fastapi import APIRouter, HTTPException
from datetime import datetime, timezone

FHIR_BASE_URL = "https://fhir-open.cerner.com/r4/ec2458f2-1e24-41c8-b71b-0e701af7583d"

async def get_cerner_patient_info(client, headers, patient_id):
    resp = await client.get(f"{FHIR_BASE_URL}/Patient/{patient_id}", headers=headers)
    if resp.status_code != 200:
        raise HTTPException(status_code=400, detail="Failed to fetch patient info")
    return resp.json()


async def get_cerner_observations(client, headers, patient_id):
    resp = await client.get(
        f"{FHIR_BASE_URL}/Observation?patient={patient_id}&category=vital-signs",
        headers=headers
    )
    if resp.status_code != 200:
        raise HTTPException(status_code=400, detail="Failed to fetch observations")
    return resp.json().get("entry", [])

async def get_cerner_observations_lab(client, headers, patient_id):
    resp = await client.get(
        f"{FHIR_BASE_URL}/Observation?patient={patient_id}&category=laboratory&_count=100",
        headers=headers
    )
    if resp.status_code != 200:
        raise HTTPException(status_code=400, detail="Failed to fetch observations")
    return resp.json().get("entry", [])

async def get_cerner_diagnostic_lab(client, headers, patient_id):
    resp = await client.get(
        f"{FHIR_BASE_URL}/DiagnosticReport?patient={patient_id}",
        headers=headers
    )
    if resp.status_code != 200:
        raise HTTPException(status_code=400, detail="Failed to fetch observations")
    return resp.json().get("entry", [])

async def get_cerner_medication(client, headers, patient_id):
    resp = await client.get(
        f"{FHIR_BASE_URL}/MedicationRequest?patient={patient_id}",
        headers=headers
    )
    if resp.status_code != 200:
        raise HTTPException(status_code=400, detail="Failed to fetch observations")
    return resp.json().get("entry", [])

async def get_cerner_condition(client, headers, patient_id):
    resp = await client.get(
        f"{FHIR_BASE_URL}/Condition?patient={patient_id}",
        headers=headers,
        timeout=100
    )
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

async def get_appointments(client, headers, patient_id: str) -> dict:
    current_date = datetime.now(timezone.utc).isoformat()
    after_url = (
        f"{FHIR_BASE_URL}/Appointment?patient={patient_id}&date=ge2025-05-01T13:45:00Z"
        f"&_sort=date"
    )

    after_resp = await client.get(after_url, headers=headers)
    after_data = after_resp.json().get("entry", [])

    after_appointment = after_data[0].get("resource", {}) if after_data else {}

    return { 
        "after_appointment": after_appointment      
    }

async def get_procedure(client, headers, patient_id: str):
    url = f"{FHIR_BASE_URL}/Procedure?patient={patient_id}"

    response = await client.get(url, headers=headers)

    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail="Failed to fetch conditions")

    procedure = response.json().get("entry", [])
    
    return [entry.get("resource", {}) for entry in procedure]


async def get_allergy(client, headers, patient_id: str):
    allergy_url = f"{FHIR_BASE_URL}/AllergyIntolerance?patient={patient_id}"
    response = await client.get(allergy_url, headers=headers)

    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail="Failed to fetch conditions")

    allergy = response.json().get("entry", [])
    immun_url = f"{FHIR_BASE_URL}/Immunization?patient={patient_id}"

    response = await client.get(immun_url, headers=headers)

    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail="Failed to fetch conditions")

    immunization = response.json().get("entry", [])
    
    return {"allergy":[entry.get("resource", {}) for entry in allergy], "immunization":[entry.get("resource", {}) for entry in immunization]}

async def get_nutrition(client, headers, patient_id):
    resp = await client.get(
        f"{FHIR_BASE_URL}/NutritionOrder?patient={patient_id}&_count=50",
        headers=headers
    )
    if resp.status_code != 200:
        return []
    return resp.json().get("entry", [])