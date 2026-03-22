"""Application configuration loading."""

from dataclasses import dataclass
import os
from pathlib import Path
from typing import Optional

from mcporacle.errors import ConfigurationError


def load_dotenv(path: Path) -> None:
    """Load a minimal .env file without adding extra dependencies."""

    if not path.exists():
        return

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("export "):
            line = line[7:].strip()
        if "=" not in line:
            continue

        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip("'").strip('"')
        if key and key not in os.environ:
            os.environ[key] = value


@dataclass(frozen=True)
class Settings:
    """Runtime settings for the mcporacle server."""

    oracle_user: str
    oracle_password: str
    oracle_dsn: str
    log_level: str = "INFO"

    @classmethod
    def from_env(cls, env_file: str = ".env") -> "Settings":
        load_dotenv(Path.cwd() / env_file)
        return cls(
            oracle_user=_required_env("MCPORACLE_ORACLE_USER"),
            oracle_password=_required_env("MCPORACLE_ORACLE_PASSWORD"),
            oracle_dsn=_required_env("MCPORACLE_ORACLE_DSN"),
            log_level=os.getenv("MCPORACLE_LOG_LEVEL", "INFO").upper(),
        )


def _required_env(name: str) -> str:
    value = os.getenv(name)
    if value and value.strip():
        return value.strip()
    raise ConfigurationError(
        "Missing required environment variable: {name}".format(name=name)
    )
