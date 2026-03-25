from typer.testing import CliRunner

from cli.main import app
from cli.models import AnalysisMode


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
