from pymongo import MongoClient
from .config import settings

client = MongoClient(settings.MONGO_URI)
db = client[settings.MONGO_DB_NAME]

def get_org_collection_name(org_name: str) -> str:
    # normalize a bit (lowercase, underscores)
    normalized = org_name.strip().lower().replace(" ", "_")
    return f"org_{normalized}"
