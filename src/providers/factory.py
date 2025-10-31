"""Factory for creating provider clients."""

from typing import Optional

from ..config import get_config
from .base_client import BaseClient
from .openai_client import OpenAIClient
from .anthropic_client import AnthropicClient
from .google_client import GoogleClient
from .cohere_client import CohereClient


class ClientFactory:
    """Factory for creating API clients."""

    @staticmethod
    def create_client(
        provider: str,
        api_key: Optional[str] = None,
        **kwargs
    ) -> BaseClient:
        """Create a client for the specified provider.

        Args:
            provider: Provider name (openai, anthropic, google, cohere)
            api_key: Optional API key (will use config if not provided)
            **kwargs: Additional provider-specific parameters

        Returns:
            Initialized client instance

        Raises:
            ValueError: If provider is not supported
        """
        config = get_config()

        # Get API key from config if not provided
        if api_key is None:
            provider_config = config.get_provider_config(provider)
            if provider_config is None:
                raise ValueError(
                    f"No configuration found for provider '{provider}'. "
                    "Please add API key to config/api_keys.json or .env file."
                )
            api_key = provider_config.api_key

        # Create client based on provider
        if provider.lower() == "openai":
            provider_config = config.get_provider_config(provider)
            return OpenAIClient(
                api_key=api_key,
                organization_id=provider_config.organization_id if provider_config else None,
                **kwargs
            )

        elif provider.lower() == "anthropic":
            return AnthropicClient(api_key=api_key, **kwargs)

        elif provider.lower() == "google":
            provider_config = config.get_provider_config(provider)
            return GoogleClient(
                api_key=api_key,
                project_id=provider_config.project_id if provider_config else None,
                location=provider_config.location if provider_config else "us-central1",
                **kwargs
            )

        elif provider.lower() == "cohere":
            return CohereClient(api_key=api_key, **kwargs)

        else:
            raise ValueError(
                f"Unsupported provider: {provider}. "
                f"Supported providers: openai, anthropic, google, cohere"
            )


def get_client(provider: str, **kwargs) -> BaseClient:
    """Convenience function to get a client.

    Args:
        provider: Provider name
        **kwargs: Additional parameters

    Returns:
        Initialized client instance
    """
    return ClientFactory.create_client(provider, **kwargs)
