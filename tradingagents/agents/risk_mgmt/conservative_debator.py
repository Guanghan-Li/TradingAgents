
from tradingagents.agents.utils.agent_utils import (
    build_compact_risk_handoff_context,
    build_structured_stock_priority_context,
    invoke_committee_debate_llm,
)


def create_conservative_debator(llm):
    def conservative_node(state) -> dict:
        risk_debate_state = state["risk_debate_state"]
        history = risk_debate_state.get("history", "")
        conservative_history = risk_debate_state.get("conservative_history", "")

        current_aggressive_response = risk_debate_state.get("current_aggressive_response", "")
        current_neutral_response = risk_debate_state.get("current_neutral_response", "")

        analyst_report_context = build_compact_risk_handoff_context(state)
        structured_stock_context = build_structured_stock_priority_context(state)

        trader_decision = state["trader_investment_plan"]

        prompt = f"""As the Conservative Risk Analyst, analyze the trader's plan through a capital-preservation lens. Prioritize downside protection, volatility control, and scenario discipline. When evaluating the plan, identify where it may expose the firm to undue risk and what guardrails would be required before proceeding. Here is the trader's decision:

{trader_decision}

Your task is to challenge the Aggressive and Neutral Analysts where they may overlook threat scenarios, weak assumptions, or sustainability concerns. Respond directly to their points, drawing from the following data sources to support a lower-risk interpretation or tighter controls around the trader's decision:

{analyst_report_context}
Structured Stock Underwriting Outputs To Prioritize: {structured_stock_context}
Here is the current conversation history: {history} Here is the last response from the aggressive analyst: {current_aggressive_response} Here is the last response from the neutral analyst: {current_neutral_response}. If there are no responses from the other viewpoints yet, present your own argument based on the available data.

Question their optimism, emphasize overlooked downside paths, and state what evidence would be needed to justify relaxing the conservative view. Focus on rigorous committee critique, not persuasion tactics. Output conversationally as if you are speaking without any special formatting."""

        response = invoke_committee_debate_llm(llm, "Conservative Risk Analyst", prompt)

        argument = f"Conservative Analyst: {response.content}"

        new_risk_debate_state = {
            "history": history + "\n" + argument,
            "aggressive_history": risk_debate_state.get("aggressive_history", ""),
            "conservative_history": conservative_history + "\n" + argument,
            "neutral_history": risk_debate_state.get("neutral_history", ""),
            "latest_speaker": "Conservative",
            "current_aggressive_response": risk_debate_state.get(
                "current_aggressive_response", ""
            ),
            "current_conservative_response": argument,
            "current_neutral_response": risk_debate_state.get(
                "current_neutral_response", ""
            ),
            "count": risk_debate_state["count"] + 1,
        }

        return {"risk_debate_state": new_risk_debate_state}

    return conservative_node
