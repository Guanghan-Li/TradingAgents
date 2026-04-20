from tradingagents.agents.utils.agent_utils import invoke_committee_debate_llm


def create_pm_conservative_debator(llm):
    def conservative_node(state) -> dict:
        risk_debate_state = state["risk_debate_state"]
        history = risk_debate_state.get("history", "")
        conservative_history = risk_debate_state.get("conservative_history", "")

        current_aggressive_response = risk_debate_state.get("current_aggressive_response", "")
        current_neutral_response = risk_debate_state.get("current_neutral_response", "")

        event_report = state["event_report"]
        odds_report = state["odds_report"]
        information_report = state["information_report"]
        sentiment_report = state["sentiment_report"]

        trader_decision = state["trader_investment_plan"]

        prompt = f"""As the Conservative Risk Analyst for prediction markets, analyze the proposed position through a capital-preservation lens. Prioritize downside protection, careful assessment of resolution risk, and thorough evaluation of risks unique to prediction markets. When evaluating the trader's decision, identify where the position may expose us to undue risk and what guardrails would be required before proceeding.

Key risks to focus on:
- RESOLUTION AMBIGUITY RISK: How clear are the resolution criteria? Could the market resolve in an unexpected way due to vague or disputed criteria? Has the resolution source been reliable historically?
- LIQUIDITY RISK: Can we exit the position if our thesis changes? What is the bid-ask spread? Could we be stuck in an illiquid position as resolution approaches?
- CORRELATION EXPOSURE: Are we already exposed to similar outcomes through other positions? Does this position concentrate risk in a single domain or event type?
- MODEL UNCERTAINTY: How confident can we really be in our probability estimate? What is the estimation error band? Small errors in probability estimation can eliminate the perceived edge entirely.
- TIME DECAY: How long until resolution? Extended time horizons increase the chance of regime changes, new information, or shifts that invalidate our current analysis. Capital locked in long-duration positions has opportunity cost.

Here is the trader's decision:

{trader_decision}

Your task is to challenge the Aggressive and Neutral Analysts where they may overlook potential threats or prediction-market-specific risks. Respond directly to their points, drawing from the following data sources to support a cautious interpretation or tighter controls around the position:

Event Analysis Report: {event_report}
Odds Analysis Report: {odds_report}
Information Analysis Report: {information_report}
Sentiment Analysis Report: {sentiment_report}
Here is the current conversation history: {history} Here is the last response from the aggressive analyst: {current_aggressive_response} Here is the last response from the neutral analyst: {current_neutral_response}. If there are no responses from the other viewpoints, do not hallucinate and just present your point.

Question their optimism, emphasize overlooked downside paths, and state what evidence would be needed to relax the conservative view. Focus on rigorous committee critique, not persuasion tactics. Output conversationally as if you are speaking without any special formatting."""

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
