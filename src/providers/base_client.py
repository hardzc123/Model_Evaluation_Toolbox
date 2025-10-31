"""Base client interface for all model providers."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from pydantic import BaseModel


class ChatMessage(BaseModel):
    """Represents a chat message."""

    role: str  # system, user, assistant
    content: str


class UsageStats(BaseModel):
    """Token usage statistics."""

    prompt_tokens: int
    completion_tokens: int
    total_tokens: int


class ChatResponse(BaseModel):
    """Response from a chat completion."""

    content: str
    model: str
    usage: UsageStats
    finish_reason: Optional[str] = None
    raw_response: Optional[Dict[str, Any]] = None


class BaseClient(ABC):
    """Abstract base class for all model provider clients."""

    def __init__(
        self,
        api_key: str,
        base_url: Optional[str] = None,
        timeout: float = 60.0,
        max_retries: int = 3,
    ):
        """Initialize the client.

        Args:
            api_key: API key for authentication
            base_url: Optional custom base URL
            timeout: Request timeout in seconds
            max_retries: Maximum number of retry attempts
        """
        self.api_key = api_key
        self.base_url = base_url
        self.timeout = timeout
        self.max_retries = max_retries

    @abstractmethod
    async def chat_completion(
        self,
        messages: List[ChatMessage],
        model: str,
        temperature: float = 1.0,
        max_tokens: Optional[int] = None,
        **kwargs,
    ) -> ChatResponse:
        """Generate a chat completion.

        Args:
            messages: List of chat messages
            model: Model identifier
            temperature: Sampling temperature (0-2)
            max_tokens: Maximum tokens to generate
            **kwargs: Additional provider-specific parameters

        Returns:
            ChatResponse with generated content and usage stats
        """
        pass

    @abstractmethod
    async def chat_completion_sync(
        self,
        messages: List[ChatMessage],
        model: str,
        temperature: float = 1.0,
        max_tokens: Optional[int] = None,
        **kwargs,
    ) -> ChatResponse:
        """Synchronous version of chat_completion.

        Args:
            messages: List of chat messages
            model: Model identifier
            temperature: Sampling temperature (0-2)
            max_tokens: Maximum tokens to generate
            **kwargs: Additional provider-specific parameters

        Returns:
            ChatResponse with generated content and usage stats
        """
        pass

    @abstractmethod
    def count_tokens(self, text: str, model: str) -> int:
        """Count tokens in text for a specific model.

        Args:
            text: Text to count tokens for
            model: Model identifier

        Returns:
            Number of tokens
        """
        pass

    def calculate_cost(
        self,
        usage: UsageStats,
        model: str,
        pricing: Dict[str, float]
    ) -> float:
        """Calculate cost based on usage and pricing.

        Args:
            usage: Token usage statistics
            model: Model identifier
            pricing: Pricing dict with input_per_1k_tokens and output_per_1k_tokens

        Returns:
            Total cost in USD
        """
        input_cost = (usage.prompt_tokens / 1000) * pricing.get("input_per_1k_tokens", 0)
        output_cost = (usage.completion_tokens / 1000) * pricing.get("output_per_1k_tokens", 0)
        return input_cost + output_cost
