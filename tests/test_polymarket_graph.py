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
    assert set(graph.tool_nodes) == {"event", "odds", "information", "sentiment"}
