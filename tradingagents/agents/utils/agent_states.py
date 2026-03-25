from typing import Annotated, Any, Sequence
from datetime import date, timedelta, datetime
from typing_extensions import TypedDict, Optional
from langchain_openai import ChatOpenAI
from tradingagents.agents import *
from langgraph.prebuilt import ToolNode
from langgraph.graph import END, StateGraph, START, MessagesState


# Researcher team state
class InvestDebateState(TypedDict):
    bull_history: Annotated[
        str, "Bullish Conversation history"
    ]  # Bullish Conversation history
    bear_history: Annotated[
        str, "Bearish Conversation history"
    ]  # Bullish Conversation history
    history: Annotated[str, "Conversation history"]  # Conversation history
    current_response: Annotated[str, "Latest response"]  # Last response
    judge_decision: Annotated[str, "Final judge decision"]  # Last response
    count: Annotated[int, "Length of the current conversation"]  # Conversation length


# Risk management team state
class RiskDebateState(TypedDict):
    aggressive_history: Annotated[
        str, "Aggressive Agent's Conversation history"
    ]  # Conversation history
    conservative_history: Annotated[
        str, "Conservative Agent's Conversation history"
    ]  # Conversation history
    neutral_history: Annotated[
        str, "Neutral Agent's Conversation history"
    ]  # Conversation history
    history: Annotated[str, "Conversation history"]  # Conversation history
    latest_speaker: Annotated[str, "Analyst that spoke last"]
    current_aggressive_response: Annotated[
        str, "Latest response by the aggressive analyst"
    ]  # Last response
    current_conservative_response: Annotated[
        str, "Latest response by the conservative analyst"
    ]  # Last response
    current_neutral_response: Annotated[
        str, "Latest response by the neutral analyst"
    ]  # Last response
    judge_decision: Annotated[str, "Judge's decision"]
    count: Annotated[int, "Length of the current conversation"]  # Conversation length


class SegmentDataState(TypedDict):
    ticker: Annotated[str, "Instrument ticker analyzed for segment conclusions"]
    analysis_date: Annotated[str, "Trade date associated with the segment analysis"]
    business_unit_decomposition: Annotated[
        list[dict[str, Any]],
        "Structured list of major business units and their roles",
    ]
    segment_economics: Annotated[
        dict[str, Any],
        "Structured economics summary such as margin profile and cyclicality",
    ]
    value_driver_map: Annotated[
        list[dict[str, Any]],
        "Structured list mapping drivers to impacted segments and directionality",
    ]


class ScenarioCatalystDataState(TypedDict):
    ticker: Annotated[str, "Instrument ticker analyzed for scenario/catalyst conclusions"]
    analysis_date: Annotated[
        str,
        "Trade date associated with the scenario/catalyst analysis",
    ]
    scenario_map: Annotated[
        list[dict[str, Any]],
        "Structured bull/base/bear scenario map with probability and thesis details",
    ]
    dated_catalyst_map: Annotated[
        list[dict[str, Any]],
        "Structured list of dated catalysts linked to scenario outcomes",
    ]
    invalidation_triggers: Annotated[
        list[dict[str, Any]],
        "Structured list of thesis invalidation triggers and evidence to monitor",
    ]


class ChiefAnalystVerdictState(TypedDict):
    rating: Annotated[str, "Canonical top-level rating from the portfolio manager"]
    summary: Annotated[str, "Compressed execution-oriented summary of the verdict"]
    thesis: Annotated[str, "Compressed investment thesis supporting the verdict"]


class ChiefAnalystFairValueState(TypedDict):
    bull_case: Annotated[str, "Bull-case fair-value framing or upside scenario"]
    base_case: Annotated[str, "Base-case fair-value framing or core scenario"]
    bear_case: Annotated[str, "Bear-case fair-value framing or downside scenario"]


class ChiefAnalystExecutionState(TypedDict):
    research_plan: Annotated[str, "Research manager direction carried into execution"]
    trader_plan: Annotated[str, "Trader execution plan carried into the final summary"]
    portfolio_manager_guidance: Annotated[
        str,
        "Execution guidance compressed from the portfolio manager decision",
    ]


class ChiefAnalystTailRiskState(TypedDict):
    risk_summary: Annotated[str, "Compressed risk summary from the risk debate"]
    invalidation_triggers: Annotated[
        list[dict[str, str]],
        "Structured triggers that would invalidate the current thesis",
    ]


class ChiefAnalystVariantPerceptionState(TypedDict):
    business_segments: Annotated[
        list[str],
        "Business segments relevant to the market's potential blind spot",
    ]
    value_drivers: Annotated[
        list[str],
        "Drivers relevant to the market's potential blind spot",
    ]


class ChiefAnalystDataState(TypedDict):
    ticker: Annotated[str, "Instrument ticker analyzed for the final summary"]
    analysis_date: Annotated[str, "Trade date associated with the final summary"]
    verdict: Annotated[ChiefAnalystVerdictState, "Canonical verdict data"]
    fair_value: Annotated[ChiefAnalystFairValueState, "Stable bull/base/bear framing"]
    catalysts: Annotated[
        list[dict[str, str]],
        "Structured near-term catalysts that can change the verdict",
    ]
    execution: Annotated[ChiefAnalystExecutionState, "Execution guidance"]
    tail_risk: Annotated[ChiefAnalystTailRiskState, "Risk summary and invalidations"]
    variant_perception: Annotated[
        ChiefAnalystVariantPerceptionState,
        "Segment and driver framing for what the market may be underappreciating",
    ]


def build_chief_analyst_data_defaults(
    ticker: str = "",
    analysis_date: str = "",
) -> ChiefAnalystDataState:
    return {
        "ticker": ticker,
        "analysis_date": analysis_date,
        "verdict": {
            "rating": "",
            "summary": "",
            "thesis": "",
        },
        "fair_value": {
            "bull_case": "",
            "base_case": "",
            "bear_case": "",
        },
        "catalysts": [],
        "execution": {
            "research_plan": "",
            "trader_plan": "",
            "portfolio_manager_guidance": "",
        },
        "tail_risk": {
            "risk_summary": "",
            "invalidation_triggers": [],
        },
        "variant_perception": {
            "business_segments": [],
            "value_drivers": [],
        },
    }


class AgentState(MessagesState):
    company_of_interest: Annotated[str, "Company that we are interested in trading"]
    trade_date: Annotated[str, "What date we are trading at"]

    sender: Annotated[str, "Agent that sent this message"]

    # research step
    market_report: Annotated[str, "Report from the Market Analyst"]
    sentiment_report: Annotated[str, "Report from the Social Media Analyst"]
    news_report: Annotated[
        str, "Report from the News Researcher of current world affairs"
    ]
    fundamentals_report: Annotated[str, "Report from the Fundamentals Researcher"]
    segment_report: Annotated[str, "Report from the Segment Analyst"]
    segment_data: Annotated[
        SegmentDataState,
        "Structured segment analysis output for downstream consumption",
    ]
    scenario_catalyst_report: Annotated[
        str,
        "Report from the Scenario and Catalyst Analyst",
    ]
    scenario_catalyst_data: Annotated[
        ScenarioCatalystDataState,
        "Structured scenario and catalyst analysis output for downstream consumption",
    ]
    chief_analyst_report: Annotated[
        str,
        "Concise final summary report from the Chief Analyst",
    ]
    chief_analyst_data: Annotated[
        ChiefAnalystDataState,
        "Structured final summary from the Chief Analyst",
    ]

    # researcher team discussion step
    investment_debate_state: Annotated[
        InvestDebateState, "Current state of the debate on if to invest or not"
    ]
    investment_plan: Annotated[str, "Plan generated by the Analyst"]

    trader_investment_plan: Annotated[str, "Plan generated by the Trader"]

    # risk management team discussion step
    risk_debate_state: Annotated[
        RiskDebateState, "Current state of the debate on evaluating risk"
    ]
    final_trade_decision: Annotated[str, "Final decision made by the Risk Analysts"]
