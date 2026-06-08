"""
Locators — Employee (PIM) Page
OrangeHRM: /web/index.php/pim/viewEmployeeList
"""

from selenium.webdriver.common.by import By


class EmployeeLocators:
    """All locators for Employee Management (PIM) module."""

    # ── Navigation ────────────────────────────────────────────────────────────
    PIM_MENU_ITEM = (By.XPATH, "//span[text()='PIM']")
    EMPLOYEE_LIST_MENU = (By.XPATH, "//a[text()='Employee List']")
    ADD_EMPLOYEE_MENU = (By.XPATH, "//a[text()='Add Employee']")

    # ── Employee List Page ────────────────────────────────────────────────────
    SEARCH_FIRSTNAME = (
        By.XPATH,
        "//label[contains(text(),'Employee Name')]/ancestor::div[contains(@class,'oxd-input-group')]//input",
    )
    SEARCH_LASTNAME = (
        By.XPATH,
        "//label[contains(text(),'Employee Name')]/ancestor::div[contains(@class,'oxd-input-group')]//input",
    )
    SEARCH_EMPLOYEE_ID = (By.XPATH, "//label[text()='Employee Id']/following::input[1]")
    SEARCH_BUTTON = (By.XPATH, "//button[@type='submit']")
    RESET_BUTTON = (By.XPATH, "//button[@type='reset']")

    EMPLOYEE_TABLE = (By.XPATH, "//div[contains(@class,'oxd-table')]")
    EMPLOYEE_ROWS = (By.XPATH, "//div[@role='row'][contains(@class,'oxd-table-row')]")
    NO_RECORDS_MSG = (By.XPATH, "//span[text()='No Records Found']")

    # First result row cells
    FIRST_ROW_ID = (By.XPATH, "(//div[@role='row'][contains(@class,'oxd-table-row')])[2]//div[2]")
    FIRST_ROW_FULLNAME = (By.XPATH, "(//div[@role='row'][contains(@class,'oxd-table-row')])[2]//div[3]")

    # ── Add Employee Page ─────────────────────────────────────────────────────
    ADD_EMP_FIRSTNAME = (By.NAME, "firstName")
    ADD_EMP_MIDDLENAME = (By.NAME, "middleName")
    ADD_EMP_LASTNAME = (By.NAME, "lastName")
    ADD_EMP_ID = (By.XPATH, "//label[text()='Employee Id']/following::input[1]")
    ADD_EMP_PHOTO = (By.XPATH, "//input[@type='file']")
    CREATE_LOGIN_TOGGLE = (By.XPATH, "//span[contains(@class,'oxd-switch-input')]")
    ADD_EMP_USERNAME = (By.XPATH, "//label[text()='Username']/following::input[1]")
    ADD_EMP_PASSWORD = (By.XPATH, "//label[text()='Password']/following::input[1]")
    ADD_EMP_CONFIRM_PASS = (By.XPATH, "//label[text()='Confirm Password']/following::input[1]")
    SAVE_BUTTON = (By.XPATH, "//button[@type='submit']")

    # ── Employee Profile Page ─────────────────────────────────────────────────
    PROFILE_FIRSTNAME = (By.NAME, "firstName")
    PROFILE_LASTNAME = (By.NAME, "lastName")
    PROFILE_EMPLOYEE_ID = (By.XPATH, "//label[text()='Employee Id']/following::input[1]")
    PROFILE_SAVE_BUTTON = (By.XPATH, "//button[@type='submit']")
    SUCCESS_TOAST = (
        By.XPATH,
        "//div[contains(@class,'oxd-toast-content')]//p[contains(@class,'oxd-text--toast-message')]",
    )

    # ── Delete Employee ───────────────────────────────────────────────────────
    DELETE_CHECKBOX_ALL = (By.XPATH, "//label[contains(@class,'oxd-checkbox-input-icon')]")
    DELETE_BUTTON = (By.XPATH, "//button[contains(@class,'delete-btn')]")
    CONFIRM_DELETE_BUTTON = (By.XPATH, "//button[text()=' Yes, Delete ']")
    CANCEL_DELETE_BUTTON = (By.XPATH, "//button[text()=' No, Cancel ']")
