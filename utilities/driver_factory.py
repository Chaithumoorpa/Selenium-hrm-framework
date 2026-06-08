"""
Enterprise Selenium HRM Framework — WebDriver Factory
------------------------------------------------------
Design Patterns:
  - Factory Pattern:   Creates browser-specific drivers
  - Singleton Pattern: One driver per thread (thread-local for parallel runs)

Supported Browsers: Chrome, Firefox, Edge
Capabilities:
  - Headless mode via config or HEADLESS env var
  - Remote WebDriver (Selenium Grid / Docker)
  - webdriver-manager for automatic driver binaries
  - Custom browser options from config
"""

import os
import threading
from typing import Optional

from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.remote.webdriver import WebDriver
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from webdriver_manager.microsoft import EdgeChromiumDriverManager

from utilities.config_reader import ConfigReader
from utilities.logger import get_logger

logger = get_logger(__name__)

# ──────────────────────────────────────────────────────────────────────────────
# Thread-local storage for parallel test execution
# ──────────────────────────────────────────────────────────────────────────────
_thread_local = threading.local()


class DriverFactory:
    """
    Factory class for creating and managing WebDriver instances.

    - Thread-local singleton ensures each parallel worker has its own driver
    - Supports local Chrome/Firefox/Edge and remote Selenium Grid
    - All options sourced from environment config

    Usage:
        driver = DriverFactory.get_driver()
        # ... run tests ...
        DriverFactory.quit_driver()
    """

    @staticmethod
    def get_driver(
        browser: Optional[str] = None,
        headless: Optional[bool] = None,
        remote_url: Optional[str] = None,
    ) -> WebDriver:
        """
        Get or create a WebDriver for the current thread.

        Args:
            browser:    Browser name override (chrome/firefox/edge)
            headless:   Headless mode override
            remote_url: Selenium Grid URL for remote execution

        Returns:
            WebDriver instance (thread-local singleton)
        """
        if getattr(_thread_local, "driver", None) is not None:
            return _thread_local.driver

        config = ConfigReader.get_config()
        _browser = (browser or config.browser).lower()
        _headless = headless if headless is not None else config.headless
        _remote_url = remote_url or os.environ.get("SELENIUM_REMOTE_URL")

        logger.info(
            "driver_creating",
            browser=_browser,
            headless=_headless,
            remote=bool(_remote_url),
        )

        if _remote_url:
            driver = DriverFactory._create_remote(_browser, _headless, _remote_url)
        else:
            driver = DriverFactory._create_local(_browser, _headless, config)

        # Configure timeouts
        driver.set_page_load_timeout(config.get("app.page_load_timeout", 60))
        driver.implicitly_wait(config.get("app.implicit_wait", 10))
        driver.maximize_window()

        _thread_local.driver = driver
        logger.info("driver_created", session_id=driver.session_id, browser=_browser)
        return driver

    @staticmethod
    def _create_local(
        browser: str, headless: bool, config: ConfigReader
    ) -> WebDriver:
        """Create a local browser WebDriver."""
        extra_options: list = config.get("browser.options") or []

        if browser == "chrome":
            options = ChromeOptions()
            options.add_argument("--window-size=1920,1080")
            for opt in extra_options:
                options.add_argument(opt)
            if headless:
                options.add_argument("--headless=new")
                options.add_argument("--disable-gpu")
            options.add_experimental_option("excludeSwitches", ["enable-logging"])
            service = ChromeService(ChromeDriverManager().install())
            return webdriver.Chrome(service=service, options=options)

        elif browser == "firefox":
            options = FirefoxOptions()
            options.add_argument("--width=1920")
            options.add_argument("--height=1080")
            if headless:
                options.add_argument("--headless")
            service = FirefoxService(GeckoDriverManager().install())
            return webdriver.Firefox(service=service, options=options)

        elif browser == "edge":
            options = EdgeOptions()
            options.add_argument("--window-size=1920,1080")
            for opt in extra_options:
                options.add_argument(opt)
            if headless:
                options.add_argument("--headless=new")
            service = EdgeService(EdgeChromiumDriverManager().install())
            return webdriver.Edge(service=service, options=options)

        else:
            raise ValueError(
                f"Unsupported browser: '{browser}'. "
                f"Choose from: chrome, firefox, edge"
            )

    @staticmethod
    def _create_remote(browser: str, headless: bool, remote_url: str) -> WebDriver:
        """Create a remote WebDriver for Selenium Grid."""
        if browser == "chrome":
            options = ChromeOptions()
            if headless:
                options.add_argument("--headless=new")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
        elif browser == "firefox":
            options = FirefoxOptions()
            if headless:
                options.add_argument("--headless")
        else:
            options = ChromeOptions()

        logger.info("driver_remote_connecting", grid_url=remote_url)
        return webdriver.Remote(
            command_executor=remote_url,
            options=options,
        )

    @staticmethod
    def quit_driver() -> None:
        """Quit the driver for the current thread and clean up."""
        driver: Optional[WebDriver] = getattr(_thread_local, "driver", None)
        if driver is not None:
            try:
                session_id = driver.session_id
                driver.quit()
                logger.info("driver_quit", session_id=session_id)
            except Exception as e:
                logger.warning("driver_quit_error", error=str(e))
            finally:
                _thread_local.driver = None

    @staticmethod
    def get_current_driver() -> Optional[WebDriver]:
        """Get existing driver without creating a new one."""
        return getattr(_thread_local, "driver", None)

    @staticmethod
    def is_driver_active() -> bool:
        """Check if a driver session is currently active."""
        driver = getattr(_thread_local, "driver", None)
        if driver is None:
            return False
        try:
            _ = driver.session_id
            return True
        except Exception:
            return False
