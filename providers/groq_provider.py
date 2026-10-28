"""
Echoes.exe — Groq API Provider Implementation
High-speed hosted inference with models like Llama 3.3 70B Versatile.
"""
from typing import Generator, Dict, Any, Optional
import httpx
from groq import Groq, AuthenticationError, RateLimitError, APIConnectionError, APIStatusError

from providers.base import BaseAIProvider
from config.settings import settings


class GroqProvider(BaseAIProvider):
    def __init__(self, api_key: Optional[str] = None, model_name: Optional[str] = None):
        self.api_key = (api_key or settings.GROQ_API_KEY).strip()
        super().__init__(model_name or settings.GROQ_MODEL)
        self.client = Groq(api_key=self.api_key) if self.api_key else None

    def validate_connection(self) -> Dict[str, Any]:
        """Checks if Groq API key is set and connects successfully."""
        if not self.api_key:
            return {
                "status": False,
                "provider": "groq",
                "message": "Groq API key is not configured. Add GROQ_API_KEY to .env or switch to Ollama for local offline inference.",
                "available_models": []
            }

        try:
            # Query models endpoint to test key validity
            models_response = self.client.models.list()
            model_ids = [m.id for m in models_response.data]
            model_exists = self.model_name in model_ids

            return {
                "status": True,
                "provider": "groq",
                "message": f"Connected to Groq successfully. Target model '{self.model_name}' {'is ready' if model_exists else 'not found in list, will attempt default'}.",
                "available_models": [m for m in model_ids if "llama" in m or "mixtral" in m or "gemma" in m][:10],
                "active_model": self.model_name
            }
        except AuthenticationError:
            return {
                "status": False,
                "provider": "groq",
                "message": "Groq Authentication Failed: Invalid or expired API key. Verify GROQ_API_KEY.",
                "available_models": []
            }
        except RateLimitError:
            return {
                "status": False,
                "provider": "groq",
                "message": "Groq API rate limit reached. Please wait a moment or use Gemma via Ollama locally.",
                "available_models": []
            }
        except (APIConnectionError, httpx.RequestError) as e:
            return {
                "status": False,
                "provider": "groq",
                "message": f"Network error connecting to Groq API: {str(e)}",
                "available_models": []
            }
        except Exception as e:
            return {
                "status": False,
                "provider": "groq",
                "message": f"Groq error: {str(e)}",
                "available_models": []
            }

    def generate(self, prompt: str, system_prompt: Optional[str] = None, **kwargs) -> str:
        """Synchronously generates a completion from Groq."""
        if not self.api_key or not self.client:
            raise ValueError(
                "Groq API Key missing. Set GROQ_API_KEY in server environment or choose Ollama in Settings."
            )

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        temperature = kwargs.get("temperature", 0.6)
        max_tokens = kwargs.get("max_tokens", 2048)

        try:
            completion = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            return completion.choices[0].message.content or ""
        except APIStatusError as e:
            raise RuntimeError(f"Groq generation failed (HTTP {e.status_code}): {e.message}")
        except Exception as e:
            raise RuntimeError(f"Groq API call failed: {str(e)}")

    def stream(self, prompt: str, system_prompt: Optional[str] = None, **kwargs) -> Generator[str, None, None]:
        """Streams token response chunks from Groq."""
        if not self.api_key or not self.client:
            yield "Error: Groq API Key is missing. Configure GROQ_API_KEY in .env or switch to Ollama."
            return

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        temperature = kwargs.get("temperature", 0.6)
        max_tokens = kwargs.get("max_tokens", 2048)

        try:
            stream_resp = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=True
            )
            for chunk in stream_resp:
                if chunk.choices and chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
        except Exception as e:
            yield f"\n[Spectral Interruption: Groq streaming error: {str(e)}]"

    def get_provider_info(self) -> Dict[str, Any]:
        return {
            "id": "groq",
            "name": "Groq API (Hosted AI)",
            "model": self.model_name,
            "is_configured": bool(self.api_key),
            "mode": "cloud_hosted",
            "requires_key": True
        }
