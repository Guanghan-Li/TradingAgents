# Batch Progress Dashboard Design

**Date:** 2026-04-09

**Goal**

Add a live terminal dashboard for the `batch` CLI command that shows:

- overall child-job progress at the top
- `N` worker slots where `N == --cap`
- per-slot progress bars derived from completed internal child agents

This is phase 1 only. It does not change the existing single-run interactive analysis screen.

## Scope

This design covers:

- live Rich rendering for `python -m cli.main batch`
- dynamic worker slot rendering based on `--cap`
- structured progress events emitted by each `run-stock` subprocess
- per-child progress math based on completed internal agents
- safe fallback behavior when progress events are missing or partial

## Non-Goals

- no redesign of the current single-run `run_analysis()` live UI
- no attempt to estimate time remaining
- no parsing of human-readable terminal output from child processes
- no phase-1 visualization of tool calls, token usage, or report excerpts inside batch slots

## User Requirements

The batch screen must provide two distinct progress signals:

1. A top progress indicator showing how many child jobs have finished out of the total watchlist size.
2. A worker area below that renders `N` live slots, where `N` is the `--cap` value.

Each worker slot must:

- have a stable slot label such as `Worker #1`
- show the ticker currently assigned to that worker
- show the current active internal agent when known
- show a progress bar that advances as each internal child agent completes

## Target User Experience

The batch screen is a Rich `Live` dashboard with two layers.

### Top Summary Panel

The top panel contains:

- a batch-level progress bar driven by finished child jobs
- counts for `Done`, `Failed`, `Active`, and `Queued`

Batch progress reaches 100% only when all child jobs have reached a terminal state.

### Worker Slots

Below the summary, the UI renders one slot per concurrency lane.

Each slot shows:

- worker label: `Worker #1`, `Worker #2`, and so on
- current ticker, or `Waiting for next job`
- current state: `queued`, `starting`, `running`, `completed`, or `failed`
- current active internal agent when available
- a progress bar based on completed internal agent milestones

Slots are tied to concurrency lanes, not permanent tickers. When a worker finishes one ticker and starts the next, the slot is reused in place.

## Progress Model

Per-child progress is milestone-based, not time-based.

Each child run has a deterministic total milestone count:

- all selected stock analysts for that run
- `Bull Researcher`
- `Bear Researcher`
- `Research Manager`
- `Trader`
- `Aggressive Analyst`
- `Conservative Analyst`
- `Neutral Analyst`
- `Portfolio Manager`
- `Chief Analyst`

If a run uses the default stock configuration, the total is:

- 10 selected analysts
- 10 fixed downstream agents
- 20 total milestones

Each time one internal agent reaches `completed`, the worker slot progress advances by `1 / total_milestones`.

Rules:

- `starting` with no completed agents is greater than zero visually but below the first milestone threshold
- a failed child does not continue advancing after failure
- a completed child must end at 100%
- the top batch bar uses child-job completion only and is independent from internal milestone counts

## Data Flow

The parent batch process must not scrape Rich output from child runs. Progress data must be structured and additive.

### Child Event Emission

Each `run-stock` subprocess receives a progress event file path.

As the child run advances, it appends compact JSON lines such as:

- `run_started`
- `agent_started`
- `agent_completed`
- `run_completed`
- `run_failed`

Each event should include enough metadata for the parent to reconstruct progress safely:

- ticker
- analysis date when available
- event type
- agent name when relevant
- timestamp
- total milestone count

### Parent Monitoring

The batch parent process:

- creates one progress event file per submitted child job
- launches child processes with the event-file path in arguments or environment
- polls event files while jobs are running
- maps progress updates into active worker slots
- keeps the existing batch return shape for callers

The parent should track the last processed offset for each event file to avoid reparsing the full file repeatedly.

## Integration Strategy

Keep the changes isolated and additive.

### `cli/main.py`

- add optional progress-event emission support to the non-interactive `run-stock` path
- emit structured events when agent status transitions occur
- do not change the existing interactive `run_analysis()` terminal layout in phase 1
- update the `batch` command to render a `Live` dashboard while the batch runner executes

### `cli/automation.py`

- add batch dashboard state models and helper functions
- add per-worker slot state tracking
- add progress-event polling/parsing helpers
- add a batch runner path that updates dashboard state while child futures are active
- preserve the existing final batch result contract

## Safety And Failure Handling

The dashboard must degrade gracefully.

- If a child emits no progress events, its slot still renders with coarse job states.
- If a child emits malformed progress events, ignore invalid lines and keep the job running.
- If a child fails before any internal milestone completes, the slot still shows the assigned ticker and terminal `failed` state.
- Existing batch exit-code behavior remains unchanged: any failed child still causes `batch` to exit non-zero.
- Existing `run-stock` human-readable completion output remains intact unless explicitly suppressed for child-process use.

## Testing Strategy

Add targeted tests around the new behavior.

### Unit Tests

- progress percentage from completed milestone counts
- default total-milestone calculation for stock runs
- slot assignment and slot reuse as jobs complete
- parsing of JSONL progress events
- graceful handling of empty or malformed event files

### CLI And Integration Tests

- `batch` still dispatches the runner with the expected arguments
- batch result shape and exit behavior remain unchanged
- live-state helpers correctly reflect active, queued, completed, and failed jobs
- fallback behavior works when a child produces no progress events

## Open Technical Constraints

The current local environment cannot import the CLI test modules because `langgraph` is not installed in this shell environment. Validation for this work must either:

- run in the intended project environment with dependencies installed, or
- use narrower tests that avoid the unavailable import path

## Implementation Notes

Recommended sequence:

1. Add batch-progress state helpers and tests.
2. Add structured child progress emission and tests.
3. Add parent-side progress polling and worker slot updates.
4. Add the Rich live dashboard to the `batch` command.
5. Run focused validation in the correct project environment.
