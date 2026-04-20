from langchain_core.messages import AIMessage
from langchain_core.runnables import RunnableLambda

import tradingagents.agents.analysts.fundamentals_analyst as fundamentals_analyst
from tradingagents.agents.analysts.fundamentals_analyst import create_fundamentals_analyst


def test_fundamentals_analyst_uses_prefetched_context_without_duplicate_computations(monkeypatch):
    monkeypatch.setattr(
        fundamentals_analyst,
        "route_to_vendor",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(
            AssertionError("route_to_vendor should not run when prefetched fundamentals are present")
        ),
    )
    monkeypatch.setattr(
        fundamentals_analyst,
        "get_peer_comparison_report",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(
            AssertionError("peer comparison should not run when prefetched fundamentals are present")
        ),
    )
    monkeypatch.setattr(
        fundamentals_analyst,
        "get_sector_relative_report",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(
            AssertionError("sector relative report should not run when prefetched fundamentals are present")
        ),
    )
    monkeypatch.setattr(
        fundamentals_analyst,
        "classify_macro_regime",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(
            AssertionError("macro regime should not be recomputed when prefetched fundamentals are present")
        ),
    )

    fake_llm = RunnableLambda(lambda messages: AIMessage(content="fundamentals summary", tool_calls=[]))

    node = create_fundamentals_analyst(fake_llm)
    result = node(
        {
            "trade_date": "2026-04-12",
            "company_of_interest": "AAPL",
            "messages": [("human", "Analyze AAPL")],
            "prefetched_context": {"fundamentals": "prefetched fundamentals block"},
            "macro_report": "macro handoff",
        }
    )

    assert result["fundamentals_report"] == "fundamentals summary"
