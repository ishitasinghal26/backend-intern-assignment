from ..database import db
from ..utils.security import verify_password
from ..utils.auth_utils import create_access_token

class AuthService:
    def __init__(self):
        self.admins = db["admins"]
        self.orgs = db["organizations"]

    def login_admin(self, email: str, password: str):
        admin = self.admins.find_one({"email": email})
        if not admin:
            return None

        if not verify_password(password, admin["password"]):
            return None

        org = self.orgs.find_one({"admin_id": admin["_id"]})
        if not org:
            return None

        payload = {
            "sub": str(admin["_id"]),
            "org_id": str(org["_id"]),
            "role": "admin",
        }
        token = create_access_token(payload)
        return token
