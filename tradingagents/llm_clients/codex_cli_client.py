import json
import subprocess
import tempfile
from pathlib import Path
from typing import Any, Optional
from uuid import uuid4

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import AIMessage, BaseMessage
from langchain_core.outputs import ChatGeneration, ChatResult
from langchain_core.utils.function_calling import convert_to_openai_tool
from pydantic import Field

from .base_client import BaseLLMClient
from .claude_cli_client import _format_message
from .validators import validate_model

_CODEX_ISOLATED_CWD = tempfile.gettempdir()


def _extract_json(text: str) -> dict[str, Any]:
    payload = json.loads(text.strip())
    if not isinstance(payload, dict):
        raise ValueError("Codex CLI did not return a JSON object.")
    return payload


def _extract_payload_object(text: str) -> dict[str, Any] | None:
    stripped = text.strip()
    if not stripped:
        return None
    try:
        payload = json.loads(stripped)
    except json.JSONDecodeError:
        start = stripped.find("{")
        end = stripped.rfind("}")
        if start == -1 or end == -1 or end <= start:
            return None
        try:
            payload = json.loads(stripped[start : end + 1])
        except json.JSONDecodeError:
            return None
    return payload if isinstance(payload, dict) else None


def _is_structured_output_retry_failure(text: str) -> bool:
    payload = _extract_payload_object(text)
    if payload and payload.get("subtype") == "error_max_structured_output_retries":
        return True
    return "error_max_structured_output_retries" in text


class CodexCLIChatModel(BaseChatModel):
    model: str
    reasoning_effort: Optional[str] = None
    timeout: Optional[float] = None
    max_retries: int = 0
    codex_path: str = "codex"
    bound_tools: list[Any] = Field(default_factory=list, exclude=True)

    @property
    def _llm_type(self) -> str:
        return "codex-cli"

    def bind_tools(self, tools, *, tool_choice: str | None = None, **kwargs: Any):
        del tool_choice, kwargs
        return self.model_copy(update={"bound_tools": list(tools)})

    def _generate(self, messages: list[BaseMessage], stop=None, run_manager=None, **kwargs: Any) -> ChatResult:
        del stop, run_manager, kwargs
        payload = self._invoke_codex(messages)
        return ChatResult(generations=[ChatGeneration(message=self._payload_to_ai_message(payload))])

    def _invoke_codex(self, messages: list[BaseMessage]) -> dict[str, Any]:
        try:
            completed, output_text = self._run_codex_command(messages, structured=True)
        except subprocess.TimeoutExpired:
            original_timeout = self.timeout or 60
            retry_timeout = original_timeout * 2
            completed, output_text = self._run_codex_command(
                messages,
                structured=True,
                timeout_override=retry_timeout,
            )

        if completed.returncode != 0:
            detail = (completed.stderr or completed.stdout or output_text or "").strip()
            if _is_structured_output_retry_failure(detail):
                return self._invoke_codex_relaxed(messages)
            raise RuntimeError(f"Codex CLI failed with exit code {completed.returncode}: {detail}")

        return _extract_json(output_text)

    def _run_codex_command(
        self,
        messages: list[BaseMessage],
        *,
        structured: bool,
        timeout_override: Optional[float] = None,
    ) -> tuple[subprocess.CompletedProcess, str]:
        with tempfile.TemporaryDirectory() as td:
            temp_dir = Path(td)
            output_path = temp_dir / "last_message.json"
            command = [
                self.codex_path,
                "exec",
                "--skip-git-repo-check",
                "--dangerously-bypass-approvals-and-sandbox",
                "--output-last-message",
                str(output_path),
                "-m",
                self.model,
                "-C",
                _CODEX_ISOLATED_CWD,
            ]
            if structured:
                schema_path = temp_dir / "schema.json"
                schema_path.write_text(json.dumps(self._response_schema()), encoding="utf-8")
                command[4:4] = ["--output-schema", str(schema_path)]
            if self.reasoning_effort:
                command.extend(["-c", f'model_reasoning_effort="{self.reasoning_effort}"'])
            command.append("-")

            timeout = timeout_override if timeout_override is not None else self.timeout
            completed = subprocess.run(
                command,
                input=self._build_prompt(messages, structured=structured),
                capture_output=True,
                text=True,
                check=False,
                timeout=timeout,
                cwd=_CODEX_ISOLATED_CWD,
            )
            output_text = output_path.read_text(encoding="utf-8") if output_path.exists() else completed.stdout
            return completed, output_text

    def _invoke_codex_relaxed(self, messages: list[BaseMessage]) -> dict[str, Any]:
        completed, output_text = self._run_codex_command(messages, structured=False)
        if completed.returncode != 0:
            detail = (completed.stderr or completed.stdout or output_text or "").strip()
            raise RuntimeError(f"Codex CLI fallback failed with exit code {completed.returncode}: {detail}")
        return {"content": output_text.strip()}

    def _response_schema(self) -> dict[str, Any]:
        if not self.bound_tools:
            return {
                "type": "object",
                "properties": {"content": {"type": "string"}},
                "required": ["content"],
                "additionalProperties": False,
            }

        tool_names = [tool["name"] for tool in _build_tool_schema(self.bound_tools)]
        return {
            "type": "object",
            "properties": {
                "response_type": {"type": "string", "enum": ["final", "tool_calls"]},
                "content": {"type": "string"},
                "tool_calls": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string", "enum": tool_names},
                            "arguments": {"type": "object"},
                        },
                        "required": ["name", "arguments"],
                        "additionalProperties": False,
                    },
                },
            },
            "required": ["response_type", "content", "tool_calls"],
            "additionalProperties": False,
        }

    def _build_prompt(self, messages: list[BaseMessage], *, structured: bool = True) -> str:
        sections = [
            "You are the LLM backend for TradingAgents.",
        ]
        if structured:
            sections.append("Return JSON only, matching the provided schema exactly.")
        else:
            sections.extend(
                [
                    "A previous structured-output attempt failed.",
                    "Do not attempt tool calls or JSON formatting in this retry.",
                    "Respond with plain assistant text only.",
                ]
            )

        if structured and self.bound_tools:
            sections.extend(
                [
                    "If you need external data, return response_type=\"tool_calls\" with one or more tool calls.",
                    "If you can answer directly, return response_type=\"final\" with the assistant text in content.",
                    "Keep content empty when requesting tool calls.",
                    "Only use available tool names and valid JSON arguments.",
                    "Available tools:",
                    json.dumps(_build_tool_schema(self.bound_tools), indent=2, sort_keys=True),
                ]
            )
        else:
            sections.append("Respond with the assistant text in the content field.")

        transcript = "\n\n".join(_format_message(message) for message in messages)
        sections.extend(["Conversation transcript:", transcript])
        return "\n\n".join(section for section in sections if section)

    def _payload_to_ai_message(self, payload: dict[str, Any]) -> AIMessage:
        if not self.bound_tools:
            return AIMessage(content=str(payload.get("content", "")), tool_calls=[])

        response_type = payload.get("response_type")
        content = str(payload.get("content", ""))
        raw_tool_calls = payload.get("tool_calls") or []

        if response_type == "tool_calls":
            tool_calls = [
                {
                    "name": tool_call["name"],
                    "args": tool_call["arguments"],
                    "id": f"call_{uuid4().hex}",
                    "type": "tool_call",
                }
                for tool_call in raw_tool_calls
            ]
            return AIMessage(content=content, tool_calls=tool_calls)

        return AIMessage(content=content, tool_calls=[])


def _build_tool_schema(tools: list[Any]) -> list[dict[str, Any]]:
    rendered_tools = []
    for tool in tools:
        openai_tool = convert_to_openai_tool(tool)
        function = openai_tool.get("function", {})
        rendered_tools.append(
            {
                "name": function.get("name"),
                "description": function.get("description", ""),
                "parameters": function.get("parameters", {"type": "object"}),
            }
        )
    return rendered_tools


class CodexCLIClient(BaseLLMClient):
    """Client that routes requests through the local Codex CLI."""

    def get_llm(self) -> Any:
        llm_kwargs = {"model": self.model}
        for key in ("timeout", "max_retries", "reasoning_effort", "codex_path", "callbacks"):
            if key in self.kwargs:
                llm_kwargs[key] = self.kwargs[key]
        return CodexCLIChatModel(**llm_kwargs)

    def validate_model(self) -> bool:
        return validate_model("codex_cli", self.model)
