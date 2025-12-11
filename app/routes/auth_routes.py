from fastapi import APIRouter, HTTPException
from ..schemas.admin_schemas import AdminLoginRequest, TokenResponse
from ..services.auth_service import AuthService

router = APIRouter(prefix="/admin", tags=["Admin"])
auth_service = AuthService()

@router.post("/login", response_model=TokenResponse)
def login(body: AdminLoginRequest):
    token = auth_service.login_admin(email=body.email, password=body.password)
    if not token:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return TokenResponse(access_token=token)
