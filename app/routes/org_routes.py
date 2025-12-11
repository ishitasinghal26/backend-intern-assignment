from fastapi import APIRouter, HTTPException, Depends
from ..schemas.org_schemas import OrgCreateRequest, OrgGetRequest, OrgUpdateRequest, OrgResponse
from ..services.org_service import OrgService
from ..utils.auth_utils import decode_token
from fastapi import Header

router = APIRouter(prefix="/org", tags=["Organization"])
org_service = OrgService()

def get_current_admin(authorization: str = Header(None)):
    # Expect "Bearer <token>"
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Not authenticated")
    token = authorization.split(" ", 1)[1]
    try:
        payload = decode_token(token)
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")
    return payload  # contains admin_id & org_id

@router.post("/create", response_model=OrgResponse)
def create_org(body: OrgCreateRequest):
    try:
        org = org_service.create_org(
            org_name=body.organization_name,
            email=body.email,
            password=body.password,
        )
        return org
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/get", response_model=OrgResponse)
def get_org(organization_name: str):
    org = org_service.get_org_by_name(organization_name)
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    return org

@router.put("/update")
def update_org(body: OrgUpdateRequest, current_admin=Depends(get_current_admin)):
    # Optional: check current_admin["org_id"] matches the org being updated
    try:
        org_service.update_org(
            old_name=current_admin.get("org_name", body.organization_name),  # or pass via query
            new_name=body.organization_name,
            new_email=body.email,
            new_password=body.password,
        )
        return {"message": "Organization updated successfully"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/delete")
def delete_org(organization_name: str, current_admin=Depends(get_current_admin)):
    # Ensure only the org’s own admin can delete
    # Fetch org by name and check current_admin["org_id"] matches
    org = org_service.get_org_by_name(organization_name)
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")

    if str(current_admin["org_id"]) != org["id"]:
        raise HTTPException(status_code=403, detail="Not allowed to delete this organization")

    try:
        org_service.delete_org(organization_name)
        return {"message": "Organization deleted successfully"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
