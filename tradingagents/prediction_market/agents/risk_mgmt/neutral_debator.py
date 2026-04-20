from tradingagents.agents.utils.agent_utils import invoke_committee_debate_llm


def create_pm_neutral_debator(llm):
    def neutral_node(state) -> dict:
        risk_debate_state = state["risk_debate_state"]
        history = risk_debate_state.get("history", "")
        neutral_history = risk_debate_state.get("neutral_history", "")

        current_aggressive_response = risk_debate_state.get("current_aggressive_response", "")
        current_conservative_response = risk_debate_state.get("current_conservative_response", "")

        event_report = state["event_report"]
        odds_report = state["odds_report"]
        information_report = state["information_report"]
        sentiment_report = state["sentiment_report"]

        trader_decision = state["trader_investment_plan"]

        prompt = f"""As the Neutral Risk Analyst for prediction markets, evaluate the proposed trade through a balanced risk-reward lens. Weigh the potential upside and legitimate risks fairly, evaluate the trader's probability estimate, and assess whether the sizing and risk/reward truly justify the position.

Key areas to focus on:
- BALANCED RISK/REWARD ASSESSMENT: Does the identified edge truly compensate for the risks involved? Is the trader's probability estimate reasonable given the available evidence, or could it be biased by selective analysis?
- FRACTIONAL KELLY APPROPRIATENESS: Is the proposed 0.25x fractional Kelly sizing appropriate for this specific market? Should it be more conservative (0.1x) given estimation uncertainty, or could a slightly larger fraction be justified if the edge is robust?
- TIME-TO-RESOLUTION IMPACT: How does the time remaining until resolution affect the trade? Shorter durations reduce uncertainty but may also reduce edge as markets become more efficient near resolution. Longer durations increase the chance of new information invalidating the thesis.
- POSITION SIZING CALIBRATION: Even if the direction is correct, is the size right? Consider the impact of estimation errors on Kelly sizing and whether partial positions or scaling strategies would be more prudent.
- ALTERNATIVE STRUCTURES: Could the same thesis be expressed with less risk? For example, could we wait for better entry, use a smaller position, or combine with a correlated market for a hedged expression?

Here is the trader's decision:

{trader_decision}

Your task is to challenge both the Aggressive and Conservative Analysts, pointing out where each perspective may be overstating or understating the risk/reward. Use insights from the following data sources to support a calibrated middle-ground interpretation:

Event Analysis Report: {event_report}
Odds Analysis Report: {odds_report}
Information Analysis Report: {information_report}
Sentiment Analysis Report: {sentiment_report}
Here is the current conversation history: {history} Here is the last response from the aggressive analyst: {current_aggressive_response} Here is the last response from the conservative analyst: {current_conservative_response}. If there are no responses from the other viewpoints, do not hallucinate and just present your point.

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
