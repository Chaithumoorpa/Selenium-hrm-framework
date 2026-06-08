"""
Enterprise Selenium HRM Framework — Employee Page
--------------------------------------------------
Page Object for OrangeHRM PIM (Employee) Module
URL: /web/index.php/pim/viewEmployeeList
"""

import time
from typing import List

import allure
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver

from locators.employee_locators import EmployeeLocators
from pages.base_page import BasePage
from utilities.logger import get_logger

logger = get_logger(__name__)


class EmployeePage(BasePage):
    """
    Encapsulates all interactions for OrangeHRM Employee Management.

    Covers:
      - Navigate to PIM module
      - Add new employee
      - Search employee
      - Update employee details
      - Delete employee
    """

    LIST_URL = "/web/index.php/pim/viewEmployeeList"
    ADD_URL = "/web/index.php/pim/addEmployee"

    def __init__(self, driver: WebDriver) -> None:
        super().__init__(driver)

    # ── Navigation ────────────────────────────────────────────────────────────

    @allure.step("Navigate to Employee List")
    def open_employee_list(self) -> "EmployeePage":
        self.navigate_to(self.config.base_url + self.LIST_URL)
        self.wait_for_list_page()
        return self

    @allure.step("Navigate to Add Employee")
    def open_add_employee(self) -> "EmployeePage":
        self.navigate_to(self.config.base_url + self.ADD_URL)
        self.find_element(EmployeeLocators.ADD_EMP_FIRSTNAME)
        return self

    @allure.step("Click PIM menu item")
    def click_pim_menu(self) -> "EmployeePage":
        self.click(EmployeeLocators.PIM_MENU_ITEM)
        return self

    def wait_for_list_page(self) -> None:
        self.find_element(EmployeeLocators.SEARCH_BUTTON)

    # ── Add Employee ──────────────────────────────────────────────────────────

    @allure.step("Add employee: {first_name} {last_name}")
    def add_employee(
        self,
        first_name: str,
        last_name: str,
        middle_name: str = "",
        employee_id: str = "",
        create_login: bool = False,
        username: str = "",
        password: str = "",
    ) -> str:
        """
        Add a new employee through the Add Employee form.

        Args:
            first_name:   Employee first name
            last_name:    Employee last name
            middle_name:  Middle name (optional)
            employee_id:  Custom employee ID (auto-generated if empty)
            create_login: Whether to create a system login for the employee
            username:     Login username (if create_login=True)
            password:     Login password (if create_login=True)

        Returns:
            Employee ID of the created employee
        """
        self.open_add_employee()

        self.type_text(EmployeeLocators.ADD_EMP_FIRSTNAME, first_name)
        if middle_name:
            self.type_text(EmployeeLocators.ADD_EMP_MIDDLENAME, middle_name)
        self.type_text(EmployeeLocators.ADD_EMP_LASTNAME, last_name)

        if employee_id:
            self.clear_and_type(EmployeeLocators.ADD_EMP_ID, employee_id)

        # Get generated employee ID before saving
        current_emp_id = self.get_input_value(EmployeeLocators.ADD_EMP_ID)

        if create_login and username and password:
            self.click(EmployeeLocators.CREATE_LOGIN_TOGGLE)
            time.sleep(0.5)
            self.type_text(EmployeeLocators.ADD_EMP_USERNAME, username)
            self.type_text(EmployeeLocators.ADD_EMP_PASSWORD, password)
            self.type_text(EmployeeLocators.ADD_EMP_CONFIRM_PASS, password)

        self.click(EmployeeLocators.SAVE_BUTTON)
        self.wait_for_url_to_contain("viewPersonalDetails", timeout=15)

        logger.info(
            "employee_added",
            first=first_name,
            last=last_name,
            emp_id=current_emp_id,
        )
        return current_emp_id

    # ── Search Employee ───────────────────────────────────────────────────────

    @allure.step("Search employee by name: {first_name} {last_name}")
    def search_employee(
        self,
        first_name: str = "",
        last_name: str = "",
        employee_id: str = "",
    ) -> List[dict]:
        """
        Search employees using the Employee List search form.

        Returns:
            List of dicts with employee row data
        """
        self.open_employee_list()

        if first_name:
            self.type_text(EmployeeLocators.SEARCH_FIRSTNAME, first_name)
        if last_name:
            self.type_text(EmployeeLocators.SEARCH_LASTNAME, last_name)
        if employee_id:
            self.type_text(EmployeeLocators.SEARCH_EMPLOYEE_ID, employee_id)

        self.click(EmployeeLocators.SEARCH_BUTTON)
        time.sleep(1.5)  # Wait for result render

        return self._get_table_rows()

    def _get_table_rows(self) -> List[dict]:
        """Extract all table rows from the employee list."""
        if self.is_element_visible(EmployeeLocators.NO_RECORDS_MSG, timeout=3):
            return []

        rows = self.find_elements(EmployeeLocators.EMPLOYEE_ROWS)
        result = []
        for row in rows[1:]:  # Skip header row
            cells = row.find_elements(By.XPATH, ".//div[@role='cell']")
            if cells:
                result.append({
                    "id": cells[1].text.strip() if len(cells) > 1 else "",
                    "name": cells[2].text.strip() if len(cells) > 2 else "",
                    "job_title": cells[3].text.strip() if len(cells) > 3 else "",
                    "status": cells[5].text.strip() if len(cells) > 5 else "",
                })
        logger.info("employee_search_results", count=len(result))
        return result

    @allure.step("Reset search filters")
    def reset_search(self) -> "EmployeePage":
        """Click reset to clear search filters."""
        self.click(EmployeeLocators.RESET_BUTTON)
        time.sleep(1)
        return self

    # ── State Checks ──────────────────────────────────────────────────────────

    def get_employee_count(self) -> int:
        """Get total count of employees shown in results."""
        rows = self.find_elements(EmployeeLocators.EMPLOYEE_ROWS)
        return max(0, len(rows) - 1)  # Exclude header

    def is_no_records_displayed(self) -> bool:
        """Check if 'No Records Found' message is visible."""
        return self.is_element_visible(EmployeeLocators.NO_RECORDS_MSG, timeout=5)

    def get_success_toast(self) -> str:
        """Get success toast message text."""
        return self.wait_for_toast()

    def is_on_profile_page(self, employee_id: str) -> bool:
        """Verify we are on the correct employee profile page."""
        return employee_id in self.get_current_url()
