"""Configuration management for the Model Evaluation Toolbox."""

import json
import os
from pathlib import Path
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class ProviderConfig(BaseModel):
    """Configuration for a single API provider."""

    api_key: str
    organization_id: Optional[str] = None
    base_url: Optional[str] = None
    project_id: Optional[str] = None
    location: Optional[str] = None
    endpoint: Optional[str] = None


class RateLimitConfig(BaseModel):
    """Rate limit configuration for a provider."""

    requests_per_minute: int = 60
    tokens_per_minute: Optional[int] = None


class APIKeysConfig(BaseModel):
    """Complete API keys configuration."""

    providers: Dict[str, ProviderConfig]
    rate_limits: Dict[str, RateLimitConfig] = Field(default_factory=dict)


class ModelInfo(BaseModel):
    """Information about a specific model."""

    id: str
    name: str
    provider: str
    type: str
    context_window: int
    max_output_tokens: int
    pricing: Dict[str, float]
    capabilities: list[str] = Field(default_factory=list)


class ModelsRegistry(BaseModel):
    """Registry of all available models."""

    models: Dict[str, list[ModelInfo]]
    benchmark_configs: Dict[str, Any] = Field(default_factory=dict)

    def get_model(self, model_id: str) -> Optional[ModelInfo]:
        """Get model info by ID."""
        for provider_models in self.models.values():
            for model in provider_models:
                if model.id == model_id:
                    return model
        return None

    def get_models_by_provider(self, provider: str) -> list[ModelInfo]:
        """Get all models for a specific provider."""
        return self.models.get(provider, [])

    def get_all_models(self) -> list[ModelInfo]:
        """Get all models across all providers."""
        all_models = []
        for provider_models in self.models.values():
            all_models.extend(provider_models)
        return all_models


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    # API Keys
    openai_api_key: Optional[str] = None
    openai_org_id: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    google_api_key: Optional[str] = None
    google_project_id: Optional[str] = None
    cohere_api_key: Optional[str] = None
    huggingface_api_key: Optional[str] = None

    # Database
    database_url: str = "postgresql://localhost/model_eval_db"
    database_host: str = "localhost"
    database_port: int = 5432
    database_name: str = "model_eval_db"
    database_user: str = "postgres"
    database_password: str = ""

    # Application
    environment: str = "development"
    log_level: str = "INFO"
    api_rate_limit: int = 100

    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        """Validate log level."""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in valid_levels:
            raise ValueError(f"Log level must be one of {valid_levels}")
        return v.upper()


class ConfigManager:
    """Manages all configuration loading and access."""

    def __init__(self, config_dir: Optional[Path] = None):
        """Initialize configuration manager.

        Args:
            config_dir: Path to configuration directory. Defaults to project root/config.
        """
        if config_dir is None:
            # Get project root (parent of src directory)
            project_root = Path(__file__).parent.parent
            config_dir = project_root / "config"

        self.config_dir = Path(config_dir)
        self._settings: Optional[Settings] = None
        self._api_keys: Optional[APIKeysConfig] = None
        self._models_registry: Optional[ModelsRegistry] = None

    @property
    def settings(self) -> Settings:
        """Get application settings."""
        if self._settings is None:
            self._settings = Settings()
        return self._settings

    @property
    def api_keys(self) -> APIKeysConfig:
        """Load API keys configuration."""
        if self._api_keys is None:
            self._api_keys = self._load_api_keys()
        return self._api_keys

    @property
    def models_registry(self) -> ModelsRegistry:
        """Load models registry."""
        if self._models_registry is None:
            self._models_registry = self._load_models_registry()
        return self._models_registry

    def _load_api_keys(self) -> APIKeysConfig:
        """Load API keys from JSON or environment variables."""
        api_keys_file = self.config_dir / "api_keys.json"

        if api_keys_file.exists():
            with open(api_keys_file, "r") as f:
                data = json.load(f)
                return APIKeysConfig(**data)

        # Fallback to environment variables
        settings = self.settings
        providers = {}

        if settings.openai_api_key:
            providers["openai"] = ProviderConfig(
                api_key=settings.openai_api_key,
                organization_id=settings.openai_org_id,
                base_url="https://api.openai.com/v1"
            )

        if settings.anthropic_api_key:
            providers["anthropic"] = ProviderConfig(
                api_key=settings.anthropic_api_key,
                base_url="https://api.anthropic.com"
            )

        if settings.google_api_key:
            providers["google"] = ProviderConfig(
                api_key=settings.google_api_key,
                project_id=settings.google_project_id
            )

        if settings.cohere_api_key:
            providers["cohere"] = ProviderConfig(
                api_key=settings.cohere_api_key
            )

        if settings.huggingface_api_key:
            providers["huggingface"] = ProviderConfig(
                api_key=settings.huggingface_api_key
            )

        return APIKeysConfig(providers=providers)

    def _load_models_registry(self) -> ModelsRegistry:
        """Load models registry from JSON file."""
        registry_file = self.config_dir / "models_registry.json"

        if not registry_file.exists():
            raise FileNotFoundError(
                f"Models registry not found at {registry_file}. "
                "Please ensure models_registry.json exists in the config directory."
            )

        with open(registry_file, "r") as f:
            data = json.load(f)
            return ModelsRegistry(**data)

    def get_provider_config(self, provider: str) -> Optional[ProviderConfig]:
        """Get configuration for a specific provider.

        Args:
            provider: Name of the provider (openai, anthropic, etc.)

        Returns:
            Provider configuration or None if not found.
        """
        return self.api_keys.providers.get(provider)

    def get_rate_limit(self, provider: str) -> RateLimitConfig:
        """Get rate limit configuration for a provider.

        Args:
            provider: Name of the provider.

        Returns:
            Rate limit configuration with defaults if not specified.
        """
        return self.api_keys.rate_limits.get(
            provider,
            RateLimitConfig()
        )


# Global configuration instance
_config_manager: Optional[ConfigManager] = None


def get_config() -> ConfigManager:
    """Get the global configuration manager instance."""
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigManager()
    return _config_manager


def reset_config():
    """Reset the global configuration (useful for testing)."""
    global _config_manager
    _config_manager = None
