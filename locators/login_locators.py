"""
Locators — Login Page
OrangeHRM: https://opensource-demo.orangehrmlive.com/web/index.php/auth/login
"""

from selenium.webdriver.common.by import By


class LoginLocators:
    """All locators for the Login page."""

    # ── Input Fields ──────────────────────────────────────────────────────────
    USERNAME_INPUT = (By.NAME, "username")
    PASSWORD_INPUT = (By.NAME, "password")

    # ── Buttons ───────────────────────────────────────────────────────────────
    LOGIN_BUTTON = (By.XPATH, "//button[@type='submit']")
    FORGOT_PASSWORD_LINK = (By.XPATH, "//p[contains(@class,'forgot-header')]")

    # ── Validation Messages ───────────────────────────────────────────────────
    ERROR_ALERT = (By.XPATH, "//div[contains(@class,'oxd-alert-content')]")
    FIELD_REQUIRED_MSG = (By.XPATH, "//span[contains(@class,'oxd-input-field-error-message')]")

    # ── Page Indicators ───────────────────────────────────────────────────────
    LOGIN_LOGO = (By.XPATH, "//div[contains(@class,'orangehrm-login-logo')]")
    LOGIN_TITLE = (By.XPATH, "//h5[contains(@class,'orangehrm-login-title')]")
    PAGE_TITLE = (By.XPATH, "//p[contains(@class,'orangehrm-login-slogan')]")

    # ── Dashboard (post-login) ────────────────────────────────────────────────
    DASHBOARD_HEADER = (By.XPATH, "//h6[text()='Dashboard']")
    USER_DROPDOWN = (By.XPATH, "//li[contains(@class,'oxd-userdropdown')]")
    TOP_BAR_USERNAME = (By.XPATH, "//p[contains(@class,'oxd-userdropdown-name')]")

    # ── Forgot Password Page ──────────────────────────────────────────────────
    RESET_USERNAME_INPUT = (By.NAME, "username")
    RESET_SUBMIT_BUTTON = (By.XPATH, "//button[@type='submit']")
    RESET_CANCEL_BUTTON = (By.XPATH, "//button[@type='button']")
    RESET_SUCCESS_MSG = (By.XPATH, "//div[contains(@class,'orangehrm-forgot-password-success')]")
