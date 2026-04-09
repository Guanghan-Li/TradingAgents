# ruff: noqa: E402

import sys
from pathlib import Path

import httpx
import openai


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


from langchain_openai import ChatOpenAI

import tradingagents.llm_clients.openai_client as openai_client_module
from tradingagents.llm_clients.openai_client import OpenAIClient, NormalizedChatOpenAI


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


def test_normalized_chat_openai_retries_transient_internal_server_errors(monkeypatch):
    sleeps = []
    calls = {"count": 0}

    request = httpx.Request("POST", "https://api.itgpt.chat/v1/chat/completions")
    response = httpx.Response(504, request=request, text="Gateway time-out")

    class FakeMessage:
        def __init__(self, content):
            self.content = content

    def fake_invoke(self, input, config=None, **kwargs):
        calls["count"] += 1
        if calls["count"] < 3:
            raise openai.InternalServerError(
                "Gateway time-out",
                response=response,
                body=None,
            )
        return FakeMessage("ok")

    monkeypatch.setattr(ChatOpenAI, "invoke", fake_invoke)
    monkeypatch.setattr(openai_client_module.time, "sleep", sleeps.append)

    llm = NormalizedChatOpenAI(model="gpt-5.4", api_key="test-key")

    result = llm.invoke("hello")

    assert result.content == "ok"
    assert calls["count"] == 3
    assert sleeps == [1.0, 2.0]
