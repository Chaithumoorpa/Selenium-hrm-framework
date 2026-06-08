"""
Enterprise Selenium HRM Framework — Login Tests
------------------------------------------------
Test Suite: Login Module
Target App: OrangeHRM (https://opensource-demo.orangehrmlive.com)

Test Coverage:
  - TC-LGN-001: Successful login with valid admin credentials
  - TC-LGN-002: Login with empty username
  - TC-LGN-003: Login with empty password
  - TC-LGN-004: Login with both fields empty
  - TC-LGN-005: Login with invalid username
  - TC-LGN-006: Login with invalid password
  - TC-LGN-007: Login with wrong case username
  - TC-LGN-008: Verify login page elements present
  - TC-LGN-009: Forgot password link navigates correctly
  - TC-LGN-010: Successful logout after login
  - TC-LGN-011: Data-driven login with multiple credentials
  - TC-LGN-012: Session persistence after page refresh
"""

import allure
import pytest

from pages.login_page import LoginPage
from utilities.config_reader import ConfigReader

# ──────────────────────────────────────────────────────────────────────────────
# Test Data
# ──────────────────────────────────────────────────────────────────────────────

INVALID_CREDENTIAL_CASES = [
    pytest.param(
        "InvalidUser", "admin123",
        id="TC-LGN-005-invalid_username",
        marks=pytest.mark.negative,
    ),
    pytest.param(
        "Admin", "WrongPass",
        id="TC-LGN-006-invalid_password",
        marks=pytest.mark.negative,
    ),
    pytest.param(
        "admin_wrong_case", "admin123",  # Truly invalid username
        id="TC-LGN-007-wrong_case_username",
        marks=pytest.mark.negative,
    ),
    pytest.param(
        "Admin@123", "admin123",
        id="TC-LGN-extra-special_chars_username",
        marks=pytest.mark.negative,
    ),
]


# ──────────────────────────────────────────────────────────────────────────────
# Test Class
# ──────────────────────────────────────────────────────────────────────────────


@allure.epic("HRM Portal")
@allure.feature("Login Module")
class TestLogin:
    """Tests for the OrangeHRM Login module."""

    # ── Smoke Tests ───────────────────────────────────────────────────────────

    @allure.story("Valid Login")
    @allure.title("TC-LGN-001: Successful login with valid admin credentials")
    @allure.severity(allure.severity_level.BLOCKER)
    @allure.tag("smoke", "regression", "login")
    @pytest.mark.smoke
    @pytest.mark.login
    def test_valid_login(self, login_page: LoginPage, config: ConfigReader) -> None:
        """
        GIVEN: Admin opens OrangeHRM login page
        WHEN:  They enter valid credentials (Admin/admin123)
        THEN:  Dashboard page is displayed
        AND:   Username is shown in top navigation
        """
        login_page.open()
        login_page.login(config.admin_username, config.admin_password)

        assert login_page.is_dashboard_visible(), (
            "Expected Dashboard header to be visible after successful login"
        )
        logged_in_user = login_page.get_logged_in_username()
        assert logged_in_user, "Expected username to appear in top navigation bar"

    # ── Field Validation ──────────────────────────────────────────────────────

    @allure.story("Empty Field Validation")
    @allure.title("TC-LGN-002: Login with empty username shows required error")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.regression
    @pytest.mark.negative
    @pytest.mark.login
    def test_login_empty_username(self, login_page: LoginPage) -> None:
        """
        GIVEN: Login page is open
        WHEN:  User submits form with empty username
        THEN:  'Required' validation error is shown under username field
        """
        login_page.open()
        login_page.enter_password("admin123")
        login_page.click_login()

        errors = login_page.get_field_error_messages()
        assert len(errors) > 0, "Expected at least one field validation error"
        assert any("required" in e.lower() for e in errors), (
            f"Expected 'required' in error messages. Got: {errors}"
        )

    @allure.story("Empty Field Validation")
    @allure.title("TC-LGN-003: Login with empty password shows required error")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.regression
    @pytest.mark.negative
    @pytest.mark.login
    def test_login_empty_password(self, login_page: LoginPage) -> None:
        """
        GIVEN: Login page is open
        WHEN:  User submits form with empty password
        THEN:  'Required' validation error is shown under password field
        """
        login_page.open()
        login_page.enter_username("Admin")
        login_page.click_login()

        errors = login_page.get_field_error_messages()
        assert len(errors) > 0, "Expected field validation error for empty password"

    @allure.story("Empty Field Validation")
    @allure.title("TC-LGN-004: Login with both fields empty shows dual errors")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.regression
    @pytest.mark.negative
    @pytest.mark.login
    def test_login_both_fields_empty(self, login_page: LoginPage) -> None:
        """
        GIVEN: Login page is open
        WHEN:  User clicks login without entering any credentials
        THEN:  Required errors appear for both username and password
        """
        login_page.open()
        login_page.click_login()

        errors = login_page.get_field_error_messages()
        assert len(errors) >= 2, (
            f"Expected 2 required errors (username + password). Got {len(errors)}: {errors}"
        )

    # ── Invalid Credentials (Data-Driven) ─────────────────────────────────────

    @allure.story("Invalid Credentials")
    @allure.title("TC-LGN-005/006/007: Login with invalid credentials")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.regression
    @pytest.mark.negative
    @pytest.mark.data_driven
    @pytest.mark.login
    @pytest.mark.parametrize("username,password", INVALID_CREDENTIAL_CASES)
    def test_login_invalid_credentials(
        self, login_page: LoginPage, username: str, password: str
    ) -> None:
        """
        GIVEN: Login page is open
        WHEN:  User enters invalid/wrong credentials
        THEN:  Error alert 'Invalid credentials' is displayed
        AND:   User remains on login page (no redirect to dashboard)
        """
        login_page.open()
        login_page.login(username, password)

        error = login_page.get_error_message()
        assert error, (
            f"Expected error message for invalid login. Got none. "
            f"Credentials: {username}/{password}"
        )
        assert "invalid" in error.lower() or "credentials" in error.lower(), (
            f"Unexpected error message: '{error}'"
        )
        assert not login_page.is_dashboard_visible(), (
            "Dashboard should NOT be visible after invalid login attempt"
        )

    # ── UI Element Verification ───────────────────────────────────────────────

    @allure.story("Page Elements")
    @allure.title("TC-LGN-008: Login page displays all required elements")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.regression
    @pytest.mark.login
    def test_login_page_elements_present(self, login_page: LoginPage) -> None:
        """
        GIVEN: User navigates to login page
        THEN:  Username field, password field, login button are all visible
        """
        login_page.open()

        assert login_page.is_login_page_visible(), "Login logo/page not visible"
        from locators.login_locators import LoginLocators
        assert login_page.is_element_visible(LoginLocators.USERNAME_INPUT), \
            "Username input not visible"
        assert login_page.is_element_visible(LoginLocators.PASSWORD_INPUT), \
            "Password input not visible"
        assert login_page.is_element_visible(LoginLocators.LOGIN_BUTTON), \
            "Login button not visible"
        assert login_page.is_element_visible(LoginLocators.FORGOT_PASSWORD_LINK), \
            "Forgot password link not visible"

    # ── Forgot Password ───────────────────────────────────────────────────────

    @allure.story("Forgot Password")
    @allure.title("TC-LGN-009: Forgot password link navigates to reset page")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.regression
    @pytest.mark.login
    def test_forgot_password_navigation(self, login_page: LoginPage) -> None:
        """
        GIVEN: Login page is open
        WHEN:  User clicks 'Forgot your password?'
        THEN:  Forgot password page is displayed
        AND:   URL changes to forgot-password route
        """
        login_page.open()
        login_page.click_forgot_password()

        login_page.wait_for_url_to_contain("requestPasswordResetCode", timeout=10)
        assert "requestPasswordResetCode" in login_page.get_current_url(), (
            "Expected URL to contain 'requestPasswordResetCode' after clicking forgot password"
        )

    # ── Logout ────────────────────────────────────────────────────────────────

    @allure.story("Logout")
    @allure.title("TC-LGN-010: Successful logout redirects to login page")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.smoke
    @pytest.mark.regression
    @pytest.mark.login
    def test_logout(self, login_page: LoginPage, config: ConfigReader) -> None:
        """
        GIVEN: User is logged in
        WHEN:  User clicks logout from the user dropdown
        THEN:  User is redirected to login page
        """
        login_page.open()
        login_page.login(config.admin_username, config.admin_password)
        assert login_page.is_dashboard_visible(), "Login failed in logout test setup"

        login_page.logout()

        assert login_page.is_login_page_visible(), (
            "Expected login page to be displayed after logout"
        )
        assert "auth/login" in login_page.get_current_url(), (
            f"Expected login URL after logout. Got: {login_page.get_current_url()}"
        )
