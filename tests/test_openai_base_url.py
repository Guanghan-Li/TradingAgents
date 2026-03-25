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


def test_default_config_uses_openai_base_url_env(monkeypatch):
    monkeypatch.setenv("OPENAI_BASE_URL", "https://api.itgpt.chat/v1")

    import tradingagents.default_config as default_config

    reloaded = importlib.reload(default_config)

    assert reloaded.DEFAULT_CONFIG["backend_url"] == "https://api.itgpt.chat/v1"


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
