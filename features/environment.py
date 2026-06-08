"""
BDD Behave Environment Hooks
-----------------------------
Manages driver lifecycle for Behave BDD tests.
"""

from utilities.driver_factory import DriverFactory
from utilities.config_reader import ConfigReader
from utilities.logger import setup_logging


def before_all(context):
    """Run once before all features."""
    cfg = ConfigReader.get_config()
    setup_logging(
        log_level=cfg.get("logging.level", "INFO"),
        log_file="logs/behave_test.log",
    )


def before_scenario(context, scenario):
    """Initialize WebDriver before each scenario."""
    config = ConfigReader.get_config()
    context.config_obj = config


def after_scenario(context, scenario):
    """Capture screenshot on failure and quit driver."""
    if scenario.status == "failed":
        driver = getattr(context, "driver", None)
        if driver:
            from utilities.screenshot_utils import capture_screenshot
            capture_screenshot(
                driver,
                name=f"BDD_FAILURE_{scenario.name}",
                attach_to_allure=False,
            )
    DriverFactory.quit_driver()


def after_all(context):
    """Cleanup after all features."""
    DriverFactory.quit_driver()
