# Batch Progress Dashboard Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a live batch dashboard that shows overall child-job completion at the top and `N` worker slots below, with each slot advancing from completed internal child-agent milestones.

**Architecture:** Keep the existing batch command and result contract, but add a reusable progress helper module for milestone tracking, JSONL progress events, worker-slot state, and Rich rendering. Update the non-interactive `run-stock` path to emit machine-readable progress events while streaming graph chunks, then update the batch runner to schedule jobs into explicit worker slots and poll those event files into a live dashboard.

**Tech Stack:** Python 3.11, Typer, Rich, concurrent.futures, pathlib, json, pytest

---

## File Structure

**Files:**

- Create: `cli/batch_progress.py`
- Modify: `cli/automation.py`
- Modify: `cli/main.py`
- Create: `tests/test_batch_progress.py`
- Modify: `tests/test_batch_cli.py`

`cli/batch_progress.py` will hold the focused progress logic:

- milestone planning for stock child runs
- JSONL progress event writing and parsing
- worker-slot and batch-dashboard state models
- Rich render helpers for the live batch screen

`cli/automation.py` will remain the orchestration layer:

- add optional progress-file support to child jobs
- stream `run_stock_command()` when progress emission is requested
- replace the current all-at-once batch submission with explicit slot-based scheduling
- poll child progress files and publish dashboard updates while preserving the existing batch return shape

`cli/main.py` will stay the CLI entrypoint:

- add a hidden `--progress-file` pass-through for `run-stock`
- wrap the `batch` command in a `Live` dashboard using the new progress helper
- keep the existing interactive single-run analysis flow unchanged

`tests/test_batch_progress.py` will cover:

- milestone totals and percentage math
- JSONL progress event parsing
- slot assignment and reuse
- graceful handling of malformed or missing progress events

`tests/test_batch_cli.py` will continue covering CLI behavior while adding:

- `run-stock` progress-file integration
- batch progress-callback behavior
- batch exit-code compatibility with the live dashboard path

### Task 1: Add Reusable Batch Progress Models And Event Helpers

**Files:**
- Create: `cli/batch_progress.py`
- Create: `tests/test_batch_progress.py`

- [ ] **Step 1: Write the failing tests**

```python
from cli.batch_progress import (
    DEFAULT_FIXED_AGENT_MILESTONES,
    BatchWorkerSlot,
    compute_progress_fraction,
    parse_progress_events,
    total_run_milestones,
)


def test_total_run_milestones_counts_selected_plus_fixed_agents():
    assert total_run_milestones(["market", "news"]) == 2 + len(DEFAULT_FIXED_AGENT_MILESTONES)


def test_parse_progress_events_skips_malformed_lines():
    events = parse_progress_events('{"event":"agent_completed","agent":"Trader"}\nnot-json\n')
    assert [event.event for event in events] == ["agent_completed"]


def test_compute_progress_fraction_uses_completed_agent_count():
    slot = BatchWorkerSlot(slot_index=1, ticker="MSFT", total_milestones=20, completed_agents={"Trader", "Chief Analyst"})
    assert compute_progress_fraction(slot) == 0.10
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python -m pytest tests/test_batch_progress.py -q`
Expected: FAIL with `ModuleNotFoundError: No module named 'cli.batch_progress'`

- [ ] **Step 3: Write the minimal implementation**

Implement `cli/batch_progress.py` with:

- a constant list of fixed downstream agent milestones
- dataclasses for parsed progress events and worker-slot state
- helper functions:
  - `total_run_milestones(selected_analysts)`
  - `compute_progress_fraction(slot)`
  - `append_progress_event(path, payload)`
  - `parse_progress_events(text)`
- defensive parsing that ignores malformed JSON lines

- [ ] **Step 4: Run tests to verify they pass**

Run: `python -m pytest tests/test_batch_progress.py -q`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add cli/batch_progress.py tests/test_batch_progress.py
git commit -m "feat: add batch progress helper models"
```

### Task 2: Emit Structured Progress Events From `run-stock`

**Files:**
- Modify: `cli/automation.py`
- Modify: `cli/main.py`
- Modify: `tests/test_batch_cli.py`
- Modify: `tests/test_batch_progress.py`

- [ ] **Step 1: Write the failing tests**

```python
def test_run_stock_command_writes_progress_events(monkeypatch, tmp_path):
    from cli.automation import run_stock_command

    progress_file = tmp_path / "progress.jsonl"

    class FakeGraph:
        def __init__(self, selected_analysts, debug, config):
            self.selected_analysts = selected_analysts
            self.debug = debug
            self.config = config
            self.propagator = FakePropagator()
            self.graph = FakeStreamGraph()

        def process_signal(self, decision):
            return decision

    monkeypatch.setattr("cli.automation.TradingAgentsGraph", FakeGraph)

    result = run_stock_command(ticker="MSFT", progress_file=str(progress_file))

    payload = progress_file.read_text()
    assert '"event": "agent_completed"' in payload
    assert result["decision"]
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python -m pytest tests/test_batch_cli.py::test_run_stock_command_writes_progress_events -q`
Expected: FAIL because `run_stock_command()` does not accept `progress_file` and does not stream progress events

- [ ] **Step 3: Write the minimal implementation**

Implement:

- hidden `--progress-file` option on `run-stock` in `cli/main.py`
- optional `progress_file` parameter in `run_stock_command()` in `cli/automation.py`
- a streamed execution path for `run_stock_command()` when `progress_file` is provided:
  - create initial state with `graph.propagator.create_initial_state(...)`
  - iterate `graph.graph.stream(...)`
  - update a milestone tracker from each chunk
  - append JSONL events for:
    - `run_started`
    - `agent_started`
    - `agent_completed`
    - `run_completed`
    - `run_failed`
- preserve existing return shape and artifact writing

- [ ] **Step 4: Run tests to verify they pass**

Run: `python -m pytest tests/test_batch_cli.py::test_run_stock_command_writes_progress_events -q`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add cli/automation.py cli/main.py tests/test_batch_cli.py tests/test_batch_progress.py
git commit -m "feat: emit run-stock progress events"
```

### Task 3: Add Slot-Based Batch Scheduling And Progress Polling

**Files:**
- Modify: `cli/automation.py`
- Modify: `cli/batch_progress.py`
- Modify: `tests/test_batch_progress.py`
- Modify: `tests/test_batch_cli.py`

- [ ] **Step 1: Write the failing tests**

```python
def test_run_batch_command_reuses_worker_slots(monkeypatch, tmp_path):
    from cli.automation import run_batch_command

    updates = []

    def fake_run_cli_stock_job(job):
        progress_file = Path(job["progress_file"])
        progress_file.write_text(
            '{"event":"run_started","ticker":"' + job["ticker"] + '"}\n'
            '{"event":"agent_completed","agent":"Trader","ticker":"' + job["ticker"] + '"}\n'
            '{"event":"run_completed","ticker":"' + job["ticker"] + '"}\n'
        )
        return {"ticker": job["ticker"], "status": "completed", "returncode": 0, "stdout": "", "stderr": ""}

    monkeypatch.setattr("cli.automation.run_cli_stock_job", fake_run_cli_stock_job)

    result = run_batch_command(
        watchlist_path=watchlist_path,
        cap=2,
        progress_callback=lambda state: updates.append(state.snapshot()),
    )

    assert result["completed"] == ["MSFT", "NVDA", "AAPL"]
    assert any(slot["slot_index"] == 1 for update in updates for slot in update["slots"])
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python -m pytest tests/test_batch_progress.py tests/test_batch_cli.py::test_run_batch_command_reuses_worker_slots -q`
Expected: FAIL because `run_batch_command()` does not expose slot state or progress polling

- [ ] **Step 3: Write the minimal implementation**

Implement:

- manual queue scheduling in `run_batch_command()` instead of submitting the entire watchlist at once
- one explicit worker slot per active future
- progress-file path assignment per job
- periodic polling of in-flight child progress files
- optional `progress_callback(state)` hook that receives dashboard state updates
- preserved final return shape:
  - `jobs`
  - `results`
  - `completed`
  - `failed`

- [ ] **Step 4: Run tests to verify they pass**

Run: `python -m pytest tests/test_batch_progress.py tests/test_batch_cli.py::test_run_batch_command_reuses_worker_slots -q`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add cli/automation.py cli/batch_progress.py tests/test_batch_progress.py tests/test_batch_cli.py
git commit -m "feat: track batch worker slot progress"
```

### Task 4: Render The Live Batch Dashboard In The CLI

**Files:**
- Modify: `cli/main.py`
- Modify: `cli/batch_progress.py`
- Modify: `tests/test_batch_cli.py`

- [ ] **Step 1: Write the failing tests**

```python
def test_batch_command_passes_progress_callback(monkeypatch, tmp_path):
    calls = []

    def fake_run_batch_command(**kwargs):
        calls.append(kwargs)
        return {"completed": ["MSFT"], "failed": [], "jobs": [], "results": []}

    monkeypatch.setattr("cli.main.run_batch_command", fake_run_batch_command)

    result = runner.invoke(app, ["batch", "--watchlist", str(watchlist_path), "--cap", "4"])

    assert result.exit_code == 0
    assert callable(calls[0]["progress_callback"])
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python -m pytest tests/test_batch_cli.py::test_batch_command_passes_progress_callback -q`
Expected: FAIL because the `batch` command does not create a live dashboard callback

- [ ] **Step 3: Write the minimal implementation**

Implement:

- Rich dashboard render helpers in `cli/batch_progress.py`
- a `Live(...)` wrapper in the `batch` command in `cli/main.py`
- a callback that refreshes the dashboard as slot state changes
- final summary printing and non-zero exit behavior unchanged after the live session closes

- [ ] **Step 4: Run tests to verify they pass**

Run: `python -m pytest tests/test_batch_cli.py::test_batch_command_passes_progress_callback -q`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add cli/main.py cli/batch_progress.py tests/test_batch_cli.py
git commit -m "feat: add live batch dashboard"
```

### Task 5: Validate The Batch Dashboard End To End

**Files:**
- Modify: `cli/batch_progress.py`
- Modify: `cli/automation.py`
- Modify: `cli/main.py`
- Modify: `tests/test_batch_progress.py`
- Modify: `tests/test_batch_cli.py`

- [ ] **Step 1: Run the focused automated test suite**

Run: `python -m pytest tests/test_batch_progress.py tests/test_batch_cli.py tests/test_cli_display.py -q`
Expected: PASS with the existing pandas `bottleneck` warning only

- [ ] **Step 2: Run one manual batch smoke check in the prod worktree**

Run:

```bash
tmp_watchlist="$(mktemp /tmp/tradingagents-watchlist.XXXXXX.yaml)"
cat > "$tmp_watchlist" <<'YAML'
tickers:
  - MSFT
  - NVDA
YAML
python -m cli.main batch --watchlist "$tmp_watchlist" --cap 2
```

Expected:

- live dashboard opens
- top bar advances as child jobs finish
- exactly 2 worker slots render
- slot bars advance as internal child agents complete

- [ ] **Step 3: Fix any validation issues**

If the focused suite or smoke check fails, fix only the relevant files and re-run the exact failing command before moving on.

- [ ] **Step 4: Commit final polish**

```bash
git add cli/batch_progress.py cli/automation.py cli/main.py tests/test_batch_progress.py tests/test_batch_cli.py
git commit -m "test: validate batch progress dashboard"
```
