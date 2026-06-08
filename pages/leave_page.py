"""
Enterprise Selenium HRM Framework — Leave Page
-----------------------------------------------
Page Object for OrangeHRM Leave Management Module
"""

import time
from typing import List

import allure
from selenium.webdriver.remote.webdriver import WebDriver

from locators.leave_locators import LeaveLocators
from pages.base_page import BasePage
from utilities.logger import get_logger

logger = get_logger(__name__)


class LeavePage(BasePage):
    """Encapsulates all interactions for OrangeHRM Leave Management."""

    APPLY_URL = "/web/index.php/leave/applyLeave"
    LIST_URL = "/web/index.php/leave/viewLeaveList"

    def __init__(self, driver: WebDriver) -> None:
        super().__init__(driver)

    # ── Navigation ────────────────────────────────────────────────────────────

    @allure.step("Open Apply Leave page")
    def open_apply_leave(self) -> "LeavePage":
        self.navigate_to(self.config.base_url + self.APPLY_URL)
        self.find_element(LeaveLocators.LEAVE_TYPE_DROPDOWN)
        return self

    @allure.step("Open Leave List page")
    def open_leave_list(self) -> "LeavePage":
        self.navigate_to(self.config.base_url + self.LIST_URL)
        self.find_element(LeaveLocators.SEARCH_BUTTON)
        return self

    # ── Apply Leave ───────────────────────────────────────────────────────────

    @allure.step("Apply leave: type={leave_type}, from={from_date}, to={to_date}")
    def apply_leave(
        self,
        leave_type: str,
        from_date: str,
        to_date: str,
        comment: str = "",
    ) -> "LeavePage":
        """
        Apply for leave.

        Args:
            leave_type: Leave type name (e.g., "Annual Leave")
            from_date:  From date in yyyy-mm-dd format
            to_date:    To date in yyyy-mm-dd format
            comment:    Optional comment

        Returns:
            self for method chaining
        """
        self.open_apply_leave()

        # Select leave type from custom dropdown
        self.select_custom_dropdown(LeaveLocators.LEAVE_TYPE_DROPDOWN, leave_type)
        time.sleep(0.5)

        # Enter dates
        self.clear_and_type(LeaveLocators.FROM_DATE_INPUT, from_date)
        self.press_enter(LeaveLocators.FROM_DATE_INPUT)

        self.clear_and_type(LeaveLocators.TO_DATE_INPUT, to_date)
        self.press_enter(LeaveLocators.TO_DATE_INPUT)

        if comment:
            self.type_text(LeaveLocators.COMMENT_TEXTAREA, comment)

        self.click(LeaveLocators.APPLY_BUTTON)
        logger.info(
            "leave_applied",
            type=leave_type,
            from_date=from_date,
            to_date=to_date,
        )
        return self

    # ── State Checks ──────────────────────────────────────────────────────────

    def get_leave_balance(self) -> str:
        """Get leave balance displayed on the apply page."""
        if self.is_element_visible(LeaveLocators.LEAVE_BALANCE, timeout=5):
            return self.get_text(LeaveLocators.LEAVE_BALANCE)
        return ""

    def get_success_message(self) -> str:
        """Get success toast notification text."""
        return self.wait_for_toast(timeout=10)

    def get_error_messages(self) -> List[str]:
        """Get all field validation error messages."""
        errors = self.find_elements(LeaveLocators.FIELD_ERROR)
        return [e.text.strip() for e in errors]

    def is_leave_submitted(self) -> bool:
        """Check if leave was successfully submitted (URL changes)."""
        try:
            self.wait_for_url_to_contain("viewLeaveList", timeout=5)
            return True
        except Exception:
            return self.is_element_visible(LeaveLocators.SUCCESS_TOAST, timeout=3)

    def get_leave_list_row_count(self) -> int:
        """Get number of leave records in leave list table."""
        rows = self.find_elements(LeaveLocators.LEAVE_TABLE_ROWS)
        return max(0, len(rows) - 1)  # Exclude header

    def is_no_records_displayed(self) -> bool:
        return self.is_element_visible(LeaveLocators.NO_RECORDS_MSG, timeout=5)
