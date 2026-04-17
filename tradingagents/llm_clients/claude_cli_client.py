import json
import os
import subprocess
import tempfile
from typing import Any, Optional
from uuid import uuid4

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage, ToolMessage
from langchain_core.outputs import ChatGeneration, ChatResult
from langchain_core.utils.function_calling import convert_to_openai_tool
from pydantic import Field

from .base_client import BaseLLMClient
from .validators import validate_model

_CLAUDE_ISOLATED_CWD = tempfile.gettempdir()
_CLAUDE_ENV_BLOCKLIST_PREFIXES = ("CMUX_",)


def _stringify_content(content: Any) -> str:
    if content is None:
        return ""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for item in content:
            if isinstance(item, str):
                parts.append(item)
            elif isinstance(item, dict) and "text" in item:
                parts.append(str(item["text"]))
            else:
                parts.append(json.dumps(item, sort_keys=True))
        return "\n".join(part for part in parts if part)
    if isinstance(content, dict):
        return json.dumps(content, indent=2, sort_keys=True)
    return str(content)


def _format_message(message: BaseMessage) -> str:
    content = _stringify_content(message.content)

    if isinstance(message, SystemMessage):
        return f"[SYSTEM]\n{content}"

    if isinstance(message, HumanMessage):
        return f"[USER]\n{content}"

    if isinstance(message, ToolMessage):
        tool_name = getattr(message, "name", None) or "tool"
        return (
            f"[TOOL RESULT name={tool_name} id={message.tool_call_id} status={message.status}]\n"
            f"{content}"
        )

    if isinstance(message, AIMessage):
        lines = []
        if content:
            lines.append(f"[ASSISTANT]\n{content}")
        if getattr(message, "tool_calls", None):
            rendered_calls = json.dumps(message.tool_calls, indent=2, sort_keys=True)
            lines.append(f"[ASSISTANT TOOL CALLS]\n{rendered_calls}")
        return "\n".join(lines) if lines else "[ASSISTANT]"

    return f"[MESSAGE type={message.type}]\n{content}"


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


def _extract_json(stdout: str) -> dict[str, Any]:
    text = stdout.strip()
    try:
        payload = json.loads(text)
    except json.JSONDecodeError:
        start = text.find("{")
        end = text.rfind("}")
        if start == -1 or end == -1 or end <= start:
            raise ValueError("Claude CLI did not return valid JSON.") from None
        try:
            payload = json.loads(text[start : end + 1])
        except json.JSONDecodeError as exc:
            raise ValueError("Claude CLI did not return valid JSON.") from exc

    if isinstance(payload, dict) and isinstance(payload.get("structured_output"), dict):
        return payload["structured_output"]

    if isinstance(payload, dict) and isinstance(payload.get("result"), str):
        result_text = payload["result"].strip()
        if result_text.startswith("{") and result_text.endswith("}"):
            try:
                return json.loads(result_text)
            except json.JSONDecodeError:
                pass

    if isinstance(payload, dict):
        return payload

    raise ValueError("Claude CLI did not return a JSON object.")


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


def _build_claude_subprocess_env(*, tmpdir: str) -> dict[str, str]:
    env = {
        key: value
        for key, value in os.environ.items()
        if not any(key.startswith(prefix) for prefix in _CLAUDE_ENV_BLOCKLIST_PREFIXES)
    }
    env["TMPDIR"] = tmpdir
    env["TMP"] = tmpdir
    env["TEMP"] = tmpdir
    return env


class ClaudeCodeChatModel(BaseChatModel):
    model: str
    effort: Optional[str] = None
    timeout: Optional[float] = None
    max_retries: int = 0
    claude_path: str = "claude"
    bound_tools: list[Any] = Field(default_factory=list, exclude=True)

    @property
    def _llm_type(self) -> str:
        return "claude-code"

    def bind_tools(self, tools, *, tool_choice: str | None = None, **kwargs: Any):
        del tool_choice, kwargs
        return self.model_copy(update={"bound_tools": list(tools)})

    def _generate(self, messages: list[BaseMessage], stop=None, run_manager=None, **kwargs: Any) -> ChatResult:
        del stop, run_manager, kwargs
        payload = self._invoke_claude(messages)
        message = self._payload_to_ai_message(payload)
        return ChatResult(generations=[ChatGeneration(message=message)])

    def _invoke_claude(self, messages: list[BaseMessage]) -> dict[str, Any]:
        try:
            completed = self._run_claude_command(
                messages,
                structured=True,
            )
        except subprocess.TimeoutExpired:
            # Retry once with 2x timeout in fresh subprocess/tmpdir
            original_timeout = self.timeout or 60
            retry_timeout = original_timeout * 2
            completed = self._run_claude_command(
                messages,
                structured=True,
                timeout_override=retry_timeout,
            )

        if completed.returncode != 0:
            stderr = (completed.stderr or completed.stdout or "").strip()
            if _is_structured_output_retry_failure(stderr):
                return self._invoke_claude_relaxed(messages)
            raise RuntimeError(f"Claude CLI failed with exit code {completed.returncode}: {stderr}")

        return _extract_json(completed.stdout)

    def _run_claude_command(
        self,
        messages: list[BaseMessage],
        *,
        structured: bool,
        timeout_override: Optional[float] = None,
    ) -> subprocess.CompletedProcess:
        schema = self._response_schema()
        command = [
            self.claude_path,
            "-p",
            "--output-format",
            "json" if structured else "text",
            "--input-format",
            "text",
            "--setting-sources",
            "user",
            "--model",
            self.model,
        ]
        if structured:
            command.extend(
                [
                    "--tools",
                    "",
                    "--json-schema",
                    json.dumps(schema, separators=(",", ":"), sort_keys=True),
                ]
            )
        if self.effort:
            command.extend(["--effort", self.effort])

        timeout = timeout_override if timeout_override is not None else self.timeout
        with tempfile.TemporaryDirectory(prefix="tradingagents-claude-cli-") as tmpdir:
            return subprocess.run(
                command,
                input=self._build_prompt(messages, structured=structured),
                capture_output=True,
                text=True,
                check=False,
                timeout=timeout,
                cwd=tmpdir,
                env=_build_claude_subprocess_env(tmpdir=tmpdir),
            )

    def _invoke_claude_relaxed(self, messages: list[BaseMessage]) -> dict[str, Any]:
        completed = self._run_claude_command(messages, structured=False)
        if completed.returncode != 0:
            stderr = (completed.stderr or completed.stdout or "").strip()
            raise RuntimeError(f"Claude CLI fallback failed with exit code {completed.returncode}: {stderr}")
        return {"content": completed.stdout.strip()}

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
                    "Return the best plain-text answer you can from the same conversation.",
                    "Do not attempt tool calls or JSON formatting in this retry.",
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
            sections.append(
                "Respond with the assistant text in the content field."
                if structured
                else "Respond with plain text only."
            )

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


class ClaudeCLIClient(BaseLLMClient):
    """Client that routes requests through the local Claude Code CLI."""

    def get_llm(self) -> Any:
        llm_kwargs = {"model": self.model}
        for key in ("timeout", "max_retries", "effort", "claude_path", "callbacks"):
            if key in self.kwargs:
                llm_kwargs[key] = self.kwargs[key]
        return ClaudeCodeChatModel(**llm_kwargs)

    def validate_model(self) -> bool:
        return validate_model("claude_code", self.model)
