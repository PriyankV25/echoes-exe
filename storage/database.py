"""
Echoes.exe — Storage Manager & Unified Gateway
Coordinates Local SQLite storage and MongoDB Atlas Cloud memory.
"""
from typing import Dict, Any, List, Optional

from config.settings import settings
from storage.local_repository import LocalStorageRepository
from storage.atlas_repository import AtlasRepository, CloudConsentRequiredError


class StorageManager:
    def __init__(self):
        self.local = LocalStorageRepository()
        self.atlas = AtlasRepository()

    def get_status(self) -> Dict[str, Any]:
        """Returns comprehensive storage configuration and connectivity status."""
        atlas_test = self.atlas.test_connection()
        return {
            "mode": settings.STORAGE_MODE,
            "local_ready": True,
            "local_db_path": str(settings.SQLITE_DB_PATH),
            "atlas_configured": bool(settings.MONGODB_URI.strip()),
            "atlas_connected": atlas_test.get("status", False),
            "atlas_message": atlas_test.get("message")
        }

    def save_investigation(
        self,
        record: Dict[str, Any],
        user_consent: bool = False,
        mode: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Saves investigation to Local SQLite (always) and MongoDB Atlas (if mode=atlas and consent=True).
        """
        chosen_mode = (mode or settings.STORAGE_MODE).lower()
        local_id = self.local.save_investigation(record)

        atlas_id = None
        atlas_error = None

        if chosen_mode == "atlas":
            if not user_consent:
                atlas_error = "Cloud consent toggle not enabled. Saved to local Memory Vault only."
            else:
                try:
                    atlas_id = self.atlas.save_investigation(record, user_consent=True)
                except Exception as e:
                    atlas_error = f"Atlas sync error: {str(e)}"

        return {
            "id": local_id,
            "atlas_id": atlas_id,
            "mode": chosen_mode,
            "atlas_error": atlas_error
        }

    def get_investigation(self, inv_id: str, mode: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Retrieves investigation from local or atlas storage."""
        chosen_mode = (mode or settings.STORAGE_MODE).lower()
        if chosen_mode == "atlas" and settings.MONGODB_URI:
            try:
                res = self.atlas.get_investigation(inv_id)
                if res:
                    return res
            except Exception:
                pass
        return self.local.get_investigation(inv_id)

    def list_investigations(self, mode: Optional[str] = None, limit: int = 50) -> List[Dict[str, Any]]:
        """Lists investigations from local or atlas storage."""
        chosen_mode = (mode or settings.STORAGE_MODE).lower()
        if chosen_mode == "atlas" and settings.MONGODB_URI:
            try:
                return self.atlas.list_investigations(limit=limit)
            except Exception:
                pass
        return self.local.list_investigations(limit=limit)

    def delete_investigation(self, inv_id: str, mode: Optional[str] = None) -> bool:
        """Deletes investigation across stores."""
        chosen_mode = (mode or settings.STORAGE_MODE).lower()
        if chosen_mode == "atlas" and settings.MONGODB_URI:
            try:
                self.atlas.delete_investigation(inv_id)
            except Exception:
                pass
        return self.local.delete_investigation(inv_id)

    def save_chat_message(self, inv_id: str, role: str, content: str):
        self.local.save_chat_message(inv_id, role, content)

    def get_chat_history(self, inv_id: str, limit: int = 20) -> List[Dict[str, str]]:
        return self.local.get_chat_history(inv_id, limit=limit)


db_manager = StorageManager()
