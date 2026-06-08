"""
Enterprise Selenium HRM Framework — Base Page
----------------------------------------------
Design Patterns: Page Object Model + Page Factory
  - BasePage is the parent of all page classes
  - Encapsulates all raw Selenium calls
  - All child pages inherit and use only high-level actions
  - Page Factory pattern via lazy element resolution
"""

import time
from typing import List, Optional

import allure
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import Select

from utilities.config_reader import ConfigReader
from utilities.logger import get_logger
from utilities.retry_utils import retry_on_failure
from utilities.screenshot_utils import capture_page_source, capture_screenshot
from utilities.wait_utils import WaitUtils

logger = get_logger(__name__)


class BasePage:
    """
    Base class for all Page Objects.

    Provides:
      - Element interaction methods (click, type, select, hover)
      - Smart waits via WaitUtils
      - Screenshot and page source capture
      - Navigation helpers
      - Allure step decorators for all actions
    """

    def __init__(self, driver: WebDriver) -> None:
        self.driver = driver
        self.config = ConfigReader.get_config()
        self.wait = WaitUtils(
            driver,
            timeout=self.config.explicit_wait,
        )
        logger.debug("page_initialized", page=self.__class__.__name__)

    # ── Navigation ────────────────────────────────────────────────────────────

    @allure.step("Navigate to URL: {url}")
    def navigate_to(self, url: str) -> None:
        """Navigate to a URL."""
        logger.info("navigate_to", url=url, page=self.__class__.__name__)
        self.driver.get(url)
        self.wait.for_page_load()

    def navigate_to_base(self) -> None:
        """Navigate to the configured base URL."""
        self.navigate_to(self.config.base_url)

    def get_current_url(self) -> str:
        return self.driver.current_url

    def get_page_title(self) -> str:
        return self.driver.title

    def refresh_page(self) -> None:
        self.driver.refresh()
        self.wait.for_page_load()

    def go_back(self) -> None:
        self.driver.back()
        self.wait.for_page_load()

    # ── Element Finding ───────────────────────────────────────────────────────

    def find_element(self, locator: tuple, timeout: Optional[int] = None) -> WebElement:
        """Find visible element with explicit wait."""
        return self.wait.for_element_visible(locator, timeout)

    def find_elements(self, locator: tuple, timeout: Optional[int] = None) -> List[WebElement]:
        """Find all visible matching elements."""
        try:
            return self.wait.for_all_elements_visible(locator, timeout)
        except TimeoutException:
            return []

    def find_element_present(self, locator: tuple, timeout: Optional[int] = None) -> WebElement:
        """Find element present in DOM (may be hidden)."""
        return self.wait.for_element_present(locator, timeout)

    def is_element_visible(self, locator: tuple, timeout: int = 5) -> bool:
        """Check if element is visible without raising exception."""
        try:
            self.wait.for_element_visible(locator, timeout)
            return True
        except (TimeoutException, NoSuchElementException):
            return False

    def is_element_present(self, locator: tuple, timeout: int = 5) -> bool:
        """Check if element exists in DOM."""
        try:
            self.wait.for_element_present(locator, timeout)
            return True
        except (TimeoutException, NoSuchElementException):
            return False

    # ── Interactions ──────────────────────────────────────────────────────────

    @allure.step("Click element")
    @retry_on_failure(max_attempts=3, wait_seconds=1.0)
    def click(self, locator: tuple, timeout: Optional[int] = None) -> None:
        """Click a visible, clickable element."""
        element = self.wait.for_element_clickable(locator, timeout)
        element.click()
        logger.debug("element_clicked", locator=str(locator))

    @allure.step("JS Click element")
    def js_click(self, locator: tuple) -> None:
        """Click element via JavaScript (bypasses overlays)."""
        element = self.find_element(locator)
        self.driver.execute_script("arguments[0].click();", element)
        logger.debug("js_click", locator=str(locator))

    @allure.step("Type text in field")
    def type_text(self, locator: tuple, text: str, clear_first: bool = True) -> None:
        """Type text into an input field."""
        element = self.wait.for_element_clickable(locator)
        if clear_first:
            element.clear()
        element.send_keys(text)
        logger.debug("text_typed", locator=str(locator), length=len(text))

    @allure.step("Clear and type in field")
    def clear_and_type(self, locator: tuple, text: str) -> None:
        """Triple-click to select all, then type."""
        element = self.find_element(locator)
        element.click()
        element.send_keys(Keys.CONTROL + "a")
        element.send_keys(Keys.DELETE)
        element.send_keys(text)

    def press_enter(self, locator: tuple) -> None:
        """Press Enter key on element."""
        element = self.find_element(locator)
        element.send_keys(Keys.RETURN)

    # ── Dropdown / Select ─────────────────────────────────────────────────────

    @allure.step("Select from dropdown")
    def select_by_visible_text(self, locator: tuple, value: str) -> None:
        """Select from a <select> dropdown by visible text."""
        element = self.find_element(locator)
        Select(element).select_by_visible_text(value)

    def select_by_value(self, locator: tuple, value: str) -> None:
        """Select from <select> dropdown by value attribute."""
        element = self.find_element(locator)
        Select(element).select_by_value(value)

    # ── Custom Dropdown (div-based) ───────────────────────────────────────────

    @allure.step("Select custom dropdown option")
    def select_custom_dropdown(self, trigger_locator: tuple, option_text: str) -> None:
        """
        Handle OrangeHRM's custom div-based dropdowns.
        Click trigger → wait for options → click matching option.
        If the matching option is not found, fall back to the first non-empty option.
        """
        self.click(trigger_locator)
        time.sleep(0.5)  # Allow dropdown animation
        option_locator = (
            By.XPATH,
            f"//div[@role='option']//span[text()='{option_text}']",
        )
        if self.is_element_visible(option_locator, timeout=3):
            self.click(option_locator)
            logger.debug("custom_dropdown_selected", option=option_text)
            return

        # Fallback to first available option
        options_locator = (By.XPATH, "//div[@role='option']/span")
        elements = self.find_elements(options_locator, timeout=3)
        for el in elements:
            text = el.text.strip()
            if text and text != "-- Select --":
                el.click()
                logger.warning(
                    "dropdown_fallback_selected",
                    expected=option_text,
                    actual=text,
                )
                return
        raise NoSuchElementException(f"Could not find dropdown option '{option_text}' or any valid fallback options.")

    # ── Getters ───────────────────────────────────────────────────────────────

    def get_text(self, locator: tuple, timeout: Optional[int] = None) -> str:
        """Get visible text of element."""
        element = self.find_element(locator, timeout)
        return element.text.strip()

    def get_attribute(self, locator: tuple, attribute: str) -> str:
        """Get attribute value of element."""
        element = self.find_element(locator)
        return element.get_attribute(attribute) or ""

    def get_input_value(self, locator: tuple) -> str:
        """Get current value of an input field."""
        return self.get_attribute(locator, "value")

    def get_all_texts(self, locator: tuple) -> List[str]:
        """Get text content of all matching elements."""
        elements = self.find_elements(locator)
        return [el.text.strip() for el in elements]

    # ── State Checks ─────────────────────────────────────────────────────────

    def is_selected(self, locator: tuple) -> bool:
        """Check if checkbox/radio is selected."""
        return self.find_element(locator).is_selected()

    def is_enabled(self, locator: tuple) -> bool:
        """Check if element is enabled (not greyed out)."""
        return self.find_element(locator).is_enabled()

    # ── Wait Helpers ──────────────────────────────────────────────────────────

    def wait_for_toast(self, timeout: int = 10) -> str:
        """Wait for OrangeHRM toast notification and return its text."""
        toast_locator = (
            By.XPATH,
            "//p[contains(@class,'oxd-text--toast-message')]",
        )
        try:
            element = self.wait.for_element_visible(toast_locator, timeout)
            return element.text.strip()
        except TimeoutException:
            return ""

    def wait_for_url_to_contain(self, partial: str, timeout: int = 15) -> None:
        """Wait for URL to contain a substring."""
        self.wait.for_url_contains(partial, timeout)

    def wait_for_element_to_disappear(self, locator: tuple, timeout: int = 10) -> None:
        """Wait for a spinner/loader to disappear."""
        self.wait.for_element_invisible(locator, timeout)

    # ── Mouse Actions ─────────────────────────────────────────────────────────

    def hover(self, locator: tuple) -> None:
        """Hover over element."""
        element = self.find_element(locator)
        ActionChains(self.driver).move_to_element(element).perform()

    def scroll_to_element(self, locator: tuple) -> None:
        """Scroll element into view."""
        element = self.find_element(locator)
        self.driver.execute_script(
            "arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});",
            element,
        )

    def scroll_to_top(self) -> None:
        self.driver.execute_script("window.scrollTo(0, 0);")

    def scroll_to_bottom(self) -> None:
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

    # ── Screenshots ───────────────────────────────────────────────────────────

    def take_screenshot(self, name: str = "screenshot") -> str:
        """Capture screenshot and attach to Allure."""
        return capture_screenshot(
            self.driver,
            name=f"{self.__class__.__name__}_{name}",
            attach_to_allure=True,
        )

    def take_page_source(self, name: str = "page_source") -> None:
        """Capture page source and attach to Allure."""
        capture_page_source(self.driver, name=name, attach_to_allure=True)

    # ── JavaScript Helpers ────────────────────────────────────────────────────

    def execute_script(self, script: str, *args) -> any:
        """Execute JavaScript in browser."""
        return self.driver.execute_script(script, *args)

    def highlight_element(self, locator: tuple) -> None:
        """Highlight element with yellow border (debugging aid)."""
        element = self.find_element(locator)
        self.driver.execute_script("arguments[0].style.border='3px solid yellow'", element)
