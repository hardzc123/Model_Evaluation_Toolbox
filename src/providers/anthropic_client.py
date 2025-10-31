"""Anthropic API client implementation."""

from typing import List, Optional

import anthropic
from anthropic import AsyncAnthropic, Anthropic

from ..utils import get_logger, retry_with_backoff, count_tokens
from .base_client import BaseClient, ChatMessage, ChatResponse, UsageStats

logger = get_logger(__name__)


class AnthropicClient(BaseClient):
    """Client for Anthropic (Claude) API."""

    def __init__(
        self,
        api_key: str,
        base_url: Optional[str] = None,
        timeout: float = 60.0,
        max_retries: int = 3,
    ):
        """Initialize Anthropic client.

        Args:
            api_key: Anthropic API key
            base_url: Optional custom base URL
            timeout: Request timeout in seconds
            max_retries: Maximum retry attempts
        """
        super().__init__(api_key, base_url, timeout, max_retries)

        # Initialize async client
        self.async_client = AsyncAnthropic(
            api_key=api_key,
            base_url=base_url,
            timeout=timeout,
            max_retries=max_retries,
        )

        # Initialize sync client
        self.sync_client = Anthropic(
            api_key=api_key,
            base_url=base_url,
            timeout=timeout,
            max_retries=max_retries,
        )

    @retry_with_backoff(max_attempts=3)
    async def chat_completion(
        self,
        messages: List[ChatMessage],
        model: str,
        temperature: float = 1.0,
        max_tokens: Optional[int] = None,
        **kwargs,
    ) -> ChatResponse:
        """Generate a chat completion using Anthropic API.

        Args:
            messages: List of chat messages
            model: Anthropic model identifier
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate (required for Anthropic)
            **kwargs: Additional Anthropic parameters

        Returns:
            ChatResponse with generated content
        """
        # Separate system message if present
        system_message = None
        anthropic_messages = []

        for msg in messages:
            if msg.role == "system":
                system_message = msg.content
            else:
                anthropic_messages.append({
                    "role": msg.role,
                    "content": msg.content
                })

        # Default max_tokens if not provided (required by Anthropic)
        if max_tokens is None:
            max_tokens = 4096

        try:
            params = {
                "model": model,
                "messages": anthropic_messages,
                "temperature": temperature,
                "max_tokens": max_tokens,
                **kwargs,
            }

            if system_message:
                params["system"] = system_message

            response = await self.async_client.messages.create(**params)

            usage = UsageStats(
                prompt_tokens=response.usage.input_tokens,
                completion_tokens=response.usage.output_tokens,
                total_tokens=response.usage.input_tokens + response.usage.output_tokens,
            )

            return ChatResponse(
                content=response.content[0].text,
                model=response.model,
                usage=usage,
                finish_reason=response.stop_reason,
                raw_response=response.model_dump(),
            )

        except Exception as e:
            logger.error(f"Anthropic API error: {str(e)}", model=model)
            raise

    @retry_with_backoff(max_attempts=3)
    def chat_completion_sync(
        self,
        messages: List[ChatMessage],
        model: str,
        temperature: float = 1.0,
        max_tokens: Optional[int] = None,
        **kwargs,
    ) -> ChatResponse:
        """Synchronous chat completion.

        Args:
            messages: List of chat messages
            model: Anthropic model identifier
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            **kwargs: Additional Anthropic parameters

        Returns:
            ChatResponse with generated content
        """
        # Separate system message if present
        system_message = None
        anthropic_messages = []

        for msg in messages:
            if msg.role == "system":
                system_message = msg.content
            else:
                anthropic_messages.append({
                    "role": msg.role,
                    "content": msg.content
                })

        # Default max_tokens if not provided
        if max_tokens is None:
            max_tokens = 4096

        try:
            params = {
                "model": model,
                "messages": anthropic_messages,
                "temperature": temperature,
                "max_tokens": max_tokens,
                **kwargs,
            }

            if system_message:
                params["system"] = system_message

            response = self.sync_client.messages.create(**params)

            usage = UsageStats(
                prompt_tokens=response.usage.input_tokens,
                completion_tokens=response.usage.output_tokens,
                total_tokens=response.usage.input_tokens + response.usage.output_tokens,
            )

            return ChatResponse(
                content=response.content[0].text,
                model=response.model,
                usage=usage,
                finish_reason=response.stop_reason,
                raw_response=response.model_dump(),
            )

        except Exception as e:
            logger.error(f"Anthropic API error: {str(e)}", model=model)
            raise

    def count_tokens(self, text: str, model: str) -> int:
        """Count tokens for Anthropic models.

        Args:
            text: Text to count tokens for
            model: Model identifier

        Returns:
            Number of tokens
        """
        return count_tokens(text, model, provider="anthropic")
