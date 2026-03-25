import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


from tradingagents.llm_clients.openai_client import OpenAIClient


def test_openai_client_uses_responses_api_for_native_openai():
    client = OpenAIClient("gpt-5.4", provider="openai", api_key="test-key")

    llm = client.get_llm()

    assert llm.use_responses_api is True


def test_openai_client_disables_responses_api_for_custom_openai_base_url():
    client = OpenAIClient(
        "gpt-5.4",
        base_url="https://api.itgpt.chat/v1",
        provider="openai",
        api_key="test-key",
    )

    llm = client.get_llm()

    assert llm.use_responses_api is False
