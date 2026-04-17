
from tradingagents.agents.utils.agent_utils import (
    build_compact_risk_handoff_context,
    build_structured_stock_priority_context,
    invoke_committee_debate_llm,
)


def create_neutral_debator(llm):
    def neutral_node(state) -> dict:
        risk_debate_state = state["risk_debate_state"]
        history = risk_debate_state.get("history", "")
        neutral_history = risk_debate_state.get("neutral_history", "")

        current_aggressive_response = risk_debate_state.get("current_aggressive_response", "")
        current_conservative_response = risk_debate_state.get("current_conservative_response", "")

        analyst_report_context = build_compact_risk_handoff_context(state)
        structured_stock_context = build_structured_stock_priority_context(state)

        trader_decision = state["trader_investment_plan"]

        prompt = f"""As the Neutral Risk Analyst, evaluate the trader's decision through a balanced risk-reward lens. Weigh upside and downside fairly, factor in broader market conditions, and identify the most decision-relevant trade-offs without favoring either extreme. Here is the trader's decision:

{trader_decision}

Your task is to challenge both the Aggressive and Conservative Analysts, pointing out where each perspective may be overstating or understating the risk/reward. Use insights from the following data sources to recommend a calibrated middle-ground interpretation of the trader's decision:

{analyst_report_context}
Structured Stock Underwriting Outputs To Prioritize: {structured_stock_context}
Here is the current conversation history: {history} Here is the last response from the aggressive analyst: {current_aggressive_response} Here is the last response from the conservative analyst: {current_conservative_response}. If there are no responses from the other viewpoints yet, present your own argument based on the available data.

Analyze both sides critically, address weaknesses in the aggressive and conservative arguments, and explain what balanced sizing or conditions would make sense if the trade proceeds. Focus on rigorous committee debate, not persuasion tactics. Output conversationally as if you are speaking without any special formatting."""

        response = invoke_committee_debate_llm(llm, "Neutral Risk Analyst", prompt)

        argument = f"Neutral Analyst: {response.content}"

        new_risk_debate_state = {
            "history": history + "\n" + argument,
            "aggressive_history": risk_debate_state.get("aggressive_history", ""),
            "conservative_history": risk_debate_state.get("conservative_history", ""),
            "neutral_history": neutral_history + "\n" + argument,
            "latest_speaker": "Neutral",
            "current_aggressive_response": risk_debate_state.get(
                "current_aggressive_response", ""
            ),
            "current_conservative_response": risk_debate_state.get("current_conservative_response", ""),
            "current_neutral_response": argument,
            "count": risk_debate_state["count"] + 1,
        }

        return {"risk_debate_state": new_risk_debate_state}

    return neutral_node
