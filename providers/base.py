"""
Echoes.exe — Base AI Provider Abstract Interface
"""
from abc import ABC, abstractmethod
from typing import Generator, Dict, Any, Optional


class BaseAIProvider(ABC):
    """Abstract Base Class for all AI model providers."""

    def __init__(self, model_name: str):
        self.model_name = model_name

    @abstractmethod
    def generate(self, prompt: str, system_prompt: Optional[str] = None, **kwargs) -> str:
        """Generates a complete response synchronously."""
        pass

    @abstractmethod
    def stream(self, prompt: str, system_prompt: Optional[str] = None, **kwargs) -> Generator[str, None, None]:
        """Streams response tokens as they are generated."""
        pass

    @abstractmethod
    def validate_connection(self) -> Dict[str, Any]:
        """
        Validates connectivity, credentials, and model availability.
        Returns: { "status": bool, "message": str, "available_models": list }
        """
        pass

    @abstractmethod
    def get_provider_info(self) -> Dict[str, Any]:
        """Returns safe provider metadata for UI display."""
        pass
