from .gemini import GeminiProvider
from .openai import OpenAIProvider

class LLMService:
    """Selects a provider without leaking provider details to domain services."""
    def __init__(self, provider: str, gemini_api_key: str = "", openai_api_key: str = ""):
        providers = {"gemini": GeminiProvider(gemini_api_key), "openai": OpenAIProvider(openai_api_key)}
        if provider not in providers: raise ValueError(f"Unsupported LLM provider: {provider}")
        self.provider = providers[provider]
    def generate(self, prompt: str) -> str: return self.provider.generate(prompt)
