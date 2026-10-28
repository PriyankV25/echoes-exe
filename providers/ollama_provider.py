"""
Echoes.exe — Gemma through Ollama Provider Implementation
100% Local, Offline Inference with Google's Gemma models.
"""
import json
from typing import Generator, Dict, Any, Optional
import requests

from providers.base import BaseAIProvider
from config.settings import settings


class OllamaProvider(BaseAIProvider):
    def __init__(self, base_url: Optional[str] = None, model_name: Optional[str] = None):
        self.base_url = (base_url or settings.OLLAMA_BASE_URL).rstrip("/")
        super().__init__(model_name or settings.OLLAMA_MODEL)
        self.timeout = 90  # Local models may take longer to warm up

    def validate_connection(self) -> Dict[str, Any]:
        """Validates if Ollama service is reachable and if the target model is installed."""
        try:
            # 1. Check Ollama server status and available models
            resp = requests.get(f"{self.base_url}/api/tags", timeout=5)
            if resp.status_code == 200:
                data = resp.json()
                models = [m.get("name") for m in data.get("models", [])]
                
                # Check if requested model matches (exact or prefix like gemma3:latest)
                model_found = any(
                    self.model_name == m or m.startswith(f"{self.model_name}:")
                    for m in models
                )

                if model_found:
                    return {
                        "status": True,
                        "provider": "ollama",
                        "message": f"Connected to local Ollama. Model '{self.model_name}' is loaded and ready for private offline inference.",
                        "available_models": models,
                        "active_model": self.model_name
                    }
                else:
                    return {
                        "status": False,
                        "provider": "ollama",
                        "message": (
                            f"Ollama is running at {self.base_url}, but target model '{self.model_name}' is not downloaded. "
                            f"To install, open your terminal and run: `ollama run {self.model_name}`"
                        ),
                        "available_models": models,
                        "active_model": self.model_name
                    }
            else:
                return {
                    "status": False,
                    "provider": "ollama",
                    "message": f"Ollama service returned unexpected HTTP {resp.status_code}.",
                    "available_models": []
                }
        except requests.ConnectionError:
            return {
                "status": False,
                "provider": "ollama",
                "message": (
                    f"Could not connect to Ollama at {self.base_url}. "
                    "Make sure the Ollama application is running locally. "
                    "Download it from https://ollama.ai and start it."
                ),
                "available_models": []
            }
        except Exception as e:
            return {
                "status": False,
                "provider": "ollama",
                "message": f"Ollama connection check failed: {str(e)}",
                "available_models": []
            }

    def generate(self, prompt: str, system_prompt: Optional[str] = None, **kwargs) -> str:
        """Generates synchronous response from local Ollama model."""
        payload = {
            "model": self.model_name,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": kwargs.get("temperature", 0.6)
            }
        }
        if system_prompt:
            payload["system"] = system_prompt

        try:
            resp = requests.post(
                f"{self.base_url}/api/generate",
                json=payload,
                timeout=self.timeout
            )
            if resp.status_code == 200:
                return resp.json().get("response", "")
            else:
                raise RuntimeError(f"Ollama returned HTTP {resp.status_code}: {resp.text}")
        except requests.ConnectionError:
            raise RuntimeError(
                f"Cannot reach Ollama at {self.base_url}. Ensure Ollama is running and has model '{self.model_name}' installed."
            )
        except requests.Timeout:
            raise TimeoutError(f"Ollama generation timed out after {self.timeout}s.")
        except Exception as e:
            raise RuntimeError(f"Ollama call failed: {str(e)}")

    def stream(self, prompt: str, system_prompt: Optional[str] = None, **kwargs) -> Generator[str, None, None]:
        """Streams tokens from local Ollama model."""
        payload = {
            "model": self.model_name,
            "prompt": prompt,
            "stream": True,
            "options": {
                "temperature": kwargs.get("temperature", 0.6)
            }
        }
        if system_prompt:
            payload["system"] = system_prompt

        try:
            with requests.post(
                f"{self.base_url}/api/generate",
                json=payload,
                stream=True,
                timeout=self.timeout
            ) as resp:
                if resp.status_code != 200:
                    yield f"Error: Ollama returned HTTP {resp.status_code}"
                    return

                for line in resp.iter_lines():
                    if line:
                        chunk = json.loads(line.decode("utf-8"))
                        token = chunk.get("response", "")
                        if token:
                            yield token
                        if chunk.get("done", False):
                            break
        except requests.ConnectionError:
            yield f"\n[Connection Lost: Ollama daemon at {self.base_url} is not responding.]"
        except Exception as e:
            yield f"\n[Spectral Interruption: Ollama streaming error: {str(e)}]"

    def get_provider_info(self) -> Dict[str, Any]:
        return {
            "id": "ollama",
            "name": f"Gemma ({self.model_name}) via Ollama",
            "model": self.model_name,
            "base_url": self.base_url,
            "mode": "local_offline",
            "requires_key": False
        }
