from langchain_core.messages import AIMessage, ToolMessage
from langchain_core.runnables import RunnableLambda

import tradingagents.agents.analysts.market_analyst as market_analyst
from tradingagents.agents.analysts.market_analyst import (
    _compress_indicator_message,
    _compress_market_context_messages,
    _compress_stock_data_message,
    create_market_analyst,
)


def test_compress_stock_data_message_replaces_raw_csv_with_summary():
    content = (
        "# Stock data for AMD from 2026-04-01 to 2026-04-10\n"
        "# Total records: 8\n\n"
        "Date,Open,High,Low,Close,Volume\n"
        "2026-04-01,207.59,213.83,205.84,210.21,40835800\n"
        "2026-04-02,204.05,217.78,200.62,217.5,38463500\n"
        "2026-04-06,219.28,226.31,217.73,220.18,30786400\n"
        "2026-04-07,218.26,222.10,215.38,221.53,26483000\n"
        "2026-04-08,232.12,234.00,227.09,231.82,35496400\n"
        "2026-04-09,233.01,237.10,230.91,236.64,27126200\n"
        "2026-04-10,239.00,249.58,238.96,245.04,36398600\n"
    )

    summary = _compress_stock_data_message(content)

    assert "## Market data summary for analyst context" in summary
    assert "Latest close (2026-04-10): 245.04" in summary
    assert "Recent 5 trading rows" in summary
    assert "Date,Open,High,Low,Close,Volume" not in summary


def test_compress_indicator_message_replaces_long_history_with_summary():
    content = (
        "## atr values from 2026-02-10 to 2026-04-11:\n\n"
        "## Showing latest 20 dates for LLM context\n\n"
        "2026-04-11: N/A: Not a trading day\n"
        "2026-04-10: 10.22\n"
        "2026-04-09: 10.01\n"
        "2026-04-08: 10.30\n"
        "2026-04-07: 10.14\n"
        "2026-04-06: 10.40\n"
        "\n\n"
        "ATR: Averages true range to measure volatility."
    )

    summary = _compress_indicator_message(content)

    assert "## atr summary for analyst context" in summary
    assert "Latest valid reading: 2026-04-10 = 10.22" in summary
    assert "Short-term direction" in summary
    assert "2026-04-06: 10.40" in summary
    assert "2026-04-11: N/A" not in summary


def test_compress_market_context_messages_updates_tool_messages_only():
    messages = [
        ("human", "AMD"),
        ToolMessage(
            content="# Stock data for AMD from 2026-04-01 to 2026-04-10\n# Total records: 1\n\nDate,Open,High,Low,Close,Volume\n2026-04-10,239.00,249.58,238.96,245.04,36398600\n",
            tool_call_id="stock-1",
        ),
    ]

    compressed = _compress_market_context_messages(messages)

    assert compressed[0] == ("human", "AMD")
    assert "## Market data summary for analyst context" in compressed[1].content


def test_market_analyst_invokes_llm_with_compressed_tool_context(monkeypatch):
    captured = {}

    def fake_classify_macro_regime(_curr_date):
        return {"regime": "risk_on"}

    def fake_format_macro_report(_payload):
        return "macro overlay"

    monkeypatch.setattr(market_analyst, "classify_macro_regime", fake_classify_macro_regime)
    monkeypatch.setattr(market_analyst, "format_macro_report", fake_format_macro_report)

    class FakeLLM:
        def bind_tools(self, _tools):
            def _invoke(messages):
                captured["messages"] = messages
                return AIMessage(content="market summary", tool_calls=[])

            return RunnableLambda(_invoke)

    node = create_market_analyst(FakeLLM())
    result = node(
        {
            "trade_date": "2026-04-11",
            "company_of_interest": "AMD",
            "macro_report": "macro handoff",
            "messages": [
                ("human", "AMD"),
                ToolMessage(
                    content="# Stock data for AMD from 2026-04-01 to 2026-04-10\n# Total records: 1\n\nDate,Open,High,Low,Close,Volume\n2026-04-10,239.00,249.58,238.96,245.04,36398600\n",
                    tool_call_id="stock-1",
                ),
            ],
        }
    )

    assert result["market_report"] == "market summary"
    prompt_messages = captured["messages"].messages
    assert any(
        "## Market data summary for analyst context" in getattr(message, "content", "")
        for message in prompt_messages
    )
