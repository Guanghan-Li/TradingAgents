import os
from pathlib import Path

from dotenv import load_dotenv


ENV_FILE_NAME = ".env"
ENV_FILE_OVERRIDE = "TRADINGAGENTS_ENV_FILE"
DEFAULT_OPENAI_BASE_URL = "https://api.openai.com/v1"
DEFAULT_ANTHROPIC_BASE_URL = "https://api.anthropic.com"
OPENAI_BASE_URL_ENV_VARS = (
    "TRADINGAGENTS_OPENAI_BASE_URL",
    "OPENAI_BASE_URL",
    "OPENAI_API_BASE",
)
ANTHROPIC_BASE_URL_ENV_VARS = (
    "TRADINGAGENTS_ANTHROPIC_BASE_URL",
    "ANTHROPIC_BASE_URL",
)


def _iter_search_dirs(start_dir: Path | None = None) -> list[Path]:
    candidates: list[Path] = []
    seen: set[Path] = set()

    for path in (Path.cwd(), start_dir, Path(__file__).resolve().parent):
        if path is None:
            continue

        resolved = path.resolve()
        if resolved.is_file():
            resolved = resolved.parent

        for directory in (resolved, *resolved.parents):
            if directory in seen:
                continue
            seen.add(directory)
            candidates.append(directory)

    return candidates


def load_project_dotenv(start_dir: Path | None = None, *, override: bool = False) -> Path | None:
    """Load TradingAgents .env files from nearest to farthest.

    Search order:
    1. Explicit path from TRADINGAGENTS_ENV_FILE
    2. Current working directory and its parents
    3. start_dir and its parents
    4. Package directory and its parents

    The nearest .env wins for overlapping keys. Parent .env files are still
    loaded afterward so worktrees can inherit missing secrets from the main
    checkout without overriding worktree-specific values.
    """

    explicit_path = os.environ.get(ENV_FILE_OVERRIDE)
    if explicit_path:
        env_path = Path(explicit_path).expanduser().resolve()
        if env_path.is_file():
            load_dotenv(env_path, override=override)
            return env_path

    loaded_path: Path | None = None
    for directory in _iter_search_dirs(start_dir):
        env_path = directory / ENV_FILE_NAME
        if env_path.is_file():
            load_dotenv(env_path, override=override)
            if loaded_path is None:
                loaded_path = env_path

    return loaded_path


def get_openai_base_url(default: str = DEFAULT_OPENAI_BASE_URL) -> str:
    """Return the configured OpenAI-compatible base URL."""
    for env_name in OPENAI_BASE_URL_ENV_VARS:
        value = os.environ.get(env_name)
        if value and value.strip():
            return value.strip()
    return default


def get_anthropic_base_url(default: str = DEFAULT_ANTHROPIC_BASE_URL) -> str:
    """Return the configured Anthropic-compatible base URL."""
    for env_name in ANTHROPIC_BASE_URL_ENV_VARS:
        value = os.environ.get(env_name)
        if value and value.strip():
            return value.strip()
    return default
