# =============================================================================
# Enterprise Selenium HRM Framework — Dockerfile
# Multi-stage build for minimal production image
# =============================================================================

# ──────────────────────────────────────────────────────────────────────────────
# Stage 1: Base Python + Chrome
# ──────────────────────────────────────────────────────────────────────────────
FROM python:3.12-slim AS base

# Install system dependencies + Google Chrome
RUN apt-get update && apt-get install -y \
    wget \
    gnupg2 \
    curl \
    unzip \
    fonts-liberation \
    libappindicator3-1 \
    libasound2 \
    libatk-bridge2.0-0 \
    libcairo-gobject2 \
    libcups2 \
    libdbus-1-3 \
    libdrm2 \
    libgbm1 \
    libglib2.0-0 \
    libgtk-3-0 \
    libnspr4 \
    libnss3 \
    libx11-6 \
    libx11-xcb1 \
    libxcb1 \
    libxcomposite1 \
    libxcursor1 \
    libxdamage1 \
    libxext6 \
    libxfixes3 \
    libxi6 \
    libxrandr2 \
    libxrender1 \
    libxss1 \
    libxtst6 \
    xdg-utils \
    --no-install-recommends \
    && curl -fsSL https://dl.google.com/linux/linux_signing_key.pub | gpg --dearmor -o /usr/share/keyrings/google-chrome.gpg \
    && sh -c 'echo "deb [arch=amd64 signed-by=/usr/share/keyrings/google-chrome.gpg] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list' \
    && apt-get update \
    && apt-get install -y google-chrome-stable --no-install-recommends \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# ──────────────────────────────────────────────────────────────────────────────
# Stage 2: Dependencies
# ──────────────────────────────────────────────────────────────────────────────
FROM base AS deps

WORKDIR /app

# Copy requirements first for Docker layer caching
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# ──────────────────────────────────────────────────────────────────────────────
# Stage 3: Final Runtime Image
# ──────────────────────────────────────────────────────────────────────────────
FROM deps AS runtime

WORKDIR /app

# Copy project files
COPY pages/          pages/
COPY tests/          tests/
COPY locators/       locators/
COPY utilities/      utilities/
COPY features/       features/
COPY step_definitions/ step_definitions/
COPY config/         config/
COPY testdata/       testdata/
COPY resources/      resources/
COPY pytest.ini      .
COPY Makefile        .

# Create output directories
RUN mkdir -p reports/allure-results reports/allure-report logs resources/screenshots drivers

# Environment defaults
ENV ENV=dev \
    BROWSER=chrome \
    HEADLESS=true \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    WDM_LOG_LEVEL=0

# Non-root user for security
RUN groupadd -r testrunner && useradd -r -g testrunner testrunner
RUN chown -R testrunner:testrunner /app
USER testrunner

# Health check
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
    CMD python3 -c "import selenium; print('OK')" || exit 1

# Default entrypoint: run smoke tests
ENTRYPOINT ["python3", "-m", "pytest"]
CMD ["tests/", "-m", "smoke", "--alluredir=reports/allure-results", "-v", "--tb=short"]

# Labels
LABEL maintainer="SDET Team" \
      version="1.0.0" \
      description="Enterprise Selenium HRM Test Framework" \
      framework="selenium-pytest" \
      app="orangehrm"
