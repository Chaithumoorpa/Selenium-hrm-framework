"""
Enterprise Selenium HRM Framework — Login Page
-----------------------------------------------
Page Object for OrangeHRM Login
URL: https://opensource-demo.orangehrmlive.com/web/index.php/auth/login
"""

import allure
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver

from locators.login_locators import LoginLocators
from pages.base_page import BasePage
from utilities.logger import get_logger

logger = get_logger(__name__)


class LoginPage(BasePage):
    """
    Encapsulates all interactions on the OrangeHRM Login page.

    Usage:
        login_page = LoginPage(driver)
        login_page.login("Admin", "admin123")
        assert login_page.is_dashboard_visible()
    """

    PAGE_URL = "/web/index.php/auth/login"

    def __init__(self, driver: WebDriver) -> None:
        super().__init__(driver)

    # ── Navigation ────────────────────────────────────────────────────────────

    @allure.step("Open Login page")
    def open(self) -> "LoginPage":
        """Navigate to the login page."""
        url = self.config.base_url + self.PAGE_URL
        self.navigate_to(url)
        self.wait_for_page_ready()
        logger.info("login_page_opened", url=url)
        return self

    def wait_for_page_ready(self) -> None:
        """Wait until login form is rendered."""
        self.find_element(LoginLocators.USERNAME_INPUT)

    # ── Actions ───────────────────────────────────────────────────────────────

    @allure.step("Enter username: {username}")
    def enter_username(self, username: str) -> "LoginPage":
        """Type username into the username input field."""
        self.type_text(LoginLocators.USERNAME_INPUT, username)
        logger.debug("username_entered", username=username)
        return self

    @allure.step("Enter password")
    def enter_password(self, password: str) -> "LoginPage":
        """Type password into the password input field."""
        self.type_text(LoginLocators.PASSWORD_INPUT, password)
        return self

    @allure.step("Click Login button")
    def click_login(self) -> "LoginPage":
        """Click the login submit button."""
        self.click(LoginLocators.LOGIN_BUTTON)
        return self

    @allure.step("Login with username='{username}'")
    def login(self, username: str, password: str) -> "LoginPage":
        """
        Complete login flow: enter credentials + submit.

        Args:
            username: HRM username
            password: HRM password

        Returns:
            self for method chaining
        """
        self.enter_username(username)
        self.enter_password(password)
        self.click_login()
        logger.info("login_submitted", username=username)
        return self

    @allure.step("Login as Admin using config credentials")
    def login_as_admin(self) -> "LoginPage":
        """Login using admin credentials from config."""
        return self.login(
            self.config.admin_username,
            self.config.admin_password,
        )

    @allure.step("Click Forgot Password link")
    def click_forgot_password(self) -> None:
        """Click the 'Forgot your password?' link."""
        self.click(LoginLocators.FORGOT_PASSWORD_LINK)

    @allure.step("Submit forgot password for username: {username}")
    def submit_forgot_password(self, username: str) -> None:
        """Fill and submit the forgot password form."""
        self.type_text(LoginLocators.RESET_USERNAME_INPUT, username)
        self.click(LoginLocators.RESET_SUBMIT_BUTTON)

    @allure.step("Cancel forgot password")
    def cancel_forgot_password(self) -> None:
        """Click the Cancel button on the forgot password page."""
        self.click(LoginLocators.RESET_CANCEL_BUTTON)

    # ── Assertions / State Checks ─────────────────────────────────────────────

    def is_login_page_visible(self) -> bool:
        """Verify login page is displayed."""
        return self.is_element_visible(LoginLocators.LOGIN_LOGO)

    def is_dashboard_visible(self) -> bool:
        """Verify successful login by checking Dashboard header."""
        return self.is_element_visible(LoginLocators.DASHBOARD_HEADER, timeout=15)

    def get_error_message(self) -> str:
        """Get the error alert text (invalid credentials)."""
        if self.is_element_visible(LoginLocators.ERROR_ALERT, timeout=5):
            return self.get_text(LoginLocators.ERROR_ALERT)
        return ""

    def get_field_error_messages(self) -> list:
        """Get all field-level validation error messages."""
        errors = self.find_elements(LoginLocators.FIELD_REQUIRED_MSG)
        return [e.text.strip() for e in errors]

    def get_logged_in_username(self) -> str:
        """Get the username shown in the top navigation bar."""
        if self.is_element_visible(LoginLocators.TOP_BAR_USERNAME, timeout=10):
            return self.get_text(LoginLocators.TOP_BAR_USERNAME)
        return ""

    def is_reset_success_visible(self) -> bool:
        """Verify the forgot password success message is shown."""
        return self.is_element_visible(LoginLocators.RESET_SUCCESS_MSG, timeout=10)

    @allure.step("Logout")
    def logout(self) -> None:
        """Click user dropdown and logout."""
        self.click(LoginLocators.USER_DROPDOWN)
        logout_locator = (By.XPATH, "//a[text()='Logout']")
        self.click(logout_locator)
        self.wait_for_page_ready()
        logger.info("user_logged_out")
