"""
Echoes.exe — Spectral Voice Narration via ElevenLabs
Optional audio synthesis for 'The Last Transmission' digital obituary.
Strictly disabled by default, zero autoplay, safe backend proxy.
"""
from typing import Dict, Any, Optional
import requests

from config.settings import settings


class VoiceEngine:
    BASE_URL = "https://api.elevenlabs.io/v1"

    @classmethod
    def get_status(cls) -> Dict[str, Any]:
        """Checks if ElevenLabs voice synthesis is enabled."""
        has_key = bool(settings.ELEVENLABS_API_KEY.strip())
        return {
            "available": has_key,
            "voice_id": settings.ELEVENLABS_VOICE_ID,
            "status": "ready" if has_key else "unconfigured",
            "message": "Voice synthesis ready." if has_key else "Set ELEVENLABS_API_KEY in .env to enable ghost narration."
        }

    @classmethod
    def synthesize_speech(cls, text: str) -> Dict[str, Any]:
        """
        Synthesizes speech using ElevenLabs Text-to-Speech API.
        Returns audio bytes or error status.
        """
        api_key = settings.ELEVENLABS_API_KEY.strip()
        if not api_key:
            return {
                "success": False,
                "error": "ElevenLabs API key is not configured.",
                "audio_bytes": None
            }

        voice_id = settings.ELEVENLABS_VOICE_ID
        url = f"{cls.BASE_URL}/text-to-speech/{voice_id}"

        headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": api_key
        }

        # Truncate to safe length to prevent timeout or credit drain
        safe_text = text[:800]

        payload = {
            "text": safe_text,
            "model_id": "eleven_monolingual_v1",
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.75
            }
        }

        try:
            resp = requests.post(url, json=payload, headers=headers, timeout=20)
            if resp.status_code == 200:
                return {
                    "success": True,
                    "audio_bytes": resp.content,
                    "content_type": "audio/mpeg"
                }
            else:
                return {
                    "success": False,
                    "error": f"ElevenLabs API returned HTTP {resp.status_code}: {resp.text[:200]}",
                    "audio_bytes": None
                }
        except requests.RequestException as e:
            return {
                "success": False,
                "error": f"Failed to contact ElevenLabs: {str(e)}",
                "audio_bytes": None
            }
