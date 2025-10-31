"""Token counting utilities for various model providers."""

from typing import Optional

import tiktoken


class TokenCounter:
    """Handles token counting for different model providers."""

    def __init__(self):
        """Initialize token counter with encoding caches."""
        self._encodings = {}

    def count_tokens(
        self,
        text: str,
        model: str,
        provider: Optional[str] = None
    ) -> int:
        """Count tokens in text for a specific model.

        Args:
            text: Text to count tokens for
            model: Model identifier
            provider: Provider name (openai, anthropic, etc.)

        Returns:
            Number of tokens
        """
        if provider == "openai" or model.startswith("gpt"):
            return self._count_openai_tokens(text, model)
        elif provider == "anthropic" or model.startswith("claude"):
            return self._count_anthropic_tokens(text)
        elif provider == "google" or model.startswith("gemini"):
            return self._count_google_tokens(text)
        else:
            # Fallback to approximate counting
            return self._approximate_token_count(text)

    def _count_openai_tokens(self, text: str, model: str) -> int:
        """Count tokens using OpenAI's tiktoken."""
        try:
            encoding = self._get_encoding(model)
            return len(encoding.encode(text))
        except Exception:
            # Fallback if model not found
            encoding = tiktoken.get_encoding("cl100k_base")
            return len(encoding.encode(text))

    def _get_encoding(self, model: str):
        """Get or cache encoding for a model."""
        if model not in self._encodings:
            try:
                self._encodings[model] = tiktoken.encoding_for_model(model)
            except KeyError:
                # Default to cl100k_base for unknown models
                self._encodings[model] = tiktoken.get_encoding("cl100k_base")
        return self._encodings[model]

    def _count_anthropic_tokens(self, text: str) -> int:
        """Count tokens for Anthropic models.

        Anthropic uses a similar tokenization to GPT, so we use cl100k_base.
        """
        encoding = tiktoken.get_encoding("cl100k_base")
        return len(encoding.encode(text))

    def _count_google_tokens(self, text: str) -> int:
        """Count tokens for Google models.

        Using approximate counting as Google's tokenizer is not publicly available.
        """
        return self._approximate_token_count(text)

    def _approximate_token_count(self, text: str) -> int:
        """Approximate token count using word splitting.

        Rough estimate: 1 token ≈ 4 characters or 0.75 words.
        """
        # Average of character-based and word-based estimates
        char_estimate = len(text) / 4
        word_estimate = len(text.split()) / 0.75
        return int((char_estimate + word_estimate) / 2)


# Global token counter instance
_token_counter = TokenCounter()


def count_tokens(
    text: str,
    model: str,
    provider: Optional[str] = None
) -> int:
    """Count tokens in text for a specific model.

    Args:
        text: Text to count tokens for
        model: Model identifier
        provider: Provider name (openai, anthropic, etc.)

    Returns:
        Number of tokens
    """
    return _token_counter.count_tokens(text, model, provider)
