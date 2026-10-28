"""
Tests for Local SQLite and MongoDB Atlas Storage Repositories
"""
import pytest
from pathlib import Path
from storage.local_repository import LocalStorageRepository
from storage.atlas_repository import AtlasRepository, CloudConsentRequiredError
from storage.database import StorageManager


def test_local_sqlite_crud(tmp_path):
    db_file = tmp_path / "test_echoes.db"
    repo = LocalStorageRepository(db_path=db_file)

    sample_record = {
        "id": "test_inv_001",
        "project_name": "legacy-sample",
        "source_type": "sample",
        "health_score": 85,
        "primary_language": "Python",
        "report": {"project_name": "legacy-sample", "summary": "test"},
        "evidence": {"total_files": 12}
    }

    # Save
    inv_id = repo.save_investigation(sample_record)
    assert inv_id == "test_inv_001"

    # Get
    fetched = repo.get_investigation("test_inv_001")
    assert fetched is not None
    assert fetched["project_name"] == "legacy-sample"
    assert fetched["health_score"] == 85
    assert fetched["report"]["summary"] == "test"

    # Chat history
    repo.save_chat_message("test_inv_001", "user", "Hello ghost")
    repo.save_chat_message("test_inv_001", "assistant", "I remember the commits")
    history = repo.get_chat_history("test_inv_001")
    assert len(history) == 2
    assert history[0]["role"] == "user"

    # List
    all_invs = repo.list_investigations()
    assert len(all_invs) >= 1

    # Delete
    deleted = repo.delete_investigation("test_inv_001")
    assert deleted is True
    assert repo.get_investigation("test_inv_001") is None


def test_atlas_privacy_consent_guard():
    atlas_repo = AtlasRepository(uri="mongodb://dummy", db_name="test_vault")
    sample_record = {"project_name": "secret-repo"}

    # Attempting to save without explicit user consent must raise CloudConsentRequiredError
    with pytest.raises(CloudConsentRequiredError):
        atlas_repo.save_investigation(sample_record, user_consent=False)
