"""OpenAI API client implementation."""

import asyncio
from typing import List, Optional

import openai
from openai import AsyncOpenAI, OpenAI

from ..utils import get_logger, retry_with_backoff, count_tokens
from .base_client import BaseClient, ChatMessage, ChatResponse, UsageStats

logger = get_logger(__name__)


class OpenAIClient(BaseClient):
    """Client for OpenAI API."""

    def __init__(
        self,
        api_key: str,
        organization_id: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout: float = 60.0,
        max_retries: int = 3,
    ):
        """Initialize OpenAI client.

        Args:
            api_key: OpenAI API key
            organization_id: Optional organization ID
            base_url: Optional custom base URL
            timeout: Request timeout in seconds
            max_retries: Maximum retry attempts
        """
        super().__init__(api_key, base_url, timeout, max_retries)
        self.organization_id = organization_id

        # Initialize async client
        self.async_client = AsyncOpenAI(
            api_key=api_key,
            organization=organization_id,
            base_url=base_url,
            timeout=timeout,
            max_retries=max_retries,
        )

        # Initialize sync client
        self.sync_client = OpenAI(
            api_key=api_key,
            organization=organization_id,
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
        """Generate a chat completion using OpenAI API.

        Args:
            messages: List of chat messages
            model: OpenAI model identifier
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            **kwargs: Additional OpenAI parameters

        Returns:
            ChatResponse with generated content
        """
        # Convert messages to OpenAI format
        openai_messages = [
            {"role": msg.role, "content": msg.content}
            for msg in messages
        ]

        try:
            response = await self.async_client.chat.completions.create(
                model=model,
                messages=openai_messages,
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs,
            )

            usage = UsageStats(
                prompt_tokens=response.usage.prompt_tokens,
                completion_tokens=response.usage.completion_tokens,
                total_tokens=response.usage.total_tokens,
            )

            return ChatResponse(
                content=response.choices[0].message.content,
                model=response.model,
                usage=usage,
                finish_reason=response.choices[0].finish_reason,
                raw_response=response.model_dump(),
            )

        except Exception as e:
            logger.error(f"OpenAI API error: {str(e)}", model=model)
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
            model: OpenAI model identifier
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            **kwargs: Additional OpenAI parameters

        Returns:
            ChatResponse with generated content
        """
        # Convert messages to OpenAI format
        openai_messages = [
            {"role": msg.role, "content": msg.content}
            for msg in messages
        ]

        try:
            response = self.sync_client.chat.completions.create(
                model=model,
                messages=openai_messages,
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs,
            )

            usage = UsageStats(
                prompt_tokens=response.usage.prompt_tokens,
                completion_tokens=response.usage.completion_tokens,
                total_tokens=response.usage.total_tokens,
            )

            return ChatResponse(
                content=response.choices[0].message.content,
                model=response.model,
                usage=usage,
                finish_reason=response.choices[0].finish_reason,
                raw_response=response.model_dump(),
            )

        except Exception as e:
            logger.error(f"OpenAI API error: {str(e)}", model=model)
            raise

    def count_tokens(self, text: str, model: str) -> int:
        """Count tokens using tiktoken.

        Args:
            text: Text to count tokens for
            model: Model identifier

        Returns:
            Number of tokens
        """
        return count_tokens(text, model, provider="openai")
