"""
BDD Step Definitions — Login Feature
-------------------------------------
Implements Behave steps for features/login.feature
"""

from behave import given, when, then
from pages.login_page import LoginPage
from utilities.driver_factory import DriverFactory
from utilities.config_reader import ConfigReader


@given("the HRM login page is open")
def step_open_login_page(context):
    """Set up driver and navigate to login page."""
    config = ConfigReader.get_config()
    context.driver = DriverFactory.get_driver(browser=config.browser, headless=config.headless)
    context.login_page = LoginPage(context.driver)
    context.login_page.open()


@when('I enter username "{username}"')
def step_enter_username(context, username: str):
    context.login_page.enter_username(username)


@when('I enter password "{password}"')
def step_enter_password(context, password: str):
    context.login_page.enter_password(password)


@when("I click the Login button")
def step_click_login(context):
    context.login_page.click_login()


@then("the Dashboard page should be displayed")
def step_assert_dashboard_visible(context):
    assert context.login_page.is_dashboard_visible(), \
        "Expected Dashboard to be visible after login"


@then("the Dashboard page should NOT be displayed")
def step_assert_dashboard_not_visible(context):
    assert not context.login_page.is_dashboard_visible(), \
        "Dashboard should NOT be visible after invalid login"


@then("my username should be visible in the top navigation")
def step_assert_username_visible(context):
    username = context.login_page.get_logged_in_username()
    assert username, "Expected logged-in username in top navigation"


@then("a required validation error should be displayed for the username field")
def step_assert_username_required_error(context):
    errors = context.login_page.get_field_error_messages()
    assert any("required" in e.lower() for e in errors), \
        f"Expected 'Required' error for username. Got: {errors}"


@then("a required validation error should be displayed for the password field")
def step_assert_password_required_error(context):
    errors = context.login_page.get_field_error_messages()
    assert len(errors) > 0, f"Expected validation error for password. Got: {errors}"


@then("required validation errors should appear for both username and password")
def step_assert_both_required_errors(context):
    errors = context.login_page.get_field_error_messages()
    assert len(errors) >= 2, \
        f"Expected at least 2 required errors. Got {len(errors)}: {errors}"


@then('an error alert should be displayed with text containing "{text}"')
def step_assert_error_alert(context, text: str):
    error = context.login_page.get_error_message()
    assert error, "Expected error alert to be displayed"
    assert text.lower() in error.lower() or "invalid" in error.lower(), \
        f"Expected error containing '{text}'. Got: '{error}'"


@when('I click the "{link_text}" link')
def step_click_link(context, link_text: str):
    if "forgot" in link_text.lower():
        context.login_page.click_forgot_password()


@then("the forgot password page should be displayed")
def step_assert_forgot_password_page(context):
    context.login_page.wait_for_url_to_contain("requestPasswordResetCode")


@then('the URL should contain "{partial}"')
def step_assert_url_contains(context, partial: str):
    current_url = context.login_page.get_current_url()
    assert partial in current_url, \
        f"Expected URL to contain '{partial}'. Current: '{current_url}'"


@when("I click the user dropdown and select Logout")
def step_logout(context):
    context.login_page.logout()


@then("the Login page should be displayed")
def step_assert_login_page(context):
    assert context.login_page.is_login_page_visible(), \
        "Expected login page to be visible after logout"
