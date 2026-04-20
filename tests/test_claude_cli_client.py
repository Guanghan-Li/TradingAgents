import json
from subprocess import CompletedProcess

import pytest
from langchain_core.messages import AIMessage, HumanMessage

from tradingagents.llm_clients.claude_cli_client import ClaudeCodeChatModel, ClaudeCLIClient


TEST_TOOL = {
    "type": "function",
    "function": {
        "name": "get_stock_data",
        "description": "Fetch stock data for a ticker.",
        "parameters": {
            "type": "object",
            "properties": {
                "ticker": {"type": "string"},
            },
            "required": ["ticker"],
        },
    },
}


def test_claude_cli_client_returns_chat_model():
    client = ClaudeCLIClient(model="claude-sonnet-4-6")

    llm = client.get_llm()

    assert isinstance(llm, ClaudeCodeChatModel)
    assert llm.model == "claude-sonnet-4-6"


def test_claude_code_chat_model_returns_final_ai_message(monkeypatch):
    captured = {}

    def fake_run(command, **kwargs):
        captured["command"] = command
        captured["kwargs"] = kwargs
        return CompletedProcess(
            args=command,
            returncode=0,
            stdout=json.dumps(
                {
                    "type": "result",
                    "subtype": "success",
                    "structured_output": {"content": "final analysis"},
                }
            ),
            stderr="",
        )

    monkeypatch.setattr(
        "tradingagents.llm_clients.claude_cli_client.subprocess.run",
        fake_run,
    )

    llm = ClaudeCodeChatModel(model="claude-sonnet-4-6", effort="high")

    result = llm.invoke([HumanMessage(content="Analyze AAPL")])

    assert isinstance(result, AIMessage)
    assert result.content == "final analysis"
    assert result.tool_calls == []
    assert "--model" in captured["command"]
    assert "claude-sonnet-4-6" in captured["command"]
    assert "--effort" in captured["command"]
    assert "high" in captured["command"]
    assert "--output-format" in captured["command"]
    assert "json" in captured["command"]
    assert "--setting-sources" in captured["command"]
    assert "user" in captured["command"]
    assert captured["kwargs"]["cwd"]


def test_claude_code_chat_model_returns_tool_calls(monkeypatch):
    def fake_run(command, **kwargs):
        return CompletedProcess(
            args=command,
            returncode=0,
            stdout=json.dumps(
                {
                    "type": "result",
                    "subtype": "success",
                    "structured_output": {
                        "response_type": "tool_calls",
                        "content": "",
                        "tool_calls": [
                            {
                                "name": "get_stock_data",
                                "arguments": {"ticker": "AAPL"},
                            }
                        ],
                    },
                }
            ),
            stderr="",
        )

    monkeypatch.setattr(
        "tradingagents.llm_clients.claude_cli_client.subprocess.run",
        fake_run,
    )

    llm = ClaudeCodeChatModel(model="claude-sonnet-4-6").bind_tools([TEST_TOOL])

    result = llm.invoke([HumanMessage(content="Get the latest AAPL stock data")])

    assert result.content == ""
    assert len(result.tool_calls) == 1
    assert result.tool_calls[0]["name"] == "get_stock_data"
    assert result.tool_calls[0]["args"] == {"ticker": "AAPL"}
    assert result.tool_calls[0]["type"] == "tool_call"


def test_claude_code_chat_model_raises_on_invalid_json(monkeypatch):
    def fake_run(command, **kwargs):
        return CompletedProcess(
            args=command,
            returncode=0,
            stdout="not json",
            stderr="",
        )

    monkeypatch.setattr(
        "tradingagents.llm_clients.claude_cli_client.subprocess.run",
        fake_run,
    )

    llm = ClaudeCodeChatModel(model="claude-sonnet-4-6")

    with pytest.raises(ValueError, match="valid JSON"):
        llm.invoke([HumanMessage(content="Analyze AAPL")])


def test_claude_code_chat_model_falls_back_to_plain_text_on_structured_output_retries(monkeypatch):
    calls = []

    def fake_run(command, **kwargs):
        calls.append({"command": command, "kwargs": kwargs})
        if len(calls) == 1:
            return CompletedProcess(
                args=command,
                returncode=1,
                stdout=json.dumps(
                    {
                        "type": "result",
                        "subtype": "error_max_structured_output_retries",
                        "is_error": True,
                        "errors": ["Failed to provide valid structured output after 5 attempts"],
                    }
                ),
                stderr="",
            )
        return CompletedProcess(
            args=command,
            returncode=0,
            stdout="fallback analyst report",
            stderr="",
        )

    monkeypatch.setattr(
        "tradingagents.llm_clients.claude_cli_client.subprocess.run",
        fake_run,
    )

    llm = ClaudeCodeChatModel(model="claude-sonnet-4-6").bind_tools([TEST_TOOL])

    result = llm.invoke([HumanMessage(content="Analyze AAPL social context")])

    assert result.content == "fallback analyst report"
    assert result.tool_calls == []
    assert len(calls) == 2
    assert "--json-schema" in calls[0]["command"]
    assert "--json-schema" not in calls[1]["command"]


def test_claude_code_chat_model_sanitizes_cmux_environment(monkeypatch):
    captured = {}

    def fake_run(command, **kwargs):
        captured["env"] = kwargs["env"]
        captured["cwd"] = kwargs["cwd"]
        return CompletedProcess(
            args=command,
            returncode=0,
            stdout=json.dumps(
                {
                    "type": "result",
                    "subtype": "success",
                    "structured_output": {"content": "ok"},
                }
            ),
            stderr="",
        )

    monkeypatch.setattr(
        "tradingagents.llm_clients.claude_cli_client.subprocess.run",
        fake_run,
    )

    with monkeypatch.context() as m:
        m.setenv("CMUX_SOCKET", "/tmp/cmux.sock")
        m.setenv("CMUX_TAB_ID", "abc")
        m.setenv("TMPDIR", "/tmp/shared")
        llm = ClaudeCodeChatModel(model="claude-sonnet-4-6")
        llm.invoke([HumanMessage(content="Analyze AAPL")])

    assert "CMUX_SOCKET" not in captured["env"]
    assert "CMUX_TAB_ID" not in captured["env"]
    assert captured["env"]["TMPDIR"] != "/tmp/shared"
    assert captured["env"]["TEMP"] == captured["env"]["TMPDIR"]
    assert captured["env"]["TMP"] == captured["env"]["TMPDIR"]
    assert captured["cwd"] == captured["env"]["TMPDIR"]


def test_claude_code_chat_model_preserves_non_cmux_environment(monkeypatch):
    captured = {}

    def fake_run(command, **kwargs):
        captured["env"] = kwargs["env"]
        return CompletedProcess(
            args=command,
            returncode=0,
            stdout=json.dumps(
                {
                    "type": "result",
                    "subtype": "success",
                    "structured_output": {"content": "ok"},
                }
            ),
            stderr="",
        )

    monkeypatch.setattr(
        "tradingagents.llm_clients.claude_cli_client.subprocess.run",
        fake_run,
    )

    with monkeypatch.context() as m:
        m.setenv("OPENAI_API_KEY", "keep-me")
        llm = ClaudeCodeChatModel(model="claude-sonnet-4-6")
        llm.invoke([HumanMessage(content="Analyze AAPL")])

    assert captured["env"]["OPENAI_API_KEY"] == "keep-me"
