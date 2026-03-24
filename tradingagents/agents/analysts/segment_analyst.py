from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from tradingagents.agents.utils.agent_utils import (
    build_instrument_context,
    get_segment_fundamentals,
    get_segment_income_statement,
    get_segment_news,
)


def _build_segment_data(ticker: str, analysis_date: str, report: str) -> dict:
    return {
        "ticker": ticker,
        "analysis_date": analysis_date,
        "has_report": bool(report),
        "report": report,
    }


def create_segment_analyst(llm):
    def segment_analyst_node(state):
        current_date = state["trade_date"]
        ticker = state["company_of_interest"]
        instrument_context = build_instrument_context(ticker)

        tools = [
            get_segment_fundamentals,
            get_segment_income_statement,
            get_segment_news,
        ]

        system_message = (
            "You are a segment analyst focused on business-mix quality and revenue durability. "
            "Use `get_segment_fundamentals` to summarize business lines and strategic positioning, "
            "`get_segment_income_statement` to infer segment-level margin direction from reported trends, "
            "and `get_segment_news` to identify demand, pricing, and competitive catalysts for key segments. "
            "Deliver a concise segment-by-segment view, highlight concentration risks, and append a Markdown "
            "table that maps each major segment to growth outlook, margin trend, and trading implication."
        )

        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "You are a helpful AI assistant, collaborating with other assistants."
                    " Use the provided tools to progress towards answering the question."
                    " If you are unable to fully answer, that's OK; another assistant with different tools"
                    " will help where you left off. Execute what you can to make progress."
                    " If you or any other assistant has the FINAL TRANSACTION PROPOSAL: **BUY/HOLD/SELL** or deliverable,"
                    " prefix your response with FINAL TRANSACTION PROPOSAL: **BUY/HOLD/SELL** so the team knows to stop."
                    " You have access to the following tools: {tool_names}.\n{system_message}"
                    "For your reference, the current date is {current_date}. {instrument_context}",
                ),
                MessagesPlaceholder(variable_name="messages"),
            ]
        )

        prompt = prompt.partial(system_message=system_message)
        prompt = prompt.partial(tool_names=", ".join(tool.name for tool in tools))
        prompt = prompt.partial(current_date=current_date)
        prompt = prompt.partial(instrument_context=instrument_context)

        chain = prompt | llm.bind_tools(tools)
        result = chain.invoke(state["messages"])

        tool_calls = getattr(result, "tool_calls", None) or []
        report = result.content if len(tool_calls) == 0 else ""

        return {
            "messages": [result],
            "segment_report": report,
            "segment_data": _build_segment_data(ticker, current_date, report),
        }

    return segment_analyst_node
