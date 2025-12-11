from typing import Optional
from bson import ObjectId
from pymongo import errors
from ..database import db, get_org_collection_name
from ..utils.security import hash_password
import logging

logger = logging.getLogger(__name__)

class OrgService:
    def __init__(self):
        self.orgs = db["organizations"]
        self.admins = db["admins"]

        # Ensure helpful unique indexes exist (idempotent)
        try:
            self.orgs.create_index("organization_name", unique=True)
            self.admins.create_index("email", unique=True)
        except Exception as e:
            # index creation can fail in some environments, but it's not fatal here
            logger.warning("Index creation failed or already exists: %s", e)

    def _ensure_org_not_exists(self, org_name: str):
        return self.orgs.find_one({"organization_name": org_name}) is None

    def create_org(self, org_name: str, email: str, password: str) -> dict:
        org_name = org_name.strip()
        if not org_name:
            raise ValueError("organization_name is required")

        # Check if org exists
        if not self._ensure_org_not_exists(org_name):
            raise ValueError("Organization already exists")

        # Check admin email uniqueness
        if self.admins.find_one({"email": email}):
            raise ValueError("Admin email already in use")

        collection_name = get_org_collection_name(org_name)

        try:
            # Create dynamic collection handle (Mongo creates it on first insert)
            org_collection = db[collection_name]

            # Hash password and create admin
            hashed = hash_password(password)
            admin_doc = {
                "email": email,
                "password": hashed,
                "role": "admin",
            }
            admin_result = self.admins.insert_one(admin_doc)
            admin_id = admin_result.inserted_id

            # Create org metadata in master DB
            org_doc = {
                "organization_name": org_name,
                "collection_name": collection_name,
                "admin_id": admin_id,
            }
            org_result = self.orgs.insert_one(org_doc)
            org_id = org_result.inserted_id

            # Update admin with org reference
            self.admins.update_one({"_id": admin_id}, {"$set": {"org_id": org_id}})

            return {
                "id": str(org_id),
                "organization_name": org_name,
                "collection_name": collection_name,
                "admin_email": email,
            }

        except errors.DuplicateKeyError as e:
            # In case of race conditions and unique index enforcement
            logger.exception("Duplicate key error creating org or admin: %s", e)
            raise ValueError("Organization or admin already exists")
        except Exception as e:
            # Ideally rollback created documents if partial failure occurred.
            logger.exception("Failed to create org: %s", e)
            # Try to clean up partial writes (best-effort)
            try:
                if 'admin_id' in locals():
                    self.admins.delete_one({"_id": admin_id})
                if 'org_id' in locals():
                    self.orgs.delete_one({"_id": org_id})
            except Exception:
                logger.exception("Cleanup after failed create_org also failed")
            raise ValueError("Failed to create organization: " + str(e))

    def get_org_by_name(self, org_name: str) -> Optional[dict]:
        org = self.orgs.find_one({"organization_name": org_name})
        if not org:
            return None

        admin = None
        try:
            admin = self.admins.find_one({"_id": org["admin_id"]})
        except Exception:
            logger.exception("Failed to fetch admin for org %s", org_name)

        return {
            "id": str(org["_id"]),
            "organization_name": org["organization_name"],
            "collection_name": org["collection_name"],
            "admin_email": admin["email"] if admin else None,
        }

    def update_org(self, old_name: str, new_name: str, new_email: str, new_password: str) -> bool:
        old_name = old_name.strip()
        new_name = new_name.strip()
        if not old_name or not new_name:
            raise ValueError("Organization names cannot be empty")

        org = self.orgs.find_one({"organization_name": old_name})
        if not org:
            raise ValueError("Organization not found")

        # If changing name, ensure new name not taken
        if new_name != old_name and not self._ensure_org_not_exists(new_name):
            raise ValueError("New organization name already exists")

        old_collection_name = org["collection_name"]
        new_collection_name = get_org_collection_name(new_name)

        try:
            # If collection name changed, copy docs then drop old
            if new_collection_name != old_collection_name:
                old_collection = db[old_collection_name]
                new_collection = db[new_collection_name]

                docs = list(old_collection.find({}))
                if docs:
                    # remove existing _id to avoid conflicts
                    for d in docs:
                        d.pop("_id", None)
                    new_collection.insert_many(docs)

                # drop old collection
                old_collection.drop()

            # Update org metadata
            self.orgs.update_one(
                {"_id": org["_id"]},
                {"$set": {
                    "organization_name": new_name,
                    "collection_name": new_collection_name
                }}
            )

            # Update admin (email + password)
            hashed = hash_password(new_password)
            self.admins.update_one(
                {"_id": org["admin_id"]},
                {"$set": {"email": new_email, "password": hashed}}
            )

            return True

        except errors.DuplicateKeyError as e:
            logger.exception("Duplicate key on update: %s", e)
            raise ValueError("Duplicate data found while updating")
        except Exception as e:
            logger.exception("Failed to update org %s -> %s : %s", old_name, new_name, e)
            raise ValueError("Failed to update organization: " + str(e))

    def delete_org(self, org_name: str) -> bool:
        org = self.orgs.find_one({"organization_name": org_name})
        if not org:
            raise ValueError("Organization not found")

        try:
            # Drop dynamic collection (no-op if not exists)
            db[org["collection_name"]].drop()

            # Delete admin and org metadata
            self.admins.delete_one({"_id": org["admin_id"]})
            self.orgs.delete_one({"_id": org["_id"]})
            return True
        except Exception as e:
            logger.exception("Failed to delete organization %s: %s", org_name, e)
            raise ValueError("Failed to delete organization: " + str(e))

