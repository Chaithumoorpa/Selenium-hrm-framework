"""
Enterprise Selenium HRM Framework — Recruitment Page
-----------------------------------------------------
Page Object for OrangeHRM Recruitment Module
"""

import time

import allure
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver

from locators.recruitment_locators import RecruitmentLocators
from pages.base_page import BasePage
from utilities.logger import get_logger

logger = get_logger(__name__)


class RecruitmentPage(BasePage):
    """Encapsulates interactions for the Recruitment module."""

    VACANCIES_URL = "/web/index.php/recruitment/viewJobVacancy"
    CANDIDATES_URL = "/web/index.php/recruitment/viewCandidates"
    ADD_VACANCY_URL = "/web/index.php/recruitment/addJobVacancy"

    def __init__(self, driver: WebDriver) -> None:
        super().__init__(driver)

    # ── Navigation ────────────────────────────────────────────────────────────

    @allure.step("Open Vacancies page")
    def open_vacancies(self) -> "RecruitmentPage":
        self.navigate_to(self.config.base_url + self.VACANCIES_URL)
        self.find_element(RecruitmentLocators.ADD_VACANCY_BUTTON)
        return self

    @allure.step("Open Candidates page")
    def open_candidates(self) -> "RecruitmentPage":
        self.navigate_to(self.config.base_url + self.CANDIDATES_URL)
        return self

    # ── Add Vacancy ───────────────────────────────────────────────────────────

    @allure.step("Add vacancy: {vacancy_name}")
    def add_vacancy(
        self,
        vacancy_name: str,
        job_title: str,
        hiring_manager: str,
        positions: str = "1",
        description: str = "",
        status: str = "Active",
    ) -> "RecruitmentPage":
        """Create a new job vacancy."""
        self.navigate_to(self.config.base_url + self.ADD_VACANCY_URL)
        self.find_element(RecruitmentLocators.VACANCY_NAME_INPUT)

        self.type_text(RecruitmentLocators.VACANCY_NAME_INPUT, vacancy_name)
        self.select_custom_dropdown(RecruitmentLocators.JOB_TITLE_DROPDOWN, job_title)
        self.type_text(RecruitmentLocators.HIRING_MANAGER, hiring_manager)

        # Wait for autocomplete and click first suggestion
        time.sleep(1)
        options = self.find_elements((By.XPATH, "//div[@role='option']"))
        if options:
            options[0].click()

        self.clear_and_type(RecruitmentLocators.NO_OF_POSITIONS, positions)
        if description:
            self.type_text(RecruitmentLocators.DESCRIPTION_TEXTAREA, description)

        self.click(RecruitmentLocators.SAVE_BUTTON)
        logger.info("vacancy_added", name=vacancy_name, title=job_title)
        return self

    # ── Add Candidate ─────────────────────────────────────────────────────────

    @allure.step("Add candidate: {first_name} {last_name}")
    def add_candidate(
        self,
        first_name: str,
        last_name: str,
        email: str,
        vacancy: str,
    ) -> "RecruitmentPage":
        """Add a new candidate to a vacancy."""
        self.click(RecruitmentLocators.ADD_CANDIDATE_BUTTON)
        self.type_text(RecruitmentLocators.CANDIDATE_FIRSTNAME, first_name)
        self.type_text(RecruitmentLocators.CANDIDATE_LASTNAME, last_name)
        self.type_text(RecruitmentLocators.CANDIDATE_EMAIL, email)
        self.select_custom_dropdown(RecruitmentLocators.CANDIDATE_VACANCY, vacancy)
        self.click(RecruitmentLocators.SAVE_CANDIDATE_BUTTON)
        logger.info("candidate_added", name=f"{first_name} {last_name}", email=email)
        return self

    # ── State Checks ──────────────────────────────────────────────────────────

    def get_vacancy_count(self) -> int:
        rows = self.find_elements(RecruitmentLocators.VACANCY_TABLE_ROWS)
        return max(0, len(rows) - 1)

    def is_no_records_displayed(self) -> bool:
        return self.is_element_visible(RecruitmentLocators.NO_RECORDS_MSG, timeout=5)

    def get_success_message(self) -> str:
        return self.wait_for_toast()
