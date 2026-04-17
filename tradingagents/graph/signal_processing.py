# TradingAgents/graph/signal_processing.py

import re

from langchain_openai import ChatOpenAI


_VALID_ACTIONS = ("BUY", "HOLD", "SELL")


def _normalize_action(raw: str) -> str | None:
    normalized = (raw or "").strip().upper().strip("*").strip()
    if normalized in _VALID_ACTIONS:
        return normalized
    if normalized == "OVERWEIGHT":
        return "BUY"
    if normalized == "UNDERWEIGHT":
        return "SELL"
    return None


def _extract_action(full_signal: str) -> str | None:
    patterns = [
        r"FINAL TRANSACTION PROPOSAL:\s*\*\*(BUY|HOLD|SELL)\*\*",
        r"FINAL TRANSACTION PROPOSAL:\s*(BUY|HOLD|SELL)",
        r"\*\*Absolute Action\*\*:\s*\**(BUY|HOLD|SELL)\**",
        r"Absolute Action:\s*\**(BUY|HOLD|SELL)\**",
        r"\*\*Rating\*\*:\s*\**(BUY|OVERWEIGHT|HOLD|UNDERWEIGHT|SELL)\**",
        r"Rating:\s*\**(BUY|OVERWEIGHT|HOLD|UNDERWEIGHT|SELL)\**",
    ]
    for pattern in patterns:
        match = re.search(pattern, full_signal or "", re.IGNORECASE)
        if match:
            action = _normalize_action(match.group(1))
            if action:
                return action

    for action in ("BUY", "HOLD", "SELL", "OVERWEIGHT", "UNDERWEIGHT"):
        if re.search(rf"\b{action}\b", full_signal or "", re.IGNORECASE):
            normalized = _normalize_action(action)
            if normalized:
                return normalized
    return None


class SignalProcessor:
    """Processes trading signals to extract actionable decisions."""

    def __init__(self, quick_thinking_llm: ChatOpenAI):
        """Initialize with an LLM for processing."""
        self.quick_thinking_llm = quick_thinking_llm

    def process_signal(self, full_signal: str) -> str:
        """
        Process a full trading signal to extract the core decision.

        Args:
            full_signal: Complete trading signal text

        Returns:
            Extracted absolute action (BUY, HOLD, or SELL)
        """
        extracted = _extract_action(full_signal)
        if extracted:
            return extracted
        return "HOLD"
