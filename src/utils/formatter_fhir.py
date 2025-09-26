import re
import json
from typing import List, Dict
from datetime import datetime, timedelta

def extract_patient_name(patient_data):
    name_data = patient_data.get("name", [{}])[0]
    return name_data.get("given", [""])[0] or "Patient"


def extract_value_quantity(resource):
    value_quantity = resource.get("valueQuantity")
    if value_quantity:
        return value_quantity

    components = resource.get("component", [])
    if components:
        systolic = None
        diastolic = None
        for comp in components:
            code_text = comp.get("code", {}).get("text", "").lower()
            val = comp.get("valueQuantity")
            if not val:
                continue

            if "systolic" in code_text:
                systolic = val
            elif "diastolic" in code_text:
                diastolic = val

        return {
            "systolic": systolic,
            "diastolic": diastolic
        }

    return None
def preprocess_observations(observations):
    vitals = []
    labs = []

    for item in observations:
        resource = item.get('resource', {})
        value_quantity = extract_value_quantity(resource)
        performer = resource.get('performer', [{}])[0]
        category_list = resource.get('category', [])
        categories = [cat.get('coding', [{}])[0].get('code') for cat in category_list]
        obs_data = {
            "id": f"Observation/{resource.get('id')}",
            "datetime": resource.get("effectiveDateTime"),
            "patient": resource.get("subject", {}).get("display"),
            "encounter": resource.get("encounter", {}).get("display"),
            "performed_by": performer.get("display"),
            "observation_type": resource.get("code", {}).get("text"),
            "value": None,
            "unit": None
        }
        if isinstance(value_quantity, dict) and "systolic" in value_quantity:
            obs_data["value"] = {
                "systolic": value_quantity["systolic"].get("value"),
                "diastolic": value_quantity["diastolic"].get("value")
            }
            obs_data["unit"] = value_quantity["systolic"].get("unit")  
        elif value_quantity:
            obs_data["value"] = value_quantity.get("value")
            obs_data["unit"] = value_quantity.get("unit")

        if "vital-signs" in categories:
            vitals.append(obs_data)
        elif "laboratory" in categories:
            labs.append(obs_data)

    return {
        "vital_signs": vitals,
        "lab_results": labs
    }
def extract_observations(observations):
    vitals = []
    labs = []

    for item in observations:
        resource = item.get('resource', {})
        value_quantity = extract_value_quantity(resource)
        performer = resource.get('performer', [{}])[0]
        category_list = resource.get('category', [])
        categories = [cat.get('coding', [{}])[0].get('code') for cat in category_list]
        obs_data = {
            # "id": f"Observation/{resource.get('id')}",
            "datetime": resource.get("effectiveDateTime"),
            # "patient": resource.get("subject", {}).get("display"),
            # "encounter": resource.get("encounter", {}).get("display"),
            # "performed_by": performer.get("display"),
            "observation_type": resource.get("code", {}).get("text"),
            "value": None,
            "unit": None
        }
        if isinstance(value_quantity, dict) and "systolic" in value_quantity:
            obs_data["value"] = {
                "systolic": value_quantity["systolic"].get("value"),
                "diastolic": value_quantity["diastolic"].get("value")
            }
            obs_data["unit"] = value_quantity["systolic"].get("unit")  
        elif value_quantity:
            obs_data["value"] = value_quantity.get("value")
            obs_data["unit"] = value_quantity.get("unit")

        if "vital-signs" in categories:
            vitals.append(obs_data)
        elif "laboratory" in categories:
            labs.append(obs_data)

    return {
        "vital_signs": vitals,
        "lab_results": labs
    }

def preprocess_observations_epic(observations):
    processed_observations = []
    for item in observations:
        # print(item)
        resource = item  # Assuming each item is already the Observation resource

        if not resource or resource.get("resourceType") != "Observation":
            continue

        # Extract categories
        category_list = resource.get("category", [])
        categories = [cat.get("text") for cat in category_list if "text" in cat]

        # Extract coding display (e.g., LOINC code display name)
        code_list = resource.get("code", {}).get("coding", [])
        code_display = next((code.get("display") for code in code_list if code.get("display")), None)

        # Get reference range text if available
        reference_range = resource.get("referenceRange", [])
        reference_range_text = reference_range[0].get("text") if reference_range else None

        # Determine value (can be valueQuantity, valueString, etc.)
        value = None
        if "valueQuantity" in resource:
            value = {
                "value": resource["valueQuantity"].get("value"),
                "unit": resource["valueQuantity"].get("unit")
            }
        elif "valueString" in resource:
            value = resource["valueString"]
        elif "valueCodeableConcept" in resource:
            value = resource["valueCodeableConcept"].get("text")

        observation_data = {
            "id": f"Observation/{resource.get('id')}",
            "based_on": [ref.get("display") for ref in resource.get("basedOn", [])],
            "status": resource.get("status"),
            "categories": categories,
            "code_text": resource.get("code", {}).get("text"),
            "code_display": code_display,
            "patient": resource.get("subject", {}).get("display"),
            "encounter": resource.get("encounter", {}).get("display"),
            "effective_datetime": resource.get("effectiveDateTime"),
            "issued": resource.get("issued"),
            "value": value,
            "reference_range": reference_range_text,
            "interpretation": [interp.get("text") for interp in resource.get("interpretation", [])] if resource.get("interpretation") else [],
            "note": [note.get("text") for note in resource.get("note", [])] if resource.get("note") else [],
            "specimen": resource.get("specimen", {}).get("display"),
        }

        processed_observations.append(observation_data)

    return processed_observations

def extract_observations_epic(observations):
    processed_observations = []
    for item in observations:
        # print(item)
        resource = item  # Assuming each item is already the Observation resource

        if not resource or resource.get("resourceType") != "Observation":
            continue

        # Extract categories
        category_list = resource.get("category", [])
        categories = [cat.get("text") for cat in category_list if "text" in cat]

        # Extract coding display (e.g., LOINC code display name)
        code_list = resource.get("code", {}).get("coding", [])
        code_display = next((code.get("display") for code in code_list if code.get("display")), None)

        # Get reference range text if available
        reference_range = resource.get("referenceRange", [])
        reference_range_text = reference_range[0].get("text") if reference_range else None

        # Determine value (can be valueQuantity, valueString, etc.)
        value = None
        if "valueQuantity" in resource:
            value = {
                "value": resource["valueQuantity"].get("value"),
                "unit": resource["valueQuantity"].get("unit")
            }
        elif "valueString" in resource:
            value = resource["valueString"]
        elif "valueCodeableConcept" in resource:
            value = resource["valueCodeableConcept"].get("text")

        observation_data = {
            # "id": f"Observation/{resource.get('id')}",
            # "based_on": [ref.get("display") for ref in resource.get("basedOn", [])],
            "status": resource.get("status"),
            # "categories": categories,
            # "code_text": resource.get("code", {}).get("text"),
            "code_display": code_display,
            # "patient": resource.get("subject", {}).get("display"),
            # "encounter": resource.get("encounter", {}).get("display"),
            # "effective_datetime": resource.get("effectiveDateTime"),
            # "issued": resource.get("issued"),
            "value": value,
            "reference_range": reference_range_text,
            # "interpretation": [interp.get("text") for interp in resource.get("interpretation", [])] if resource.get("interpretation") else [],
            "note": [note.get("text") for note in resource.get("note", [])] if resource.get("note") else [],
            "specimen": resource.get("specimen", {}).get("display"),
        }

        processed_observations.append(observation_data)

    return processed_observations

def preprocess_diagnostic_reports(reports):
    """Extracts key details from FHIR DiagnosticReport resources for summarization or display."""
    processed = []

    for report in reports:
        data = {
            "report_id": f"DiagnosticReport/{report.get('id')}",
            "report_type": report.get("code", {}).get("text"),
            "status": report.get("status"),
            "category": [cat.get("text") for cat in report.get("category", [])],
            "effective_date": report.get("effectiveDateTime"),
            "issued_date": report.get("issued"),
            "subject": report.get("subject", {}).get("display"),
            "encounter": report.get("encounter", {}).get("display"),
            "service_request": [req.get("display") for req in report.get("basedOn", [])],
            "performers": [perf.get("display") for perf in report.get("performer", [])],
            "results": [res.get("display") for res in report.get("result", [])],
        }

        # Optional: include imaging studies if present
        if "imagingStudy" in report:
            data["imaging_studies"] = [study.get("reference") for study in report["imagingStudy"]]

        # Optional: include interpreter(s)
        if "resultsInterpreter" in report:
            data["interpreters"] = [interp.get("display") for interp in report["resultsInterpreter"]]

        processed.append(data)

    return processed

def preprocess_medications(medications):
    processed_medications = []

    for entry in medications:
        resource = entry.get("resource", {}) 
        # Get medication display name from any available coding
        medication_code = None
        med_codeable = resource.get("medicationCodeableConcept", {})
        codings = med_codeable.get("coding", [])
        if codings:
            medication_code = codings[0].get("display") or med_codeable.get("text")

        # Get dosage instruction
        dosage_instruction = None
        dosage_list = resource.get("dosageInstruction", [])
        if dosage_list:
            dosage_instruction = dosage_list[0].get("text")

        # Get patient name
        patient = resource.get("subject", {}).get("display")

        # Get prescriber
        prescriber = resource.get("requester", {}).get("display")
        if not prescriber:
            # Fallback: Check extension inside requester
            requester_ext = resource.get("requester", {}).get("extension", [])
            if requester_ext:
                prescriber = requester_ext[0].get("valueCode", "Unknown Prescriber")

        medication_data = {
            "id": f"MedicationRequest/{resource.get('id')}",
            "status": resource.get("status"),
            "medication_code": medication_code,
            "dosage_instruction": dosage_instruction,
            "patient": patient,
            "prescriber": prescriber,
            "authored_on": resource.get("authoredOn")
        }

        processed_medications.append(medication_data)

    return processed_medications

def preprocess_epic_medications(medications):
    processed_medications = []

    for entry in medications:
        resource = entry.get("resource", {})
        if not resource:
            continue

        # Medication name from medicationReference.display
        medication_code = resource.get("medicationReference", {}).get("display")

        # Dosage instruction text and dose quantity
        dosage_instruction = None
        dose_quantity = None
        dosage_list = resource.get("dosageInstruction", [])
        if dosage_list:
            first_dosage = dosage_list[0]
            dosage_instruction = first_dosage.get("text")

            # Try to extract doseQuantity from any of the doseAndRate items
            dose_and_rate = first_dosage.get("doseAndRate", [])
            for dose_entry in dose_and_rate:
                dq = dose_entry.get("doseQuantity")
                if dq:
                    dose_quantity = f"{dq.get('value')} {dq.get('unit')}"
                    break  # Use the first available doseQuantity

        # Patient name
        patient = resource.get("subject", {}).get("display")

        # Prescriber name
        prescriber = resource.get("requester", {}).get("display", "Unknown Prescriber")

        medication_data = {
            "id": f"MedicationRequest/{resource.get('id')}",
            "status": resource.get("status"),
            "medication_code": medication_code,
            "dosage_instruction": dosage_instruction,
            "dose_quantity": dose_quantity,
            "patient": patient,
            "prescriber": prescriber,
            "authored_on": resource.get("authoredOn")
        }

        processed_medications.append(medication_data)

    return processed_medications

def extract_epic_medications(medications):
    processed_medications = []

    for entry in medications:
        resource = entry.get("resource", {})
        if not resource:
            continue

        # Medication name from medicationReference.display
        medication_code = resource.get("medicationReference", {}).get("display")

        # Dosage instruction text and dose quantity
        dosage_instruction = None
        dose_quantity = None
        dosage_list = resource.get("dosageInstruction", [])
        if dosage_list:
            first_dosage = dosage_list[0]
            dosage_instruction = first_dosage.get("text")

            # Try to extract doseQuantity from any of the doseAndRate items
            dose_and_rate = first_dosage.get("doseAndRate", [])
            for dose_entry in dose_and_rate:
                dq = dose_entry.get("doseQuantity")
                if dq:
                    dose_quantity = f"{dq.get('value')} {dq.get('unit')}"
                    break  # Use the first available doseQuantity

        # Patient name
        patient = resource.get("subject", {}).get("display")

        # Prescriber name
        prescriber = resource.get("requester", {}).get("display", "Unknown Prescriber")

        medication_data = {
            # "id": f"MedicationRequest/{resource.get('id')}",
            "status": resource.get("status"),
            "medication_code": medication_code,
            # "dosage_instruction": dosage_instruction,
            "dose_quantity": dose_quantity,
            "patient": patient,
            # "prescriber": prescriber,
            # "authored_on": resource.get("authoredOn")
        }

        processed_medications.append(medication_data)

    return processed_medications

def clean_fhir_data(data: str) -> dict:
    data = re.sub(r'https?://[^\s\',"]+', '', data)  
    data = re.sub(r'urn:oid:[^\s\',"]+', '', data) 
    data = re.sub(r'urn:[^\s\',"]+', '', data)  
    data = re.sub(r"'system':\s*'[^']*'", "", data)  
    data = re.sub(r"'fullUrl':\s*'[^']*',?", "", data)  
    data = re.sub(r"'link':\s*\[[^\]]*\],?", "", data)  
    data = re.sub(r",\s*}", "}", data)  
    data = re.sub(r"{\s*,", "{", data)  
    cleaned_data = json.loads(data)
    try:
        cleaned_data = json.loads(data)
    except json.JSONDecodeError:
        cleaned_data = {}
    return cleaned_data

def preprocess_procedure(procedures):
    processed_procedures = []
    for resource in procedures:
        procedure_data = {
            "id": f"Procedure/{resource.get('id')}",
            "status": resource.get("status"),
            "procedure_code": resource.get("code", {}).get("coding", [{}])[0].get("display"),
            "performed_period": resource.get("performedPeriod", {}),
            "patient": resource.get("subject", {}).get("display")
        }
        processed_procedures.append(procedure_data)
    return processed_procedures

def extract_procedure(procedures):
    processed_procedures = []
    for resource in procedures:
        procedure_data = {
            # "id": f"Procedure/{resource.get('id')}",
            # "status": resource.get("status"),
            "procedure_code": resource.get("code", {}).get("coding", [{}])[0].get("display"),
            "performed_period": resource.get("performedPeriod", {}),
            # "patient": resource.get("subject", {}).get("display")
        }
        processed_procedures.append(procedure_data)
    return processed_procedures

def process_allergy(allergy):
    processed_allergies = []
    for resource in allergy:
        reactions = []
        for reaction in resource.get("reaction", []):
            for manifestation in reaction.get("manifestation", []):
                reactions.append({
                    "text": manifestation.get("text"),
                    "severity": reaction.get("severity")
                })

        allergy_data = {
            "id": f"AllergyIntolerance/{resource.get('id')}",
            "clinical_status": resource.get("clinicalStatus", {}).get("coding", [{}])[0].get("code"),
            "verification_status": resource.get("verificationStatus", {}).get("coding", [{}])[0].get("code"),
            "type": resource.get("type"),
            "category": resource.get("category"),
            "criticality": resource.get("criticality"),
            "substance": resource.get("code", {}).get("coding", [{}])[0].get("display"),
            "recorded_date": resource.get("recordedDate"),
            "reaction": reactions
        }
        processed_allergies.append(allergy_data)
    return processed_allergies

def extract_allergy(allergy):
    processed_allergies = []
    for resource in allergy:
        reactions = []
        for reaction in resource.get("reaction", []):
            for manifestation in reaction.get("manifestation", []):
                reactions.append({
                    "text": manifestation.get("text"),
                    "severity": reaction.get("severity")
                })

        allergy_data = {
            # "id": f"AllergyIntolerance/{resource.get('id')}",
            "clinical_status": resource.get("clinicalStatus", {}).get("coding", [{}])[0].get("code"),
            # "verification_status": resource.get("verificationStatus", {}).get("coding", [{}])[0].get("code"),
            "type": resource.get("type"),
            "category": resource.get("category"),
            # "criticality": resource.get("criticality"),
            "substance": resource.get("code", {}).get("coding", [{}])[0].get("display"),
            # "recorded_date": resource.get("recordedDate"),
            # "reaction": reactions
        }
        processed_allergies.append(allergy_data)
    return processed_allergies

def process_immunization(immunization_resources):
    processed_immunizations = []

    for resource in immunization_resources:
        # Extract performers
        performers = resource.get("performer", [])
        provider = None
        organization = None
        for performer in performers:
            actor = performer.get("actor", {})
            if actor.get("reference", "").startswith("Practitioner"):
                provider = actor.get("display")
            elif actor.get("reference", "").startswith("Organization"):
                organization = actor.get("display")

        # Extract target diseases
        target_diseases = []
        for protocol in resource.get("protocolApplied", []):
            for disease in protocol.get("targetDisease", []):
                target_diseases.append(disease.get("text"))

        immunization_data = {
            "id": f"Immunization/{resource.get('id')}",
            "status": resource.get("status"),
            "vaccine": resource.get("vaccineCode", {}).get("coding", [{}])[0].get("display"),
            "occurrence_date": resource.get("occurrenceDateTime"),
            "patient": resource.get("patient", {}).get("display"),
            "location": resource.get("location", {}).get("display"),
            "dose_quantity": resource.get("doseQuantity", {}).get("value"),
            "dose_unit": resource.get("doseQuantity", {}).get("unit"),
            "provider": provider,
            "organization": organization,
            "target_diseases": target_diseases,
            "dose_number": resource.get("protocolApplied", [{}])[0].get("doseNumberString")
        }

        processed_immunizations.append(immunization_data)

    return processed_immunizations

def preprocess_condition(conditions):
    processed_conditions = []
    half_len = (len(conditions) // 2)+10
    for item in conditions:
        # print(item)
        resource = item.get('resource', {})
        condition_data = {
            "id": f"Condition/{resource.get('id')}",
            "datetime": resource.get("onsetDateTime"),
            "status": resource.get("clinicalStatus", {}).get("coding", [{}])[0].get("code"),
            "patient": resource.get("subject", {}).get("display"),
            "condition_type": resource.get("code", {}).get("text")
        }
        processed_conditions.append(condition_data)
        print(condition_data["status"])
    return processed_conditions

def extract_condition(conditions):
    processed_conditions = []
    half_len = (len(conditions) // 2)+10
    for item in conditions:
        # print(item)
        resource = item.get('resource', {})
        condition_data = {
            # "id": f"Condition/{resource.get('id')}",
            "datetime": resource.get("onsetDateTime"),
            "status": resource.get("clinicalStatus", {}).get("coding", [{}])[0].get("code"),
            # "patient": resource.get("subject", {}).get("display"),
            "condition_type": resource.get("code", {}).get("text")
        }
        processed_conditions.append(condition_data)
        print(condition_data["status"])
    return processed_conditions

def preprocess_epic_conditions(conditions):
    processed_conditions = []

    for resource in conditions:
        if not resource or resource.get("resourceType") != "Condition":
            continue

        # Extract categories
        category_list = resource.get("category", [])
        categories = [cat.get("text") for cat in category_list if "text" in cat]

        # Extract coding display for diagnosis (e.g., SNOMED or ICD)
        diagnosis_codes = resource.get("code", {}).get("coding", [])
        diagnosis_display = next((code.get("display") for code in diagnosis_codes if code.get("display")), None)

        # Extract evidence displays
        evidence_refs = []
        for ev in resource.get("evidence", []):
            for detail in ev.get("detail", []):
                display = detail.get("display")
                if display:
                    evidence_refs.append(display)

        condition_data = {
            "id": f"Condition/{resource.get('id')}",
            "datetime": resource.get("onsetDateTime"),
            "recorded_date": resource.get("recordedDate"),
            "status": resource.get("clinicalStatus", {}).get("coding", [{}])[0].get("code"),
            "verification_status": resource.get("verificationStatus", {}).get("coding", [{}])[0].get("code"),
            "patient": resource.get("subject", {}).get("display"),
            "condition_type": resource.get("code", {}).get("text"),
            "diagnosis_display": diagnosis_display,
            "categories": categories,
            "encounter": resource.get("encounter", {}).get("display"),
            "evidence": evidence_refs
        }

        processed_conditions.append(condition_data)

    return processed_conditions

def extract_epic_condition(conditions):
    processed_conditions = []

    for resource in conditions:
        if not resource or resource.get("resourceType") != "Condition":
            continue

        # Extract categories
        category_list = resource.get("category", [])
        categories = [cat.get("text") for cat in category_list if "text" in cat]

        # Extract coding display for diagnosis (e.g., SNOMED or ICD)
        diagnosis_codes = resource.get("code", {}).get("coding", [])
        diagnosis_display = next((code.get("display") for code in diagnosis_codes if code.get("display")), None)

        # Extract evidence displays
        evidence_refs = []
        for ev in resource.get("evidence", []):
            for detail in ev.get("detail", []):
                display = detail.get("display")
                if display:
                    evidence_refs.append(display)

        condition_data = {
            # "id": f"Condition/{resource.get('id')}",
            "datetime": resource.get("onsetDateTime"),
            # "recorded_date": resource.get("recordedDate"),
            "status": resource.get("clinicalStatus", {}).get("coding", [{}])[0].get("code"),
            # "verification_status": resource.get("verificationStatus", {}).get("coding", [{}])[0].get("code"),
            # "patient": resource.get("subject", {}).get("display"),
            "condition_type": resource.get("code", {}).get("text"),
            "diagnosis_display": diagnosis_display,
            # "categories": categories,
            # "encounter": resource.get("encounter", {}).get("display"),
            # "evidence": evidence_refs
        }

        processed_conditions.append(condition_data)

    return processed_conditions


def clean_fhir_data_diagnostics(data: str) -> dict:
    data = re.sub(r'https?://[^\s\',"]+', '', data) 
    data = re.sub(r'urn:oid:[^\s\',"]+', '', data)  
    data = re.sub(r'urn:[^\s\',"]+', '', data)       
    data = re.sub(r"'system':\s*'[^']*'", "", data)  
    data = re.sub(r"'fullUrl':\s*'[^']*',?", "", data)  
    data = re.sub(r"'link':\s*\[[^\]]*\],?", "", data)  
    data = re.sub(r",\s*}", "}", data)  
    data = re.sub(r"{\s*,", "{", data)  
    try:
        cleaned_data = json.loads(data)
    except json.JSONDecodeError:
        return {}

    relevant_keys = {'id', 'status', 'code', 'effectiveDateTime', 'issued', 'subject', 'performer', 'result'}

    if 'entry' in cleaned_data:
        cleaned_entries = []
        for entry in cleaned_data['entry']:
            resource = entry.get('resource', {})
            filtered_resource = {key: resource[key] for key in resource if key in relevant_keys}
            filtered_resource['original_id'] = resource.get('id')
            cleaned_entries.append(filtered_resource)
        cleaned_data['entry'] = cleaned_entries

    return cleaned_data



# def chunk_list(data, size):
#     for i in range(0, len(data), size):
#         yield data[i:i + size]
import re

def move_citations_to_end(text):
    citations = re.findall(r"\[Citation:.*?\]", text, re.DOTALL)

    text_without_citations = re.sub(r"\[Citation:.*?\]", "", text)

    text_without_citations = re.sub(r'\n{2,}', '\n\n', text_without_citations.strip())

    citation_section = "\n\n## Citations\n\n" + "\n\n".join(citations)

    return text_without_citations + citation_section

def extract_hours(timing: str) -> int | None:
    """
    Extract hours from a timing string.
    Returns number of hours as int or None if not parseable.
    """
    timing = timing.lower()

    if "every" in timing:
        match = re.search(r'every\s+(\d+)\s*hr', timing)
        if match:
            return int(match.group(1))
        match = re.search(r'every\s+(\d+)\s*day', timing)
        if match:
            return int(match.group(1)) * 24
    elif "daily" in timing:
        return 24
    elif "at bedtime" in timing:
        return 24
    return None

def build_reminder_schedule(medications, start_time=None):
    start_time = start_time or datetime.now()
    reminders = []

    for med in medications:
        interval_hr = extract_hours(med['timing'])
        if interval_hr:
            next_time = start_time
            for i in range(6):  # e.g., next 6 reminders
                reminder = {
                    "medication": med['name'],
                    "dosage": med['dosage'],
                    "instruction": med['instruction'],
                    "reminder_time": next_time.strftime("%Y-%m-%d %H:%M")
                }
                reminders.append(reminder)
                next_time += timedelta(hours=interval_hr)
    
    return reminders

def parse_medication_table(table_text: str) -> List[Dict]:
    lines = table_text.strip().split('\n')
    rows = [line.strip() for line in lines if line.strip() and '|' in line]

    if len(rows) < 2:
        return []

    headers = [h.strip().lower().replace(" ", "_") for h in rows[1].split('|')[1:-1]]

    medications = []
    for row in rows[2:]:
        cols = [c.strip() for c in row.split('|')[1:-1]]
        med = dict(zip(headers, cols))

        # Try to extract repeat interval from instruction
        instruction = med.get("instruction", "").lower()

        repeat_match = re.search(r"(every\s+\d+\s*(hr|hour|day)s?)", instruction)
        if repeat_match:
            med["repeat_interval"] = repeat_match.group(1)
        else:
            med["repeat_interval"] = "Not specified"

        medications.append(med)

    return medications    

def parse_markdown_table(table_text: str) -> list:
    lines = [line.strip() for line in table_text.strip().split('\n') if '|' in line]
    
    if len(lines) < 2:
        return []

    # Parse header
    headers = [cell.strip() for cell in lines[0].strip('|').split('|')]

    # Parse rows
    data = []
    for row_line in lines[2:]:  # skip header and separator
        cells = [cell.strip() for cell in row_line.strip('|').split('|')]
        if len(cells) != len(headers):
            continue
        row_dict = {headers[i]: cells[i] for i in range(len(headers))}
        data.append(row_dict)
    
    # Normalize keys to a clean format
    normalized_data = []
    for item in data:
        normalized_item = {
            'name': item.get('Medication Name', 'Not specified'),
            'dosage': item.get('Dosage', 'Not specified'),
            'instruction': item.get('Instruction', 'Not specified'),
            'timing': item.get('Repeat Interval', 'Not specified'),
        }
        normalized_data.append(normalized_item)
    
    return normalized_data