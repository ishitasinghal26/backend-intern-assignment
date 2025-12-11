from pydantic import BaseModel, EmailStr

class OrgCreateRequest(BaseModel):
    organization_name: str
    email: EmailStr
    password: str

class OrgUpdateRequest(BaseModel):
    organization_name: str      # new name
    email: EmailStr
    password: str

class OrgGetRequest(BaseModel):
    organization_name: str

class OrgResponse(BaseModel):
    id: str
    organization_name: str
    collection_name: str
    admin_email: EmailStr
