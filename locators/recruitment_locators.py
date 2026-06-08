"""
Locators — Recruitment Module Page
OrangeHRM: /web/index.php/recruitment/viewJobVacancy
"""

from selenium.webdriver.common.by import By


class RecruitmentLocators:
    """All locators for the Recruitment module."""

    # ── Navigation ────────────────────────────────────────────────────────────
    RECRUITMENT_MENU = (By.XPATH, "//span[text()='Recruitment']")
    VACANCIES_MENU = (By.XPATH, "//a[text()='Vacancies']")
    CANDIDATES_MENU = (By.XPATH, "//a[text()='Candidates']")

    # ── Vacancies List ────────────────────────────────────────────────────────
    ADD_VACANCY_BUTTON = (By.XPATH, "//button[contains(.,'Add')]")
    SEARCH_JOB_TITLE = (By.XPATH, "//label[text()='Job Title']/following::div[contains(@class,'oxd-select-text')][1]")
    SEARCH_BUTTON = (By.XPATH, "//button[@type='submit']")
    VACANCY_TABLE_ROWS = (By.XPATH, "//div[@role='row'][contains(@class,'oxd-table-row')]")
    NO_RECORDS_MSG = (By.XPATH, "//span[text()='No Records Found']")

    # ── Add Vacancy Form ──────────────────────────────────────────────────────
    VACANCY_NAME_INPUT = (By.XPATH, "//label[text()='Vacancy Name']/following::input[1]")
    JOB_TITLE_DROPDOWN = (By.XPATH, "//label[text()='Job Title']/following::div[contains(@class,'oxd-select-text')][1]")
    JOB_TITLE_OPTION = (By.XPATH, "//div[@role='listbox']//span[text()='{}']")
    HIRING_MANAGER = (By.XPATH, "//label[text()='Hiring Manager']/following::input[1]")
    HIRING_MANAGER_OPTION = (By.XPATH, "//div[@role='option']//span[text()='{}']")
    NO_OF_POSITIONS = (By.XPATH, "//label[text()='No of Positions']/following::input[1]")
    DESCRIPTION_TEXTAREA = (By.XPATH, "//label[text()='Description']/following::textarea[1]")
    STATUS_DROPDOWN = (By.XPATH, "//label[text()='Status']/following::div[contains(@class,'oxd-select-text')][1]")
    IS_PUBLISHED = (By.XPATH, "//label[contains(@class,'oxd-switch-wrapper')]//input[@type='checkbox']")
    SAVE_BUTTON = (By.XPATH, "//button[@type='submit']")

    # ── Candidates ────────────────────────────────────────────────────────────
    ADD_CANDIDATE_BUTTON = (By.XPATH, "//button[contains(.,'Add')]")
    CANDIDATE_FIRSTNAME = (By.XPATH, "//label[text()='First Name']/following::input[1]")
    CANDIDATE_LASTNAME = (By.XPATH, "//label[text()='Last Name']/following::input[1]")
    CANDIDATE_EMAIL = (By.XPATH, "//label[text()='Email']/following::input[1]")
    CANDIDATE_VACANCY = (By.XPATH, "//label[text()='Vacancy']/following::div[contains(@class,'oxd-select-text')][1]")
    RESUME_UPLOAD = (By.XPATH, "//input[@type='file']")
    CONSENT_CHECKBOX = (By.XPATH, "//label[contains(@class,'oxd-checkbox-wrapper')]//input[@type='checkbox']")
    SAVE_CANDIDATE_BUTTON = (By.XPATH, "//button[@type='submit']")

    # ── Status Messages ───────────────────────────────────────────────────────
    SUCCESS_TOAST = (By.XPATH, "//p[contains(@class,'oxd-text--toast-message')]")
    ERROR_MSG = (By.XPATH, "//span[contains(@class,'oxd-input-field-error-message')]")
