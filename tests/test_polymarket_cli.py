from typer.testing import CliRunner

from cli.main import app
from cli.models import AnalysisMode, PMAnalystType


runner = CliRunner()


def test_analyze_polymarket_mode_dispatches_to_prediction_market_runner(monkeypatch):
    calls = []

    def fake_run_stock_analysis():
        raise AssertionError("stock runner should not be used for polymarket mode")

    def fake_run_polymarket_analysis():
        calls.append(AnalysisMode.POLYMARKET)

    monkeypatch.setattr("cli.main.run_analysis", fake_run_stock_analysis)
    monkeypatch.setattr(
        "cli.main.run_polymarket_analysis",
        fake_run_polymarket_analysis,
        raising=False,
    )

    result = runner.invoke(app, ["--mode", "polymarket"])

    assert result.exit_code == 0, result.output
    assert calls == [AnalysisMode.POLYMARKET]


def test_analyze_polymarket_mode_runs_product_entrypoint(monkeypatch):
    class FakePredictionMarketGraph:
        instances = []
        propagate_calls = []

        def __init__(self, selected_analysts, config, debug):
            self.selected_analysts = selected_analysts
            self.config = config
            self.debug = debug
            self.product = "polymarket"
            FakePredictionMarketGraph.instances.append(self)

        def propagate(self, market_id, analysis_date, market_question=""):
            FakePredictionMarketGraph.propagate_calls.append(
                (market_id, analysis_date, market_question)
            )
            return (
                {"market_id": market_id, "market_question": market_question},
                '{"signal":"PASS"}',
            )

    monkeypatch.setattr("cli.main.get_market_id", lambda: ("12345", "Will it happen?"))
    monkeypatch.setattr("cli.main.get_analysis_date", lambda: "2026-03-24")
    monkeypatch.setattr(
        "cli.main.select_pm_analysts",
        lambda: [PMAnalystType.EVENT, PMAnalystType.ODDS],
    )
    monkeypatch.setattr("cli.main.select_research_depth", lambda: 3)
    monkeypatch.setattr(
        "cli.main.select_llm_provider",
        lambda: ("openai", "https://api.openai.com/v1"),
    )
    monkeypatch.setattr("cli.main.select_shallow_thinking_agent", lambda provider: "gpt-5-mini")
    monkeypatch.setattr("cli.main.select_deep_thinking_agent", lambda provider: "gpt-5.2")
    monkeypatch.setattr("cli.main.ask_openai_reasoning_effort", lambda: "medium")
    monkeypatch.setattr("cli.main.PredictionMarketGraph", FakePredictionMarketGraph)
    monkeypatch.setattr("cli.main.run_analysis", lambda: (_ for _ in ()).throw(AssertionError("stock runner should not be used")))

    result = runner.invoke(app, ["--mode", "polymarket"])

    assert result.exit_code == 0, result.output
    assert len(FakePredictionMarketGraph.instances) == 1
    instance = FakePredictionMarketGraph.instances[0]
    assert instance.selected_analysts == ["event", "odds"]
    assert instance.config["market_type"] == "polymarket"
    assert instance.config["max_debate_rounds"] == 3
    assert instance.config["openai_reasoning_effort"] == "medium"
    assert FakePredictionMarketGraph.propagate_calls == [
        ("12345", "2026-03-24", "Will it happen?")
    ]
    assert "Polymarket decision" in result.output
