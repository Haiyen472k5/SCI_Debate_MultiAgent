"""Abstract LLM interface.

Mọi backend (Ollama, OpenAI, OpenRouter, ...) phải implement BaseLLM.
Agent code chỉ gọi qua interface này, không phụ thuộc backend cụ thể.
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class LLMResponse:
    """Kết quả trả về từ LLM."""
    content: str
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    model: str = ""


class BaseLLM(ABC):
    """Abstract LLM backend.

    Các method bắt buộc implement:
        - generate(messages, **kwargs) -> LLMResponse
    """

    def __init__(self, model: str, temperature: float = 0.0, max_tokens: int = 1024):
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens

    @abstractmethod
    def generate(self, messages: list[dict], **kwargs) -> LLMResponse:
        """Sinh response từ messages.

        Args:
            messages: list dict dạng [{"role": "user", "content": "..."}]
            **kwargs: override temperature, max_tokens nếu cần

        Returns:
            LLMResponse
        """
        pass

    def __repr__(self):
        return f"{self.__class__.__name__}(model={self.model})"