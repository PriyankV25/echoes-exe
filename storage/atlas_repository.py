"""
Echoes.exe — MongoDB Atlas Cloud Storage & Vector Search Repository
Integrates persistent cloud memory and semantic search with strict privacy consent controls.
"""
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
import pymongo
from pymongo.errors import ConnectionFailure, ConfigurationError, OperationFailure

from config.settings import settings


class CloudConsentRequiredError(Exception):
    """Raised when an attempt to upload repository data to Atlas occurs without explicit consent."""
    pass


class AtlasRepository:
    def __init__(self, uri: Optional[str] = None, db_name: Optional[str] = None):
        self.uri = (uri or settings.MONGODB_URI).strip()
        self.db_name = (db_name or settings.MONGODB_DB_NAME).strip()
        self._client: Optional[pymongo.MongoClient] = None
        self._db = None

    def _get_db(self):
        if not self.uri:
            raise ConfigurationError("MongoDB Atlas URI is not configured in environment.")
        if self._client is None:
            self._client = pymongo.MongoClient(self.uri, serverSelectionTimeoutMS=5000)
            self._db = self._client[self.db_name]
        return self._db

    def test_connection(self) -> Dict[str, Any]:
        """Validates Atlas connection and checks collection indices."""
        if not self.uri:
            return {
                "status": False,
                "message": "MongoDB Atlas URI is empty. Add MONGODB_URI to .env to enable cloud memory & vector search.",
                "database": self.db_name
            }
        try:
            db = self._get_db()
            # Send ping
            db.command("ping")
            collections = db.list_collection_names()
            return {
                "status": True,
                "message": f"Successfully connected to MongoDB Atlas database '{self.db_name}'.",
                "database": self.db_name,
                "collections": collections
            }
        except (ConnectionFailure, ConfigurationError) as e:
            return {
                "status": False,
                "message": f"Could not connect to MongoDB Atlas cluster: {str(e)}",
                "database": self.db_name
            }
        except Exception as e:
            return {
                "status": False,
                "message": f"Atlas connection error: {str(e)}",
                "database": self.db_name
            }

    def save_investigation(self, record: Dict[str, Any], user_consent: bool = False) -> str:
        """
        Saves investigation record to MongoDB Atlas.
        STRICT REQUIREMENT: Requires user_consent=True.
        """
        if not user_consent:
            raise CloudConsentRequiredError(
                "Explicit user consent is required before transmitting repository archives or metadata to MongoDB Atlas."
            )

        db = self._get_db()
        inv_id = record.get("id") or f"atlas_inv_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}"
        doc = {
            "_id": inv_id,
            "project_name": record.get("project_name", "Unknown"),
            "source_type": record.get("source_type", "local"),
            "url": record.get("url"),
            "health_score": record.get("health_score", 0),
            "primary_language": record.get("primary_language", "Unknown"),
            "created_at": record.get("created_at") or datetime.now(timezone.utc).isoformat(),
            "report": record.get("report", {}),
            "evidence_summary": {
                "total_files": record.get("evidence", {}).get("total_files", 0),
                "total_loc": record.get("evidence", {}).get("total_loc", 0),
                "git_available": record.get("evidence", {}).get("git_evidence", {}).get("available", False)
            }
        }
        db.investigations.replace_one({"_id": inv_id}, doc, upsert=True)

        # Store evidence chunks if present
        chunks = record.get("evidence", {}).get("evidence_chunks", [])
        if chunks:
            chunk_docs = []
            for c in chunks:
                chunk_docs.append({
                    "investigation_id": inv_id,
                    "chunk_id": c.get("chunk_id"),
                    "source_type": c.get("source_type"),
                    "source_path": c.get("source_path"),
                    "citation": c.get("citation"),
                    "category": c.get("category", "FACT"),
                    "content": c.get("content")
                })
            # Insert in batch, replace existing for this inv_id
            db.evidence_chunks.delete_many({"investigation_id": inv_id})
            db.evidence_chunks.insert_many(chunk_docs)

        return inv_id

    def list_investigations(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Lists cloud investigations."""
        db = self._get_db()
        cursor = db.investigations.find(
            {},
            {"_id": 1, "project_name": 1, "source_type": 1, "url": 1, "health_score": 1, "primary_language": 1, "created_at": 1}
        ).sort("created_at", -1).limit(limit)

        results = []
        for doc in cursor:
            results.append({
                "id": str(doc["_id"]),
                "project_name": doc.get("project_name"),
                "source_type": doc.get("source_type"),
                "url": doc.get("url"),
                "health_score": doc.get("health_score"),
                "primary_language": doc.get("primary_language"),
                "created_at": doc.get("created_at")
            })
        return results

    def get_investigation(self, inv_id: str) -> Optional[Dict[str, Any]]:
        """Retrieves investigation document from Atlas."""
        db = self._get_db()
        doc = db.investigations.find_one({"_id": inv_id})
        if not doc:
            return None
        doc["id"] = str(doc.pop("_id"))
        return doc

    def delete_investigation(self, inv_id: str) -> bool:
        """Removes investigation and chunks from Atlas."""
        db = self._get_db()
        res = db.investigations.delete_one({"_id": inv_id})
        db.evidence_chunks.delete_many({"investigation_id": inv_id})
        return res.deleted_count > 0

    def vector_search(self, inv_id: str, query_embedding: List[float], top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Executes an Atlas Vector Search pipeline over evidence_chunks.
        Requires an Atlas Vector Search index configured on collection 'evidence_chunks' named 'vector_index'.
        Falls back gracefully if index is not yet built.
        """
        db = self._get_db()
        try:
            pipeline = [
                {
                    "$vectorSearch": {
                        "index": "vector_index",
                        "path": "embedding",
                        "queryVector": query_embedding,
                        "numCandidates": top_k * 10,
                        "limit": top_k,
                        "filter": {"investigation_id": inv_id}
                    }
                },
                {
                    "$project": {
                        "_id": 0,
                        "chunk_id": 1,
                        "source_type": 1,
                        "source_path": 1,
                        "citation": 1,
                        "category": 1,
                        "content": 1,
                        "score": {"$meta": "vectorSearchScore"}
                    }
                }
            ]
            return list(db.evidence_chunks.aggregate(pipeline))
        except OperationFailure as e:
            # Vector search index missing on Atlas
            return []
