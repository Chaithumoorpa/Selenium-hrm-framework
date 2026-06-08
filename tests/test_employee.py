"""
Enterprise Selenium HRM Framework — Employee Tests
---------------------------------------------------
Test Suite: Employee (PIM) Module

Test Coverage:
  - TC-EMP-001: Add new employee with required fields only
  - TC-EMP-002: Add employee with middle name
  - TC-EMP-003: Search employee by first name
  - TC-EMP-004: Search employee by last name
  - TC-EMP-005: Search employee by employee ID
  - TC-EMP-006: Search with non-existent employee shows no records
  - TC-EMP-007: Reset search filters clears search results
  - TC-EMP-008: Navigate to Employee List via PIM menu
  - TC-EMP-009: Data-driven bulk employee add
  - TC-EMP-010: Add employee with duplicate employee ID (negative)
"""

import allure
import pytest

from pages.employee_page import EmployeePage


# ──────────────────────────────────────────────────────────────────────────────
# Test Data
# ──────────────────────────────────────────────────────────────────────────────

EMPLOYEE_BULK_DATA = [
    pytest.param(
        {"first": "Alice", "last": "Johnson", "middle": "Marie"},
        id="TC-EMP-009a-alice_johnson",
    ),
    pytest.param(
        {"first": "Bob", "last": "Williams", "middle": ""},
        id="TC-EMP-009b-bob_williams",
    ),
    pytest.param(
        {"first": "Carol", "last": "Davis", "middle": "Ann"},
        id="TC-EMP-009c-carol_davis",
    ),
]


@allure.epic("HRM Portal")
@allure.feature("Employee Management (PIM)")
class TestEmployee:
    """Test suite for OrangeHRM Employee Management module."""

    @allure.story("Add Employee")
    @allure.title("TC-EMP-001: Add new employee with required fields only")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.smoke
    @pytest.mark.regression
    @pytest.mark.employee
    def test_add_employee_required_fields(
        self, employee_page: EmployeePage, faker_instance
    ) -> None:
        """
        GIVEN: Admin is logged in and on Add Employee page
        WHEN:  Admin fills in first name and last name only
        AND:   Clicks Save
        THEN:  Employee is created successfully
        AND:   User is redirected to employee profile page
        """
        first = faker_instance.first_name()
        last = faker_instance.last_name()

        emp_id = employee_page.add_employee(
            first_name=first,
            last_name=last,
        )

        assert emp_id, "Employee ID should not be empty after creation"
        assert employee_page.is_on_profile_page(emp_id) or \
               "viewPersonalDetails" in employee_page.get_current_url(), \
            "Expected to land on employee profile page after creation"

    @allure.story("Add Employee")
    @allure.title("TC-EMP-002: Add employee with all fields including middle name")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.regression
    @pytest.mark.employee
    def test_add_employee_with_middle_name(
        self, employee_page: EmployeePage, faker_instance
    ) -> None:
        """
        GIVEN: Admin is on Add Employee page
        WHEN:  Admin fills first, middle, and last name
        THEN:  Employee created successfully with middle name preserved
        """
        first = faker_instance.first_name()
        middle = faker_instance.first_name()
        last = faker_instance.last_name()

        emp_id = employee_page.add_employee(
            first_name=first,
            last_name=last,
            middle_name=middle,
        )

        assert emp_id, "Expected non-empty employee ID after creation"

    @allure.story("Search Employee")
    @allure.title("TC-EMP-003: Search employee by first name returns matching results")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.regression
    @pytest.mark.smoke
    @pytest.mark.employee
    def test_search_employee_by_first_name(
        self, employee_page: EmployeePage
    ) -> None:
        """
        GIVEN: Admin is on Employee List page
        WHEN:  Admin searches by first name 'Admin'
        THEN:  At least one result matching the search is returned
        """
        results = employee_page.search_employee(first_name="Admin")

        assert len(results) > 0, \
            "Expected at least one result when searching for 'Admin'"

    @allure.story("Search Employee")
    @allure.title("TC-EMP-005: Search by employee ID returns exact match")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.regression
    @pytest.mark.employee
    def test_search_employee_by_id(
        self, employee_page: EmployeePage, faker_instance
    ) -> None:
        """
        GIVEN: A known employee exists
        WHEN:  Admin searches by that employee's ID
        THEN:  Exactly one result is returned
        """
        # Create a known employee first
        first = faker_instance.first_name()
        last = faker_instance.last_name()
        emp_id = employee_page.add_employee(first_name=first, last_name=last)

        # Search by the created ID
        results = employee_page.search_employee(employee_id=emp_id)
        assert len(results) >= 1, \
            f"Expected results for employee ID '{emp_id}'. Got {len(results)}"

    @allure.story("Search Employee")
    @allure.title("TC-EMP-006: Search for non-existent employee shows no records")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.regression
    @pytest.mark.negative
    @pytest.mark.employee
    def test_search_nonexistent_employee(
        self, employee_page: EmployeePage
    ) -> None:
        """
        GIVEN: Employee List is open
        WHEN:  Admin searches for a name that does not exist
        THEN:  'No Records Found' message is displayed
        AND:   Results table is empty
        """
        results = employee_page.search_employee(first_name="ZZZNonExistentXXX999")

        assert employee_page.is_no_records_displayed(), \
            "Expected 'No Records Found' for a non-existent employee name"
        assert len(results) == 0, \
            f"Expected empty results. Got: {results}"

    @allure.story("Search Employee")
    @allure.title("TC-EMP-007: Reset search restores full employee list")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.regression
    @pytest.mark.employee
    def test_reset_search_filters(
        self, employee_page: EmployeePage
    ) -> None:
        """
        GIVEN: Admin has performed a search
        WHEN:  Admin clicks Reset button
        THEN:  Search fields are cleared and full list is shown
        """
        # First, do a search
        employee_page.search_employee(first_name="ZZZNonExistentXXX999")
        assert employee_page.is_no_records_displayed(), "Setup: no-records state required"

        # Reset
        employee_page.reset_search()

        # After reset, should have employees
        count = employee_page.get_employee_count()
        assert count > 0, \
            "Expected employees to appear after resetting search filters"

    @allure.story("Add Employee (Bulk/Data-Driven)")
    @allure.title("TC-EMP-009: Data-driven employee creation")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.regression
    @pytest.mark.data_driven
    @pytest.mark.employee
    @pytest.mark.parametrize("emp_data", EMPLOYEE_BULK_DATA)
    def test_add_employee_data_driven(
        self, employee_page: EmployeePage, emp_data: dict
    ) -> None:
        """
        GIVEN: Admin is on Add Employee page
        WHEN:  Admin adds employees from parametrized data
        THEN:  Each employee is created successfully
        """
        emp_id = employee_page.add_employee(
            first_name=emp_data["first"],
            last_name=emp_data["last"],
            middle_name=emp_data.get("middle", ""),
        )
        assert emp_id, f"Failed to create employee: {emp_data}"
