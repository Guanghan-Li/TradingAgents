import functools

from tradingagents.agents.utils.agent_utils import (
    add_educational_use_context,
    build_analyst_report_context,
    build_instrument_context,
)
from tradingagents.agents.utils.analyst_resilience import is_claude_code_refusal_text


def create_trader(llm, memory):
    def trader_node(state, name):
        company_name = state["company_of_interest"]
        instrument_context = build_instrument_context(company_name)
        analyst_report_context = build_analyst_report_context(state)
        investment_plan = state["investment_plan"]

        curr_situation = analyst_report_context
        past_memories = memory.get_memories(curr_situation, n_matches=2)

        past_memory_str = ""
        if past_memories:
            for i, rec in enumerate(past_memories, 1):
                past_memory_str += rec["recommendation"] + "\n\n"
        else:
            past_memory_str = "No past memories found."

        context = {
            "role": "user",
            "content": f"Based on a comprehensive analysis by a team of analysts, here is an investment plan tailored for {company_name}. {instrument_context} This plan incorporates insights from current technical market trends, macroeconomic indicators, and social media sentiment. Use this plan as a foundation for evaluating your next trading decision.\n\nSource Analyst Reports:\n{analyst_report_context}\n\nProposed Investment Plan: {investment_plan}\n\nLeverage these insights to make an informed and strategic decision.",
        }

        messages = [
            {
                "role": "system",
                "content": add_educational_use_context(
                    f"""You are a trading agent analyzing market data to make investment decisions. Based on your analysis, provide a specific recommendation to buy, sell, or hold. End with a firm decision and always conclude your response with 'FINAL TRANSACTION PROPOSAL: **BUY/HOLD/SELL**' to confirm your recommendation. Apply lessons from past decisions to strengthen your analysis. Here are reflections from similar situations you traded in and the lessons learned: {past_memory_str}"""
                ),
            },
            context,
        ]

        result = llm.invoke(messages)
        trader_plan = result.content
        if is_claude_code_refusal_text(trader_plan):
            trader_plan = investment_plan

        return {
            "messages": [result],
            "trader_investment_plan": trader_plan,
            "sender": name,
        }

    return functools.partial(trader_node, name="Trader")
