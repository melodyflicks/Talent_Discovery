import json
import re
from typing import Optional, Type, TypeVar
from pydantic import BaseModel, ValidationError
from .base import LLMProvider
from .gemini import GeminiProvider
from .openai import OpenAIProvider

T = TypeVar("T", bound=BaseModel)


class LLMService:
    """Central service for LLM calls with Pydantic JSON validation and retry/repair."""

    def __init__(self, provider: str = "gemini", gemini_api_key: str = "", openai_api_key: str = ""):
        self.providers = {
            "gemini": GeminiProvider(gemini_api_key),
            "openai": OpenAIProvider(openai_api_key),
        }
        self.provider_name = provider.lower()
        self.provider: LLMProvider = self.providers.get(self.provider_name, self.providers["gemini"])

    def is_available(self) -> bool:
        return self.provider.is_available()

    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> Optional[str]:
        if not self.is_available():
            return None
        try:
            return self.provider.generate(prompt, system_prompt=system_prompt)
        except Exception:
            return None

    def generate_json(
        self,
        prompt: str,
        schema_cls: Type[T],
        system_prompt: Optional[str] = None,
        max_retries: int = 2,
    ) -> Optional[T]:
        """Generate structured JSON matching Pydantic schema with retry/repair."""
        if not self.is_available():
            return None

        schema_json = schema_cls.model_json_schema()
        json_instruction = (
            f"\n\nRespond ONLY with valid JSON matching this schema:\n{json.dumps(schema_json, indent=2)}\n"
            "Do not include any intro text, conversational filler, or explanations outside the JSON object."
        )

        full_prompt = prompt + json_instruction

        for attempt in range(max_retries + 1):
            raw_response = self.generate(full_prompt, system_prompt=system_prompt)
            if not raw_response:
                return None

            cleaned_json = self._extract_json_str(raw_response)
            try:
                parsed_dict = json.loads(cleaned_json)
                return schema_cls.model_validate(parsed_dict)
            except (json.JSONDecodeError, ValidationError) as e:
                if attempt < max_retries:
                    # Repair prompt for next retry
                    full_prompt = (
                        f"Your previous response failed validation with error: {str(e)}.\n"
                        f"Previous invalid output was:\n{cleaned_json}\n"
                        f"Please fix all errors and output valid JSON matching:\n{json.dumps(schema_json)}"
                    )
                else:
                    return None
        return None

    @staticmethod
    def _extract_json_str(text: str) -> str:
        """Extract clean JSON string from raw text response."""
        text = text.strip()
        # Look for markdown JSON block ```json ... ```
        match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", text, re.IGNORECASE)
        if match:
            return match.group(1).strip()
        # Look for JSON object or array bounds
        obj_match = re.search(r"(\{[\s\S]*\}|\[[\s\S]*\])", text)
        if obj_match:
            return obj_match.group(1).strip()
        return text
