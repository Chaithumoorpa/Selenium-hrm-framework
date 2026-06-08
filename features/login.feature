# =============================================================================
# Feature: Login Module
# Application: OrangeHRM HRM Portal
# Author: SDET Automation Engineer
# =============================================================================

Feature: HRM Portal Login
  As an HRM system user
  I want to authenticate securely
  So that I can access the HRM portal features

  Background:
    Given the HRM login page is open

  @smoke @login
  Scenario: Successful login with valid admin credentials
    When I enter username "Admin"
    And I enter password "admin123"
    And I click the Login button
    Then the Dashboard page should be displayed
    And my username should be visible in the top navigation

  @regression @negative @login
  Scenario: Login with empty username shows required error
    When I enter password "admin123"
    And I click the Login button
    Then a required validation error should be displayed for the username field

  @regression @negative @login
  Scenario: Login with empty password shows required error
    When I enter username "Admin"
    And I click the Login button
    Then a required validation error should be displayed for the password field

  @regression @negative @login
  Scenario: Login with both fields empty shows dual validation errors
    When I click the Login button
    Then required validation errors should appear for both username and password

  @regression @negative @login
  Scenario Outline: Login with invalid credentials shows error alert
    When I enter username "<username>"
    And I enter password "<password>"
    And I click the Login button
    Then an error alert should be displayed with text containing "Invalid credentials"
    And the Dashboard page should NOT be displayed

    Examples:
      | username    | password   | description          |
      | InvalidUser | admin123   | Invalid username     |
      | Admin       | WrongPass  | Invalid password     |
      | admin       | admin123   | Case sensitive user  |

  @regression @login
  Scenario: Forgot password link navigates to reset page
    When I click the "Forgot your password?" link
    Then the forgot password page should be displayed
    And the URL should contain "requestPasswordResetCode"

  @smoke @regression @login
  Scenario: Successful logout after login
    When I enter username "Admin"
    And I enter password "admin123"
    And I click the Login button
    And the Dashboard page should be displayed
    When I click the user dropdown and select Logout
    Then the Login page should be displayed
    And the URL should contain "auth/login"
