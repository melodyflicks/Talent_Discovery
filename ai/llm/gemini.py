from .base import LLMProvider

class GeminiProvider(LLMProvider):
    def __init__(self, api_key: str): self.api_key = api_key
    def generate(self, prompt: str) -> str:
        raise NotImplementedError("Gemini integration is planned for a later phase.")
