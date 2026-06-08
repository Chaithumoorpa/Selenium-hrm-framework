# =============================================================================
# Enterprise Selenium + PyTest HRM Framework — Makefile
# Developer CLI: one command per workflow
# =============================================================================

.DEFAULT_GOAL := help
SHELL         := /bin/bash
PYTHON        := python3
PIP           := pip3
PYTEST        := pytest
VENV          := .venv
REPORTS_DIR   := reports
ALLURE_DIR    := $(REPORTS_DIR)/allure-results
ENV           ?= dev
BROWSER       ?= chrome
WORKERS       ?= 4

# --------------------------------------------------------------------------- #
# COLORS
# --------------------------------------------------------------------------- #
GREEN  := \033[0;32m
YELLOW := \033[0;33m
CYAN   := \033[0;36m
RESET  := \033[0m

# --------------------------------------------------------------------------- #
# HELP
# --------------------------------------------------------------------------- #
.PHONY: help
help: ## Show this help message
	@echo ""
	@echo "$(CYAN)╔══════════════════════════════════════════════════════╗$(RESET)"
	@echo "$(CYAN)║   Enterprise Selenium HRM Framework — Makefile       ║$(RESET)"
	@echo "$(CYAN)╚══════════════════════════════════════════════════════╝$(RESET)"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  $(GREEN)%-25s$(RESET) %s\n", $$1, $$2}'
	@echo ""

# --------------------------------------------------------------------------- #
# SETUP
# --------------------------------------------------------------------------- #
.PHONY: venv
venv: ## Create virtual environment
	@echo "$(YELLOW)Creating virtual environment...$(RESET)"
	$(PYTHON) -m venv $(VENV)
	@echo "$(GREEN)Virtual environment created. Activate with: source $(VENV)/bin/activate$(RESET)"

.PHONY: install
install: ## Install all dependencies
	@echo "$(YELLOW)Installing dependencies...$(RESET)"
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt
	@echo "$(GREEN)Dependencies installed successfully$(RESET)"

.PHONY: install-dev
install-dev: install ## Install with dev/pre-commit hooks
	pre-commit install
	@echo "$(GREEN)Pre-commit hooks installed$(RESET)"

# --------------------------------------------------------------------------- #
# CODE QUALITY
# --------------------------------------------------------------------------- #
.PHONY: lint
lint: ## Run flake8 + pylint
	@echo "$(YELLOW)Running flake8...$(RESET)"
	flake8 pages/ tests/ utilities/ locators/ step_definitions/ --max-line-length=120 --exclude=__pycache__
	@echo "$(YELLOW)Running pylint...$(RESET)"
	pylint pages/ utilities/ locators/ --fail-under=8.0
	@echo "$(GREEN)Linting complete$(RESET)"

.PHONY: format
format: ## Auto-format with black + isort
	black pages/ tests/ utilities/ locators/ step_definitions/ --line-length=120
	isort pages/ tests/ utilities/ locators/ step_definitions/
	@echo "$(GREEN)Formatting complete$(RESET)"

.PHONY: typecheck
typecheck: ## Run mypy type checking
	mypy pages/ utilities/ --ignore-missing-imports
	@echo "$(GREEN)Type checking complete$(RESET)"

.PHONY: quality
quality: format lint typecheck ## Run all quality checks

# --------------------------------------------------------------------------- #
# TEST EXECUTION
# --------------------------------------------------------------------------- #
.PHONY: test
test: ## Run full regression suite (ENV=dev BROWSER=chrome)
	@echo "$(YELLOW)Running full test suite | ENV=$(ENV) BROWSER=$(BROWSER)$(RESET)"
	ENV=$(ENV) BROWSER=$(BROWSER) $(PYTEST) tests/ -m "not flaky" --alluredir=$(ALLURE_DIR)

.PHONY: smoke
smoke: ## Run smoke test suite only
	@echo "$(YELLOW)Running smoke tests...$(RESET)"
	ENV=$(ENV) BROWSER=$(BROWSER) $(PYTEST) tests/ -m "smoke" --alluredir=$(ALLURE_DIR)

.PHONY: regression
regression: ## Run full regression suite
	ENV=$(ENV) BROWSER=$(BROWSER) $(PYTEST) tests/ -m "regression" --alluredir=$(ALLURE_DIR)

.PHONY: test-login
test-login: ## Run login module tests only
	ENV=$(ENV) $(PYTEST) tests/test_login.py --alluredir=$(ALLURE_DIR) -v

.PHONY: test-employee
test-employee: ## Run employee module tests only
	ENV=$(ENV) $(PYTEST) tests/test_employee.py --alluredir=$(ALLURE_DIR) -v

.PHONY: test-leave
test-leave: ## Run leave module tests only
	ENV=$(ENV) $(PYTEST) tests/test_leave.py --alluredir=$(ALLURE_DIR) -v

.PHONY: test-parallel
test-parallel: ## Run tests in parallel (WORKERS=4)
	@echo "$(YELLOW)Running tests in parallel with $(WORKERS) workers...$(RESET)"
	ENV=$(ENV) $(PYTEST) tests/ -n $(WORKERS) --alluredir=$(ALLURE_DIR)

.PHONY: test-bdd
test-bdd: ## Run BDD tests with Behave
	ENV=$(ENV) behave features/ --no-capture --format allure_behave.formatter:AllureFormatter -o $(ALLURE_DIR)

# --------------------------------------------------------------------------- #
# REPORTING
# --------------------------------------------------------------------------- #
.PHONY: report
report: ## Generate and open Allure report
	@echo "$(YELLOW)Generating Allure report...$(RESET)"
	allure generate $(ALLURE_DIR) -o $(REPORTS_DIR)/allure-report --clean
	allure open $(REPORTS_DIR)/allure-report

.PHONY: report-serve
report-serve: ## Serve Allure report (background)
	allure serve $(ALLURE_DIR)

# --------------------------------------------------------------------------- #
# DOCKER
# --------------------------------------------------------------------------- #
.PHONY: docker-build
docker-build: ## Build Docker image
	@echo "$(YELLOW)Building Docker image...$(RESET)"
	docker build -t selenium-hrm-framework:latest .
	@echo "$(GREEN)Docker image built: selenium-hrm-framework:latest$(RESET)"

.PHONY: docker-run
docker-run: ## Run tests inside Docker
	docker run --rm \
		-e ENV=$(ENV) \
		-e BROWSER=chrome \
		-v $(PWD)/reports:/app/reports \
		-v $(PWD)/logs:/app/logs \
		selenium-hrm-framework:latest

.PHONY: docker-compose-up
docker-compose-up: ## Start full test environment with Docker Compose
	docker-compose up -d
	@echo "$(GREEN)Test environment started$(RESET)"

.PHONY: docker-compose-down
docker-compose-down: ## Stop Docker Compose environment
	docker-compose down -v

.PHONY: docker-compose-run
docker-compose-run: ## Run tests via Docker Compose
	docker-compose run --rm test-runner

# --------------------------------------------------------------------------- #
# KUBERNETES
# --------------------------------------------------------------------------- #
.PHONY: k8s-apply
k8s-apply: ## Apply all Kubernetes manifests
	kubectl apply -f k8s/
	@echo "$(GREEN)Kubernetes resources applied$(RESET)"

.PHONY: k8s-delete
k8s-delete: ## Delete all Kubernetes resources
	kubectl delete -f k8s/

.PHONY: k8s-dry-run
k8s-dry-run: ## Validate K8s manifests (dry-run)
	kubectl apply -f k8s/ --dry-run=client

.PHONY: k8s-status
k8s-status: ## Check pod status
	kubectl get pods -n selenium-hrm

# --------------------------------------------------------------------------- #
# CLEANUP
# --------------------------------------------------------------------------- #
.PHONY: clean
clean: ## Clean build artifacts and reports
	@echo "$(YELLOW)Cleaning artifacts...$(RESET)"
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	rm -rf $(REPORTS_DIR)/allure-results $(REPORTS_DIR)/allure-report $(REPORTS_DIR)/html
	rm -f logs/*.log
	find resources/screenshots -name "*.png" -delete 2>/dev/null || true
	@echo "$(GREEN)Cleanup complete$(RESET)"

.PHONY: clean-docker
clean-docker: ## Remove Docker images and volumes
	docker-compose down -v --rmi all

# --------------------------------------------------------------------------- #
# UTILITIES
# --------------------------------------------------------------------------- #
.PHONY: env-check
env-check: ## Verify environment setup
	@echo "$(CYAN)Environment Check$(RESET)"
	@$(PYTHON) --version
	@$(PIP) --version
	@$(PYTEST) --version
	@allure --version 2>/dev/null || echo "Allure CLI not found. Install: https://allurereport.org/docs/install/"
	@docker --version 2>/dev/null || echo "Docker not found"
	@kubectl version --client 2>/dev/null || echo "kubectl not found"

.PHONY: create-dirs
create-dirs: ## Create required directories
	mkdir -p reports/allure-results reports/allure-report reports/html
	mkdir -p logs resources/screenshots drivers
	@echo "$(GREEN)Directories created$(RESET)"

.PHONY: show-markers
show-markers: ## Show all custom pytest markers
	$(PYTEST) --markers

.PHONY: collect
collect: ## Dry-run: collect all tests without executing
	$(PYTEST) tests/ --collect-only -q
