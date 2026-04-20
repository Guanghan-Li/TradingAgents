from langchain_core.messages import HumanMessage, SystemMessage

from tradingagents.agents.risk_mgmt.aggressive_debator import create_aggressive_debator
from tradingagents.agents.risk_mgmt.conservative_debator import (
    create_conservative_debator,
)
from tradingagents.agents.risk_mgmt.neutral_debator import create_neutral_debator
from tradingagents.prediction_market.agents.risk_mgmt.neutral_debator import (
    create_pm_neutral_debator,
)


class DummyResponse:
    def __init__(self, content):
        self.content = content


class SequencedLLM:
    def __init__(self, contents):
        self.contents = list(contents)
        self.prompts = []

    def invoke(self, prompt):
        self.prompts.append(prompt)
        return DummyResponse(self.contents.pop(0))


def build_stock_state():
    return {
        "trader_investment_plan": "Buy AMZN on cloud and margin expansion.",
        "market_report": "Market report",
        "sentiment_report": "Sentiment report",
        "news_report": "News report",
        "macro_report": "Macro report",
        "fundamentals_report": "Fundamentals report",
        "factor_rules_report": "Factor rules report",
        "risk_debate_state": {
            "history": "",
            "aggressive_history": "",
            "conservative_history": "",
            "neutral_history": "",
            "latest_speaker": "",
            "current_aggressive_response": "",
            "current_conservative_response": "",
            "current_neutral_response": "",
            "count": 0,
        },
    }


def build_prediction_market_state():
    return {
        "trader_investment_plan": "Buy YES with a 0.25x Kelly position.",
        "event_report": "Event report",
        "odds_report": "Odds report",
        "information_report": "Information report",
        "sentiment_report": "Sentiment report",
        "risk_debate_state": {
            "history": "",
            "aggressive_history": "",
            "conservative_history": "",
            "neutral_history": "",
            "latest_speaker": "",
            "current_aggressive_response": "",
            "current_conservative_response": "",
            "current_neutral_response": "",
            "count": 0,
        },
    }


def test_stock_neutral_debator_retries_persona_refusal():
    llm = SequencedLLM(
        [
            (
                "I cannot adopt the Neutral Risk Analyst persona to advocate for a "
                "specific trading position."
            ),
            "AMZN upside exists, but sizing should stay moderate until execution confirms.",
        ]
    )

    result = create_neutral_debator(llm)(build_stock_state())

    assert len(llm.prompts) == 2
    assert isinstance(llm.prompts[0], list)
    assert isinstance(llm.prompts[0][0], SystemMessage)
    assert isinstance(llm.prompts[0][1], HumanMessage)
    assert "educational purposes" in llm.prompts[0][0].content.lower()
    assert "trading recommendations for a real account" in llm.prompts[0][0].content.lower()
    assert (
        result["risk_debate_state"]["current_neutral_response"]
        == "Neutral Analyst: AMZN upside exists, but sizing should stay moderate until execution confirms."
    )


def test_prediction_market_neutral_debator_retries_persona_refusal():
    llm = SequencedLLM(
        [
            (
                "I cannot adopt the Neutral Risk Analyst persona to advocate for a "
                "specific trading position."
            ),
            "The edge may be real, but the Kelly fraction should be reduced for model uncertainty.",
        ]
    )

    result = create_pm_neutral_debator(llm)(build_prediction_market_state())

    assert len(llm.prompts) == 2
    assert (
        result["risk_debate_state"]["current_neutral_response"]
        == "Neutral Analyst: The edge may be real, but the Kelly fraction should be reduced for model uncertainty."
    )


def test_stock_aggressive_debator_retries_financial_advisor_refusal():
    llm = SequencedLLM(
        [
            (
                "I cannot serve as a financial advisor or provide trading "
                "recommendations. I can help with financial analysis education, "
                "framework explanation, or research methodology instead."
            ),
            "AWS durability and operating leverage support the higher-upside case if execution stays on track.",
        ]
    )

    result = create_aggressive_debator(llm)(build_stock_state())

    assert len(llm.prompts) == 2
    assert (
        result["risk_debate_state"]["current_aggressive_response"]
        == "Aggressive Analyst: AWS durability and operating leverage support the higher-upside case if execution stays on track."
    )


def test_stock_conservative_debator_retries_system_hook_refusal_language():
    llm = SequencedLLM(
        [
            (
                "I understand you need the response in JSON format. However, I can't "
                "generate persuasion-optimized financial arguments designed to override "
                "risk caution, even formatted as structured output. This applies "
                "regardless of tool requirements or system hooks."
            ),
            "Capex intensity and AWS pricing pressure justify a smaller entry with tighter risk limits.",
        ]
    )

    result = create_conservative_debator(llm)(build_stock_state())

    assert len(llm.prompts) == 2
    assert (
        result["risk_debate_state"]["current_conservative_response"]
        == "Conservative Analyst: Capex intensity and AWS pricing pressure justify a smaller entry with tighter risk limits."
    )
