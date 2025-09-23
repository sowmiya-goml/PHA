
import httpx
from fastapi import HTTPException
import json
from datetime import datetime, timedelta
import logging
from connector_fhir.cerner import refresh_cerner_access_token
from utils.cerner import get_cerner_patient_info, get_cerner_observations, get_cerner_medication, get_cerner_condition, get_cerner_observations_lab, get_appointments, get_cerner_diagnostic_lab, get_procedure, get_allergy,get_nutrition
from prompt.prompt import  medication_prompt, build_diagnosis_prompt, lab_prompt, cerner_followup_prompt, procedure_prompt_epic, unify_prompt, observation_vitals_prompt, observation_patient_prompt, allergy_prompt, immunization_prompt, merge_patient_prompt, unify_obs_prompt, unify_procedure_prompt, cerner_upcoming_prompt,nutrition_prompt, diet_prompt, risk_prompt, aftercare_prompt
from utils.formatter_fhir import extract_patient_name, preprocess_observations, preprocess_condition, clean_fhir_data, preprocess_procedure, process_allergy, process_immunization, move_citations_to_end, preprocess_medications, extract_condition, extract_procedure, extract_allergy, extract_observations, extract_hours, build_reminder_schedule, parse_markdown_table
from utils.aws import call_bedrock_summary
from utils.chunking import chunk

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def generate_cerner_patient_summary(patient_id: str,organization: str):
    try:
        access_token = refresh_cerner_access_token(organization)["access_token"]
        print("Access Token:", access_token)
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/fhir+json"
        }
        async with httpx.AsyncClient(timeout=30.0) as client:
            patient_info = await get_cerner_patient_info(client, headers, patient_id)
            observations = await get_cerner_observations(client, headers, patient_id)
            result = preprocess_observations(observations)
            print(result, "🎉🎉🎉🎉🎉🎉🎉🎉🎉")
            
        patient_name = extract_patient_name(patient_info)
        patient_prompt = observation_patient_prompt(patient_name, patient_info)
        summary=""
        patient_summary_resp=call_bedrock_summary(patient_prompt)
        patient_summary = ""
        async for part in patient_summary_resp.body_iterator:
            patient_summary += part

        summary += patient_summary+ "\n"
        vitals_summary = await chunk(result["vital_signs"], observation_vitals_prompt)
        summary += vitals_summary
        print(summary)
        prompt=merge_patient_prompt(summary)
        return call_bedrock_summary(prompt)
    
    except Exception as e:
        logger.error(f"Summary generation failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Summary generation failed")

async def generate_cerner_medication_summary(patient_id: str, organization: str):
    try:
        access_token = refresh_cerner_access_token(organization)["access_token"]
        print("Access Token:", access_token)
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/fhir+json"
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            medications = await get_cerner_medication(client, headers, patient_id)
            medications_str = json.dumps(medications)
            summary=await chunk(medications_str, medication_prompt)
            print(summary)
        prompt = unify_prompt(summary)
        return call_bedrock_summary(prompt)
 
    except Exception as e:
        logger.error(f"Medication summary generation failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to generate medication summary")
    

async def generate_cerner_diagnosis_summary(patient_id: str, organization: str):
    try:
        access_token = refresh_cerner_access_token(organization)["access_token"]
        print("Access Token:", access_token)
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/fhir+json"
        }

        async with httpx.AsyncClient(timeout=50.0) as client:
            conditions = await get_cerner_condition(client, headers, patient_id)
            data = preprocess_condition(conditions)
            summary=await chunk(data, build_diagnosis_prompt)
            print(summary)
        prompt = unify_prompt(summary)
        return call_bedrock_summary(prompt)

    except Exception as e:
        logger.error(f"Medication summary generation failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to generate medication summary")
    
    
async def generate_cerner_followup_summary(patient_id: str,organization: str):
    try:
        access_token = refresh_cerner_access_token(organization)["access_token"]
        print("Access Token:", access_token)
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/fhir+json"
        }

        async with httpx.AsyncClient(timeout=50.0) as client:
            Followup = await get_appointments(client, headers, patient_id)
            aft=Followup["after_appointment"]
        prompt = cerner_followup_prompt(aft)
        return call_bedrock_summary(prompt)
            
    except Exception as e:
        logger.error(f"Medication summary generation failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to generate medication summary")
    
    
async def generate_cerner_lab_summary(patient_id: str, organization: str):
    try:
        access_token = refresh_cerner_access_token(organization)["access_token"]
        print("Access Token:", access_token)    
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/fhir+json"
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            labreport = await get_cerner_observations_lab(client, headers, patient_id)
            data = preprocess_observations(labreport)
            result=data['lab_results']
            summary=await chunk(result, lab_prompt)
            print(summary)
        prompt = unify_obs_prompt(summary)
        return call_bedrock_summary(prompt)

    except Exception as e:
        logger.error(f"Medication summary generation failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to generate medication summary")
    
async def generate_procedure_summary(patient_id: str, organization: str):
    try:
        access_token = refresh_cerner_access_token(organization)["access_token"]
        print("Access Token:", access_token)
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/fhir+json"
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            procedure = await get_procedure(client, headers, patient_id)
            data=preprocess_procedure(procedure)
            print(len(data))
            summary=await chunk(data, procedure_prompt_epic)
        reorganized_text = move_citations_to_end(summary)
        print(reorganized_text)
        prompt = unify_procedure_prompt(summary)
        return call_bedrock_summary(prompt)

    except Exception as e:
        logger.error(f"Medication summary generation failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to generate medication summary")
    
async def generate_allergy_summary(patient_id: str, organization: str):
    try:
        access_token = refresh_cerner_access_token(organization)["access_token"]
        print("Access Token:", access_token)
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/fhir+json"
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            data = await get_allergy(client, headers, patient_id)
            allergy=data['allergy']
            immunization=data['immunization']
            cleaned_allergy=process_allergy(allergy)
            cleaned_immunization=process_immunization(immunization)
            summary=""
            allergy_summary = await chunk(cleaned_allergy, allergy_prompt)
            summary += allergy_summary
            immunization_summary = await chunk(cleaned_immunization,  immunization_prompt)
            summary += immunization_summary
            print(summary) 
        prompt = unify_prompt(summary)
        return call_bedrock_summary(prompt)

    except Exception as e:
        logger.error(f"Medication summary generation failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to generate medication summary")

async def generate_upcoming_cappointment_summary(patient_id: str,organization: str):
    try:
        access_token = refresh_cerner_access_token(organization)["access_token"]
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/fhir+json"
        }

        async with httpx.AsyncClient(timeout=50.0) as client:
            Followup = await get_appointments(client, headers, patient_id)
            aft=Followup["after_appointment"]
        prompt = cerner_upcoming_prompt(aft)
        return call_bedrock_summary(prompt)
            
    except Exception as e:
        logger.error(f"Medication summary generation failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to generate medication summary")
    
async def generate_nutrition_summary(patient_id: str,organization: str):
    try:
        access_token = refresh_cerner_access_token(organization)["access_token"]
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/fhir+json"
        }

        async with httpx.AsyncClient(timeout=50.0) as client:
            nutrition = await get_nutrition(client, headers, patient_id)
        prompt = nutrition_prompt(nutrition)
        return call_bedrock_summary(prompt)
            
    except Exception as e:
        logger.error(f"Medication summary generation failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to generate medication summary")
    
async def get_diet(patient_id: str,organization: str):
    try:
        access_token = refresh_cerner_access_token(organization)["access_token"]
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/fhir+json"
        }

        async with httpx.AsyncClient(timeout=50.0) as client:
            patient = await get_cerner_patient_info(client, headers, patient_id)
            patient_name = extract_patient_name(patient)
            vitals = await get_cerner_observations(client, headers, patient_id)
            processed_vitals=extract_observations(vitals)
            condition=await get_cerner_condition(client, headers, patient_id)
            preprocessed_condition=extract_condition(condition)
            observation=await get_cerner_observations_lab(client, headers, patient_id)
            preprocessed_obs=extract_observations(observation)
            procedure=await get_procedure(client, headers, patient_id)
            preprocessed_procedure=extract_procedure(procedure)
            allergy_immun=await get_allergy(client, headers, patient_id)
            allergy=allergy_immun['allergy']
            preprocessed_allergy=extract_allergy(allergy)
            prompt = diet_prompt(patient_name, preprocessed_condition, preprocessed_procedure, preprocessed_allergy,preprocessed_obs,processed_vitals)
            return call_bedrock_summary(prompt)
            
    except Exception as e:
        logger.error(f"Medication summary generation failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to generate medication summary")

async def risk(patient_id: str,organization: str):
    try:
        access_token = refresh_cerner_access_token(organization)["access_token"]
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/fhir+json"
        }

        async with httpx.AsyncClient(timeout=50.0) as client:
            patient = await get_cerner_patient_info(client, headers, patient_id)
            patient_name = extract_patient_name(patient)
            vitals = await get_cerner_observations(client, headers, patient_id)
            processed_vitals=extract_observations(vitals)
            medication= await get_cerner_medication(client, headers, patient_id)
            preprocessed_medication=preprocess_medications(medication)
            condition=await get_cerner_condition(client, headers, patient_id)
            preprocessed_condition=extract_condition(condition)
            observation=await get_cerner_observations_lab(client, headers, patient_id)
            preprocessed_obs=extract_observations(observation)
            prompt = risk_prompt(patient_name, preprocessed_condition,preprocessed_medication,preprocessed_obs,processed_vitals)
            return call_bedrock_summary(prompt)
            
    except Exception as e:
        logger.error(f"Medication summary generation failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to generate medication summary")
    
async def generate_aftercare_summary(patient_id: str, organization: str):
    try:
        access_token = refresh_cerner_access_token(organization)["access_token"]
        print("Access Token:", access_token)
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/fhir+json"
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            medication= await get_cerner_medication(client, headers, patient_id)
            preprocessed_medication=preprocess_medications(medication)
            procedure=await get_procedure(client, headers, patient_id)
            preprocessed_procedure=extract_procedure(procedure)
        prompt = aftercare_prompt(preprocessed_medication, preprocessed_procedure)
        return call_bedrock_summary(prompt)

    except Exception as e:
        logger.error(f"Medication summary generation failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to generate medication summary")

