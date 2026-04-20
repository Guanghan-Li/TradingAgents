import json
import subprocess
from subprocess import CompletedProcess

from langchain_core.messages import AIMessage, HumanMessage

from tradingagents.llm_clients.codex_cli_client import CodexCLIClient, CodexCLIChatModel


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


def test_codex_cli_client_returns_chat_model():
    client = CodexCLIClient(model="gpt-5.4", reasoning_effort="medium")

    llm = client.get_llm()

    assert isinstance(llm, CodexCLIChatModel)
    assert llm.model == "gpt-5.4"
    assert llm.reasoning_effort == "medium"


def test_codex_cli_chat_model_returns_final_ai_message(monkeypatch, tmp_path):
    captured = {}
    output_file = tmp_path / "last_message.json"

    def fake_run(command, **kwargs):
        captured["command"] = command
        captured["kwargs"] = kwargs
        output_file.write_text(json.dumps({"content": "final analysis"}), encoding="utf-8")
        return CompletedProcess(args=command, returncode=0, stdout="", stderr="")

    monkeypatch.setattr(
        "tradingagents.llm_clients.codex_cli_client.subprocess.run",
        fake_run,
    )
    monkeypatch.setattr(
        "tradingagents.llm_clients.codex_cli_client.tempfile.TemporaryDirectory",
        lambda: _TempDir(tmp_path),
    )

    llm = CodexCLIChatModel(model="gpt-5.4", reasoning_effort="medium")
    result = llm.invoke([HumanMessage(content="Analyze AAPL")])

    assert isinstance(result, AIMessage)
    assert result.content == "final analysis"
    assert result.tool_calls == []
    assert captured["command"][:2] == ["codex", "exec"]
    assert "-m" in captured["command"]
    assert "gpt-5.4" in captured["command"]
    assert "model_reasoning_effort=\"medium\"" in captured["command"]


def test_codex_cli_chat_model_returns_tool_calls(monkeypatch, tmp_path):
    output_file = tmp_path / "last_message.json"

    def fake_run(command, **kwargs):
        output_file.write_text(
            json.dumps(
                {
                    "response_type": "tool_calls",
                    "content": "",
                    "tool_calls": [
                        {
                            "name": "get_stock_data",
                            "arguments": {"ticker": "AAPL"},
                        }
                    ],
                }
            ),
            encoding="utf-8",
        )
        return CompletedProcess(args=command, returncode=0, stdout="", stderr="")

    monkeypatch.setattr(
        "tradingagents.llm_clients.codex_cli_client.subprocess.run",
        fake_run,
    )
    monkeypatch.setattr(
        "tradingagents.llm_clients.codex_cli_client.tempfile.TemporaryDirectory",
        lambda: _TempDir(tmp_path),
    )

    llm = CodexCLIChatModel(model="gpt-5.4", reasoning_effort="medium").bind_tools([TEST_TOOL])
    result = llm.invoke([HumanMessage(content="Get AAPL data")])

    assert result.content == ""
    assert result.tool_calls[0]["name"] == "get_stock_data"
    assert result.tool_calls[0]["args"] == {"ticker": "AAPL"}
    assert result.tool_calls[0]["type"] == "tool_call"


def test_codex_cli_retries_once_on_timeout(monkeypatch, tmp_path):
    output_file = tmp_path / "last_message.json"
    calls = []

    def fake_run(command, **kwargs):
        calls.append(kwargs.get("timeout"))
        if len(calls) == 1:
            raise subprocess.TimeoutExpired(command, kwargs.get("timeout"))
        output_file.write_text(json.dumps({"content": "retried"}), encoding="utf-8")
        return CompletedProcess(args=command, returncode=0, stdout="", stderr="")

    monkeypatch.setattr(
        "tradingagents.llm_clients.codex_cli_client.subprocess.run",
        fake_run,
    )
    monkeypatch.setattr(
        "tradingagents.llm_clients.codex_cli_client.tempfile.TemporaryDirectory",
        lambda: _TempDir(tmp_path),
    )

    llm = CodexCLIChatModel(model="gpt-5.4", reasoning_effort="medium", timeout=30)
    result = llm.invoke([HumanMessage(content="Analyze AAPL")])

    assert result.content == "retried"
    assert calls == [30, 60]


def test_codex_cli_falls_back_after_structured_output_failure(monkeypatch, tmp_path):
    output_file = tmp_path / "last_message.json"
    commands = []

    def fake_run(command, **kwargs):
        commands.append(command)
        if len(commands) == 1:
            return CompletedProcess(
                args=command,
                returncode=1,
                stdout="",
                stderr="error_max_structured_output_retries",
            )
        output_file.write_text("relaxed answer", encoding="utf-8")
        return CompletedProcess(args=command, returncode=0, stdout="", stderr="")

    monkeypatch.setattr(
        "tradingagents.llm_clients.codex_cli_client.subprocess.run",
        fake_run,
    )
    monkeypatch.setattr(
        "tradingagents.llm_clients.codex_cli_client.tempfile.TemporaryDirectory",
        lambda: _TempDir(tmp_path),
    )

    llm = CodexCLIChatModel(model="gpt-5.4", reasoning_effort="medium")
    result = llm.invoke([HumanMessage(content="Analyze AAPL")])

    assert result.content == "relaxed answer"
    assert "--output-schema" in commands[0]
    assert "--output-schema" not in commands[1]


class _TempDir:
    def __init__(self, path):
        self.path = path

    def __enter__(self):
        return str(self.path)

    def __exit__(self, exc_type, exc, tb):
        return False
