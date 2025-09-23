from pydantic import BaseModel

class Credentials(BaseModel):
    client_id:str
    secret_id:str
    redirect_uri:str
    organization_name:str
    password:str

from pydantic import BaseModel

class PatientSummary(BaseModel):
    summary: str
  
class PatientRequest(BaseModel):
    patient_id: str
    organization_name: str
  
class Summary(BaseModel):
    patient_info:str
    medications:str  
    diagnoses:str
    lab_results:str
    
class LoginRequest(BaseModel):
    organization_name: str
    password: str