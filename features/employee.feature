# =============================================================================
# Feature: Employee Management (PIM)
# Application: OrangeHRM HRM Portal
# =============================================================================

Feature: Employee Management
  As an HRM Administrator
  I want to manage employee records
  So that employee information is accurate and up to date

  Background:
    Given I am logged in as Admin

  @smoke @employee
  Scenario: Add new employee with required fields
    Given I navigate to the Add Employee page
    When I enter first name "Alice"
    And I enter last name "Johnson"
    And I click Save
    Then the employee profile page should be displayed
    And an employee ID should be assigned

  @regression @employee
  Scenario: Search employee by first name returns results
    Given I navigate to the Employee List page
    When I search for employees with first name "Admin"
    And I click Search
    Then at least one employee record should appear in results

  @regression @negative @employee
  Scenario: Search for non-existent employee shows no records
    Given I navigate to the Employee List page
    When I search for employees with first name "ZZZNonExistentXXX999"
    And I click Search
    Then "No Records Found" message should be displayed

  @regression @employee
  Scenario Outline: Add multiple employees with different names
    Given I navigate to the Add Employee page
    When I enter first name "<first>"
    And I enter last name "<last>"
    And I click Save
    Then the employee should be created successfully

    Examples:
      | first | last      |
      | Bob   | Williams  |
      | Carol | Davis     |
      | David | Martinez  |
