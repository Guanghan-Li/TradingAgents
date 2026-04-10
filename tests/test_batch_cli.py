import httpx
import openai
from typer.testing import CliRunner

import cli.main as cli_main
from cli.main import app
from cli.models import AnalystType


runner = CliRunner()


def test_root_cli_without_subcommand_runs_interactive_stock_flow(monkeypatch):
    calls = []

    monkeypatch.setattr("cli.main.run_analysis", lambda: calls.append("interactive"))

    result = runner.invoke(app, [])

    assert result.exit_code == 0, result.output
    assert calls == ["interactive"]


def test_run_stock_command_dispatches_non_interactive_runner(monkeypatch):
    calls = []

    def fake_run_stock_command(**kwargs):
        calls.append(kwargs)
        return {"ticker": "MSFT", "decision": "BUY"}

    monkeypatch.setattr("cli.main.run_stock_command", fake_run_stock_command, raising=False)

    result = runner.invoke(app, ["run-stock", "--ticker", "MSFT"])

    assert result.exit_code == 0, result.output
    assert calls == [{"ticker": "MSFT"}]


def test_run_stock_command_accepts_non_interactive_flags(monkeypatch):
    calls = []

    def fake_run_stock_command(**kwargs):
        calls.append(kwargs)
        return {"ticker": "MSFT", "decision": "BUY"}

    monkeypatch.setattr("cli.main.run_stock_command", fake_run_stock_command)

    result = runner.invoke(
        app,
        [
            "run-stock",
            "--ticker",
            "MSFT",
            "--date",
            "2026-04-08",
            "--model",
            "gpt-5.4",
            "--reasoning-effort",
            "high",
            "--depth",
            "deep",
        ],
    )

    assert result.exit_code == 0, result.output
    assert calls == [
        {
            "ticker": "MSFT",
            "analysis_date": "2026-04-08",
            "model": "gpt-5.4",
            "reasoning_effort": "high",
            "depth": "deep",
        }
    ]


def test_build_batch_config_uses_itgpt_gpt54_defaults():
    from cli.automation import build_batch_config

    config = build_batch_config()

    assert config["llm_provider"] == "openai"
    assert config["backend_url"] == "https://api.itgpt.chat/v1"
    assert config["quick_think_llm"] == "gpt-5-mini"
    assert config["deep_think_llm"] == "gpt-5.4"
    assert config["openai_reasoning_effort"] == "high"
    assert config["max_debate_rounds"] == 5
    assert config["max_risk_discuss_rounds"] == 5
    assert config["llm_routing"]["default"]["model"] == "gpt-5-mini"
    assert config["llm_routing"]["roles"]["chief_analyst"]["model"] == "gpt-5.4"


def test_run_stock_command_defaults_date_to_today(monkeypatch):
    from datetime import date

    from cli.automation import run_stock_command

    class FakeDate(date):
        @classmethod
        def today(cls):
            return cls(2026, 4, 8)

    class FakeGraph:
        instances = []
        propagate_calls = []

        def __init__(self, selected_analysts, debug, config):
            self.selected_analysts = selected_analysts
            self.debug = debug
            self.config = config
            FakeGraph.instances.append(self)

        def propagate(self, ticker, analysis_date):
            FakeGraph.propagate_calls.append((ticker, analysis_date))
            return (
                {
                    "chief_analyst_data": {
                        "verdict": {
                            "rating": "Overweight",
                            "summary": "Stage in.",
                            "thesis": "Good setup.",
                        }
                    }
                },
                "BUY",
            )

    monkeypatch.setattr("cli.automation.date", FakeDate)
    monkeypatch.setattr("cli.automation.TradingAgentsGraph", FakeGraph)

    result = run_stock_command(ticker="MSFT")

    assert FakeGraph.instances[0].selected_analysts == [
        "market",
        "social",
        "news",
        "fundamentals",
        "macro",
        "factor_rules",
        "valuation",
        "segment",
        "scenario",
        "position_sizing",
    ]
    assert FakeGraph.instances[0].config["backend_url"] == "https://api.itgpt.chat/v1"
    assert FakeGraph.instances[0].config["openai_reasoning_effort"] == "high"
    assert FakeGraph.propagate_calls == [("MSFT", "2026-04-08")]
    assert result["analysis_date"] == "2026-04-08"
    assert result["decision"] == "BUY"


def test_run_stock_command_writes_progress_events(monkeypatch, tmp_path):
    from cli.automation import run_stock_command

    progress_file = tmp_path / "progress.jsonl"

    class FakePropagator:
        def create_initial_state(self, ticker, analysis_date):
            return {"ticker": ticker, "analysis_date": analysis_date}

        def get_graph_args(self):
            return {}

    class FakeStreamGraph:
        def stream(self, init_agent_state, **kwargs):
            yield {"messages": [], "market_report": "Market body"}
            yield {"messages": [], "trader_investment_plan": "Trade body"}
            yield {
                "messages": [],
                "chief_analyst_report": "Chief body",
                "chief_analyst_data": {"verdict": {"rating": "Buy"}},
                "final_trade_decision": "BUY",
            }

    class FakeGraph:
        def __init__(self, selected_analysts, debug, config):
            self.selected_analysts = selected_analysts
            self.debug = debug
            self.config = config
            self.propagator = FakePropagator()
            self.graph = FakeStreamGraph()

        def process_signal(self, decision):
            return decision

        def propagate(self, ticker, analysis_date):
            raise AssertionError("streaming path should be used when progress_file is set")

    monkeypatch.setattr("cli.automation.TradingAgentsGraph", FakeGraph)

    result = run_stock_command(ticker="MSFT", progress_file=str(progress_file))

    payload = progress_file.read_text()
    assert '"event": "run_started"' in payload
    assert '"event": "agent_completed"' in payload
    assert "Market Analyst" in payload
    assert "Chief Analyst" in payload
    assert result["decision"] == "BUY"


def test_root_cli_handles_upstream_gateway_timeout_cleanly(monkeypatch, tmp_path):
    class FakePropagator:
        def create_initial_state(self, ticker, analysis_date):
            return {"messages": []}

        def get_graph_args(self, **kwargs):
            return {}

    class FakeStreamGraph:
        def stream(self, init_agent_state, **kwargs):
            request = httpx.Request("POST", "https://api.itgpt.chat/v1/chat/completions")
            response = httpx.Response(504, request=request, text="Gateway time-out")
            raise openai.InternalServerError(
                "Gateway time-out",
                response=response,
                body=None,
            )

    class FakeGraph:
        def __init__(self, selected_analysts, config, debug, callbacks):
            self.propagator = FakePropagator()
            self.graph = FakeStreamGraph()

    monkeypatch.setattr(
        "cli.main.get_user_selections",
        lambda: {
            "ticker": "SOFI",
            "analysis_date": "2026-04-09",
            "analysts": [AnalystType.MACRO],
            "research_depth": 5,
            "llm_provider": "OpenAI Compatible",
            "backend_url": "https://api.itgpt.chat/v1",
            "shallow_thinker": "gpt-5.4",
            "deep_thinker": "gpt-5.4",
            "google_thinking_level": None,
            "openai_reasoning_effort": "high",
            "anthropic_effort": None,
        },
    )
    monkeypatch.setattr("cli.main.TradingAgentsGraph", FakeGraph)
    monkeypatch.setitem(cli_main.DEFAULT_CONFIG, "results_dir", str(tmp_path))

    result = runner.invoke(app, [])

    assert result.exit_code == 1
    assert "Gateway time-out" in result.output
    assert "Traceback" not in result.output


def test_run_batch_command_loads_watchlist_and_runs_each_ticker(monkeypatch, tmp_path):
    from cli.automation import run_batch_command

    watchlist_path = tmp_path / "watchlist.yaml"
    watchlist_path.write_text(
        "defaults:\n"
        "  model: gpt-5.4\n"
        "tickers:\n"
        "  - MSFT\n"
        "  - NVDA\n"
        "  - AAPL\n"
    )

    observed_tickers = []

    def fake_run_cli_stock_job(job):
        observed_tickers.append(job["ticker"])
        return {"ticker": job["ticker"], "status": "completed", "returncode": 0}

    monkeypatch.setattr("cli.automation.run_cli_stock_job", fake_run_cli_stock_job)

    result = run_batch_command(watchlist_path=watchlist_path, cap=4)

    assert observed_tickers == ["MSFT", "NVDA", "AAPL"]
    assert result["completed"] == ["MSFT", "NVDA", "AAPL"]
    assert result["failed"] == []


def test_batch_command_dispatches_runner(monkeypatch, tmp_path):
    from cli.automation import DEFAULT_BATCH_LAUNCH_STAGGER_SECONDS

    watchlist_path = tmp_path / "watchlist.yaml"
    watchlist_path.write_text("tickers:\n  - MSFT\n")
    calls = []

    def fake_run_batch_command(**kwargs):
        calls.append(kwargs)
        return {"completed": ["MSFT"], "failed": []}

    monkeypatch.setattr("cli.main.run_batch_command", fake_run_batch_command, raising=False)

    result = runner.invoke(
        app,
        [
            "batch",
            "--watchlist",
            str(watchlist_path),
            "--cap",
            "6",
            "--date",
            "2026-04-08",
            "--model",
            "gpt-5.4",
            "--reasoning-effort",
            "high",
            "--depth",
            "deep",
            "--results-dir",
            str(tmp_path / "results"),
        ],
    )

    assert result.exit_code == 0, result.output
    assert calls == [
        {
            "watchlist_path": watchlist_path,
            "cap": 6,
            "analysis_date": "2026-04-08",
            "model": "gpt-5.4",
            "reasoning_effort": "high",
            "depth": "deep",
            "results_dir": tmp_path / "results",
            "launch_stagger_seconds": DEFAULT_BATCH_LAUNCH_STAGGER_SECONDS,
            "progress_callback": calls[0]["progress_callback"],
        }
    ]
    assert callable(calls[0]["progress_callback"])


def test_batch_command_passes_progress_callback(monkeypatch, tmp_path):
    watchlist_path = tmp_path / "watchlist.yaml"
    watchlist_path.write_text("tickers:\n  - MSFT\n")
    calls = []

    def fake_run_batch_command(**kwargs):
        calls.append(kwargs)
        return {"completed": ["MSFT"], "failed": [], "jobs": [], "results": []}

    monkeypatch.setattr("cli.main.run_batch_command", fake_run_batch_command, raising=False)

    result = runner.invoke(app, ["batch", "--watchlist", str(watchlist_path), "--cap", "4"])

    assert result.exit_code == 0, result.output
    assert callable(calls[0]["progress_callback"])


def test_run_batch_command_honors_cap(monkeypatch, tmp_path):
    import threading
    import time

    from cli.automation import run_batch_command

    watchlist_path = tmp_path / "watchlist.yaml"
    watchlist_path.write_text(
        "tickers:\n"
        "  - MSFT\n"
        "  - NVDA\n"
        "  - AAPL\n"
        "  - AMZN\n"
        "  - META\n"
    )

    state = {"active": 0, "max_active": 0}
    lock = threading.Lock()

    def fake_run_cli_stock_job(job):
        with lock:
            state["active"] += 1
            state["max_active"] = max(state["max_active"], state["active"])
        time.sleep(0.05)
        with lock:
            state["active"] -= 1
        return {"ticker": job["ticker"], "status": "completed", "returncode": 0}

    monkeypatch.setattr("cli.automation.run_cli_stock_job", fake_run_cli_stock_job)

    result = run_batch_command(watchlist_path=watchlist_path, cap=2)

    assert state["max_active"] == 2
    assert len(result["completed"]) == 5


def test_run_batch_command_staggers_launches(monkeypatch, tmp_path):
    import time

    from cli.automation import run_batch_command

    watchlist_path = tmp_path / "watchlist.yaml"
    watchlist_path.write_text(
        "tickers:\n"
        "  - MSFT\n"
        "  - NVDA\n"
        "  - AAPL\n"
    )

    started_at = []

    def fake_run_cli_stock_job(job):
        started_at.append(time.monotonic())
        time.sleep(0.01)
        return {
            "ticker": job["ticker"],
            "status": "completed",
            "returncode": 0,
            "stdout": "",
            "stderr": "",
        }

    monkeypatch.setattr("cli.automation.run_cli_stock_job", fake_run_cli_stock_job)

    result = run_batch_command(
        watchlist_path=watchlist_path,
        cap=3,
        launch_stagger_seconds=0.05,
    )

    assert result["completed"] == ["MSFT", "NVDA", "AAPL"]
    assert len(started_at) == 3
    assert started_at[1] - started_at[0] >= 0.04
    assert started_at[2] - started_at[1] >= 0.04


def test_run_batch_command_reuses_worker_slots(monkeypatch, tmp_path):
    import time
    from pathlib import Path

    from cli.automation import run_batch_command

    watchlist_path = tmp_path / "watchlist.yaml"
    watchlist_path.write_text(
        "tickers:\n"
        "  - MSFT\n"
        "  - NVDA\n"
        "  - AAPL\n"
    )

    updates = []

    def fake_run_cli_stock_job(job):
        progress_file = Path(job["progress_file"])
        progress_file.write_text(
            '{"event":"run_started","ticker":"' + job["ticker"] + '"}\n'
            '{"event":"agent_completed","agent":"Trader","ticker":"' + job["ticker"] + '"}\n'
            '{"event":"run_completed","ticker":"' + job["ticker"] + '"}\n'
        )
        if job["ticker"] == "NVDA":
            time.sleep(0.1)
        else:
            time.sleep(0.02)
        return {
            "ticker": job["ticker"],
            "status": "completed",
            "returncode": 0,
            "stdout": "",
            "stderr": "",
        }

    monkeypatch.setattr("cli.automation.run_cli_stock_job", fake_run_cli_stock_job)

    result = run_batch_command(
        watchlist_path=watchlist_path,
        cap=2,
        progress_callback=lambda state: updates.append(state.snapshot()),
    )

    seen_slot_assignments = {
        (slot["slot_index"], slot["ticker"])
        for update in updates
        for slot in update["slots"]
        if slot["ticker"]
    }

    assert result["completed"] == ["MSFT", "NVDA", "AAPL"]
    assert (1, "MSFT") in seen_slot_assignments
    assert (1, "AAPL") in seen_slot_assignments


def test_summarize_command_dispatches_runner(monkeypatch, tmp_path):
    calls = []

    def fake_summarize_runs_for_date(**kwargs):
        calls.append(kwargs)
        return {"analysis_date": "2026-04-08"}

    monkeypatch.setattr(
        "cli.main.summarize_runs_for_date",
        fake_summarize_runs_for_date,
        raising=False,
    )

    result = runner.invoke(
        app,
        ["summarize", "--date", "2026-04-08", "--results-dir", str(tmp_path)],
    )

    assert result.exit_code == 0, result.output
    assert calls == [{"analysis_date": "2026-04-08", "results_dir": tmp_path}]
