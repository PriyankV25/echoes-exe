"""
Echoes.exe — Local SQLite Storage Repository
Persistent Memory Vault for investigations and conversation history with zero cloud setup.
"""
import sqlite3
import json
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from pathlib import Path

from config.settings import settings


class LocalStorageRepository:
    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = db_path or settings.SQLITE_DB_PATH
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _get_connection(self):
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        """Creates local database schema if not already initialized."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS investigations (
                    id TEXT PRIMARY KEY,
                    project_name TEXT NOT NULL,
                    source_type TEXT NOT NULL,
                    url TEXT,
                    health_score INTEGER,
                    primary_language TEXT,
                    created_at TEXT NOT NULL,
                    report_json TEXT NOT NULL,
                    evidence_json TEXT NOT NULL
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS chat_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    investigation_id TEXT NOT NULL,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    FOREIGN KEY (investigation_id) REFERENCES investigations(id) ON DELETE CASCADE
                )
            """)
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_inv_name ON investigations(project_name)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_chat_inv ON chat_history(investigation_id)")
            conn.commit()

    def save_investigation(self, record: Dict[str, Any]) -> str:
        """Saves or updates an investigation record in local SQLite."""
        inv_id = record.get("id") or f"inv_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}"
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO investigations (
                    id, project_name, source_type, url, health_score,
                    primary_language, created_at, report_json, evidence_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                inv_id,
                record.get("project_name", "Unknown"),
                record.get("source_type", "local"),
                record.get("url"),
                record.get("health_score", 0),
                record.get("primary_language", "Unknown"),
                record.get("created_at") or datetime.now(timezone.utc).isoformat(),
                json.dumps(record.get("report", {})),
                json.dumps(record.get("evidence", {}))
            ))
            conn.commit()
        return inv_id

    def get_investigation(self, inv_id: str) -> Optional[Dict[str, Any]]:
        """Retrieves single investigation with parsed JSON data."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM investigations WHERE id = ?", (inv_id,))
            row = cursor.fetchone()
            if not row:
                return None
            return {
                "id": row["id"],
                "project_name": row["project_name"],
                "source_type": row["source_type"],
                "url": row["url"],
                "health_score": row["health_score"],
                "primary_language": row["primary_language"],
                "created_at": row["created_at"],
                "report": json.loads(row["report_json"]),
                "evidence": json.loads(row["evidence_json"])
            }

    def list_investigations(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Lists saved investigations ordered by most recent."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, project_name, source_type, url, health_score, primary_language, created_at
                FROM investigations
                ORDER BY created_at DESC
                LIMIT ?
            """, (limit,))
            rows = cursor.fetchall()
            return [dict(row) for row in rows]

    def delete_investigation(self, inv_id: str) -> bool:
        """Deletes investigation and its chat messages."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM investigations WHERE id = ?", (inv_id,))
            cursor.execute("DELETE FROM chat_history WHERE investigation_id = ?", (inv_id,))
            conn.commit()
            return cursor.rowcount > 0

    def save_chat_message(self, inv_id: str, role: str, content: str) -> None:
        """Appends a chat message to the investigation's conversation log."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO chat_history (investigation_id, role, content, timestamp)
                VALUES (?, ?, ?, ?)
            """, (
                inv_id,
                role,
                content,
                datetime.now(timezone.utc).isoformat()
            ))
            conn.commit()

    def get_chat_history(self, inv_id: str, limit: int = 20) -> List[Dict[str, str]]:
        """Fetches chronological conversation history for an investigation."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT role, content, timestamp
                FROM chat_history
                WHERE investigation_id = ?
                ORDER BY id ASC
                LIMIT ?
            """, (inv_id, limit))
            rows = cursor.fetchall()
            return [{"role": r["role"], "content": r["content"], "timestamp": r["timestamp"]} for r in rows]
