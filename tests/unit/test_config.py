"""Tests for configuration management."""

import pytest
from src.config import ConfigManager, Settings, ModelsRegistry


def test_settings_defaults():
    """Test default settings values."""
    settings = Settings()
    assert settings.environment == "development"
    assert settings.log_level == "INFO"
    assert settings.api_rate_limit == 100


def test_config_manager_initialization():
    """Test config manager initialization."""
    config = ConfigManager()
    assert config.config_dir.exists()
    assert config.settings is not None


def test_models_registry_get_model():
    """Test getting a model from registry."""
    config = ConfigManager()
    registry = config.models_registry

    # Should have models
    assert len(registry.get_all_models()) > 0

    # Test getting specific model
    model = registry.get_model("gpt-3.5-turbo")
    if model:
        assert model.provider == "openai"
        assert model.context_window > 0


def test_models_registry_get_by_provider():
    """Test getting models by provider."""
    config = ConfigManager()
    registry = config.models_registry

    openai_models = registry.get_models_by_provider("openai")
    assert len(openai_models) > 0
    assert all(m.provider == "openai" for m in openai_models)
