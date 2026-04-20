"""Lightweight timing wrapper around llm.invoke so long-running calls are visible in logs."""
from __future__ import annotations

import sys
import time


def timed_invoke(label: str, llm, prompt, **kwargs):
    start = time.monotonic()
    print(f"[llm_timing] {label}: invoke start", flush=True, file=sys.stderr)
    try:
        response = llm.invoke(prompt, **kwargs)
    except Exception as exc:
        elapsed = time.monotonic() - start
        print(
            f"[llm_timing] {label}: invoke FAILED after {elapsed:.1f}s: "
            f"{type(exc).__name__}: {exc}",
            flush=True,
            file=sys.stderr,
        )
        raise
    elapsed = time.monotonic() - start
    print(f"[llm_timing] {label}: invoke ok in {elapsed:.1f}s", flush=True, file=sys.stderr)
    return response
