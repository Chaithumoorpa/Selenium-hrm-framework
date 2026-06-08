"""
Enterprise Selenium HRM Framework — Screenshot Utilities
---------------------------------------------------------
Captures screenshots on failure, attaches to Allure reports,
and saves to timestamped files.
"""

import os
from datetime import datetime
from pathlib import Path
from typing import Optional

import allure
from selenium.webdriver.remote.webdriver import WebDriver

from utilities.logger import get_logger

logger = get_logger(__name__)

SCREENSHOT_DIR = Path("resources/screenshots")


def _ensure_dir(directory: Path) -> None:
    directory.mkdir(parents=True, exist_ok=True)


def capture_screenshot(
    driver: WebDriver,
    name: str = "screenshot",
    directory: Optional[str] = None,
    attach_to_allure: bool = True,
) -> str:
    """
    Capture a screenshot and optionally attach to Allure report.

    Args:
        driver:           WebDriver instance
        name:             Base name for the screenshot file
        directory:        Save directory (default: resources/screenshots)
        attach_to_allure: Whether to attach screenshot to Allure

    Returns:
        Absolute path to saved screenshot
    """
    save_dir = Path(directory) if directory else SCREENSHOT_DIR
    _ensure_dir(save_dir)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    safe_name = "".join(c if c.isalnum() or c in "-_" else "_" for c in name)
    filename = f"{safe_name}_{timestamp}.png"
    filepath = save_dir / filename

    try:
        driver.save_screenshot(str(filepath))
        logger.info("screenshot_saved", path=str(filepath), test=name)

        if attach_to_allure:
            with open(filepath, "rb") as f:
                allure.attach(
                    f.read(),
                    name=f"Screenshot: {name}",
                    attachment_type=allure.attachment_type.PNG,
                )
            logger.debug("screenshot_attached_to_allure", name=name)

        return str(filepath)

    except Exception as e:
        logger.error("screenshot_failed", error=str(e), test=name)
        return ""


def capture_page_source(
    driver: WebDriver,
    name: str = "page_source",
    attach_to_allure: bool = True,
) -> None:
    """Capture page HTML source and attach to Allure report."""
    try:
        source = driver.page_source
        if attach_to_allure:
            allure.attach(
                source,
                name=f"Page Source: {name}",
                attachment_type=allure.attachment_type.HTML,
            )
    except Exception as e:
        logger.error("page_source_capture_failed", error=str(e))


def attach_logs_to_allure(log_content: str, name: str = "Test Logs") -> None:
    """Attach log content as text to Allure report."""
    try:
        allure.attach(
            log_content,
            name=name,
            attachment_type=allure.attachment_type.TEXT,
        )
    except Exception as e:
        logger.error("log_attach_failed", error=str(e))
