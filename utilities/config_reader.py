"""
Enterprise Selenium HRM Framework — Configuration Reader
---------------------------------------------------------
Design Pattern: Strategy Pattern
  - ConfigReader selects strategy based on ENV environment variable
  - Supports YAML multi-environment configs + .env secrets
  - Singleton: config loaded once and cached
  - Resolves ${ENV_VAR} placeholders in YAML values
"""

import os
import re
from pathlib import Path
from typing import Any, Optional

import yaml
from dotenv import load_dotenv

from utilities.logger import get_logger

logger = get_logger(__name__)

# ──────────────────────────────────────────────────────────────────────────────
# Constants
# ──────────────────────────────────────────────────────────────────────────────
CONFIG_DIR = Path(__file__).parent.parent / "config"
SUPPORTED_ENVS = ("dev", "staging", "prod")
ENV_VAR_PATTERN = re.compile(r"\$\{([^}]+)\}")


def _resolve_env_vars(value: Any) -> Any:
    """
    Recursively resolve ${ENV_VAR} placeholders in config values.

    Examples:
        "${PROD_ADMIN_USER}" → os.environ["PROD_ADMIN_USER"]
        "https://${HOST}/path" → "https://myhost.com/path"
    """
    if isinstance(value, str):

        def replacer(match: re.Match) -> str:
            var_name = match.group(1)
            env_val = os.environ.get(var_name)
            if env_val is None:
                logger.warning(
                    "env_var_not_found",
                    variable=var_name,
                    hint="Set in .env or system environment",
                )
                return match.group(0)  # Keep placeholder if not found
            return env_val

        return ENV_VAR_PATTERN.sub(replacer, value)
    elif isinstance(value, dict):
        return {k: _resolve_env_vars(v) for k, v in value.items()}
    elif isinstance(value, list):
        return [_resolve_env_vars(item) for item in value]
    return value


class ConfigReader:
    """
    Singleton configuration reader.

    Loads YAML config for the active environment, resolves environment
    variable placeholders, and provides a clean dict-like interface.

    Usage:
        config = ConfigReader.get_config()
        base_url = config.get("app.base_url")
        username = config.get("credentials.admin.username")
    """

    _instance: Optional["ConfigReader"] = None
    _config: Optional[dict] = None

    def __new__(cls) -> "ConfigReader":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        if self._config is None:
            self._load()

    def _load(self) -> None:
        """Load + merge base config and environment-specific overrides."""
        # Load .env secrets first
        env_file = Path(".env")
        if env_file.exists():
            load_dotenv(env_file)
            logger.debug("dotenv_loaded", file=str(env_file))

        env = os.environ.get("ENV", "dev").lower()
        if env not in SUPPORTED_ENVS:
            logger.warning(
                "unsupported_env",
                env=env,
                fallback="dev",
                supported=SUPPORTED_ENVS,
            )
            env = "dev"

        config_file = CONFIG_DIR / f"{env}.yaml"
        if not config_file.exists():
            raise FileNotFoundError(
                f"Config file not found: {config_file}\n"
                f"Expected one of: {[str(CONFIG_DIR / f'{e}.yaml') for e in SUPPORTED_ENVS]}"
            )

        with open(config_file, encoding="utf-8") as f:
            raw_config = yaml.safe_load(f)

        self._config = _resolve_env_vars(raw_config)
        logger.info("config_loaded", env=env, file=str(config_file))

    @classmethod
    def get_config(cls) -> "ConfigReader":
        """Get the singleton ConfigReader instance."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    @classmethod
    def reset(cls) -> None:
        """Reset singleton — useful for testing ConfigReader itself."""
        cls._instance = None
        cls._config = None

    def get(self, key_path: str, default: Any = None) -> Any:
        """
        Get config value by dot-notation key path.

        Args:
            key_path: Dot-separated path, e.g. "app.base_url"
            default:  Value to return if key not found

        Returns:
            Config value or default

        Example:
            config.get("credentials.admin.username")  # → "Admin"
            config.get("browser.headless")            # → False
        """
        keys = key_path.split(".")
        value = self._config
        for key in keys:
            if not isinstance(value, dict):
                return default
            value = value.get(key)
            if value is None:
                return default
        return value

    def get_required(self, key_path: str) -> Any:
        """
        Get config value; raises ValueError if missing.

        Use for critical config values (base_url, credentials).
        """
        value = self.get(key_path)
        if value is None:
            raise ValueError(
                f"Required config key '{key_path}' not found. "
                f"Check your {os.environ.get('ENV', 'dev')}.yaml config file."
            )
        return value

    @property
    def base_url(self) -> str:
        return self.get_required("app.base_url")

    @property
    def admin_username(self) -> str:
        return self.get_required("credentials.admin.username")

    @property
    def admin_password(self) -> str:
        return self.get_required("credentials.admin.password")

    @property
    def browser(self) -> str:
        return os.environ.get("BROWSER") or self.get("browser.default", "chrome")

    @property
    def headless(self) -> bool:
        env_headless = os.environ.get("HEADLESS")
        if env_headless is not None:
            return env_headless.lower() in ("true", "1", "yes")
        return self.get("browser.headless", False)

    @property
    def timeout(self) -> int:
        return self.get("app.timeout", 30)

    @property
    def explicit_wait(self) -> int:
        return self.get("app.explicit_wait", 20)

    @property
    def screenshot_on_failure(self) -> bool:
        return self.get("screenshot.on_failure", True)

    @property
    def screenshot_dir(self) -> str:
        return self.get("screenshot.directory", "resources/screenshots")

    @property
    def allure_results_dir(self) -> str:
        return self.get("allure.results_dir", "reports/allure-results")

    def __repr__(self) -> str:
        env = os.environ.get("ENV", "dev")
        return f"ConfigReader(env={env}, base_url={self.base_url})"
