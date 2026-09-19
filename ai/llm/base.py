from abc import ABC, abstractmethod

class LLMProvider(ABC):
    """Minimal contract implemented by configured LLM providers."""
    @abstractmethod
    def generate(self, prompt: str) -> str:
        raise NotImplementedError
