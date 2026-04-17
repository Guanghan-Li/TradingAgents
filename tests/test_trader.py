from langchain_core.messages import AIMessage

from tradingagents.agents.trader.trader import create_trader


class DummyMemory:
    def get_memories(self, _situation, n_matches=2):
        return []


class FakeLLM:
    def __init__(self, content):
        self.content = content
        self.prompts = []

    def invoke(self, messages):
        self.prompts.append(messages)
        return AIMessage(content=self.content)


def test_trader_reuses_investment_plan_when_claude_returns_refusal():
    refusal = (
        "I cannot provide definitive BUY/HOLD/SELL trading recommendations. "
        "I am Claude, made by Anthropic."
    )
    llm = FakeLLM(refusal)
    node = create_trader(llm, DummyMemory())

    result = node(
        {
            "company_of_interest": "AMZN",
            "investment_plan": "Research manager plan: Hold until earnings.",
            "market_report": "market",
            "sentiment_report": "sentiment",
            "news_report": "news",
            "fundamentals_report": "fundamentals",
            "macro_report": "macro",
            "factor_rules_report": "factor rules",
        }
    )

    assert result["trader_investment_plan"] == "Research manager plan: Hold until earnings."


def test_trader_preserves_normal_response_when_not_refusal():
    llm = FakeLLM("Trader-specific execution plan.")
    node = create_trader(llm, DummyMemory())

    result = node(
        {
            "company_of_interest": "AMZN",
            "investment_plan": "Research manager plan: Hold until earnings.",
            "market_report": "market",
            "sentiment_report": "sentiment",
            "news_report": "news",
            "fundamentals_report": "fundamentals",
            "macro_report": "macro",
            "factor_rules_report": "factor rules",
        }
    )

    assert result["trader_investment_plan"] == "Trader-specific execution plan."
