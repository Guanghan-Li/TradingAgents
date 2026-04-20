# TradingAgents Batch Automation CLI Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a non-interactive stock automation flow to the TradingAgents CLI while preserving the current interactive manual flow.

**Architecture:** Convert the CLI root into a callback-based Typer app that still runs the current interactive stock flow when invoked without a subcommand. Add focused automation helpers for config resolution, single-stock execution, bounded parallel batch execution, and daily summary generation from per-run structured artifacts.

**Tech Stack:** Python 3.11, Typer, Rich, pathlib, concurrent.futures, json, pytest

---

### File Structure

**Files:**
- Modify: `cli/main.py`
- Modify: `cli/models.py`
- Modify: `cli/utils.py`
- Create: `cli/automation.py`
- Create: `tests/test_batch_cli.py`
- Create: `tests/test_batch_summary.py`
- Modify: `tests/test_polymarket_cli.py`

`cli/main.py` will keep the root CLI entrypoint and wire subcommands.

`cli/automation.py` will hold non-interactive automation helpers:
- watchlist loading
- default config building
- single-stock execution
- bounded parallel batch runner
- summary artifact writing
- daily summary synthesis input collection

`tests/test_batch_cli.py` will cover the root callback behavior and new subcommands.

`tests/test_batch_summary.py` will cover deterministic summary artifact generation and daily rollup behavior.

### Task 1: Preserve Root Interactive CLI While Adding Subcommands

**Files:**
- Modify: `cli/main.py`
- Modify: `tests/test_polymarket_cli.py`
- Create: `tests/test_batch_cli.py`

- [ ] **Step 1: Write the failing tests**

```python
from typer.testing import CliRunner

from cli.main import app

runner = CliRunner()


def test_root_cli_without_subcommand_runs_interactive_stock_flow(monkeypatch):
    calls = []
    monkeypatch.setattr("cli.main.run_analysis", lambda: calls.append("interactive"))

    result = runner.invoke(app, [])

    assert result.exit_code == 0
    assert calls == ["interactive"]


def test_run_stock_command_dispatches_non_interactive_runner(monkeypatch, tmp_path):
    calls = []

    def fake_run_stock_command(**kwargs):
        calls.append(kwargs)
        return {"ticker": "MSFT", "decision": "BUY"}

    monkeypatch.setattr("cli.main.run_stock_command", fake_run_stock_command)

    result = runner.invoke(app, ["run-stock", "--ticker", "MSFT"])

    assert result.exit_code == 0
    assert calls[0]["ticker"] == "MSFT"
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `/Users/garrick/anaconda3/envs/tradingagents/bin/python -m pytest tests/test_batch_cli.py -q`
Expected: FAIL because the new callback/subcommand wiring does not exist yet.

- [ ] **Step 3: Implement the minimal CLI callback and subcommand wiring**

Add a Typer callback with `invoke_without_command=True` and `typer.Context` handling so:
- no subcommand -> existing interactive flow
- `run-stock`, `batch`, `summarize` -> explicit command execution
- existing `--mode polymarket` behavior remains available at the root callback

- [ ] **Step 4: Run tests to verify they pass**

Run: `/Users/garrick/anaconda3/envs/tradingagents/bin/python -m pytest tests/test_batch_cli.py tests/test_polymarket_cli.py -q`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add cli/main.py tests/test_batch_cli.py tests/test_polymarket_cli.py
git commit -m "feat: add callback-based CLI root for automation commands"
```

### Task 2: Add Automation Config Resolution And Single-Stock Runner

**Files:**
- Create: `cli/automation.py`
- Modify: `cli/models.py`
- Create: `tests/test_batch_cli.py`

- [ ] **Step 1: Write the failing tests**

```python
def test_build_batch_config_uses_itgpt_gpt54_defaults():
    config = build_batch_config()

    assert config["llm_provider"] == "openai"
    assert config["backend_url"] == "https://api.itgpt.chat/v1"
    assert config["quick_think_llm"] == "gpt-5.4"
    assert config["deep_think_llm"] == "gpt-5.4"
    assert config["openai_reasoning_effort"] == "high"
    assert config["max_debate_rounds"] == 5
    assert config["max_risk_discuss_rounds"] == 5


def test_run_stock_command_defaults_date_to_today(monkeypatch):
    monkeypatch.setattr("cli.automation.date", FakeDate)
    ...
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `/Users/garrick/anaconda3/envs/tradingagents/bin/python -m pytest tests/test_batch_cli.py -q`
Expected: FAIL because automation config helpers do not exist.

- [ ] **Step 3: Implement minimal config and single-stock execution helpers**

Implement:
- depth preset mapping `shallow|medium|deep -> 1|3|5`
- default ITGPT-compatible backend config
- default model alias that sets both quick and deep models together
- date defaulting to `date.today().isoformat()`
- all-analysts default
- single-stock runner that calls `TradingAgentsGraph.propagate()`

- [ ] **Step 4: Run tests to verify they pass**

Run: `/Users/garrick/anaconda3/envs/tradingagents/bin/python -m pytest tests/test_batch_cli.py -q`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add cli/automation.py cli/models.py tests/test_batch_cli.py
git commit -m "feat: add non-interactive stock automation config"
```

### Task 3: Persist Structured Run Artifacts For Automation

**Files:**
- Modify: `cli/automation.py`
- Create: `tests/test_batch_summary.py`

- [ ] **Step 1: Write the failing tests**

```python
def test_run_stock_writes_run_summary_json(tmp_path):
    result = write_run_summary(...)

    payload = json.loads((tmp_path / "run_summary.json").read_text())
    assert payload["ticker"] == "MSFT"
    assert payload["analysis_date"] == "2026-04-08"
    assert payload["chief_rating"] == "Overweight"
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `/Users/garrick/anaconda3/envs/tradingagents/bin/python -m pytest tests/test_batch_summary.py -q`
Expected: FAIL because run summary persistence does not exist.

- [ ] **Step 3: Implement structured artifact writing**

Write one deterministic summary artifact per run under the existing results directory, containing:
- ticker
- analysis date
- status
- provider/model settings
- decision
- chief analyst verdict fields
- paths to reports
- timestamps

- [ ] **Step 4: Run tests to verify they pass**

Run: `/Users/garrick/anaconda3/envs/tradingagents/bin/python -m pytest tests/test_batch_summary.py -q`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add cli/automation.py tests/test_batch_summary.py
git commit -m "feat: write structured artifacts for automated runs"
```

### Task 4: Add Watchlist Loading And Bounded Parallel Batch Execution

**Files:**
- Modify: `cli/automation.py`
- Modify: `cli/main.py`
- Modify: `tests/test_batch_cli.py`

- [ ] **Step 1: Write the failing tests**

```python
def test_batch_command_loads_watchlist_and_runs_each_ticker(monkeypatch, tmp_path):
    ...
    assert observed_tickers == ["MSFT", "NVDA", "AAPL"]


def test_batch_command_honors_cap(monkeypatch, tmp_path):
    ...
    assert max_seen_concurrency == 4
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `/Users/garrick/anaconda3/envs/tradingagents/bin/python -m pytest tests/test_batch_cli.py -q`
Expected: FAIL because batch queueing does not exist.

- [ ] **Step 3: Implement minimal batch runner**

Implement:
- YAML watchlist loading
- CLI flag overrides over YAML defaults
- bounded concurrency using `ThreadPoolExecutor`
- per-job success/failure capture
- batch-level exit code policy that surfaces failed tickers clearly

- [ ] **Step 4: Run tests to verify they pass**

Run: `/Users/garrick/anaconda3/envs/tradingagents/bin/python -m pytest tests/test_batch_cli.py -q`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add cli/automation.py cli/main.py tests/test_batch_cli.py
git commit -m "feat: add watchlist-driven batch stock runner"
```

### Task 5: Add Daily Summary Command

**Files:**
- Modify: `cli/automation.py`
- Modify: `cli/main.py`
- Modify: `tests/test_batch_summary.py`

- [ ] **Step 1: Write the failing tests**

```python
def test_summarize_command_collects_todays_run_summaries(tmp_path):
    ...
    assert payload["analysis_date"] == "2026-04-08"
    assert payload["counts"]["bullish"] == 2


def test_summarize_command_writes_markdown_report(tmp_path):
    ...
    assert "Strongest bullish ideas" in markdown
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `/Users/garrick/anaconda3/envs/tradingagents/bin/python -m pytest tests/test_batch_summary.py -q`
Expected: FAIL because daily summary generation does not exist.

- [ ] **Step 3: Implement deterministic summary collection and reporting**

Implement:
- collection of `run_summary.json` artifacts by date
- simple categorization by rating/decision
- `daily_summary.json`
- `daily_summary.md`
- CLI output with paths and failed/incomplete names

Do not add LLM synthesis in this task unless the deterministic pipeline is already green.

- [ ] **Step 4: Run tests to verify they pass**

Run: `/Users/garrick/anaconda3/envs/tradingagents/bin/python -m pytest tests/test_batch_summary.py -q`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add cli/automation.py cli/main.py tests/test_batch_summary.py
git commit -m "feat: add daily summary command for automated runs"
```

### Task 6: End-to-End Validation And Cleanup

**Files:**
- Modify: `cli/main.py`
- Modify: `cli/automation.py`
- Modify: `tests/test_batch_cli.py`
- Modify: `tests/test_batch_summary.py`

- [ ] **Step 1: Run focused validation for new behavior**

Run:
`/Users/garrick/anaconda3/envs/tradingagents/bin/python -m pytest tests/test_batch_cli.py tests/test_batch_summary.py tests/test_polymarket_cli.py tests/test_run_itgpt.py tests/test_openai_base_url.py -q`

Expected: PASS

- [ ] **Step 2: Run the full suite**

Run:
`/Users/garrick/anaconda3/envs/tradingagents/bin/python -m pytest tests -q`

Expected: PASS

- [ ] **Step 3: Run Python validation tools**

Run:
`ruff check cli tests tradingagents`

If available, also run:
`bandit -r cli tradingagents -ll`

- [ ] **Step 4: Smoke-test the new CLI help surfaces**

Run:
`/Users/garrick/anaconda3/envs/tradingagents/bin/python -m cli.main --help`

Run:
`/Users/garrick/anaconda3/envs/tradingagents/bin/python -m cli.main batch --help`

Run:
`/Users/garrick/anaconda3/envs/tradingagents/bin/python -m cli.main summarize --help`

- [ ] **Step 5: Commit**

```bash
git add cli/main.py cli/automation.py tests/test_batch_cli.py tests/test_batch_summary.py docs/superpowers/plans/2026-04-08-batch-automation-cli.md
git commit -m "feat: add batch automation and summary CLI"
```
