"""Pytest configuration and fixtures."""

import pytest
from unittest.mock import Mock

from src.config import reset_config
from src.providers.base_client import ChatMessage, ChatResponse, UsageStats


@pytest.fixture
def mock_chat_response():
    """Create a mock chat response."""
    return ChatResponse(
        content="Test response",
        model="test-model",
        usage=UsageStats(
            prompt_tokens=10,
            completion_tokens=20,
            total_tokens=30
        ),
        finish_reason="stop"
    )


@pytest.fixture
def mock_client(mock_chat_response):
    """Create a mock client."""
    client = Mock()
    client.chat_completion = Mock(return_value=mock_chat_response)
    client.chat_completion_sync = Mock(return_value=mock_chat_response)
    client.count_tokens = Mock(return_value=10)
    return client


@pytest.fixture(autouse=True)
def reset_config_after_test():
    """Reset config after each test."""
    yield
    reset_config()
