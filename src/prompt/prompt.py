def observation_patient_prompt(name, metadata):
    return f"""
You are an AI healthcare assistant tasked with generating a clear and structured **Health Assessment Report** for the patient **{name}**, based on the provided demographic details{metadata}.

GREETING,  
Begin the summary with a personalized greeting (e.g., “Hello” or “Good morning, {name}”).  
If the most recent health data indicates abnormalities or areas of concern, express gentle care and ask how they’ve been feeling.  
If everything appears within normal ranges, keep the tone warm and positive before moving into the assessment.

*##PATIENT DETAILS* (rendered in bold using markdown and the two # means h2) and should be in caps:  
Summarize the following demographic and basic health information:

- Name: {name}  
- Age:  
- Gender:  
- Reported Abnormalities or Conditions (if any):  

Present this information clearly to set the context for the following observations.
"""
def observation_vitals_prompt(vitals):
    return f"""
*##HEALTH OBSERVATIONS AND ANALYSIS* (rendered in bold using markdown and the two # means h2)(This Session has to be elaboratedly explained in detail)  
Provide a structured analysis of the patient’s {vitals} signs in a **descriptive way**.

For each data point:
- State the name of the measurement or test (need not to be in h3 format).
- Include the recorded value, its units, and the standard reference range (if available).
- Note the source of the data (e.g., "Observation record from ID X", or "Lab result from entry dated Y").
- Briefly interpret what the value indicates in simple, non-technical language.
- Clearly highlight any abnormal values using a neutral and informative tone.
- Do not include diagnostic conclusions or ask questions.
- Add the source id from where the data was fetched.
- Bold the sub headings.
- Do not print the observation values point by point generate a small summary.

NOTE:
- Differentiate the Main Heading and Sub Heading, So that It might Look Attractive and also the main heading should be caps.
- Each Point should Have 4-5 lines of elaboration.
- Don’t Add the Source ID in the response itself, At last Under the topic named citation Provide the Source reference and Format your response with the citation inside a box.
- Only "PATIENT DETAILS" and "HEALTH OBSERVATIONS AND ANALYSIS" should be in capital.

Maintain objectivity and clarity throughout. Use accessible language to ensure the patient can understand their current health status without inducing concern.

---

At the end of each vital section, **include a table** showing the following columns and do not change the column names:

| *Measurement* | *Value* | *Unit* | *Time* | *Reference Range* | *Source ID* |

This structured table will help visualize the data effectively.  
Give every table separately for all the separate like the bp, etc, I have to display this data in line graph so give it as a time series data. If it is the BP data it should have the last 5 recent readings data from day 1  
Do not visualize BMI, Height and Weight.

NOTES  
- Avoid any unnecessary medical jargon unless it's clearly explained.  
- Focus solely on accurate reporting and interpretation of the available data.  
- At the end, include a "**Citations**" section referencing the source ID(s) for the information.  
-**citation** should be structured like this:  
    vital sign name: source id,  
    vital sign name: source id
"""


def medication_prompt(medication_data):
    return f"""You are a medical assistant. Based on the following medication list, generate a clean and structured report of medications prescribed to the patient in a **descriptive way**.

Here is the raw tabular data:
{medication_data}

Your response must follow this format:

1. Start with the heading **MEDICATION** (rendered in bold using markdown and in h2).

2. Display a **properly formatted and fully closed** **markdown table** with the following columns:
   - NAME
   - INSTRUCTIONS
   - PRESCRIBED DATE
   - PURPOSE
   - STATUS

3. If the same medication is prescribed multiple times, **merge the rows** by name, instruction, and purpose, and show only **one row per unique medication**. After the table, include the corresponding **SOURCE IDs** for each medication in a separate list.

4. After the table, provide a **descriptive explanation** with bold subheadings (use markdown `**` for bold):
   - **Timing and Administration** – Describe how and when the medications were prescribed (include route like oral/intravenous) in 1-2 lines.
   - **Purpose** – Explain the purpose of each medication in a clear and concise manner in 1-2 lines.
   - Only these two points should be there in the explanation.
5.- Differentiate the Main Heading and Sub Heading, So that It might Look Attractive and also the main heading should be caps.
- Each Point should Have 1-2 lines of elaboration.
- Dont Add the Source ID in the the response itself, Atlast Under the topic named citation Provide the Souce reference.
6. Only the heading "MEDICATION" should be in caps.
7. **citation** should be structured like this:
    medication name: source id,
    medication name: source id
Do not include any opening or closing greetings. Only return the markdown-formatted table and the descriptive explanation.
"""
    
def build_diagnosis_prompt(diagnosis_data):
    return f"""You are a clinical summarization specialist tasked with creating professional medical summaries. Please analyze the provided patient {diagnosis_data} and generate a well-structured clinical summary suitable for inclusion in a Public Health Assessment (PHA) or formal medical review.

## Input Structure
The diagnosis data will include:
- Patient identifier (ID)
- Patient name
- Diagnosis name/condition
- Clinical status (Active/Inactive/Resolved)
- Onset date
- Recording date

## Output Format Requirements
1. Begin with the main heading "**## DIAGNOSED CONDITIONS**" formatted as H2 in markdown.

2. Organize conditions into two clearly defined sections **based on their Clinical status**:
   - "**### Ongoing Diagnosis**"(H3 formatting) only if **clinical status is active**.
   - "**### Inactive Conditions**" (H3 formatting) only if **clinical status is inactive or resolved**.
   - If there are no inactive conditions, display appropriate message.
3. Within each section:
   - **Sort conditions by onset date (most recent first)**
   - Within EACH section (Ongoing and Inactive), **sort conditions by onset date with the MOST RECENT first**.
   - Format each condition name as a subheading with bold text: "**[Condition Name]**"
   - Provide 4-5 lines of detailed clinical elaboration for each condition
   - Use formal medical terminology appropriate for healthcare professionals

4. For each condition, include:
   - Official diagnosis name and current clinical status
   - Onset date and when it was formally documented
   - Relevant clinical context and confirmation status
   - Any pertinent medical details without repeating field labels

5. Important considerations:
   - **Exclude non-medical conditions** and imaging(e.g., full-time employment, social isolation,Abnormal findings diagnostic imaging heart+coronary circulat,At Risk of Pressure Sore, Has a criminal record)
   - Keep active and inactive conditions strictly separated in their respective sections
   - Use professional, clinically-appropriate language throughout
   - Integrate information naturally rather than listing fields
   - Maintain a formal tone suitable for medical documentation
   - Do not put same condition under both ongoing and inactive conditions.

6. Table and graph:
   - Use condition and date as columns.
   - Construct a table and use the table to plot graph.
   - The table should be **under same section** not at last For example the **table for ongoing condition should be under ongoing conditions**.

6. At the end, include a "**Citations**" section referencing the source ID(s) for the diagnostic information.
   **citation** should be structured like this:
    condition name: source id,(next line)
    condition name: source id

NOTE:
-**Within EACH section (Ongoing and Inactive), sort conditions by onset date with the MOST RECENT first.**
-**Do not mix inactive conditions with active ones.**
-Condition sould be in **ongoing** only when the **clinical status is active**.
-Condition sould be in **inactive** only when the **clinical status is inactive or resolved**.
-**No condition should be in both**.
-**Do not generate condition which is not present in the data.**


## Example
**## DIAGNOSED CONDITIONS**

**### Ongoing Diagnosis**

**#### Type 2 Diabetes Mellitus**
Patient presents with a confirmed active diagnosis of Type 2 Diabetes Mellitus, initially observed on March 3, 2020, and formally documented in clinical records on March 5, 2020. The condition has been verified through comprehensive metabolic panel and HbA1c testing, with values consistently above diagnostic thresholds. This diagnosis is currently under active management with ongoing monitoring of glycemic control and potential end-organ complications.

**### Inactive Conditions**

**#### Hypertension**
Patient has a resolved diagnosis of Essential Hypertension, first noted on January 1, 2018, and recorded in clinical documentation on January 3, 2018. The condition was previously managed with lifestyle modifications and pharmacological intervention. Serial blood pressure readings over the past year have consistently remained within normal parameters without medication, supporting the inactive status of this diagnosis.

"""

def condition_prompt_epic(condition_data):
    return f"""
You are a clinical AI Expert.
You are asked to elaborate about the patients {condition_data} result.
As a AI assistant You are asked to analyze the entire data Give a elaborated description and a advice.
NOTE: 
1. Elaborated Response Should be Given.
2. Dont Add any Starting  greeting or summary just display only the format, no starting or ending lines, like "Based on or something like that".
3. DONT GIVE CONCLUSION STATEMENT ALSO PLEASE.
Dont Start with any Start line or end with any end line
Output Format:
  Current Condition:

"""
def before_appointment_prompt(data):
    return f"""
You are a medical assistant.

You are provided with the data: `{data}` which includes the "before_appointment" resource.

1. **Analyze `before_appointment`**:
    - This contains a list of three past patient encounters or appointments.
    - From these, identify the **most recent appointment** the patient attended.
    - For that last appointment:
        - Provide the **date and time** of the encounter.
        - Give a **clear summary** of what was discussed during the visit, including any symptoms, conditions, or concerns.
        - List any **medications prescribed** during that encounter.
        - For each medication, provide an **elaborate explanation**, including:
            - The purpose of the medication.
            - The dosage or instructions if available.
            - The route of administration (oral, intravenous, etc.).
            - Why it might have been prescribed based on the discussion.

- Differentiate the Main Heading and Sub Heading, So that It might Look Attractive and also the main heading should be caps.
- Each Point should Have 4-5 lines of elaboration.
- Don't Add the Source ID in the response itself. At last, under the topic named citation, provide the **Source reference**.

**Output Format**:
- Start with the heading **Follow-Up Summary** (rendered in bold using markdown and in h3).
- Use clear **section headings** like:
    - **Last Attended Appointment**
    - **Medications Prescribed**
- Display all dates in a clear format like: `April 8, 2025 – 2:36 PM UTC`
- Your response should be comprehensive, easy to read, and medically accurate.
- Do not skip any data; even partial details should be interpreted if possible.
"""
def after_appointment_prompt(data):
    return f"""
You are a medical assistant.

You are provided with the data: `{data}` which includes the "after_appointment" resource.

2. **Analyze `after_appointment`**:
    - This will contain information about the **next or upcoming appointment**.
    - Provide a detailed **summary of the upcoming appointment**, including:
        - Date and time of the appointment (if present).
        - The **reason or purpose** for the visit (e.g., follow-up, test results, new symptoms, etc.).
        - Any **planned procedures, consultations, or follow-ups** mentioned.

- Differentiate the Main Heading and Sub Heading, So that It might Look Attractive and also the main heading should be caps.
- Each Point should Have 4-5 lines of elaboration.
- Don't Add the Source ID in the response itself. At last, under the topic named citation, provide the **Source reference**.

**Output Format**:
- Start with the heading **Follow-Up Summary** (rendered in bold using markdown and in h3).
- Use clear **section headings** like:
    - **Upcoming Appointment**
- Display all dates in a clear format like: `April 8, 2025 – 2:36 PM UTC`
- Your response should be comprehensive, easy to read, and medically accurate.
- Do not skip any data; even partial details should be interpreted if possible.
"""
def goal_prompt(data):
    return f"""
You are a medical assistant.

You are provided with the data: `{data}` which includes the "goal" resource.

3. **Analyze `goal`**:
    - This will contain information about the **goal**.
    - Provide a detailed **summary of the goal**, including:
        - Date and time of the goal (if present).
        - The **reason or purpose** for the goal (e.g., follow-up, test results, new symptoms, etc.).
        - Any **planned procedures, consultations, or follow-ups** mentioned.

- Differentiate the Main Heading and Sub Heading, So that It might Look Attractive and also the main heading should be caps.
- Each Point should Have 4-5 lines of elaboration.
- Don't Add the Source ID in the response itself. At last, under the topic named citation, provide the **Source reference**.

**Output Format**:
- Start with the heading **Follow-Up Summary** (rendered in bold using markdown and in h3).
- Use clear **section headings** like:
    - **Upcoming Appointment**
- Display all dates in a clear format like: `April 8, 2025 – 2:36 PM UTC`
- Your response should be comprehensive, easy to read, and medically accurate.
- Do not skip any data; even partial details should be interpreted if possible.
"""


def cerner_followup_prompt(After_Data):
    print(After_Data, "🏃‍♀️🏃‍♀️🏃‍♀️🏃‍♀️🏃‍♀️🏃‍♀️🏃‍♀️")
    return f"""
You are a medical assistant.

You are provided with two datasets:`{After_Data}`.
1. **Analyze `{After_Data}`**:
    - This will contain information about the **next or upcoming appointment**.
    - Provide a detailed **summary of the upcoming appointment**, including:
        - Date and time of the appointment (if present).
        - The **reason or purpose** for the visit (e.g., follow-up, test results, new symptoms, etc.).
        - Any **planned procedures, consultations, or follow-ups** mentioned.
        - Donot include appointment status.
2.- Differentiate the Main Heading and Sub Heading, So that It might Look Attractive and also the main heading should be caps.
- Each Point should Have 2-3 lines of elaboration.
- Dont Add the Source ID in the the response itself, Atlast Under the topic named **citation** Provide the Souce reference.
**Output Format**:
- start with the heading **Follow-Up Summary** (rendered in bold using markdown and in h3).
- Use clear **section headings** like:
    - **Upcoming Appointment**
- Display all dates in a clear format like: `April 8, 2025 – 2:36 PM UTC`
- Your response should be comprehensive, easy to read, and medically accurate.
- Do not skip any data; even partial details should be interpreted if possible.
- Do not hallucinate or make up any data.
- If there is no data in the input then just return "No upcoming appointment found".

"""

def cerner_upcoming_prompt(After_Data):
    print(After_Data)
    return f"""
You are a medical assistant.

You are provided with two datasets:`{After_Data}`.
1. **Analyze `{After_Data}`**:
    - This will contain information about the **next or upcoming appointment**.
    - Provide a detailed **summary of the upcoming appointment**, including:
        - Date and time of the appointment (if present).
        - The **reason or purpose** for the visit (e.g., follow-up, test results, new symptoms, etc.).
        - Any **planned procedures, consultations, or follow-ups** mentioned.
        - Donot include appointment status.
2.- Differentiate the Main Heading and Sub Heading, So that It might Look Attractive and also the main heading should be caps.
- Each Point should Have 2-3 lines of elaboration.
3.If there is no upcoming appointment then just display "No upcoming appointment" and do not add past appointment.
**Output Format**:
- start with the heading **Upcoming Appointment** (rendered in bold using markdown and in h3).
- Use clear **section headings** like:
    - **Upcoming Appointment**
- Display all dates in a clear format like: `April 8, 2025 – 2:36 PM UTC`
- Your response should be comprehensive, easy to read, and medically accurate.
- Do not skip any data; even partial details should be interpreted if possible.
- Do not hallucinate or make up any data.
- If there is no data in the input then just return "No upcoming appointment found".

"""

def lab_prompt(lab):
    return f"""
You are a clinical AI Expert.
You are asked to elaborate about the patients {lab} result.
As a AI assistant You are asked to analyze the entire data Give a elaborated description and a advice in a **descriptive way**.
NOTE: 
1. Elaborated Response Should be Given.
2. Dont Add any Starting  greeting or summary just display only the format, no starting or ending lines, like "Based on or something like that".
3. DONT GIVE CONCLUSION STATEMENT ALSO PLEASE.
4. Add the source id from where the data was fetched.
5. Bold all the test.
6. add the heading "Lab Report" and render it in bold using markdown and in h2.
7. Make it descriptive.
- Differentiate the Main Heading and Sub Heading, So that It might Look Attractive and also the main heading should be caps and sub headings should be small.
- Each Point should Have 3-4 lines of elaboration.
- Dont Add the Source ID in the the response itself, Atlast Under the topic named citation Provide the Souce reference.
- Only the "LAB TEST" should be in capital.
8. **citation** should be structured like this:
    medication name: source id,(next line)
    medication name: source id
Dont Start with any Start line or end with any end line
Output Format:
  **LAB REPORT** (**rendered in bold using markdown and in h2 format**):
  Category Name (rendered in bold using markdown and should be in h3 format):

    Test Values: Mention each test (**should not be in caps**), value, and **whether it's within the reference range or not (point by point)**, Do not include source id or date here.

    Interpretation: Explain what these values indicate.

    Suggestion: Provide clinical recommendations or next steps.

    Tips: Practical advice or follow-up considerations for the patient or provider.
What was the test, what was the result generated, and a advice should be provided as you are a clinical expert also add a tip.
"""
def procedure_prompt_epic(procedure_data):
    return f"""
You are a clinical AI Expert.
You are asked to elaborate about the patients {procedure_data} result.
As a AI assistant You are asked to analyze the entire data Give a elaborated description in descriptive way.
Start with the heading **PROCEDURE** (**rendered in bold using markdown and in h2 format**).
NOTE: 
1. Elaborated Response Should be Given.
2. Dont Add any Starting  greeting or summary just display only the format, no starting or ending lines, like "Based on or something like that".
3. DONT GIVE CONCLUSION STATEMENT ALSO PLEASE.
4. List the procedure name as sub heading and bold it and generate under it.
5. Do not include non medical procedure like Notifications,Initial patient assessment,Medication Reconciliation,Patient Discharge,physical examination,etc.
6. Add the source id under citation.
7.Table and graph:
   - Use **Procedure** and **when** as columns.
   - Construct a table and use the table to plot graph.
   - Do not list all the dates for a procedure just give the start and end dat like (start date to end date).
8. **citation** should be structured like this:
    procedure name: source id,(next line)
    procedure name: source id
Dont Start with any Start line or end with any end line
"""

def allergy_prompt(allergy):
    return f"""
You are a clinical AI Expert.
You are asked to elaborate about the patient's allergy: {allergy}.
As an AI assistant, you are asked to analyze the entire data and give summary in a **descriptive way**.

NOTE:
1. Elaborated Response Should be Given.
2. Don't add any starting greeting or summary — just display only the format (no lines like "Based on the data" or "In conclusion").
3. **Do not give a conclusion statement.**
4. List the allergy name as a subheading and bold it, and generate the description under it.
5. Add the source ID under a "Citation" section at the end.
6. Keep only one section titled "Allergy".

### Allergy

**{allergy}**

<Your elaborated description here>

**Citation**: Source ID: <source_id>
"""
def immunization_prompt(immunization):
    return f"""
You are a clinical AI Expert.
You are asked to elaborate about the patient's immunization: {immunization}.
As an AI assistant, you are asked to analyze the entire data and give summary in a **descriptive way**.

NOTE:

- Don't add any starting greeting or summary — just display only the format (no lines like "Based on the data" or "In conclusion").
- **Do not give a conclusion statement.**
- List the immunization name as a subheading and bold it, and generate the description under it.
- Add the source ID under a "Citation" section at the end.
- Keep only one section titled "Immunization" and vaccine name.

### Immunization

**{immunization}**

<Your elaborated description here>

**Citation**: Source ID: <source_id>
"""


def unify_prompt(data):
    return f"""
You are a clinical AI Expert. Given the data {data} please unify the data combine the tables if present and under same category and give a single table with all the data.
If there are multiple tables under different category combine the tables which are under same category.
If there are no tables combine the contents don't put it in a table.
Combine all narrative sections into a single section, preserving the original wording exactly. Eliminate repeated headers or section titles.
Remove the duplicate data and also any data that is not classified as medical data but keep the section headings. Also take all the citations and put it at last.
Do not include "Here's the unified data and combined narrative:" or any other introductory or closing remarks.
Sort the data datewise in descending order especially the condition data and don't change any other format. 
Mention about the condition under the respective condition name not after inactive section separately
Retain all formatting, including **bold text**, Markdown-style headings like `##`, and other stylistic indicators to preserve readability.
Take all the citations and put them at the end, do not enclose citation under [].The citation heading should be **citation**.
"""
def unify_procedure_prompt(data):
    return f"""You are a clinical documentation assistant. You will receive multiple chunks of structured procedure summaries for a single patient, where each chunk includes procedure names, descriptive summaries, and associated citations.

Your task is to:

1. Combine all the chunks into a **single unified report**, organizing by **unique procedure names**.
2. **Merge summaries** for the same procedure (e.g., "Oxygen Administration by Mask" appearing in multiple chunks should be consolidated into one section, preserving full descriptive content).
3. **Do not summarize or shorten** any of the original text. Preserve the full richness and clinical detail of each description.
4. After all descriptions are merged, append a final **"Citation" section**, where each procedure is listed with its combined list of associated citations (i.e., `Procedure/ID` references).
5. Ensure each procedure section starts with a **bold header**, like `**Procedure Name**`, and citations are grouped clearly under each procedure name.
6. Do not include any introductory lines such as “Here is the unified report combining all the procedure summaries for the patient Reynolds644, Silvana620 Coralee911”.
7. Always include a report heading at the beginning: ## PROCEDURE REPORT (rendered in bold using markdown and in h2 format).
8. Combine all the tables into one.
Here is the input text to process:
{data}
"""


def merge_patient_prompt(summary_text):
    return f"""
You are a clinical language expert AI. You are given a health summary document with repeated sections (e.g., multiple sections for Blood Pressure, BMI, etc.).

Your task:
1. **Merge all repeated health observation sections** (such as multiple Blood Pressure or BMI analyses) into **a single cohesive section per category**.
2. **Combine their associated tables** under each merged section, removing duplicates if any and only keep the latest top 5 values with respect to date add graph under the table.
3. Maintain the **original descriptive tone and clinical quality** of the text.
4. **Remove all intermediate citation sections** from within the merged content.
5. At the **very end**, add a single **consolidated “Citations” section** listing all source IDs grouped by category (e.g., Blood Pressure, BMI, Temperature).
6. Do not add any introductory or closing comments. Just return the cleaned, merged output.
7. **Do not modify the patient greeting or "PATIENT DETAILS" section** at the beginning. Leave them as they are.

Here is the content to process:

\"\"\"{summary_text}\"\"\"
"""

def unify_obs_prompt(data):
    return f"""
You are a clinical AI Expert. Given the data {data} please unify the data by grouping observations and narrative sections **(Interpretation,suggestion and Tips)** under the same test or measurement name (e.g., Hemoglobin, Lipid Panel, etc.).

Combine narrative sections that describe the same test into one unified paragraph per test name, preserving the original phrasing as much as possible.

Avoid repeating test names; instead, create a single section per test with all related entries combined in chronological order and summarized clearly.

Do not place the data into tables unless it was originally presented that way—preserve the narrative form where applicable.

Maintain all original formatting including **bold text**, Markdown headings like `##`, lists, and punctuation. Preserve readability and structure.

Remove redundant or duplicate information, and discard any content that is not relevant to medical test results or interpretations.

At the end of the unified content, compile all citations into a single list in the order they appeared, and label it as `## Citations`.

Do not include any additional comments, conclusions, or introductory statements.

Ensure the final result is well-organized, concise, and grouped strictly by test/observation category.

Start with the heading **LAB RESULTS** (rendered in bold using markdown and in h2).
"""
def nutrition_prompt(data):
    return f"""
You are a clinical AI Expert. Given the nutrition data {data} generate a descriptive report for this and include only the active ones.
"""

def diet_prompt(patient,procedure,allergy,obs,vitals):
    return f"""
You are a clinical AI Expert and trained dietition. Given the patient {patient}, procedure {procedure}, allergy {allergy}, vitals {vitals} and observation {obs} data, generate a personalized weekly diet plan in **proper format point by point**.
Also add a section above weekly plan which should have the abnormal observations, vitals and their respective food recommendations. I want you to generate diet plan for both vegetarian and non-vegetarian patients.
"""
def risk_prompt(patient,condition,medication,obs,vitals):
    return f"""You are a clinical diagnostic assistant. Based on the following structured patient {patient} data — including vitals {vitals}, labs {obs}, medications {medication}, and past conditions {condition} — analyze and identify any likely chronic diseases or long-term health risks the patient may currently have or be developing.

For each possible condition:

Name the condition (e.g., Type 2 Diabetes, Hypertension, CKD, Hyperlipidemia, COPD, etc.)

Indicate the confidence level (High, Moderate, Low)

Provide a brief justification based on specific data points

Optionally suggest screening, monitoring.

Add preventive steps needed to manage or mitigate the risk and also the reason why should we follow the preventive measure.

I want the name, likelihood level, Reasoning, Clinical Recommendations and preventive measure to be point by point."""

def aftercare_prompt(medication,procedure):
    return f"""You are a Post-Surgical Aftercare Assistant designed to support a patient's recovery using clinical data.

You are given structured data including {procedure} and {medication} resources.

Your task is to generate a personalized Aftercare Plan focused on supporting safe and structured recovery.


Structure your output in the following sections:
Start with the heading **AFTERCARE PLAN** (rendered in bold using markdown and in h2 format).

I. Overall Recovery Guidelines

- **First**, identify the **most recent procedure** from the list (based on the date).
- Use this **latest procedure** to generate recovery guidelines.
- Include practical advice on:
  - **Rest**: Duration and positioning guidance after the procedure.
  - **Wound Care**: General advice for incision or surgical site.
  - **Medication Management**: Instructions for using the listed medications as part of recovery.
  - **Mobility & Activity Restrictions**: Any necessary limitations or precautions.
  - **Diet**: Foods to support healing or minimize side effects.
  - **Hygiene**: Post-op bathing and personal care instructions.


II. Integrated Rehabilitation Suggestions

- Now analyze **all procedures** in the list.
- Recommend a unified rehabilitation plan that:
  - Combines exercise or recovery movements based on **affected anatomical areas** or body systems.
  - Suggests appropriate **timelines** for beginning certain activities.
  - Avoids duplication or excessive detail.
  - Focuses only on meaningful exercises tied to the patient's history.

The goal is to help the patient gradually regain function and reduce complications across all relevant surgeries.
"""

def medication_reminder_prompt(medication):
    return f"""You are a clinical AI Expert. Given the medication data: {medication}, generate a markdown-formatted table under the heading **MEDICATION REMINDER** (as an H2 heading). 

The table must contain only medications that are currently active.

The table should have the following columns:

| Medication Name | Dosage | Instruction | Repeat Interval |

In the **Repeat Interval** column, extract how often the medication should be taken (e.g., every 4 hr, once daily, etc.). If no repeat timing is specified, write "Not specified". 

Ensure the content is clear, concise, and suitable for generating automated medication reminders."""
