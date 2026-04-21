from __future__ import annotations

import json
import os
import threading
import time
from pathlib import Path
from typing import Any

_lock = threading.Lock()
_count = 0


def _append_jsonl(path_str: str, payload: dict) -> None:
    try:
        path = Path(path_str)
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(payload, sort_keys=True, default=str) + "\n")
    except OSError:
        pass


def record_llm_request(provider: str) -> None:
    global _count
    with _lock:
        _count += 1
    progress_file = os.environ.get("TRADINGAGENTS_PROGRESS_FILE")
    if not progress_file:
        return
    _append_jsonl(progress_file, {
        "event": "llm_request",
        "provider": provider,
        "ticker": os.environ.get("TRADINGAGENTS_TICKER"),
    })


def _summarize_messages(messages: Any) -> dict:
    if not messages:
        return {"count": 0, "total_chars": 0, "last_role": None, "last_preview": None, "roles": []}
    roles: list[str] = []
    total_chars = 0
    for msg in messages:
        content = getattr(msg, "content", "")
        if isinstance(content, str):
            total_chars += len(content)
        else:
            total_chars += len(str(content))
        roles.append(getattr(msg, "type", None) or msg.__class__.__name__)
    last = messages[-1]
    last_content = getattr(last, "content", "")
    if not isinstance(last_content, str):
        last_content = str(last_content)
    return {
        "count": len(messages),
        "total_chars": total_chars,
        "last_role": roles[-1],
        "last_preview": last_content[:400],
        "roles": roles,
    }


def _safe_metadata(run_manager: Any) -> dict:
    md = getattr(run_manager, "metadata", None) or {}
    safe: dict[str, Any] = {}
    for key, value in md.items():
        if isinstance(value, (str, int, float, bool)):
            safe[str(key)] = value
        else:
            safe[str(key)] = str(value)[:200]
    return safe


def log_llm_request(
    provider: str,
    *,
    model: Any = None,
    messages: Any = None,
    run_manager: Any = None,
    duration_s: float | None = None,
    error: str | None = None,
) -> None:
    log_file = os.environ.get("TRADINGAGENTS_LLM_LOG_FILE")
    if not log_file:
        return
    tags = list(getattr(run_manager, "tags", None) or []) if run_manager is not None else []
    payload = {
        "ts": time.time(),
        "provider": provider,
        "model": str(model) if model is not None else None,
        "ticker": os.environ.get("TRADINGAGENTS_TICKER"),
        "pid": os.getpid(),
        "duration_s": round(duration_s, 3) if duration_s is not None else None,
        "error": error,
        "tags": tags,
        "metadata": _safe_metadata(run_manager),
        "messages": _summarize_messages(messages),
    }
    _append_jsonl(log_file, payload)


def get_count() -> int:
    return _count


def reset() -> None:
    global _count
    with _lock:
        _count = 0
