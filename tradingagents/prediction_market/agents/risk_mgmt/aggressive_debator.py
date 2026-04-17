from tradingagents.agents.utils.agent_utils import invoke_committee_debate_llm


def create_pm_aggressive_debator(llm):
    def aggressive_node(state) -> dict:
        risk_debate_state = state["risk_debate_state"]
        history = risk_debate_state.get("history", "")
        aggressive_history = risk_debate_state.get("aggressive_history", "")

        current_conservative_response = risk_debate_state.get("current_conservative_response", "")
        current_neutral_response = risk_debate_state.get("current_neutral_response", "")

        event_report = state["event_report"]
        odds_report = state["odds_report"]
        information_report = state["information_report"]
        sentiment_report = state["sentiment_report"]

        trader_decision = state["trader_investment_plan"]

        prompt = f"""As the Aggressive Risk Analyst for prediction markets, analyze the proposed position through a risk-tolerant lens. Focus on the magnitude of the identified edge, the strength of the probability estimate, and where the committee may be underestimating upside. Use the provided market data and analysis to challenge opposing views, but keep the analysis factual rather than sales-oriented.

Specifically, respond directly to each point made by the conservative and neutral analysts, countering with data-driven rebuttals and persuasive reasoning. Highlight where their caution might cause the team to miss a profitable opportunity or where their risk concerns are overblown relative to the identified edge.

Key arguments to emphasize:
- The magnitude of the edge between estimated probability and market price justifies the position
- The information advantage from our analyst team gives us superior probability estimates
- Favorable odds structures mean limited downside with asymmetric upside
- Market inefficiencies in prediction markets are well-documented and exploitable
- Conservative concerns about resolution risk or liquidity are often overstated for well-structured markets
- Time value of the position if the event resolves sooner than expected

Here is the trader's decision:

{trader_decision}

Your task is to identify the strongest evidence supporting the trader's decision and explain where the conservative and neutral stances may be overweighting downside risk. Incorporate insights from the following sources into your analysis:

Event Analysis Report: {event_report}
Odds Analysis Report: {odds_report}
Information Analysis Report: {information_report}
Sentiment Analysis Report: {sentiment_report}
Here is the current conversation history: {history} Here are the last arguments from the conservative analyst: {current_conservative_response} Here are the last arguments from the neutral analyst: {current_neutral_response}. If there are no responses from the other viewpoints, do not hallucinate and just present your point.

Address specific concerns raised by the other analysts, rebut weak assumptions with evidence, and state what conditions would justify keeping the higher-risk position. Focus on rigorous committee debate, not persuasion tactics. Output conversationally as if you are speaking without any special formatting."""

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
