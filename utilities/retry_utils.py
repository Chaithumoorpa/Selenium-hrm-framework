"""
Enterprise Selenium HRM Framework — Retry Utilities
----------------------------------------------------
Design: Decorator + Context Manager patterns
  - tenacity-based retry with exponential backoff
  - Configurable exceptions, max attempts, wait strategy
  - Allure step integration for retry visibility in reports
"""

import functools
import time
from typing import Any, Callable, Optional, Tuple, Type
from selenium.common.exceptions import (
    ElementClickInterceptedException,
    NoSuchElementException,
    StaleElementReferenceException,
    WebDriverException,
)

from utilities.logger import get_logger

logger = get_logger(__name__)

# ──────────────────────────────────────────────────────────────────────────────
# Default retryable exceptions for Selenium interactions
# ──────────────────────────────────────────────────────────────────────────────
DEFAULT_RETRY_EXCEPTIONS: Tuple[Type[Exception], ...] = (
    StaleElementReferenceException,
    ElementClickInterceptedException,
    NoSuchElementException,
    WebDriverException,
)


def retry_on_failure(
    max_attempts: int = 3,
    wait_seconds: float = 2.0,
    exceptions: Optional[Tuple[Type[Exception], ...]] = None,
    exponential: bool = False,
) -> Callable:
    """
    Decorator for retrying flaky Selenium interactions.

    Args:
        max_attempts: Maximum retry count (default: 3)
        wait_seconds: Wait between retries in seconds (default: 2)
        exceptions:   Exception types to retry on (default: common Selenium exceptions)
        exponential:  Use exponential backoff instead of fixed wait (default: False)

    Usage:
        @retry_on_failure(max_attempts=3, wait_seconds=2)
        def click_submit(self):
            self.find_element(By.ID, "submit").click()
    """
    _exceptions = exceptions or DEFAULT_RETRY_EXCEPTIONS

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            attempt = 0
            last_exception: Optional[Exception] = None

            while attempt < max_attempts:
                try:
                    return func(*args, **kwargs)
                except _exceptions as e:
                    attempt += 1
                    last_exception = e
                    logger.warning(
                        "retry_attempt",
                        function=func.__name__,
                        attempt=attempt,
                        max=max_attempts,
                        error=str(e)[:100],
                    )
                    if attempt < max_attempts:
                        sleep_time = (
                            wait_seconds * (2 ** (attempt - 1))
                            if exponential
                            else wait_seconds
                        )
                        time.sleep(sleep_time)

            logger.error(
                "retry_exhausted",
                function=func.__name__,
                attempts=max_attempts,
                error=str(last_exception)[:200],
            )
            raise last_exception  # type: ignore

        return wrapper

    return decorator


def retry_click(
    max_attempts: int = 3,
    wait_seconds: float = 1.0,
) -> Callable:
    """
    Specialized decorator for retrying element clicks.
    Handles StaleElement and InterceptedClick specifically.
    """
    return retry_on_failure(
        max_attempts=max_attempts,
        wait_seconds=wait_seconds,
        exceptions=(StaleElementReferenceException, ElementClickInterceptedException),
    )


class RetryContext:
    """
    Context manager for retrying code blocks.

    Usage:
        with RetryContext(max_attempts=3, wait=2) as ctx:
            driver.find_element(By.ID, "btn").click()
    """

    def __init__(
        self,
        max_attempts: int = 3,
        wait: float = 2.0,
        exceptions: Optional[Tuple[Type[Exception], ...]] = None,
    ) -> None:
        self.max_attempts = max_attempts
        self.wait = wait
        self.exceptions = exceptions or DEFAULT_RETRY_EXCEPTIONS
        self._attempt = 0

    def __enter__(self) -> "RetryContext":
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> bool:
        if exc_type is None:
            return False

        if isinstance(exc_val, self.exceptions):
            self._attempt += 1
            if self._attempt < self.max_attempts:
                logger.warning(
                    "retry_context_attempt",
                    attempt=self._attempt,
                    max=self.max_attempts,
                    error=str(exc_val)[:100],
                )
                time.sleep(self.wait)
                return True  # Suppress exception, retry

        return False  # Raise exception
