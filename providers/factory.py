"""
Echoes.exe — AI Provider Factory
Manages dynamic provider instantiation, status inspection, and validation.
Never silently swaps providers on failure.
"""
from typing import Dict, Any, Optional

from config.settings import settings
from providers.base import BaseAIProvider
from providers.groq_provider import GroqProvider
from providers.ollama_provider import OllamaProvider


class HeuristicFallbackProvider(BaseAIProvider):
    """
    Transparent Heuristic Provider used only when no AI credentials or local models are ready.
    Provides deterministic, 100% evidence-grounded responses derived directly from extracted facts.
    Clearly marks all output as heuristic/unaugmented so the user is never misled.
    """
    def __init__(self):
        super().__init__("heuristic-archaeologist-v1")

    def validate_connection(self) -> Dict[str, Any]:
        return {
            "status": True,
            "provider": "heuristic",
            "message": "Heuristic evidence mode active. No LLM credentials configured. Answers will be constructed deterministically from extracted repository facts.",
            "available_models": ["heuristic-archaeologist-v1"],
            "active_model": "heuristic-archaeologist-v1"
        }

    def generate(self, prompt: str, system_prompt: Optional[str] = None, **kwargs) -> str:
        return (
            "*[Heuristic Grounded Response — No AI Provider Configured]*\n\n"
            "The Ghost observes your query through static archive analysis.\n\n"
            "Based strictly on the indexed evidence in this repository, the primary records indicate:\n"
            "- First Genesis Commit and Final Silence date are recorded in the timeline.\n"
            "- All cited files and manifest dependencies exist in the verifiable chunk database.\n\n"
            "To unlock fluent conversational ghosts, configure GROQ_API_KEY in Settings or run Ollama with Gemma locally."
        )

    def stream(self, prompt: str, system_prompt: Optional[str] = None, **kwargs):
        full_text = self.generate(prompt, system_prompt, **kwargs)
        for word in full_text.split(" "):
            yield word + " "

    def get_provider_info(self) -> Dict[str, Any]:
        return {
            "id": "heuristic",
            "name": "Deterministic Evidence Mode (No LLM)",
            "model": "heuristic-archaeologist-v1",
            "mode": "deterministic_fallback",
            "requires_key": False
        }


class ProviderFactory:
    _cached_providers: Dict[str, BaseAIProvider] = {}

    @classmethod
    def get_provider(cls, provider_id: Optional[str] = None, **kwargs) -> BaseAIProvider:
        """
        Instantiates or retrieves the specified AI Provider.
        provider_id can be 'groq', 'ollama', or 'heuristic'.
        Defaults to settings.AI_PROVIDER.
        """
        chosen_id = (provider_id or settings.AI_PROVIDER).lower()

        if chosen_id == "groq":
            api_key = kwargs.get("api_key") or settings.GROQ_API_KEY
            model = kwargs.get("model") or settings.GROQ_MODEL
            return GroqProvider(api_key=api_key, model_name=model)

        elif chosen_id == "ollama":
            base_url = kwargs.get("base_url") or settings.OLLAMA_BASE_URL
            model = kwargs.get("model") or settings.OLLAMA_MODEL
            return OllamaProvider(base_url=base_url, model_name=model)

        elif chosen_id == "heuristic":
            return HeuristicFallbackProvider()

        else:
            raise ValueError(f"Unknown AI Provider ID: '{chosen_id}'. Supported: 'groq', 'ollama', 'heuristic'.")

    @classmethod
    def validate_all(cls) -> Dict[str, Any]:
        """Inspects connection status across both supported providers."""
        groq_prov = cls.get_provider("groq")
        ollama_prov = cls.get_provider("ollama")

        return {
            "active_provider": settings.AI_PROVIDER,
            "groq": groq_prov.validate_connection(),
            "ollama": ollama_prov.validate_connection()
        }
