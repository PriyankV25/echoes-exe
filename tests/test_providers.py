"""
Tests for AI Provider Implementations and Factory
"""
import pytest
from unittest.mock import patch, MagicMock
from providers.base import BaseAIProvider
from providers.groq_provider import GroqProvider
from providers.ollama_provider import OllamaProvider
from providers.factory import ProviderFactory, HeuristicFallbackProvider


def test_groq_missing_key_validation():
    provider = GroqProvider(api_key="", model_name="llama-3.3-70b-versatile")
    val = provider.validate_connection()
    assert val["status"] is False
    assert "GROQ_API_KEY" in val["message"]


def test_ollama_unreachable_validation():
    # Test connection to unreachable port
    provider = OllamaProvider(base_url="http://127.0.0.1:59999", model_name="gemma3")
    val = provider.validate_connection()
    assert val["status"] is False
    assert "Could not connect to Ollama" in val["message"]


def test_provider_factory_fallback():
    prov = ProviderFactory.get_provider("heuristic")
    assert isinstance(prov, HeuristicFallbackProvider)
    info = prov.get_provider_info()
    assert info["id"] == "heuristic"
    gen = prov.generate("Tell me about this repo")
    assert "Heuristic Grounded Response" in gen


def test_groq_generation_mock():
    with patch("providers.groq_provider.Groq") as mock_groq_cls:
        mock_client = MagicMock()
        mock_completion = MagicMock()
        mock_choice = MagicMock()
        mock_choice.message.content = "[FACT] Created in 2016 [Source: commit:7190e45]."
        mock_completion.choices = [mock_choice]
        mock_client.chat.completions.create.return_value = mock_completion
        mock_groq_cls.return_value = mock_client

        provider = GroqProvider(api_key="mock_test_key", model_name="llama-3.3-70b-versatile")
        provider.client = mock_client

        output = provider.generate("When was this project created?")
        assert "[FACT]" in output
        assert "7190e45" in output


def test_ollama_generation_mock():
    with patch("requests.post") as mock_post:
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {"response": "[FACT] Final commit in 2017 [Source: commit:cf79ea5]."}
        mock_post.return_value = mock_resp

        provider = OllamaProvider(base_url="http://localhost:11434", model_name="gemma3")
        output = provider.generate("When did it stop receiving commits?")
        assert "2017" in output
