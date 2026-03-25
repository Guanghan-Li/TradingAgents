from tradingagents.default_config import DEFAULT_CONFIG
from tradingagents.prediction_market.polymarket_graph import PredictionMarketGraph


class DummyClient:
    def get_llm(self):
        return object()


def test_prediction_market_graph_initializes_polymarket_context(monkeypatch, tmp_path):
    monkeypatch.setattr(
        "tradingagents.prediction_market.polymarket_graph.create_llm_client",
        lambda **_: DummyClient(),
    )

    config = DEFAULT_CONFIG.copy()
    config["project_dir"] = str(tmp_path)
    config["results_dir"] = str(tmp_path / "results")

    graph = PredictionMarketGraph(
        selected_analysts=["event", "odds"],
        config=config,
        debug=True,
    )

    assert graph.product == "polymarket"
    assert graph.selected_analysts == ["event", "odds"]
    assert graph.config["market_type"] == "polymarket"
    assert graph.graph is not None
    assert hasattr(graph.graph, "invoke")
    assert set(graph.tool_nodes) == {"event", "odds", "information", "sentiment"}


def test_prediction_market_graph_propagate_runs_analysis_entrypoint(monkeypatch, tmp_path):
    monkeypatch.setattr(
        "tradingagents.prediction_market.polymarket_graph.create_llm_client",
        lambda **_: DummyClient(),
    )

    config = DEFAULT_CONFIG.copy()
    config["project_dir"] = str(tmp_path)
    config["results_dir"] = str(tmp_path / "results")

    graph = PredictionMarketGraph(
        selected_analysts=["event"],
        config=config,
        debug=False,
    )

    final_state = {
        "market_id": "12345",
        "market_question": "Will it happen?",
        "trade_date": "2026-03-24",
        "event_report": "event",
        "odds_report": "odds",
        "information_report": "info",
        "sentiment_report": "sentiment",
        "investment_debate_state": {
            "yes_history": "yes",
            "no_history": "no",
            "history": "history",
            "current_response": "response",
            "judge_decision": "judge",
        },
        "trader_investment_plan": "trade plan",
        "risk_debate_state": {
            "aggressive_history": "agg",
            "conservative_history": "cons",
            "neutral_history": "neu",
            "history": "risk history",
            "judge_decision": "risk judge",
        },
        "investment_plan": "investment plan",
        "final_trade_decision": "BUY_YES",
    }

    class StubCompiledGraph:
        def invoke(self, init_agent_state, **args):
            assert init_agent_state["market_id"] == "12345"
            assert init_agent_state["market_question"] == "Will it happen?"
            assert init_agent_state["trade_date"] == "2026-03-24"
            assert args["config"]["recursion_limit"] == graph.config["max_recur_limit"]
            assert args["stream_mode"] == "values"
            return final_state

    graph.graph = StubCompiledGraph()
    monkeypatch.setattr(graph, "_log_state", lambda trade_date, state: None)
    monkeypatch.setattr(
        graph.signal_processor,
        "process_signal",
        lambda full_signal: f"processed::{full_signal}",
    )

    state, decision = graph.propagate(
        "12345",
        "2026-03-24",
        market_question="Will it happen?",
    )

    assert state == final_state
    assert decision == "processed::BUY_YES"
    assert graph.market_id == "12345"
    assert graph.curr_state == final_state
