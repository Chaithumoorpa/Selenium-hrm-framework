"""Locators package — Enterprise Selenium HRM Framework."""

from locators.employee_locators import EmployeeLocators
from locators.leave_locators import LeaveLocators
from locators.login_locators import LoginLocators
from locators.recruitment_locators import RecruitmentLocators

__all__ = [
    "LoginLocators",
    "EmployeeLocators",
    "LeaveLocators",
    "RecruitmentLocators",
]
