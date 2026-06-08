"""
Enterprise Selenium HRM Framework — Wait Utilities
---------------------------------------------------
Design: Fluent wrapper around Selenium's WebDriverWait
  - Explicit waits with meaningful error messages
  - Custom conditions for complex UI states
  - Polling intervals configurable per call
"""

from typing import Callable, List, Optional

from selenium.common.exceptions import (
    ElementClickInterceptedException,
    NoSuchElementException,
    StaleElementReferenceException,
    TimeoutException,
)
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from utilities.logger import get_logger

logger = get_logger(__name__)

# Exceptions that are safe to ignore while waiting
IGNORED_EXCEPTIONS = (
    StaleElementReferenceException,
    ElementClickInterceptedException,
    NoSuchElementException,
)


class WaitUtils:
    """
    Explicit wait helpers with structured logging.

    Usage:
        wait = WaitUtils(driver, timeout=30)
        element = wait.for_element_visible((By.ID, "username"))
        wait.for_url_contains("dashboard")
    """

    def __init__(self, driver: WebDriver, timeout: int = 20, poll: float = 0.5) -> None:
        self.driver = driver
        self.timeout = timeout
        self.poll = poll

    def _wait(self, timeout: Optional[int] = None) -> WebDriverWait:
        return WebDriverWait(
            self.driver,
            timeout or self.timeout,
            poll_frequency=self.poll,
            ignored_exceptions=list(IGNORED_EXCEPTIONS),
        )

    # ── Element Conditions ────────────────────────────────────────────────────

    def for_element_visible(self, locator: tuple, timeout: Optional[int] = None) -> WebElement:
        """Wait for element to be visible in DOM."""
        logger.debug("wait_for_visible", locator=str(locator))
        try:
            return self._wait(timeout).until(EC.visibility_of_element_located(locator))
        except TimeoutException:
            raise TimeoutException(f"Element not visible after {timeout or self.timeout}s: {locator}")

    def for_element_present(self, locator: tuple, timeout: Optional[int] = None) -> WebElement:
        """Wait for element to be present in DOM (may be hidden)."""
        try:
            return self._wait(timeout).until(EC.presence_of_element_located(locator))
        except TimeoutException:
            raise TimeoutException(f"Element not present after {timeout or self.timeout}s: {locator}")

    def for_element_clickable(self, locator: tuple, timeout: Optional[int] = None) -> WebElement:
        """Wait for element to be clickable."""
        logger.debug("wait_for_clickable", locator=str(locator))
        try:
            return self._wait(timeout).until(EC.element_to_be_clickable(locator))
        except TimeoutException:
            raise TimeoutException(f"Element not clickable after {timeout or self.timeout}s: {locator}")

    def for_element_invisible(self, locator: tuple, timeout: Optional[int] = None) -> bool:
        """Wait for element to disappear."""
        try:
            return self._wait(timeout).until(EC.invisibility_of_element_located(locator))
        except TimeoutException:
            raise TimeoutException(f"Element still visible after {timeout or self.timeout}s: {locator}")

    def for_all_elements_visible(self, locator: tuple, timeout: Optional[int] = None) -> List[WebElement]:
        """Wait for all matching elements to be visible."""
        try:
            return self._wait(timeout).until(EC.visibility_of_all_elements_located(locator))
        except TimeoutException:
            raise TimeoutException(f"Elements not all visible after {timeout or self.timeout}s: {locator}")

    # ── Text Conditions ───────────────────────────────────────────────────────

    def for_text_in_element(self, locator: tuple, text: str, timeout: Optional[int] = None) -> bool:
        """Wait until element contains specific text."""
        logger.debug("wait_for_text", locator=str(locator), text=text)
        try:
            return self._wait(timeout).until(EC.text_to_be_present_in_element(locator, text))
        except TimeoutException:
            raise TimeoutException(f"Text '{text}' not found in {locator} after {timeout or self.timeout}s")

    def for_text_in_value(self, locator: tuple, text: str, timeout: Optional[int] = None) -> bool:
        """Wait until element's value attribute contains text."""
        return self._wait(timeout).until(EC.text_to_be_present_in_element_value(locator, text))

    # ── URL / Title Conditions ────────────────────────────────────────────────

    def for_url_contains(self, partial_url: str, timeout: Optional[int] = None) -> bool:
        """Wait until current URL contains a string."""
        logger.debug("wait_for_url_contains", partial=partial_url)
        try:
            return self._wait(timeout).until(EC.url_contains(partial_url))
        except TimeoutException:
            raise TimeoutException(
                f"URL did not contain '{partial_url}' after {timeout or self.timeout}s. "
                f"Current URL: {self.driver.current_url}"
            )

    def for_title_contains(self, title: str, timeout: Optional[int] = None) -> bool:
        """Wait until page title contains a string."""
        return self._wait(timeout).until(EC.title_contains(title))

    # ── Alert Conditions ──────────────────────────────────────────────────────

    def for_alert(self, timeout: Optional[int] = None):
        """Wait for browser alert to appear."""
        return self._wait(timeout).until(EC.alert_is_present())

    # ── Custom Conditions ─────────────────────────────────────────────────────

    def for_condition(
        self,
        condition: Callable,
        timeout: Optional[int] = None,
        message: str = "Custom condition not met",
    ) -> bool:
        """Wait for any custom expected condition."""
        try:
            return self._wait(timeout).until(condition)
        except TimeoutException:
            raise TimeoutException(f"{message} after {timeout or self.timeout}s")

    def for_page_load(self, timeout: Optional[int] = None) -> None:
        """Wait for full page load (document.readyState = complete)."""
        self._wait(timeout).until(lambda d: d.execute_script("return document.readyState") == "complete")

    def for_ajax_complete(self, timeout: Optional[int] = None) -> None:
        """Wait for jQuery AJAX calls to complete."""
        try:
            self._wait(timeout).until(lambda d: d.execute_script("return jQuery.active === 0"))
        except Exception:
            pass  # Page may not use jQuery
