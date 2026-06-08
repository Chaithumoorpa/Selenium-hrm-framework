# Enterprise Selenium + PyTest HRM Framework

[![CI](https://github.com/your-org/selenium-hrm-framework/actions/workflows/selenium-hrm-ci.yml/badge.svg)](https://github.com/your-org/selenium-hrm-framework/actions)
[![Python](https://img.shields.io/badge/Python-3.12-blue?logo=python)](https://python.org)
[![Selenium](https://img.shields.io/badge/Selenium-4.23-green?logo=selenium)](https://selenium.dev)
[![Allure](https://img.shields.io/badge/Allure-Report-orange)](https://allurereport.org)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue?logo=docker)](https://docker.com)

A **production-grade enterprise test automation framework** for HRM portal testing, built with Selenium 4, PyTest, BDD (Behave), and full CI/CD integration.

---

## 📌 Business Use Case

Automates end-to-end testing of an Enterprise Human Resource Management (HRM) portal across five functional modules: **Login**, **Employee Management**, **Payroll**, **Leave Management**, and **Recruitment**. Designed to simulate a real SDET role in an HRM SaaS company.

**Target Application**: [OrangeHRM Demo](https://opensource-demo.orangehrmlive.com)

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Test Execution Layer                      │
│  pytest tests/ -m "smoke" | behave features/ | make test      │
└─────────────────────────┬───────────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────────┐
│                    Test Layer  (tests/)                       │
│  test_login.py | test_employee.py | test_leave.py            │
│  Allure decorators | pytest.mark | @parametrize              │
└─────────────────────────┬───────────────────────────────────┘
                          │ uses
┌─────────────────────────▼───────────────────────────────────┐
│                   Page Object Layer  (pages/)                 │
│  BasePage → LoginPage → EmployeePage → LeavePage             │
│  RecruitmentPage | Method chaining | Allure steps            │
└─────────────────────────┬───────────────────────────────────┘
                          │ uses
┌──────────────┬──────────▼──────────┬────────────────────────┐
│  Locators    │     Utilities        │   Config               │
│  (locators/) │  DriverFactory       │   dev.yaml             │
│  Separated   │  WaitUtils           │   staging.yaml         │
│  from pages  │  RetryUtils          │   prod.yaml            │
│              │  Logger              │   .env secrets         │
│              │  ExcelUtils          │                        │
│              │  ScreenshotUtils     │                        │
└──────────────┴─────────────────────┴────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────────┐
│                   WebDriver Layer                             │
│  Chrome | Firefox | Edge | Remote (Selenium Grid)            │
│  DriverFactory (Singleton + Factory Pattern)                 │
└─────────────────────────────────────────────────────────────┘
```

---

## 🎯 Design Patterns

| Pattern | Where Used | Why |
|---------|-----------|-----|
| **Page Object Model (POM)** | `pages/` | Separates test logic from UI interaction |
| **Page Factory** | `pages/base_page.py` | Lazy element resolution |
| **Singleton** | `DriverFactory`, `ConfigReader` | One instance per thread/session |
| **Factory** | `DriverFactory._create_local()` | Browser-type abstraction |
| **Strategy** | `ConfigReader` + env configs | Swap behaviour per environment |
| **Decorator** | `@retry_on_failure`, `@allure.step` | Cross-cutting concerns |

---

## 📁 Folder Structure

```
selenium-hrm-framework/
├── pages/                    # POM: One class per page
│   ├── base_page.py          # Parent: all raw Selenium calls here
│   ├── login_page.py
│   ├── employee_page.py
│   ├── leave_page.py
│   └── recruitment_page.py
├── tests/                    # PyTest test suites
│   ├── conftest.py           # Fixtures, hooks, Allure env setup
│   ├── test_login.py
│   ├── test_employee.py
│   └── test_leave.py
├── locators/                 # Element locators (separated from pages)
│   ├── login_locators.py
│   ├── employee_locators.py
│   ├── leave_locators.py
│   └── recruitment_locators.py
├── utilities/                # Reusable helpers
│   ├── driver_factory.py     # Singleton + Factory: WebDriver creation
│   ├── config_reader.py      # Strategy: multi-env YAML config
│   ├── logger.py             # structlog JSON logging
│   ├── wait_utils.py         # Explicit wait wrappers
│   ├── screenshot_utils.py   # Screenshot + Allure attachment
│   ├── retry_utils.py        # Tenacity retry decorators
│   └── excel_utils.py        # Excel/JSON test data reader
├── features/                 # BDD feature files (Behave)
│   ├── login.feature
│   ├── employee.feature
│   └── environment.py        # Behave hooks
├── step_definitions/         # BDD step implementations
│   └── login_steps.py
├── config/                   # Environment configs
│   ├── dev.yaml
│   ├── staging.yaml
│   └── prod.yaml
├── testdata/                 # Test data files
│   ├── login_data.json
│   └── employee_data.json
├── reports/                  # Allure results (gitignored)
├── logs/                     # Log files (gitignored)
├── resources/screenshots/    # Failure screenshots (gitignored)
├── k8s/                      # Kubernetes manifests
│   ├── namespace.yaml
│   ├── deployment.yaml
│   ├── service.yaml
│   ├── configmap.yaml
│   ├── secret.yaml
│   └── hpa.yaml
├── .github/workflows/        # GitHub Actions CI/CD
│   └── selenium-hrm-ci.yml
├── Jenkinsfile               # Jenkins multibranch pipeline
├── Dockerfile                # Multi-stage Docker image
├── docker-compose.yml        # Selenium Grid + Allure stack
├── Makefile                  # Developer CLI
├── requirements.txt
├── pytest.ini
├── .gitignore
├── README.md
├── Architecture.md
└── Contributing.md
```

---

## ⚡ Quick Start

### Prerequisites
- Python 3.12+
- Google Chrome (latest)
- Java 11+ (for Allure CLI)

### 1. Clone and Setup

```bash
git clone https://github.com/your-org/selenium-hrm-framework.git
cd selenium-hrm-framework

# Create virtual environment
python -m venv .venv
source .venv/bin/activate       # Linux/Mac
.venv\Scripts\activate          # Windows

# Install dependencies
pip install -r requirements.txt
```

### 2. Run Tests

```bash
# Smoke tests (fastest — ~5 minutes)
make smoke

# Full regression
make regression

# Specific module
make test-login
make test-employee

# BDD with Behave
make test-bdd

# Parallel execution (4 workers)
make test-parallel WORKERS=4

# Cross-browser (Firefox)
make test BROWSER=firefox ENV=dev
```

### 3. View Reports

```bash
# Generate and open Allure report
make report

# Serve Allure (stays running)
make report-serve
```

### 4. Docker Execution

```bash
# Build image
make docker-build

# Run smoke tests in Docker (headless)
make docker-run

# Full Selenium Grid environment
make docker-compose-up
docker-compose --profile test run --rm test-runner
make docker-compose-down
```

---

## 🌐 Environment Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `ENV` | `dev` | Target environment (dev/staging/prod) |
| `BROWSER` | `chrome` | Browser name |
| `HEADLESS` | `false` | Headless mode |
| `SELENIUM_REMOTE_URL` | — | Selenium Grid URL for remote execution |

```bash
# Staging headless
ENV=staging BROWSER=chrome HEADLESS=true make test

# Remote Grid
SELENIUM_REMOTE_URL=http://grid:4444/wd/hub make test
```

---

## 🧪 Test Markers

| Marker | Description |
|--------|-------------|
| `@smoke` | Critical path — run on every deployment |
| `@regression` | Full suite — run daily |
| `@negative` | Invalid input / error scenarios |
| `@data_driven` | Parametrized tests |
| `@login`, `@employee`, `@leave` | Module-specific |
| `@flaky` | Known intermittent tests (quarantined) |

---

## 📊 Reporting

- **Allure HTML Report**: `make report` — with history, categories, trends
- **JUnit XML**: `reports/junit/results.xml` — Jenkins/GitHub Actions integration
- **Screenshots**: Auto-captured on failure, attached to Allure
- **Structured Logs**: JSON format at `logs/hrm_test.log`

---

## 🔄 CI/CD

| Tool | Configuration | Trigger |
|------|--------------|---------|
| **GitHub Actions** | `.github/workflows/selenium-hrm-ci.yml` | Push, PR, Schedule |
| **Jenkins** | `Jenkinsfile` | Multibranch pipeline |
| **Docker** | `Dockerfile` + `docker-compose.yml` | On-demand |
| **Kubernetes** | `k8s/` | Jenkins `DEPLOY_K8S=true` |

---

## 💬 Interview Q&A

<details>
<summary><strong>Q: How does the Singleton pattern benefit the DriverFactory?</strong></summary>

> Each test thread gets exactly one driver instance via thread-local storage. This prevents multiple browser windows opening per test while enabling safe parallel execution with `pytest-xdist` where each worker thread maintains its own driver.

</details>

<details>
<summary><strong>Q: Why separate locators from page classes?</strong></summary>

> When the UI changes (e.g., a locator ID changes), only the locator file needs updating — not the page class. This follows the Single Responsibility Principle and makes locator updates O(1) instead of searching through page logic.

</details>

<details>
<summary><strong>Q: How does the framework handle flaky tests?</strong></summary>

> Three layers: (1) `@retry_on_failure` decorator retries individual element interactions on `StaleElementReferenceException`, (2) `pytest-rerunfailures` reruns entire failed tests up to N times, (3) `@flaky` marker quarantines known-intermittent tests from CI gates.

</details>

<details>
<summary><strong>Q: How do you manage test data across environments?</strong></summary>

> YAML configs per environment with `${ENV_VAR}` placeholder resolution. Credentials never live in YAML — they're injected via environment variables or a secrets manager. Test data is in JSON/Excel files with a consistent key schema.

</details>

<details>
<summary><strong>Q: Explain the Strategy pattern in ConfigReader.</strong></summary>

> `ConfigReader` selects a YAML file based on the `ENV` environment variable (`dev.yaml`, `staging.yaml`, `prod.yaml`). The selection strategy is determined at runtime, allowing the same test code to run against different environments without modification — a classic Strategy pattern.

</details>

---

## 🚀 Scalability Improvements

1. **Selenium Grid 4** → Scale to N browser nodes on Kubernetes
2. **pytest-xdist** → `-n auto` for CPU-count parallel workers
3. **Page Cache** → Cache post-login browser state using pickle for speed
4. **API Seeding** → Use REST API to create test data instead of UI flows
5. **Allure History** → GitHub Pages for persistent trend tracking
6. **TestRail Integration** → Sync results via TestRail API

---

## 📝 License

MIT License — See LICENSE file for details.
