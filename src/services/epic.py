import httpx
from fastapi import HTTPException
import json
import logging
from connector_fhir.epic import refresh_access_token
from utils.epic import get_lab_results, get_patient_info, get_current_conditions, get_appointments,get_upcoming_appointments, get_observations, get_medications, get_procedure, get_allergy, get_nutrition
from prompt.prompt import  medication_prompt, build_diagnosis_prompt, lab_prompt, procedure_prompt_epic, observation_patient_prompt, observation_vitals_prompt, unify_prompt, goal_prompt, before_appointment_prompt, after_appointment_prompt, allergy_prompt, immunization_prompt, merge_patient_prompt, unify_obs_prompt, cerner_upcoming_prompt, nutrition_prompt, diet_prompt, risk_prompt, aftercare_prompt
from utils.formatter_fhir import extract_patient_name, clean_fhir_data, preprocess_observations, extract_epic_condition, extract_procedure, extract_allergy, extract_observations_epic, extract_observations, extract_epic_medications
from utils.aws import call_bedrock_summary
from utils.chunking import chunk


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def generate_patient_summary(patient_id: str, organization: str):
    try:
        access_token = refresh_access_token(organization)["access_token"]
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/fhir+json"
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            patient_info = await get_patient_info(client, headers, patient_id)
            observations = await get_observations(client, headers, patient_id)
            # obs_str = json.dumps(observations)
            # result = clean_fhir_data(obs_str)
            result = preprocess_observations(observations)
            # print(result)
            print(result, "🎉🎉🎉🎉🎉🎉🎉🎉🎉")
            print("vitals",result["vital_signs"])
        patient_name = extract_patient_name(patient_info)
        patient_prompt = observation_patient_prompt(patient_name, patient_info)
        summary=""
        patient_summary_resp=call_bedrock_summary(patient_prompt)
        patient_summary = ""
        async for part in patient_summary_resp.body_iterator:
            patient_summary += part

        summary += patient_summary
        vitals_summary = await chunk(result["vital_signs"], observation_vitals_prompt)
        summary += vitals_summary
        print(summary)
        prompt=merge_patient_prompt(summary)
        # prompt = observation_prompt(patient_name, patient_info, result)
        return call_bedrock_summary(prompt)
    
    except Exception as e:
        logger.error(f"Summary generation failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Summary generation failed")
    
    
async def generate_medication_summary(patient_id: str, organization: str):
    try:
        access_token = refresh_access_token(organization)["access_token"]
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/fhir+json"
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            medications = await get_medications(client, headers, patient_id)
            medications_str = json.dumps(medications)
            # data = clean_fhir_data(medications_str)
            summary=await chunk(medications_str, medication_prompt)
        print(summary)
        prompt = unify_prompt(summary)
        # prompt=medication_prompt(data)
        return call_bedrock_summary(prompt)

    except Exception as e:
        logger.error(f"Medication summary generation failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to generate medication summary")
    
async def generate_condition_summary(patient_id: str, organization: str):
    try:
        access_token = refresh_access_token(organization)["access_token"]
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/fhir+json"
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            conditions = await get_current_conditions(client, headers, patient_id)
            folup_str = json.dumps(conditions)
            cleaned=clean_fhir_data(folup_str)
            # cleaned=preprocess_condition(conditions)
            print("condition",conditions)
            summary=await chunk(cleaned, build_diagnosis_prompt)
        prompt = unify_prompt(summary)
        return call_bedrock_summary(prompt)

    except Exception as e:
        logger.error(f"Medication summary generation failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to generate medication summary")


async def generate_Followup_summary(patient_id: str, organization:str):
    try:
        access_token = refresh_access_token(organization)["access_token"]
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/fhir+json"
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            Followup = await get_appointments(client, headers, patient_id)
            # cleaned=clean_fhir_data(Followup)
            bef=Followup["before_appointments"]
            aft=[Followup["after_appointment"]]
            Goal=[Followup["goal"]]
            # print(Goal)
            # print(bef)
            summary=""
            before_summary = await chunk(bef, before_appointment_prompt)
            summary += before_summary
            after_summary = await chunk(aft, after_appointment_prompt)
            summary += after_summary    
            goal_summary = await chunk(Goal, goal_prompt)
            summary += goal_summary
            print("goal",goal_summary)
            print(summary)
        prompt = unify_prompt(summary)
        return call_bedrock_summary(prompt)

    except Exception as e:
        logger.error(f"Medication summary generation failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to generate medication summary")

async def generate_lab_summary(patient_id: str, organization:str):
    try:
        access_token = refresh_access_token(organization)["access_token"]
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/fhir+json"
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            lab = await get_lab_results(client, headers, patient_id)
            lab_str = json.dumps(lab)
            data=clean_fhir_data(lab_str)
            diagnostic=data["diagnostic_reports"]
            observation=data["observations"]
            summary=""
            diagnostic_summary = await chunk(diagnostic, lab_prompt)
            summary += diagnostic_summary
            observation_summary = await chunk(observation,  lab_prompt)
            summary += observation_summary
            print(summary) 
        prompt = unify_obs_prompt(summary)
        return call_bedrock_summary(prompt)

    except Exception as e:
        logger.error(f"Medication summary generation failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to generate medication summary")

async def generate_procedure_summary(patient_id: str, organization: str):
    try:
        access_token = refresh_access_token(organization)["access_token"]
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/fhir+json"
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            lab = await get_procedure(client, headers, patient_id)
            lab_str = json.dumps(lab)
            data=clean_fhir_data(lab_str)
            summary=await chunk(data, procedure_prompt_epic)
            print(summary)
        prompt = unify_prompt(summary)
        return call_bedrock_summary(prompt)

    except Exception as e:
        logger.error(f"Medication summary generation failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to generate medication summary")
    
async def generate_allergy_summary(patient_id: str, organization: str):
    try:
        access_token = refresh_access_token(organization)["access_token"]
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/fhir+json"
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            allergy = await get_allergy(client, headers, patient_id)
            lab_str = json.dumps(allergy)
            data=clean_fhir_data(lab_str)
            print(data)
            allergy=data['allergy']
            immunization=data['immunization']
            summary=""
            allergy_summary = await chunk(allergy, allergy_prompt)
            summary += allergy_summary
            immunization_summary = await chunk(immunization,  immunization_prompt)
            summary += immunization_summary
            print(summary) 
        # prompt = allergy_prompt_epic(data)
        prompt = unify_prompt(summary)
        return call_bedrock_summary(prompt)

    except Exception as e:
        logger.error(f"Medication summary generation failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to generate medication summary")
    

async def generate_upcoming_appointment_summary(patient_id: str, organization:str):
    print("hello")
    try:
        print("org",organization)
        access_token = refresh_access_token(organization)["access_token"]
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/fhir+json"
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            Followup = await get_upcoming_appointments(client, headers, patient_id)
            # cleaned=clean_fhir_data(Followup)
            # bef=Followup["before_appointments"]
            aft=[Followup["after_appointment"]]
            # Goal=[Followup["goal"]]
            # print(Goal)
            # print(bef)
            # summary=""
            # before_summary = await chunk(bef, before_appointment_prompt)
            # summary += before_summary
            # after_summary = await chunk(aft, after_appointment_prompt)
            # summary += after_summary    
            # goal_summary = await chunk(Goal, goal_prompt)
            # summary += goal_summary
            # print("goal",goal_summary)
            # print(summary)
        prompt = cerner_upcoming_prompt(aft)
        print(prompt)
        return call_bedrock_summary(prompt)

    except Exception as e:
        logger.error(f"Medication summary generation failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to generate medication summary")

async def generate_nutrition_summary(patient_id: str, organization: str):
    try:
        access_token = refresh_access_token(organization)["access_token"]
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/fhir+json"
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            nutrition = await get_nutrition(client, headers, patient_id)
        prompt = nutrition_prompt(nutrition)
        return call_bedrock_summary(prompt)

    except Exception as e:
        logger.error(f"Medication summary generation failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to generate medication summary")
    
async def get_diet(patient_id: str,organization: str):
    try:
        access_token = refresh_access_token(organization)["access_token"]
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/fhir+json"
        }

        async with httpx.AsyncClient(timeout=50.0) as client:
            patient = await get_patient_info(client, headers, patient_id)
            patient_name = extract_patient_name(patient)
            vitals = await get_observations(client, headers, patient_id)
            processed_vitals=extract_observations(vitals)
            # medication= await get_cerner_medication(client, headers, patient_id)
            # print(medication)
            # preprocessed_medication=preprocess_medications(medication)
            condition=await get_current_conditions(client, headers, patient_id)
            preprocessed_condition=extract_epic_condition(condition)
            # print("condition",preprocessed_condition)
            observation=await get_lab_results(client, headers, patient_id)
            obs=observation['observations']
            preprocessed_obs=extract_observations_epic(obs)
            procedure=await get_procedure(client, headers, patient_id)
            preprocessed_procedure=extract_procedure(procedure)
            allergy_immun=await get_allergy(client, headers, patient_id)
            allergy=allergy_immun['allergy']
            print("allergyy",allergy)
            # immunization=allergy_immun['immunization']
            preprocessed_allergy=extract_allergy(allergy)
            print("allergy",preprocessed_allergy)
            # preprocessed_immunization=process_immunization(immunization)
            prompt = diet_prompt(patient_name, preprocessed_condition, preprocessed_procedure, preprocessed_allergy,preprocessed_obs,processed_vitals)
            return call_bedrock_summary(prompt)
            
    except Exception as e:
        logger.error(f"Medication summary generation failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to generate medication summary")

async def risk(patient_id: str,organization: str):
    try:
        access_token = refresh_access_token(organization)["access_token"]
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/fhir+json"
        }

        async with httpx.AsyncClient(timeout=50.0) as client:
            patient = await get_patient_info(client, headers, patient_id)
            patient_name = extract_patient_name(patient)
            vitals = await get_observations(client, headers, patient_id)
            processed_vitals=extract_observations(vitals)
            medication= await get_medications(client, headers, patient_id)
            # print(medication)
            preprocessed_medication=extract_epic_medications(medication)
            condition=await get_current_conditions(client, headers, patient_id)
            preprocessed_condition=extract_epic_condition(condition)
            # print("condition",preprocessed_condition)
            observation=await get_lab_results(client, headers, patient_id)
            obs=observation['observations']
            preprocessed_obs=extract_observations_epic(obs)
            # procedure=await get_procedure(client, headers, patient_id)
            # preprocessed_procedure=extract_procedure(procedure)
            # allergy_immun=await get_allergy(client, headers, patient_id)
            # allergy=allergy_immun['allergy']
            # print("allergyy",allergy)
            # # immunization=allergy_immun['immunization']
            # preprocessed_allergy=extract_allergy(allergy)
            # print("allergy",preprocessed_allergy)
            # preprocessed_immunization=process_immunization(immunization)
            prompt = risk_prompt(patient_name, preprocessed_condition, preprocessed_medication, preprocessed_obs,processed_vitals)
            return call_bedrock_summary(prompt)
            
    except Exception as e:
        logger.error(f"Medication summary generation failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to generate medication summary")
    
async def generate_aftercare_summary(patient_id: str, organization: str):
    try:
        access_token = refresh_access_token(organization)["access_token"]
        print("Access Token:", access_token)
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/fhir+json"
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            medication= await get_medications(client, headers, patient_id)
            # print(medication)
            preprocessed_medication=extract_epic_medications(medication)
            procedure=await get_procedure(client, headers, patient_id)
            preprocessed_procedure=extract_procedure(procedure)
            # condition=await get_cerner_condition(client, headers, patient_id)
            # preprocessed_condition=extract_condition(condition)
        prompt = aftercare_prompt(preprocessed_medication, preprocessed_procedure)
        return call_bedrock_summary(prompt)

    except Exception as e:
        logger.error(f"Medication summary generation failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to generate medication summary")