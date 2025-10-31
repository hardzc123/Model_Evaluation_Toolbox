"""Google (Gemini) API client implementation."""

from typing import List, Optional

import google.generativeai as genai

from ..utils import get_logger, retry_with_backoff, count_tokens
from .base_client import BaseClient, ChatMessage, ChatResponse, UsageStats

logger = get_logger(__name__)


class GoogleClient(BaseClient):
    """Client for Google Gemini API."""

    def __init__(
        self,
        api_key: str,
        project_id: Optional[str] = None,
        location: str = "us-central1",
        timeout: float = 60.0,
        max_retries: int = 3,
    ):
        """Initialize Google client.

        Args:
            api_key: Google API key
            project_id: Optional GCP project ID (for Vertex AI)
            location: GCP region
            timeout: Request timeout in seconds
            max_retries: Maximum retry attempts
        """
        super().__init__(api_key, None, timeout, max_retries)
        self.project_id = project_id
        self.location = location

        # Configure the API
        genai.configure(api_key=api_key)

    @retry_with_backoff(max_attempts=3)
    async def chat_completion(
        self,
        messages: List[ChatMessage],
        model: str,
        temperature: float = 1.0,
        max_tokens: Optional[int] = None,
        **kwargs,
    ) -> ChatResponse:
        """Generate a chat completion using Google Gemini API.

        Args:
            messages: List of chat messages
            model: Gemini model identifier
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            **kwargs: Additional Gemini parameters

        Returns:
            ChatResponse with generated content
        """
        try:
            # Initialize model
            gemini_model = genai.GenerativeModel(model)

            # Convert messages to Gemini format
            # Gemini uses a simpler format - system messages become part of context
            chat_history = []
            system_instruction = None

            for msg in messages[:-1]:  # All but last message go to history
                if msg.role == "system":
                    system_instruction = msg.content
                else:
                    chat_history.append({
                        "role": "user" if msg.role == "user" else "model",
                        "parts": [msg.content]
                    })

            # Start chat with history
            chat = gemini_model.start_chat(history=chat_history)

            # Send the last message
            last_message = messages[-1].content

            # Configure generation
            generation_config = genai.GenerationConfig(
                temperature=temperature,
                max_output_tokens=max_tokens,
                **kwargs
            )

            # Generate response
            response = await chat.send_message_async(
                last_message,
                generation_config=generation_config
            )

            # Extract usage information (if available)
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
                finish_reason=None,  # Gemini doesn't always provide this
                raw_response={"response": response.text},
            )

        except Exception as e:
            logger.error(f"Google Gemini API error: {str(e)}", model=model)
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
            model: Gemini model identifier
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            **kwargs: Additional Gemini parameters

        Returns:
            ChatResponse with generated content
        """
        try:
            # Initialize model
            gemini_model = genai.GenerativeModel(model)

            # Convert messages to Gemini format
            chat_history = []
            system_instruction = None

            for msg in messages[:-1]:
                if msg.role == "system":
                    system_instruction = msg.content
                else:
                    chat_history.append({
                        "role": "user" if msg.role == "user" else "model",
                        "parts": [msg.content]
                    })

            # Start chat with history
            chat = gemini_model.start_chat(history=chat_history)

            # Send the last message
            last_message = messages[-1].content

            # Configure generation
            generation_config = genai.GenerationConfig(
                temperature=temperature,
                max_output_tokens=max_tokens,
                **kwargs
            )

            # Generate response
            response = chat.send_message(
                last_message,
                generation_config=generation_config
            )

            # Extract usage information
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
                finish_reason=None,
                raw_response={"response": response.text},
            )

        except Exception as e:
            logger.error(f"Google Gemini API error: {str(e)}", model=model)
            raise

    def count_tokens(self, text: str, model: str) -> int:
        """Count tokens for Google models.

        Args:
            text: Text to count tokens for
            model: Model identifier

        Returns:
            Number of tokens
        """
        return count_tokens(text, model, provider="google")
