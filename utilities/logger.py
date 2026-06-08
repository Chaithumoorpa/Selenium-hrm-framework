"""
Enterprise Selenium HRM Framework — Structured Logger
------------------------------------------------------
Design:
  - structlog for JSON-structured log output
  - Per-test log context (test name, module, browser)
  - Log rotation via RotatingFileHandler
  - Colorized console output in dev mode
  - Thread-safe for parallel test execution
"""

import logging
import logging.handlers
import os
import sys
from pathlib import Path
from typing import Any, Optional

import colorlog
import structlog

# ──────────────────────────────────────────────────────────────────────────────
# Constants
# ──────────────────────────────────────────────────────────────────────────────
DEFAULT_LOG_DIR = Path("logs")
DEFAULT_LOG_FILE = DEFAULT_LOG_DIR / "hrm_test.log"
MAX_BYTES = 10 * 1024 * 1024  # 10 MB
BACKUP_COUNT = 5


def _ensure_log_dir(log_file: Path) -> None:
    """Create log directory if it doesn't exist."""
    log_file.parent.mkdir(parents=True, exist_ok=True)


def setup_logging(
    log_level: str = "INFO",
    log_file: Optional[str] = None,
    log_format: str = "json",
    max_bytes: int = MAX_BYTES,
    backup_count: int = BACKUP_COUNT,
) -> None:
    """
    Configure application-wide logging using structlog.

    Args:
        log_level:    Logging level string (DEBUG/INFO/WARNING/ERROR)
        log_file:     Path to log file; defaults to logs/hrm_test.log
        log_format:   'json' for structured logs, 'console' for human-readable
        max_bytes:    Max size per log file before rotation
        backup_count: Number of backup log files to retain
    """
    log_path = Path(log_file) if log_file else DEFAULT_LOG_FILE
    _ensure_log_dir(log_path)

    numeric_level = getattr(logging, log_level.upper(), logging.INFO)

    # ── stdlib root logger ────────────────────────────────────────────────────
    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)

    # Remove existing handlers to prevent duplication in pytest reruns
    root_logger.handlers.clear()

    # ── Console Handler ───────────────────────────────────────────────────────
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(numeric_level)
    color_formatter = colorlog.ColoredFormatter(
        fmt="%(log_color)s%(asctime)s [%(levelname)8s]%(reset)s %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        log_colors={
            "DEBUG": "cyan",
            "INFO": "green",
            "WARNING": "yellow",
            "ERROR": "red",
            "CRITICAL": "bold_red",
        },
    )
    console_handler.setFormatter(color_formatter)
    root_logger.addHandler(console_handler)

    # ── Rotating File Handler ─────────────────────────────────────────────────
    file_handler = logging.handlers.RotatingFileHandler(
        filename=str(log_path),
        maxBytes=max_bytes,
        backupCount=backup_count,
        encoding="utf-8",
    )
    file_handler.setLevel(logging.DEBUG)  # Always capture DEBUG to file
    file_handler.setFormatter(
        logging.Formatter(
            fmt="%(asctime)s [%(levelname)8s] %(name)s %(filename)s:%(lineno)d — %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
    )
    root_logger.addHandler(file_handler)

    # ── structlog Configuration ───────────────────────────────────────────────
    shared_processors: list[Any] = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
    ]

    if log_format == "json":
        renderer = structlog.processors.JSONRenderer()
    else:
        renderer = structlog.dev.ConsoleRenderer(colors=True)

    structlog.configure(
        processors=shared_processors + [renderer],
        wrapper_class=structlog.make_filtering_bound_logger(numeric_level),
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )


def get_logger(name: str = __name__) -> structlog.BoundLogger:
    """
    Get a structlog bound logger.

    Usage:
        logger = get_logger(__name__)
        logger.info("test_started", test="test_login_valid", browser="chrome")
    """
    return structlog.get_logger(name)


def bind_test_context(test_name: str, module: str, browser: str, env: str) -> None:
    """
    Bind test-level context to all log entries for the current execution.
    Called in conftest.py at the start of each test.
    """
    structlog.contextvars.clear_contextvars()
    structlog.contextvars.bind_contextvars(
        test=test_name,
        module=module,
        browser=browser,
        environment=env,
    )


def clear_test_context() -> None:
    """Clear test context after each test."""
    structlog.contextvars.clear_contextvars()
