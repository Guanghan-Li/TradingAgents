from __future__ import annotations

from typing import Any, Callable, Optional

import anthropic
from langchain_core.messages import AIMessage


_ANTHROPIC_GRACEFUL_STATUS_CODES = {403, 502, 503, 504, 524}
_CLAUDE_CODE_REFUSAL_PATTERNS = (
    "i'm claude, made by anthropic",
    "i'm claude, an ai assistant made by anthropic",
    "claude documentation assistant",
    "questions about claude",
    "genuine questions about claude",
    "outside the scope of what this session is configured for",
    "i don't have access to any prior conversation history",
    "system prompt telling me i'm a claude documentation assistant",
    "i won't fabricate financial analysis",
    "i won't generate fabricated trading recommendations",
    "i cannot provide trading recommendations because",
    "i cannot provide financial trading recommendations",
    "i cannot provide definitive buy/hold/sell trading recommendations",
    "i cannot provide definitive buy, hold, or sell trading recommendations",
    "i cannot make binding financial trading recommendations",
    "i don't have access to financial data tools",
    "i'm not integrated with tradingagents or live market feeds",
    "please clarify what you'd like me to continue with",
    "what is your task or question",
    "what would be most helpful here",
    "what would actually be helpful here",
    "what would actually be useful",
)


def is_anthropic_backend_failure(exc: Exception) -> bool:
    if isinstance(exc, (anthropic.APITimeoutError, anthropic.APIConnectionError)):
        return True

    if isinstance(exc, anthropic.APIStatusError):
        status_code = getattr(exc, "status_code", None)
        if status_code is None and getattr(exc, "response", None) is not None:
            status_code = getattr(exc.response, "status_code", None)
        return status_code in _ANTHROPIC_GRACEFUL_STATUS_CODES

    return False


def _extract_backend_detail(exc: Exception) -> tuple[Optional[int], str, str]:
    status_code = getattr(exc, "status_code", None)
    response = getattr(exc, "response", None)
    if status_code is None and response is not None:
        status_code = getattr(response, "status_code", None)
    request = getattr(response, "request", None) if response is not None else None
    endpoint = str(getattr(request, "url", "") or "")
    detail = str(exc).strip() or exc.__class__.__name__
    return status_code, endpoint, detail


def _build_degraded_report(analyst_name: str, state: dict[str, Any], exc: Exception) -> str:
    ticker = state.get("company_of_interest", "")
    trade_date = state.get("trade_date", "")
    status_code, endpoint, detail = _extract_backend_detail(exc)

    lines = [
        f"## {analyst_name} degraded backend fallback",
        "",
        f"- Instrument: {ticker or 'unknown'}",
        f"- Analysis date: {trade_date or 'unknown'}",
    ]
    if status_code is not None:
        lines.append(f"- Backend status: {status_code}")
    if endpoint:
        lines.append(f"- Endpoint: {endpoint}")
    lines.append(f"- Detail: {detail}")
    lines.extend(
        [
            "",
            "Claude backend was unavailable during this analyst stage, so this section is a degraded fallback rather than a live model judgment.",
            "Downstream agents should treat this section as unavailable evidence and avoid over-weighting it.",
        ]
    )
    return "\n".join(lines)


def _build_degraded_report_from_detail(
    analyst_name: str,
    state: dict[str, Any],
    detail: str,
) -> str:
    ticker = state.get("company_of_interest", "")
    trade_date = state.get("trade_date", "")
    lines = [
        f"## {analyst_name} degraded backend fallback",
        "",
        f"- Instrument: {ticker or 'unknown'}",
        f"- Analysis date: {trade_date or 'unknown'}",
        f"- Detail: {detail}",
        "",
        "Claude backend returned an unusable support/refusal response for this analyst stage.",
        "Downstream agents should treat this section as unavailable evidence and avoid over-weighting it.",
    ]
    return "\n".join(lines)


def is_claude_code_refusal_text(text: str) -> bool:
    normalized = (text or "").strip().lower()
    if not normalized:
        return False
    return any(pattern in normalized for pattern in _CLAUDE_CODE_REFUSAL_PATTERNS)


def _collect_candidate_texts(value: Any) -> list[str]:
    texts: list[str] = []

    if isinstance(value, str):
        texts.append(value)
        return texts

    if isinstance(value, dict):
        for nested_value in value.values():
            texts.extend(_collect_candidate_texts(nested_value))
        return texts

    if isinstance(value, (list, tuple, set)):
        for nested_value in value:
            texts.extend(_collect_candidate_texts(nested_value))
        return texts

    content = getattr(value, "content", None)
    if isinstance(content, str):
        texts.append(content)
    elif isinstance(content, list):
        texts.extend(_collect_candidate_texts(content))

    return texts


def wrap_quick_analyst_node(
    node: Callable[[dict[str, Any]], dict[str, Any]] | Any,
    *,
    analyst_name: str,
    report_key: str | None = None,
    extra_state_factory: Optional[Callable[[dict[str, Any], str], dict[str, Any]]] = None,
):
    if not callable(node):
        return node

    def wrapped(state: dict[str, Any]) -> dict[str, Any]:
        try:
            payload = node(state)
        except Exception as exc:
            if not is_anthropic_backend_failure(exc):
                raise

            fallback_report = _build_degraded_report(analyst_name, state, exc)
            payload: dict[str, Any] = {"messages": [AIMessage(content=fallback_report)]}
            if report_key:
                payload[report_key] = fallback_report
            if extra_state_factory is not None:
                payload.update(extra_state_factory(state, fallback_report))
            return payload

        candidate_texts = _collect_candidate_texts(payload)
        if any(is_claude_code_refusal_text(text) for text in candidate_texts):
            fallback_report = _build_degraded_report_from_detail(
                analyst_name,
                state,
                "Anthropic backend returned a Claude Code/support refusal instead of task output.",
            )
            degraded_payload: dict[str, Any] = {"messages": [AIMessage(content=fallback_report)]}
            if report_key:
                degraded_payload[report_key] = fallback_report
            if extra_state_factory is not None:
                degraded_payload.update(extra_state_factory(state, fallback_report))
            return degraded_payload

        return payload

    return wrapped


def build_degraded_stock_final_state(
    *,
    ticker: str,
    analysis_date: str,
    selected_analysts: list[str],
    backend_detail: str,
) -> tuple[dict[str, Any], str]:
    from tradingagents.agents.utils.agent_states import (
        InvestDebateState,
        RiskDebateState,
        build_chief_analyst_data_defaults,
        make_default_structured_stock_underwriting_state,
    )

    decision = "HOLD"
    report_map = {
        "market": "market_report",
        "social": "sentiment_report",
        "news": "news_report",
        "fundamentals": "fundamentals_report",
        "macro": "macro_report",
        "factor_rules": "factor_rules_report",
        "segment": "segment_report",
        "scenario": "scenario_catalyst_report",
        "position_sizing": "position_sizing_report",
    }

    final_state: dict[str, Any] = {
        "messages": [],
        "company_of_interest": ticker,
        "trade_date": analysis_date,
        "sender": "Chief Analyst",
        "market_report": "",
        "fundamentals_report": "",
        "sentiment_report": "",
        "news_report": "",
        "factor_rules_report": "",
        "macro_report": "",
        "segment_report": "",
        "scenario_catalyst_report": "",
        "position_sizing_report": "",
        "chief_analyst_report": "",
        **make_default_structured_stock_underwriting_state(),
    }

    for analyst in selected_analysts:
        report_key = report_map.get(analyst)
        if report_key:
            final_state[report_key] = (
                f"## {analyst.replace('_', ' ').title()} degraded backend fallback\n\n"
                f"Claude backend was unavailable during this run.\n\n"
                f"Detail: {backend_detail}"
            )

    final_state["investment_debate_state"] = InvestDebateState(
        {
            "bull_history": "Bull Analyst: Claude backend unavailable; no live bull debate.",
            "bear_history": "Bear Analyst: Claude backend unavailable; no live bear debate.",
            "history": "Research debate degraded because Claude backend was unavailable.",
            "current_response": "Research manager fallback: HOLD due to backend unavailability.",
            "judge_decision": "Research manager fallback: HOLD due to backend unavailability.",
            "count": 1,
        }
    )
    final_state["investment_plan"] = (
        "Research manager fallback: HOLD. Claude backend was unavailable, so no live debate-based investment plan could be produced."
    )
    final_state["trader_investment_plan"] = (
        "Trader fallback: no trade. Claude backend was unavailable, so execute no action and wait for a healthy rerun."
    )
    final_state["risk_debate_state"] = RiskDebateState(
        {
            "aggressive_history": "Aggressive Analyst: degraded backend fallback.",
            "conservative_history": "Conservative Analyst: degraded backend fallback.",
            "neutral_history": "Neutral Analyst: degraded backend fallback.",
            "history": "Risk debate degraded because Claude backend was unavailable.",
            "latest_speaker": "Judge",
            "current_aggressive_response": "Aggressive Analyst: degraded backend fallback.",
            "current_conservative_response": "Conservative Analyst: degraded backend fallback.",
            "current_neutral_response": "Neutral Analyst: degraded backend fallback.",
            "judge_decision": backend_detail,
            "count": 1,
        }
    )
    final_state["final_trade_decision"] = "\n".join(
        [
            "Absolute Action: Hold",
            "Relative Stance: Neutral",
            "Executive Summary: Claude backend was unavailable during the run, so no live portfolio decision could be produced. Preserve capital and rerun when the backend is healthy.",
            "Investment Thesis: The workflow completed in degraded mode. Use the generated fallback reports only as placeholders, not as live investment evidence.",
        ]
    )
    chief_data = build_chief_analyst_data_defaults(
        ticker=ticker,
        analysis_date=analysis_date,
    )
    chief_data["verdict"] = {
        "absolute_action": "Hold",
        "relative_stance": "Neutral",
        "summary": "Claude backend unavailable; preserve capital and rerun when the provider is healthy.",
        "thesis": "This run completed in degraded mode because the configured Claude backend was unavailable.",
    }
    chief_data["execution"] = {
        "research_plan": final_state["investment_plan"],
        "trader_plan": final_state["trader_investment_plan"],
        "portfolio_manager_guidance": chief_data["verdict"]["summary"],
    }
    chief_data["tail_risk"] = {
        "risk_summary": backend_detail,
        "invalidation_triggers": [],
    }
    final_state["chief_analyst_data"] = chief_data
    final_state["chief_analyst_report"] = "\n".join(
        [
            "## Chief Analyst Summary",
            "",
            "### Verdict",
            "- Absolute Action: Hold",
            "- Relative Stance: Neutral",
            f"- Summary: {chief_data['verdict']['summary']}",
            f"- Thesis: {chief_data['verdict']['thesis']}",
            "",
            "### Backend Health",
            f"- Detail: {backend_detail}",
        ]
    )

    return final_state, decision
