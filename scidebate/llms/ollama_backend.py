"""Ollama backend.

Ollama có API tương thích OpenAI, nên dùng openai SDK gọi tới
http://localhost:11434/v1 với api_key giả.
"""

from openai import OpenAI
from .base import BaseLLM, LLMResponse

class OllamaLLM(BaseLLM):
    """Ollama backend."""

    def __init__ (
        self,
        model: str = "qwen2.5:3b",
        temperature: float = 0.0,
        max_tokens: int = 1024,
        base_url: str = "http://localhost:11434/v1",
    ):
        super().__init__(model=model, temperature=temperature, max_tokens=max_tokens)
        self.base_url = base_url
        self._client = OpenAI(base_url=self.base_url, api_key="ollama")
    
    def generate(self, messages: list[dict], **kwargs) -> LLMResponse:
        # Cho phép override temperature/max_tokens per-call
        temperature = kwargs.get("temperature", self.temperature)
        max_tokens = kwargs.get("max_tokens", self.max_tokens)

        response = self._client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )

        usage = response.usage
        return LLMResponse(
            content=response.choices[0].message.content or "",
            prompt_tokens=usage.prompt_tokens if usage else 0,
            completion_tokens=usage.completion_tokens if usage else 0,
            total_tokens=usage.total_tokens if usage else 0,
            model=self.model,
        )
