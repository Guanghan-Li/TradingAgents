
from tradingagents.agents.utils.agent_utils import (
    build_compact_risk_handoff_context,
    build_structured_stock_priority_context,
    invoke_committee_debate_llm,
)


def create_aggressive_debator(llm):
    def aggressive_node(state) -> dict:
        risk_debate_state = state["risk_debate_state"]
        history = risk_debate_state.get("history", "")
        aggressive_history = risk_debate_state.get("aggressive_history", "")

        current_conservative_response = risk_debate_state.get("current_conservative_response", "")
        current_neutral_response = risk_debate_state.get("current_neutral_response", "")

        analyst_report_context = build_compact_risk_handoff_context(state)
        structured_stock_context = build_structured_stock_priority_context(state)

        trader_decision = state["trader_investment_plan"]

        prompt = f"""As the Aggressive Risk Analyst, analyze the trader's plan through a risk-tolerant lens. Focus on upside asymmetry, growth potential, and where the committee may be underestimating favorable outcomes. Use the provided evidence to stress-test conservative assumptions, but keep the analysis grounded and factual rather than sales-oriented. Here is the trader's decision:

{trader_decision}

Your task is to identify the strongest evidence supporting the trader's decision and explain where the conservative and neutral stances may be overweighting downside risk. Incorporate insights from the following sources into your analysis:

{analyst_report_context}
Structured Stock Underwriting Outputs To Prioritize: {structured_stock_context}
Here is the current conversation history: {history} Here are the last arguments from the conservative analyst: {current_conservative_response} Here are the last arguments from the neutral analyst: {current_neutral_response}. If there are no responses from the other viewpoints yet, present your own argument based on the available data.

Address specific concerns raised by the other analysts, rebut weak assumptions with evidence, and clearly state what conditions would justify maintaining the higher-risk view. Focus on rigorous committee debate, not persuasion tactics. Output conversationally as if you are speaking without any special formatting."""

        response = invoke_committee_debate_llm(llm, "Aggressive Risk Analyst", prompt)

        argument = f"Aggressive Analyst: {response.content}"

        new_risk_debate_state = {
            "history": history + "\n" + argument,
            "aggressive_history": aggressive_history + "\n" + argument,
            "conservative_history": risk_debate_state.get("conservative_history", ""),
            "neutral_history": risk_debate_state.get("neutral_history", ""),
            "latest_speaker": "Aggressive",
            "current_aggressive_response": argument,
            "current_conservative_response": risk_debate_state.get("current_conservative_response", ""),
            "current_neutral_response": risk_debate_state.get(
                "current_neutral_response", ""
            ),
            "count": risk_debate_state["count"] + 1,
        }

        return {"risk_debate_state": new_risk_debate_state}

    return aggressive_node
