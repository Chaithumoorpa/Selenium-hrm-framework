"""
Locators — Leave Management Page
OrangeHRM: /web/index.php/leave/viewLeaveList
"""

from selenium.webdriver.common.by import By


class LeaveLocators:
    """All locators for the Leave Management module."""

    # ── Navigation ────────────────────────────────────────────────────────────
    LEAVE_MENU_ITEM = (By.XPATH, "//span[text()='Leave']")
    APPLY_LEAVE_MENU = (By.XPATH, "//a[text()='Apply']")
    LEAVE_LIST_MENU = (By.XPATH, "//a[text()='Leave List']")
    LEAVE_ENTITLEMENT_MENU = (By.XPATH, "//a[text()='Entitlements']")

    # ── Apply Leave Page ──────────────────────────────────────────────────────
    LEAVE_TYPE_DROPDOWN = (
        By.XPATH,
        "//label[contains(text(),'Leave Type')]/following::div[contains(@class,'oxd-select-text')][1]",
    )
    LEAVE_TYPE_OPTION = (By.XPATH, "//div[@role='option']//span[text()='{}']")
    FROM_DATE_INPUT = (By.XPATH, "//label[contains(text(),'From Date')]/following::input[1]")
    TO_DATE_INPUT = (By.XPATH, "//label[contains(text(),'To Date')]/following::input[1]")
    COMMENT_TEXTAREA = (By.XPATH, "//label[contains(text(),'Comments')]/following::textarea[1]")
    APPLY_BUTTON = (By.XPATH, "//button[@type='submit']")
    CANCEL_BUTTON = (By.XPATH, "//button[@type='reset']")

    # Balance Display
    LEAVE_BALANCE = (By.XPATH, "//div[contains(@class,'orangehrm-leave-balance')]//p")

    # ── Leave List Page ───────────────────────────────────────────────────────
    DATE_FROM_FILTER = (By.XPATH, "//label[text()='Date']/following::input[1]")
    DATE_TO_FILTER = (By.XPATH, "//label[text()='Date']/following::input[2]")
    STATUS_DROPDOWN = (
        By.XPATH,
        "//label[text()='Show Leave with Status']/following::div[contains(@class,'oxd-select-text')][1]",
    )
    SEARCH_BUTTON = (By.XPATH, "//button[@type='submit']")
    LEAVE_TABLE_ROWS = (By.XPATH, "//div[@role='row'][contains(@class,'oxd-table-row')]")
    NO_RECORDS_MSG = (By.XPATH, "//span[text()='No Records Found']")

    # Leave row status
    LEAVE_STATUS_CELL = (By.XPATH, "(.//div[@role='row'][contains(@class,'oxd-table-row')])[{}]//div[5]")

    # ── Approval (Manager view) ───────────────────────────────────────────────
    APPROVE_BUTTON = (By.XPATH, "//button[text()=' Approve ']")
    REJECT_BUTTON = (By.XPATH, "//button[text()=' Reject ']")

    # ── Notifications / Toasts ────────────────────────────────────────────────
    SUCCESS_TOAST = (By.XPATH, "//p[contains(@class,'oxd-text--toast-message')]")
    ERROR_TOAST = (By.XPATH, "//p[contains(@class,'oxd-toast--error')]")

    # ── Validation Messages ───────────────────────────────────────────────────
    FIELD_ERROR = (By.XPATH, "//span[contains(@class,'oxd-input-field-error-message')]")
