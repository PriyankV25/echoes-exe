"""
Echoes.exe — Configuration and Environment Settings
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file if present
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

class Settings:
    # Application Info
    APP_NAME: str = "Echoes.exe"
    TAGLINE: str = "Every abandoned project has a last known voice."
    VERSION: str = "1.0.0"
    SECRET_KEY: str = os.getenv("SECRET_KEY", "ghost-in-the-machine-echoes-2026-secret-key")
    DEBUG: bool = os.getenv("FLASK_DEBUG", "0").lower() in ("1", "true", "yes")
    PORT: int = int(os.getenv("PORT", 5000))

    # Base Paths
    BASE_DIR: Path = BASE_DIR
    DATA_DIR: Path = BASE_DIR / "data"
    SAMPLES_DIR: Path = BASE_DIR / "samples"
    TEMP_DIR: Path = BASE_DIR / "data" / "temp"

    # AI Provider Settings
    AI_PROVIDER: str = os.getenv("AI_PROVIDER", "groq").lower()
    
    # Groq Settings
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    GROQ_MODEL: str = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
    
    # Ollama Settings
    OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434").rstrip("/")
    OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "gemma3")

    # Storage Settings
    STORAGE_MODE: str = os.getenv("STORAGE_MODE", "local").lower()  # 'local' or 'atlas'
    MONGODB_URI: str = os.getenv("MONGODB_URI", "")
    MONGODB_DB_NAME: str = os.getenv("MONGODB_DB_NAME", "echoes_vault")
    SQLITE_DB_PATH: Path = DATA_DIR / "echoes.db"

    # External Integrations
    SERPAPI_API_KEY: str = os.getenv("SERPAPI_API_KEY", "")
    SENTRY_DSN: str = os.getenv("SENTRY_DSN", "")
    ELEVENLABS_API_KEY: str = os.getenv("ELEVENLABS_API_KEY", "")
    ELEVENLABS_VOICE_ID: str = os.getenv("ELEVENLABS_VOICE_ID", "pNInz6obpgDQGcFmaJgB")

    # Limits & Security
    MAX_UPLOAD_SIZE_MB: int = int(os.getenv("MAX_UPLOAD_SIZE_MB", 30))
    MAX_CONTENT_LENGTH: int = MAX_UPLOAD_SIZE_MB * 1024 * 1024
    ALLOWED_EXTENSIONS: set = {".zip", ".tar.gz", ".tar"}
    GIT_CLONE_DEPTH: int = int(os.getenv("GIT_CLONE_DEPTH", 100))
    GIT_TIMEOUT_SECONDS: int = int(os.getenv("GIT_TIMEOUT_SECONDS", 60))

    @classmethod
    def ensure_directories(cls):
        """Ensure all required runtime directories exist."""
        cls.DATA_DIR.mkdir(parents=True, exist_ok=True)
        cls.SAMPLES_DIR.mkdir(parents=True, exist_ok=True)
        cls.TEMP_DIR.mkdir(parents=True, exist_ok=True)

    @classmethod
    def get_public_config(cls) -> dict:
        """Returns safe, non-sensitive configuration details for the frontend UI."""
        return {
            "app_name": cls.APP_NAME,
            "tagline": cls.TAGLINE,
            "version": cls.VERSION,
            "ai_provider": cls.AI_PROVIDER,
            "groq_configured": bool(cls.GROQ_API_KEY.strip()),
            "groq_model": cls.GROQ_MODEL,
            "ollama_base_url": cls.OLLAMA_BASE_URL,
            "ollama_model": cls.OLLAMA_MODEL,
            "storage_mode": cls.STORAGE_MODE,
            "atlas_configured": bool(cls.MONGODB_URI.strip()),
            "serpapi_configured": bool(cls.SERPAPI_API_KEY.strip()),
            "sentry_configured": bool(cls.SENTRY_DSN.strip()),
            "elevenlabs_configured": bool(cls.ELEVENLABS_API_KEY.strip()),
            "max_upload_size_mb": cls.MAX_UPLOAD_SIZE_MB,
        }

settings = Settings()
settings.ensure_directories()
