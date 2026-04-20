import importlib
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


def test_get_openai_base_url_prefers_tradingagents_env(monkeypatch):
    from tradingagents.env import get_openai_base_url

    monkeypatch.setenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
    monkeypatch.setenv("TRADINGAGENTS_OPENAI_BASE_URL", "https://api.itgpt.chat/v1")

    assert get_openai_base_url() == "https://api.itgpt.chat/v1"


def test_get_openai_base_url_defaults_to_openai(monkeypatch):
    from tradingagents.env import get_openai_base_url

    monkeypatch.delenv("TRADINGAGENTS_OPENAI_BASE_URL", raising=False)
    monkeypatch.delenv("OPENAI_BASE_URL", raising=False)
    monkeypatch.delenv("OPENAI_API_BASE", raising=False)

    assert get_openai_base_url() == "https://api.openai.com/v1"


def test_get_anthropic_base_url_prefers_tradingagents_env(monkeypatch):
    from tradingagents.env import get_anthropic_base_url

    monkeypatch.setenv("ANTHROPIC_BASE_URL", "https://api.anthropic.com")
    monkeypatch.setenv("TRADINGAGENTS_ANTHROPIC_BASE_URL", "https://api.routeai.cc")

    assert get_anthropic_base_url() == "https://api.routeai.cc"


def test_default_config_uses_anthropic_base_url_env(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_BASE_URL", "https://api.routeai.cc")

    import tradingagents.default_config as default_config

    reloaded = importlib.reload(default_config)

    assert reloaded.DEFAULT_CONFIG["backend_url"] == "https://api.routeai.cc"
    assert reloaded.DEFAULT_CONFIG["llm_provider"] == "anthropic"


def test_select_llm_provider_returns_openai_provider_key_for_override(monkeypatch):
    monkeypatch.setenv("OPENAI_BASE_URL", "https://api.itgpt.chat/v1")

    import cli.utils as cli_utils

    with monkeypatch.context() as mp:
        mp.setattr(
            cli_utils.questionary,
            "select",
            lambda *args, **kwargs: type(
                "Prompt",
                (),
                {"ask": lambda self: ("openai", "https://api.itgpt.chat/v1")},
            )(),
        )
        provider, url = cli_utils.select_llm_provider()

    assert provider == "openai"
    assert url == "https://api.itgpt.chat/v1"


def test_select_llm_provider_returns_claude_code_provider_key(monkeypatch):
    import cli.utils as cli_utils

    with monkeypatch.context() as mp:
        mp.setattr(
            cli_utils.questionary,
            "select",
            lambda *args, **kwargs: type(
                "Prompt",
                (),
                {"ask": lambda self: ("claude_code", "claude://local")},
            )(),
        )
        provider, url = cli_utils.select_llm_provider()

    assert provider == "claude_code"
    assert url == "claude://local"


def test_select_llm_provider_returns_codex_cli_provider_key(monkeypatch):
    import cli.utils as cli_utils

    with monkeypatch.context() as mp:
        mp.setattr(
            cli_utils.questionary,
            "select",
            lambda *args, **kwargs: type(
                "Prompt",
                (),
                {"ask": lambda self: ("codex_cli", "codex://local")},
            )(),
        )
        provider, url = cli_utils.select_llm_provider()

    assert provider == "codex_cli"
    assert url == "codex://local"


def test_select_llm_provider_returns_anthropic_provider_key_for_override(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_BASE_URL", "https://api.routeai.cc")

    import cli.utils as cli_utils

    with monkeypatch.context() as mp:
        mp.setattr(
            cli_utils.questionary,
            "select",
            lambda *args, **kwargs: type(
                "Prompt",
                (),
                {"ask": lambda self: ("anthropic", "https://api.routeai.cc")},
            )(),
        )
        provider, url = cli_utils.select_llm_provider()

    assert provider == "anthropic"
    assert url == "https://api.routeai.cc"
