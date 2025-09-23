from typing import Optional


def create_bedrock_prompt(
    schema_result: str,
    query_request: str,
    patient_id: Optional[str] = None,
    connection_id: Optional[str] = None,
    **kwargs
) -> str:
    """
    Build the prompt string for AWS Bedrock Claude.
    Includes schema, user request, patient_id, and connection_id.
    """
    prompt = f"""
You are an expert SQL generator for healthcare databases.

Database schema:
{schema_result}

User request:
{query_request}
"""

    if patient_id:
        prompt += f"\nPatient context:\nPatient ID = {patient_id}\n"

    if connection_id:
        prompt += f"\nConnection context:\nConnection ID = {connection_id}\n"

    # Add any additional context from kwargs
    if kwargs:
        prompt += f"\nAdditional context:\n{kwargs}\n"

    prompt += """
Instructions:
- Generate a valid SQL query for the above request.
- Return only the SQL query followed by a brief explanation.
"""
    return prompt.strip()
