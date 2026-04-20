from collections.abc import Mapping
import json
from typing import Any

from langchain_core.messages import HumanMessage, RemoveMessage, SystemMessage

# Import tools from separate utility files
from tradingagents.agents.utils.core_stock_tools import (
    get_stock_data
)
from tradingagents.agents.utils.technical_indicators_tools import (
    get_indicators
)
from tradingagents.agents.utils.fundamental_data_tools import (
    get_fundamentals,
    get_balance_sheet,
    get_cashflow,
    get_income_statement
)
from tradingagents.agents.utils.news_data_tools import (
    get_news,
    get_insider_transactions,
    get_global_news
)
from tradingagents.agents.utils.social_data_tools import (
    get_social_sentiment,
    has_social_sentiment_support,
)
from tradingagents.agents.utils.macro_data_tools import (
    get_economic_indicators,
    get_fed_calendar,
    get_yield_curve,
)
from tradingagents.agents.utils.scenario_tools import (
    get_catalyst_calendar,
    get_scenario_fundamentals,
    get_scenario_news,
)
from tradingagents.agents.utils.segment_tools import (
    get_segment_fundamentals,
    get_segment_income_statement,
    get_segment_news,
)
from tradingagents.agents.utils.sizing_tools import (
    get_sizing_fundamentals,
    get_sizing_indicator,
    get_sizing_price_history,
)
from tradingagents.agents.utils.valuation_tools import (
    get_valuation_inputs,
)


__all__ = [
    "add_educational_use_context",
    "build_social_tools",
    "build_instrument_context",
    "build_analyst_report_context",
    "build_compact_risk_handoff_context",
    "build_committee_debate_messages",
    "build_structured_stock_context",
    "build_structured_stock_priority_context",
    "create_msg_delete",
    "get_balance_sheet",
    "get_cashflow",
    "get_economic_indicators",
    "get_fed_calendar",
    "get_fundamentals",
    "get_global_news",
    "get_income_statement",
    "get_indicators",
    "get_insider_transactions",
    "get_news",
    "get_catalyst_calendar",
    "get_scenario_fundamentals",
    "get_scenario_news",
    "get_segment_fundamentals",
    "get_segment_income_statement",
    "get_segment_news",
    "get_sizing_fundamentals",
    "get_sizing_indicator",
    "get_sizing_price_history",
    "get_social_sentiment",
    "get_stock_data",
    "get_valuation_inputs",
    "has_social_sentiment_support",
    "invoke_committee_debate_llm",
    "get_yield_curve",
]


_ROLEPLAY_REFUSAL_MARKERS = (
    "i cannot",
    "i can't",
    "cannot adopt",
    "can't adopt",
    "cannot take on",
    "can't take on",
    "cannot act as",
    "can't act as",
    "cannot authentically fulfill",
    "can't generate",
    "not appropriate for me to do",
    "what i can do instead",
    "regardless of format",
    "system hooks",
    "structured output",
)

_FINANCIAL_REFUSAL_CONTEXT = (
    "persona",
    "roleplay",
    "financial advisor",
    "trading position",
    "trading recommendation",
    "trading recommendations",
    "trading conviction",
    "financial advice",
    "financial arguments",
    "persuasion",
    "risk caution",
)


def build_social_tools(include_social_sentiment: bool) -> list:
    tools = [get_news]
    if include_social_sentiment:
        tools.insert(0, get_social_sentiment)
    return tools


def add_educational_use_context(instruction_text: str) -> str:
    """Prefix prompts with stable educational-use framing for provider compliance."""
    return (
        "This workflow is for educational purposes, research, and software testing "
        "within a simulated investment committee. It is not personal financial "
        "advice, not regulated brokerage activity, and not trading recommendations "
        "for a real account.\n\n"
        + instruction_text
    )


def build_instrument_context(ticker: str) -> str:
    """Describe the exact instrument so agents preserve exchange-qualified tickers."""
    return (
        f"The instrument to analyze is `{ticker}`. "
        "Use this exact ticker in every tool call, report, and recommendation, "
        "preserving any exchange suffix (e.g. `.TO`, `.L`, `.HK`, `.T`)."
    )


def build_analyst_report_context(state: Mapping[str, Any]) -> str:
    """Build a stable analyst context block for downstream prompts and memory."""
    sections = [
        ("Market Research Report", state.get("market_report", "")),
        ("Social Media Sentiment Report", state.get("sentiment_report", "")),
        ("Latest World Affairs Report", state.get("news_report", "")),
        ("Macro Economic Report", state.get("macro_report", "")),
        ("Company Fundamentals Report", state.get("fundamentals_report", "")),
        ("Factor Rules Report", state.get("factor_rules_report", "")),
    ]
    return "\n".join(
        f"{label}: {content}" for label, content in sections if content
    )


def _truncate_context_block(text: str, max_chars: int) -> str:
    text = (text or "").strip()
    if not text:
        return ""
    if len(text) <= max_chars:
        return text
    return text[: max_chars - 15].rstrip() + "\n...[truncated]"


def _is_placeholder_report(text: str) -> bool:
    normalized = (text or "").strip().lower()
    if not normalized:
        return True
    placeholder_patterns = (
        "i'll analyze",
        "let me gather",
        "requesting social sentiment",
        "i cannot complete the financial analysis request as specified",
    )
    return any(pattern in normalized for pattern in placeholder_patterns)


def build_compact_risk_handoff_context(state: Mapping[str, Any]) -> str:
    """Build a compact evidence block for risk and portfolio stages.

    Risk management already receives trader/research outputs directly. Repeating
    every full analyst report can push local CLI prompts into slow or timeout
    territory, so this helper keeps only the most decision-relevant excerpts.
    """
    sections = [
        ("Market Research Report", state.get("market_report", ""), 1600),
        ("Macro Economic Report", state.get("macro_report", ""), 1400),
        ("Company Fundamentals Report", state.get("fundamentals_report", ""), 1800),
        ("Latest World Affairs Report", state.get("news_report", ""), 1000),
        ("Social Media Sentiment Report", state.get("sentiment_report", ""), 600),
        ("Factor Rules Report", state.get("factor_rules_report", ""), 900),
    ]

    rendered = []
    for label, content, max_chars in sections:
        if _is_placeholder_report(content):
            continue
        truncated = _truncate_context_block(str(content), max_chars)
        if truncated:
            rendered.append(f"{label}: {truncated}")
    return "\n\n".join(rendered)


def build_structured_stock_context(state: Mapping[str, Any]) -> str:
    """Render structured underwriting outputs into prompt-friendly text."""
    sections = []

    segment_data = state.get("segment_data", {})
    if segment_data:
        sections.append(
            "Structured segment analysis:\n"
            + json.dumps(segment_data, indent=2, sort_keys=True)
        )

    scenario_catalyst_data = state.get("scenario_catalyst_data", {})
    if scenario_catalyst_data:
        sections.append(
            "Structured scenario and catalyst analysis:\n"
            + json.dumps(scenario_catalyst_data, indent=2, sort_keys=True)
        )

    position_sizing_data = state.get("position_sizing_data", {})
    if position_sizing_data:
        sections.append(
            "Structured position sizing analysis:\n"
            + json.dumps(position_sizing_data, indent=2, sort_keys=True)
        )

    return "\n\n".join(section for section in sections if section)


def build_structured_stock_priority_context(state: Mapping[str, Any]) -> str:
    structured_context = build_structured_stock_context(state)
    if not structured_context:
        return ""
    return (
        "Prioritize the structured stock underwriting outputs below as primary evidence. "
        "Anchor your reasoning first on numeric fields such as revenue_share_pct, "
        "probability_pct, target_weight_pct, initial_weight_pct, and max_loss_pct "
        "before using freeform analyst reports for narrative color.\n\n"
        + structured_context
    )


def build_committee_debate_messages(role_name: str, task_prompt: str) -> list:
    """Frame debate prompts as an educational committee simulation."""
    system_prompt = (
        "You are participating in a simulated internal investment committee exercise used "
        "for educational purposes, research, and software testing. Aggressive, neutral, "
        "and conservative labels describe analytical lenses for stress-testing a proposed "
        "trade; they are not requests for personal financial advice, regulated brokerage "
        f"activity, trading recommendations for a real account, or identity roleplay. "
        f"Adopt the {role_name} analytical stance, stay grounded in the supplied evidence, "
        "avoid certainty, and provide the requested debate contribution instead of "
        "refusing the stance."
    )
    return [
        SystemMessage(content=system_prompt),
        HumanMessage(content=task_prompt),
    ]


def _looks_like_roleplay_refusal(content: Any) -> bool:
    text = str(content or "").strip().lower()
    if not text:
        return False
    return any(marker in text for marker in _ROLEPLAY_REFUSAL_MARKERS) and any(
        marker in text for marker in _FINANCIAL_REFUSAL_CONTEXT
    )


def invoke_committee_debate_llm(llm, role_name: str, task_prompt: str):
    """Invoke a debate model with educational framing and one refusal retry."""
    messages = build_committee_debate_messages(role_name, task_prompt)
    response = llm.invoke(messages)

    if not _looks_like_roleplay_refusal(getattr(response, "content", "")):
        return response

    retry_prompt = (
        f"{task_prompt}\n\n"
        "Reminder: this is for educational purposes, research, and software testing. "
        "Treat the requested stance as an analytical lens within a simulated committee "
        "exercise and deliver the debate response directly."
    )
    return llm.invoke(build_committee_debate_messages(role_name, retry_prompt))


def create_msg_delete():
    def delete_messages(state):
        """Clear messages and add placeholder for Anthropic compatibility"""
        messages = state["messages"]

        # Remove all messages
        removal_operations = [RemoveMessage(id=m.id) for m in messages]

        # Add a minimal placeholder message
        placeholder = HumanMessage(content="Continue")

        return {"messages": removal_operations + [placeholder]}

    return delete_messages
