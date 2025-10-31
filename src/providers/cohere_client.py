"""Cohere API client implementation."""

from typing import List, Optional

import cohere
from cohere import AsyncClient, Client

from ..utils import get_logger, retry_with_backoff, count_tokens
from .base_client import BaseClient, ChatMessage, ChatResponse, UsageStats

logger = get_logger(__name__)


class CohereClient(BaseClient):
    """Client for Cohere API."""

    def __init__(
        self,
        api_key: str,
        base_url: Optional[str] = None,
        timeout: float = 60.0,
        max_retries: int = 3,
    ):
        """Initialize Cohere client.

        Args:
            api_key: Cohere API key
            base_url: Optional custom base URL
            timeout: Request timeout in seconds
            max_retries: Maximum retry attempts
        """
        super().__init__(api_key, base_url, timeout, max_retries)

        # Initialize async client
        self.async_client = AsyncClient(
            api_key=api_key,
            timeout=timeout,
            max_retries=max_retries,
        )

        # Initialize sync client
        self.sync_client = Client(
            api_key=api_key,
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
        """Generate a chat completion using Cohere API.

        Args:
            messages: List of chat messages
            model: Cohere model identifier
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            **kwargs: Additional Cohere parameters

        Returns:
            ChatResponse with generated content
        """
        try:
            # Convert messages to Cohere format
            # Cohere uses chat_history for context and message for the current query
            chat_history = []
            system_message = None
            current_message = ""

            for msg in messages:
                if msg.role == "system":
                    system_message = msg.content
                elif msg.role == "user":
                    if current_message:  # Previous message becomes history
                        chat_history.append({
                            "role": "USER",
                            "message": current_message
                        })
                    current_message = msg.content
                elif msg.role == "assistant":
                    chat_history.append({
                        "role": "CHATBOT",
                        "message": msg.content
                    })

            params = {
                "model": model,
                "message": current_message,
                "temperature": temperature,
            }

            if chat_history:
                params["chat_history"] = chat_history

            if system_message:
                params["preamble"] = system_message

            if max_tokens:
                params["max_tokens"] = max_tokens

            params.update(kwargs)

            response = await self.async_client.chat(**params)

            # Estimate token usage (Cohere provides this in meta)
            prompt_tokens = self.count_tokens(
                " ".join([m.content for m in messages]),
                model
            )
            completion_tokens = self.count_tokens(response.text, model)

            usage = UsageStats(
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                total_tokens=prompt_tokens + completion_tokens,
            )

            return ChatResponse(
                content=response.text,
                model=model,
                usage=usage,
                finish_reason=response.finish_reason if hasattr(response, 'finish_reason') else None,
                raw_response={"text": response.text, "generation_id": response.generation_id},
            )

        except Exception as e:
            logger.error(f"Cohere API error: {str(e)}", model=model)
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
            model: Cohere model identifier
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            **kwargs: Additional Cohere parameters

        Returns:
            ChatResponse with generated content
        """
        try:
            # Convert messages to Cohere format
            chat_history = []
            system_message = None
            current_message = ""

            for msg in messages:
                if msg.role == "system":
                    system_message = msg.content
                elif msg.role == "user":
                    if current_message:
                        chat_history.append({
                            "role": "USER",
                            "message": current_message
                        })
                    current_message = msg.content
                elif msg.role == "assistant":
                    chat_history.append({
                        "role": "CHATBOT",
                        "message": msg.content
                    })

            params = {
                "model": model,
                "message": current_message,
                "temperature": temperature,
            }

            if chat_history:
                params["chat_history"] = chat_history

            if system_message:
                params["preamble"] = system_message

            if max_tokens:
                params["max_tokens"] = max_tokens

            params.update(kwargs)

            response = self.sync_client.chat(**params)

            # Estimate token usage
            prompt_tokens = self.count_tokens(
                " ".join([m.content for m in messages]),
                model
            )
            completion_tokens = self.count_tokens(response.text, model)

            usage = UsageStats(
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                total_tokens=prompt_tokens + completion_tokens,
            )

            return ChatResponse(
                content=response.text,
                model=model,
                usage=usage,
                finish_reason=response.finish_reason if hasattr(response, 'finish_reason') else None,
                raw_response={"text": response.text, "generation_id": response.generation_id},
            )

        except Exception as e:
            logger.error(f"Cohere API error: {str(e)}", model=model)
            raise

    def count_tokens(self, text: str, model: str) -> int:
        """Count tokens for Cohere models.

        Args:
            text: Text to count tokens for
            model: Model identifier

        Returns:
            Number of tokens
        """
        # Use approximate counting for Cohere
        return count_tokens(text, model, provider="cohere")
