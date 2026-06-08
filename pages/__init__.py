"""Pages package — Enterprise Selenium HRM Framework."""

from pages.base_page import BasePage
from pages.login_page import LoginPage
from pages.employee_page import EmployeePage
from pages.leave_page import LeavePage
from pages.recruitment_page import RecruitmentPage

__all__ = [
    "BasePage",
    "LoginPage",
    "EmployeePage",
    "LeavePage",
    "RecruitmentPage",
]
