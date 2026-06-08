"""
Enterprise Selenium HRM Framework — PyTest conftest.py
-------------------------------------------------------
Central fixture hub for all test modules.

Fixtures:
  - config:        ConfigReader singleton
  - driver:        WebDriver (session or function scope)
  - login_page:    LoginPage instance (function scope)
  - employee_page: EmployeePage instance
  - leave_page:    LeavePage instance
  - authenticated_driver: Pre-logged-in driver

Hooks:
  - Setup Allure environment info
  - Screenshot on failure
  - Structured log context per test
  - Retry on failure (pytest-rerunfailures)
"""

import os
import sys
from pathlib import Path
from typing import Generator

import pytest
from selenium.webdriver.remote.webdriver import WebDriver

from pages.employee_page import EmployeePage
from pages.leave_page import LeavePage
from pages.login_page import LoginPage
from pages.recruitment_page import RecruitmentPage
from utilities.config_reader import ConfigReader
from utilities.driver_factory import DriverFactory
from utilities.logger import bind_test_context, clear_test_context, get_logger, setup_logging
from utilities.screenshot_utils import capture_page_source, capture_screenshot

logger = get_logger(__name__)

# ──────────────────────────────────────────────────────────────────────────────
# Session-level setup
# ──────────────────────────────────────────────────────────────────────────────


def pytest_configure(config: pytest.Config) -> None:
    """Configure logging and Allure environment at session start."""
    cfg = ConfigReader.get_config()
    setup_logging(
        log_level=cfg.get("logging.level", "INFO"),
        log_file=cfg.get("logging.file", "logs/hrm_test.log"),
        log_format=cfg.get("logging.format", "json"),
    )
    _write_allure_environment(cfg)
    logger.info("test_session_started", env=os.environ.get("ENV", "dev"))


def _write_allure_environment(cfg: ConfigReader) -> None:
    """Write allure/environment.properties for the Allure report."""
    results_dir = Path(cfg.allure_results_dir)
    results_dir.mkdir(parents=True, exist_ok=True)

    env_props = results_dir / "environment.properties"
    content = (
        f"App=OrangeHRM\n"
        f"Version=5.x\n"
        f"Environment={os.environ.get('ENV', 'dev')}\n"
        f"Base.URL={cfg.base_url}\n"
        f"Browser={cfg.browser}\n"
        f"Headless={cfg.headless}\n"
        f"OS={os.name}\n"
        f"Python.Version={sys.version.split()[0]}\n"
    )
    env_props.write_text(content, encoding="utf-8")


# ──────────────────────────────────────────────────────────────────────────────
# Hooks
# ──────────────────────────────────────────────────────────────────────────────


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item: pytest.Item, call):
    """
    Hook: capture screenshot + page source on test failure.
    Attach to Allure report automatically.
    """
    outcome = yield
    report = outcome.get_result()

    if report.when == "call" and report.failed:
        driver: WebDriver = item.funcargs.get("driver")
        if driver:
            test_name = item.name
            logger.error(
                "test_failed",
                test=test_name,
                nodeid=item.nodeid,
            )
            capture_screenshot(
                driver,
                name=f"FAILURE_{test_name}",
                attach_to_allure=True,
            )
            capture_page_source(driver, name=f"FAILURE_source_{test_name}")


# ──────────────────────────────────────────────────────────────────────────────
# Core Fixtures
# ──────────────────────────────────────────────────────────────────────────────


@pytest.fixture(scope="session")
def config() -> ConfigReader:
    """Session-scoped ConfigReader singleton."""
    return ConfigReader.get_config()


@pytest.fixture(scope="function")
def driver(config: ConfigReader) -> Generator[WebDriver, None, None]:
    """
    Function-scoped WebDriver fixture.
    Creates a fresh browser per test, quits after test completes.
    Thread-safe via DriverFactory's thread-local storage.
    """
    browser = config.browser
    headless = config.headless

    logger.info("driver_fixture_setup", browser=browser, headless=headless)
    _driver = DriverFactory.get_driver(browser=browser, headless=headless)

    yield _driver

    logger.info("driver_fixture_teardown", test="complete")
    DriverFactory.quit_driver()


@pytest.fixture(scope="function")
def authenticated_driver(driver: WebDriver, config: ConfigReader) -> WebDriver:
    """
    Pre-authenticated driver fixture.
    Logs in as admin before yielding driver.
    Use for tests that require authenticated state.
    """
    login_page = LoginPage(driver)
    login_page.open()
    login_page.login_as_admin()
    assert login_page.is_dashboard_visible(), "Login failed during fixture setup"
    logger.info("authenticated_driver_ready")
    return driver


# ──────────────────────────────────────────────────────────────────────────────
# Page Object Fixtures
# ──────────────────────────────────────────────────────────────────────────────


@pytest.fixture(scope="function")
def login_page(driver: WebDriver) -> LoginPage:
    """LoginPage fixture — fresh driver, not authenticated."""
    return LoginPage(driver)


@pytest.fixture(scope="function")
def employee_page(authenticated_driver: WebDriver) -> EmployeePage:
    """EmployeePage fixture — requires authenticated session."""
    return EmployeePage(authenticated_driver)


@pytest.fixture(scope="function")
def leave_page(authenticated_driver: WebDriver) -> LeavePage:
    """LeavePage fixture — requires authenticated session."""
    return LeavePage(authenticated_driver)


@pytest.fixture(scope="function")
def recruitment_page(authenticated_driver: WebDriver) -> RecruitmentPage:
    """RecruitmentPage fixture — requires authenticated session."""
    return RecruitmentPage(authenticated_driver)


# ──────────────────────────────────────────────────────────────────────────────
# Test Context / Data Fixtures
# ──────────────────────────────────────────────────────────────────────────────


@pytest.fixture(autouse=True)
def test_context(request: pytest.FixtureRequest, config: ConfigReader) -> Generator:
    """
    Auto-use fixture to bind test context to every log entry.
    Runs before and after every test automatically.
    """
    test_name = request.node.name
    module = request.node.module.__name__
    bind_test_context(
        test_name=test_name,
        module=module,
        browser=config.browser,
        env=os.environ.get("ENV", "dev"),
    )
    logger.info("test_started", test=test_name)

    yield

    logger.info("test_finished", test=test_name)
    clear_test_context()


@pytest.fixture(scope="session")
def test_data_dir() -> Path:
    """Path to testdata directory."""
    return Path("testdata")


@pytest.fixture(scope="session")
def faker_instance():
    """Faker instance for generating realistic test data."""
    from faker import Faker

    return Faker()
