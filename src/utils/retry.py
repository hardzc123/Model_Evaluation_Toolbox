"""Retry utilities with exponential backoff."""

import asyncio
import functools
import time
from typing import Callable, Optional, Type, Union

from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    before_sleep_log,
)

from .logger import get_logger

logger = get_logger(__name__)


def retry_with_backoff(
    max_attempts: int = 3,
    min_wait: float = 1.0,
    max_wait: float = 60.0,
    exception_types: Optional[tuple[Type[Exception], ...]] = None,
):
    """Decorator for retrying functions with exponential backoff.

    Args:
        max_attempts: Maximum number of retry attempts
        min_wait: Minimum wait time between retries in seconds
        max_wait: Maximum wait time between retries in seconds
        exception_types: Tuple of exception types to retry on. Defaults to Exception.

    Returns:
        Decorated function with retry logic
    """
    if exception_types is None:
        exception_types = (Exception,)

    return retry(
        stop=stop_after_attempt(max_attempts),
        wait=wait_exponential(min=min_wait, max=max_wait),
        retry=retry_if_exception_type(exception_types),
        before_sleep=before_sleep_log(logger, "WARNING"),
        reraise=True,
    )


class RateLimiter:
    """Simple rate limiter for API calls."""

    def __init__(self, requests_per_minute: int = 60):
        """Initialize rate limiter.

        Args:
            requests_per_minute: Maximum requests allowed per minute
        """
        self.requests_per_minute = requests_per_minute
        self.min_interval = 60.0 / requests_per_minute
        self.last_request_time: Optional[float] = None

    async def acquire(self):
        """Acquire permission to make a request (async)."""
        if self.last_request_time is not None:
            elapsed = time.time() - self.last_request_time
            if elapsed < self.min_interval:
                wait_time = self.min_interval - elapsed
                await asyncio.sleep(wait_time)

        self.last_request_time = time.time()

    def acquire_sync(self):
        """Acquire permission to make a request (sync)."""
        if self.last_request_time is not None:
            elapsed = time.time() - self.last_request_time
            if elapsed < self.min_interval:
                wait_time = self.min_interval - elapsed
                time.sleep(wait_time)

        self.last_request_time = time.time()
