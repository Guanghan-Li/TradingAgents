from copy import deepcopy
from collections import deque
from concurrent.futures import FIRST_COMPLETED, ThreadPoolExecutor, wait
from contextlib import nullcontext
from datetime import date, datetime
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import time
from typing import Optional

import yaml

from cli.batch_progress import (
    BatchDashboardState,
    BatchWorkerSlot,
    RunProgressTracker,
    append_progress_event,
    apply_progress_event,
    read_progress_events,
)
from tradingagents.default_config import DEFAULT_CONFIG
from tradingagents.graph.trading_graph import TradingAgentsGraph

from cli.utils import (
    ANALYST_ORDER,
    build_llm_routing_config,
    resolve_gateway_model_pair,
)


DEFAULT_BATCH_PROVIDER = "openai"
DEFAULT_BATCH_BACKEND_URL = "https://api.itgpt.chat/v1"
DEFAULT_BATCH_MODEL = "gpt-5.4"
DEFAULT_REASONING_EFFORT = "high"
DEFAULT_DEPTH_PRESET = "deep"
DEFAULT_BATCH_LAUNCH_STAGGER_SECONDS = 180.0
DEPTH_PRESET_TO_ROUNDS = {
    "shallow": 1,
    "medium": 3,
    "deep": 5,
}
ALL_STOCK_ANALYSTS = [analyst.value for _, analyst in ANALYST_ORDER]
RUN_REPORT_SECTIONS = [
    "market_report",
    "sentiment_report",
    "news_report",
    "fundamentals_report",
    "macro_report",
    "factor_rules_report",
    "valuation_data",
    "segment_report",
    "scenario_catalyst_report",
    "position_sizing_report",
    "investment_plan",
    "trader_investment_plan",
    "final_trade_decision",
    "chief_analyst_report",
]


def format_report_content(content) -> str:
    if isinstance(content, str):
        return content
    if isinstance(content, (dict, list)):
        return json.dumps(content, indent=2, sort_keys=True)
    return str(content)


def has_meaningful_report_content(content) -> bool:
    if content is None:
        return False
    if isinstance(content, str):
        return bool(content.strip())
    if isinstance(content, bool):
        return True
    if isinstance(content, (int, float)):
        return True
    if isinstance(content, dict):
        return any(has_meaningful_report_content(value) for value in content.values())
    if isinstance(content, (list, tuple, set)):
        return any(has_meaningful_report_content(value) for value in content)
    return bool(content)


def resolve_analysis_date(analysis_date: Optional[str] = None) -> str:
    return analysis_date or date.today().isoformat()


def resolve_selected_analysts(analysts: Optional[list[str]] = None) -> list[str]:
    if not analysts or "all" in {analyst.lower() for analyst in analysts}:
        return ALL_STOCK_ANALYSTS.copy()
    return [analyst.lower() for analyst in analysts]


def load_watchlist(watchlist_path: str | Path) -> dict:
    payload = yaml.safe_load(Path(watchlist_path).read_text()) or {}
    return {
        "defaults": payload.get("defaults", {}) or {},
        "tickers": payload.get("tickers", []) or [],
    }


def build_batch_jobs(
    *,
    watchlist_path: str | Path,
    analysis_date: Optional[str] = None,
    provider: Optional[str] = None,
    backend_url: Optional[str] = None,
    model: Optional[str] = None,
    quick_model: Optional[str] = None,
    deep_model: Optional[str] = None,
    reasoning_effort: Optional[str] = None,
    depth: Optional[str] = None,
    results_dir: Optional[str] = None,
) -> list[dict]:
    watchlist = load_watchlist(watchlist_path)
    defaults = watchlist["defaults"]
    jobs = []

    for ticker_entry in watchlist["tickers"]:
        if isinstance(ticker_entry, str):
            job = {"ticker": ticker_entry}
        else:
            job = dict(ticker_entry)

        merged = {**defaults, **job}
        if analysis_date is not None:
            merged["analysis_date"] = analysis_date
        if provider is not None:
            merged["provider"] = provider
        if backend_url is not None:
            merged["backend_url"] = backend_url
        if model is not None:
            merged["model"] = model
        if quick_model is not None:
            merged["quick_model"] = quick_model
        if deep_model is not None:
            merged["deep_model"] = deep_model
        if reasoning_effort is not None:
            merged["reasoning_effort"] = reasoning_effort
        if depth is not None:
            merged["depth"] = depth
        if results_dir is not None:
            merged["results_dir"] = results_dir
        jobs.append(merged)

    return jobs


def build_run_stock_argv(job: dict) -> list[str]:
    argv = [sys.executable, "-m", "cli.main", "run-stock", "--ticker", job["ticker"]]
    flag_map = {
        "analysis_date": "--date",
        "provider": "--provider",
        "backend_url": "--backend-url",
        "model": "--model",
        "quick_model": "--quick-model",
        "deep_model": "--deep-model",
        "reasoning_effort": "--reasoning-effort",
        "depth": "--depth",
        "results_dir": "--results-dir",
        "progress_file": "--progress-file",
    }
    for key, flag in flag_map.items():
        value = job.get(key)
        if value:
            argv.extend([flag, str(value)])
    return argv


def run_cli_stock_job(job: dict) -> dict:
    completed = subprocess.run(
        build_run_stock_argv(job),
        capture_output=True,
        text=True,
        check=False,
    )
    return {
        "ticker": job["ticker"],
        "status": "completed" if completed.returncode == 0 else "failed",
        "returncode": completed.returncode,
        "stdout": completed.stdout,
        "stderr": completed.stderr,
    }


def run_batch_command(
    *,
    watchlist_path: str | Path,
    cap: int = 4,
    analysis_date: Optional[str] = None,
    provider: Optional[str] = None,
    backend_url: Optional[str] = None,
    model: Optional[str] = None,
    quick_model: Optional[str] = None,
    deep_model: Optional[str] = None,
    reasoning_effort: Optional[str] = None,
    depth: Optional[str] = None,
    results_dir: Optional[str] = None,
    progress_callback=None,
    launch_stagger_seconds: float = 0.0,
) -> dict:
    if cap < 1:
        raise ValueError("cap must be at least 1")

    jobs = build_batch_jobs(
        watchlist_path=watchlist_path,
        analysis_date=analysis_date,
        provider=provider,
        backend_url=backend_url,
        model=model,
        quick_model=quick_model,
        deep_model=deep_model,
        reasoning_effort=reasoning_effort,
        depth=depth,
        results_dir=results_dir,
    )

    results_by_ticker = {}
    pending_jobs = deque(dict(job) for job in jobs)
    dashboard_state = None
    if progress_callback:
        dashboard_state = BatchDashboardState(
            total_jobs=len(jobs),
            slots=[BatchWorkerSlot(slot_index=index + 1) for index in range(cap)],
        )
    slots = dashboard_state.slots if dashboard_state is not None else [
        BatchWorkerSlot(slot_index=index + 1) for index in range(cap)
    ]

    progress_dir_context = (
        tempfile.TemporaryDirectory(prefix="tradingagents-batch-progress-")
        if progress_callback
        else nullcontext(None)
    )

    with progress_dir_context as progress_dir, ThreadPoolExecutor(max_workers=cap) as executor:
        future_to_state = {}
        next_launch_at = time.monotonic()

        def publish_update():
            if progress_callback and dashboard_state is not None:
                progress_callback(dashboard_state)

        def poll_active_slots():
            for slot in dashboard_state.slots if dashboard_state is not None else []:
                if not slot.progress_file:
                    continue
                events, new_offset = read_progress_events(
                    slot.progress_file,
                    slot.progress_offset,
                )
                slot.progress_offset = new_offset
                for event in events:
                    apply_progress_event(slot, event)

        def submit_next_job(slot: BatchWorkerSlot):
            if not pending_jobs:
                return False

            job = pending_jobs.popleft()
            if progress_dir is not None:
                progress_path = Path(progress_dir) / f"{slot.slot_index}-{job['ticker']}.jsonl"
                job["progress_file"] = str(progress_path)
                slot.assign(ticker=job["ticker"], progress_file=str(progress_path))
            future = executor.submit(run_cli_stock_job, job)
            future_to_state[future] = {"job": job, "slot": slot}
            return True

        def get_available_slot():
            active_slots = {id(state["slot"]) for state in future_to_state.values()}
            for slot in slots:
                if id(slot) not in active_slots:
                    return slot
            return None

        def maybe_submit_jobs():
            nonlocal next_launch_at

            submitted_any = False
            while pending_jobs:
                slot = get_available_slot()
                if slot is None:
                    break

                now = time.monotonic()
                if launch_stagger_seconds > 0 and now < next_launch_at:
                    break

                if not submit_next_job(slot):
                    break

                submitted_any = True
                if launch_stagger_seconds > 0:
                    next_launch_at = now + launch_stagger_seconds
                    break

            return submitted_any

        maybe_submit_jobs()
        publish_update()

        while future_to_state or pending_jobs:
            maybe_submit_jobs()

            done, _ = wait(
                list(future_to_state.keys()),
                timeout=0.05 if future_to_state else 0.05,
                return_when=FIRST_COMPLETED,
            ) if future_to_state else (set(), set())

            if progress_callback and dashboard_state is not None:
                poll_active_slots()
                publish_update()

            if not done:
                if pending_jobs and not future_to_state:
                    sleep_for = 0.01
                    if launch_stagger_seconds > 0:
                        sleep_for = min(
                            max(next_launch_at - time.monotonic(), 0.0),
                            0.05,
                        )
                    time.sleep(sleep_for)
                continue

            for future in done:
                state = future_to_state.pop(future)
                job = state["job"]
                slot = state["slot"]
                result = future.result()
                results_by_ticker[job["ticker"]] = result

                if progress_callback and dashboard_state is not None:
                    poll_active_slots()
                    slot.status = "completed" if result["returncode"] == 0 else "failed"
                    slot.active_agent = None
                    if result["returncode"] == 0:
                        dashboard_state.completed_jobs += 1
                    else:
                        dashboard_state.failed_jobs += 1
                    publish_update()

    completed = [
        job["ticker"]
        for job in jobs
        if results_by_ticker[job["ticker"]]["returncode"] == 0
    ]
    failed = [
        job["ticker"]
        for job in jobs
        if results_by_ticker[job["ticker"]]["returncode"] != 0
    ]
    return {
        "jobs": jobs,
        "results": [results_by_ticker[job["ticker"]] for job in jobs],
        "completed": completed,
        "failed": failed,
    }


def build_batch_config(
    *,
    provider: str = DEFAULT_BATCH_PROVIDER,
    backend_url: str = DEFAULT_BATCH_BACKEND_URL,
    model: str = DEFAULT_BATCH_MODEL,
    quick_model: Optional[str] = None,
    deep_model: Optional[str] = None,
    reasoning_effort: str = DEFAULT_REASONING_EFFORT,
    depth: str = DEFAULT_DEPTH_PRESET,
    results_dir: Optional[str] = None,
) -> dict:
    resolved_quick_model = quick_model or model
    resolved_deep_model = deep_model or model
    resolved_quick_model, resolved_deep_model = resolve_gateway_model_pair(
        provider,
        backend_url,
        resolved_quick_model,
        resolved_deep_model,
    )
    rounds = DEPTH_PRESET_TO_ROUNDS[depth]

    config = deepcopy(DEFAULT_CONFIG)
    config["llm_provider"] = provider.lower()
    config["backend_url"] = backend_url
    config["quick_think_llm"] = resolved_quick_model
    config["deep_think_llm"] = resolved_deep_model
    config["openai_reasoning_effort"] = reasoning_effort
    config["max_debate_rounds"] = rounds
    config["max_risk_discuss_rounds"] = rounds
    config["llm_routing"] = build_llm_routing_config(
        provider=provider,
        shallow_model=resolved_quick_model,
        deep_model=resolved_deep_model,
        backend_url=backend_url,
    )
    if results_dir:
        config["results_dir"] = results_dir
    return config


def build_run_summary(
    *,
    final_state: dict,
    ticker: str,
    analysis_date: str,
    decision: str,
    config: dict,
    started_at: str,
    ended_at: str,
    status: str = "completed",
    error: Optional[str] = None,
) -> dict:
    chief_data = final_state.get("chief_analyst_data", {})
    verdict = chief_data.get("verdict", {})
    return {
        "ticker": ticker,
        "analysis_date": analysis_date,
        "status": status,
        "decision": decision,
        "chief_rating": verdict.get("rating", ""),
        "chief_summary": verdict.get("summary", ""),
        "chief_thesis": verdict.get("thesis", ""),
        "catalysts": chief_data.get("catalysts", []),
        "risk_summary": chief_data.get("tail_risk", {}).get("risk_summary", ""),
        "started_at": started_at,
        "ended_at": ended_at,
        "provider": config.get("llm_provider"),
        "backend_url": config.get("backend_url"),
        "quick_think_llm": config.get("quick_think_llm"),
        "deep_think_llm": config.get("deep_think_llm"),
        "openai_reasoning_effort": config.get("openai_reasoning_effort"),
        "results_dir": str(Path(config["results_dir"]) / ticker / analysis_date),
        "error": error,
    }


def write_run_artifacts(
    *,
    final_state: dict,
    ticker: str,
    analysis_date: str,
    decision: str,
    config: dict,
    started_at: str,
    ended_at: str,
    status: str = "completed",
    error: Optional[str] = None,
) -> dict:
    run_dir = Path(config["results_dir"]) / ticker / analysis_date
    report_dir = run_dir / "reports"
    report_dir.mkdir(parents=True, exist_ok=True)

    written_sections = []
    for section in RUN_REPORT_SECTIONS:
        content = final_state.get(section)
        if not has_meaningful_report_content(content):
            continue
        file_path = report_dir / f"{section}.md"
        file_path.write_text(format_report_content(content))
        written_sections.append((section, format_report_content(content)))

    complete_report = "\n\n".join(
        f"## {section}\n{content}" for section, content in written_sections
    )
    (run_dir / "complete_report.md").write_text(complete_report)

    summary = build_run_summary(
        final_state=final_state,
        ticker=ticker,
        analysis_date=analysis_date,
        decision=decision,
        config=config,
        started_at=started_at,
        ended_at=ended_at,
        status=status,
        error=error,
    )
    (run_dir / "run_summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True))
    return summary


def collect_run_summaries(*, results_dir: str | Path, analysis_date: str) -> list[dict]:
    base_dir = Path(results_dir)
    summaries = []
    for summary_path in sorted(base_dir.glob(f"*/{analysis_date}/run_summary.json")):
        summaries.append(json.loads(summary_path.read_text()))
    return summaries


def classify_summary(summary: dict) -> str:
    rating = (summary.get("chief_rating") or "").strip().lower()
    status = (summary.get("status") or "").strip().lower()
    if status != "completed":
        return "failed"
    if rating in {"buy", "overweight", "strong buy"}:
        return "bullish"
    if rating in {"sell", "underweight", "avoid", "strong sell"}:
        return "bearish"
    return "mixed"


def summarize_runs_for_date(*, results_dir: str | Path, analysis_date: str) -> dict:
    summaries = collect_run_summaries(results_dir=results_dir, analysis_date=analysis_date)
    buckets = {
        "bullish": [],
        "bearish": [],
        "mixed": [],
        "failed": [],
    }
    for summary in summaries:
        buckets[classify_summary(summary)].append(summary)

    payload = {
        "analysis_date": analysis_date,
        "counts": {
            "bullish": len(buckets["bullish"]),
            "bearish": len(buckets["bearish"]),
            "mixed": len(buckets["mixed"]),
            "failed": len(buckets["failed"]),
        },
        "bullish": buckets["bullish"],
        "bearish": buckets["bearish"],
        "mixed": buckets["mixed"],
        "failed": buckets["failed"],
    }

    summary_dir = Path(results_dir) / "daily_summaries" / analysis_date
    summary_dir.mkdir(parents=True, exist_ok=True)
    (summary_dir / "daily_summary.json").write_text(json.dumps(payload, indent=2, sort_keys=True))

    def format_bucket(title: str, items: list[dict]) -> str:
        if not items:
            return f"## {title}\n\n- None"
        lines = [f"## {title}", ""]
        for item in items:
            lines.append(
                f"- {item['ticker']}: {item.get('chief_rating', '') or item.get('status', '')} - {item.get('chief_summary', '')}"
            )
        return "\n".join(lines)

    markdown = "\n\n".join(
        [
            f"# Daily Summary: {analysis_date}",
            format_bucket("Strongest bullish ideas", buckets["bullish"]),
            format_bucket("Bearish or avoid ideas", buckets["bearish"]),
            format_bucket("Mixed / watchlist names", buckets["mixed"]),
            format_bucket("Failed or incomplete runs", buckets["failed"]),
        ]
    )
    (summary_dir / "daily_summary.md").write_text(markdown)
    return payload


def run_stock_command(
    *,
    ticker: str,
    analysis_date: Optional[str] = None,
    analysts: Optional[list[str]] = None,
    provider: str = DEFAULT_BATCH_PROVIDER,
    backend_url: str = DEFAULT_BATCH_BACKEND_URL,
    model: str = DEFAULT_BATCH_MODEL,
    quick_model: Optional[str] = None,
    deep_model: Optional[str] = None,
    reasoning_effort: str = DEFAULT_REASONING_EFFORT,
    depth: str = DEFAULT_DEPTH_PRESET,
    results_dir: Optional[str] = None,
    progress_file: Optional[str] = None,
    debug: bool = False,
) -> dict:
    resolved_analysis_date = resolve_analysis_date(analysis_date)
    resolved_analysts = resolve_selected_analysts(analysts)
    config = build_batch_config(
        provider=provider,
        backend_url=backend_url,
        model=model,
        quick_model=quick_model,
        deep_model=deep_model,
        reasoning_effort=reasoning_effort,
        depth=depth,
        results_dir=results_dir,
    )

    graph = TradingAgentsGraph(
        selected_analysts=resolved_analysts,
        debug=debug,
        config=config,
    )
    started_at = datetime.now().isoformat()
    if progress_file:
        tracker = RunProgressTracker(
            resolved_analysts,
            ticker=ticker,
            analysis_date=resolved_analysis_date,
        )
        append_progress_event(progress_file, tracker.build_run_started_event())

        init_agent_state = graph.propagator.create_initial_state(
            ticker,
            resolved_analysis_date,
        )
        args = graph.propagator.get_graph_args()
        final_state = init_agent_state

        try:
            for chunk in graph.graph.stream(init_agent_state, **args):
                final_state = chunk
                for event in tracker.update_from_chunk(chunk):
                    append_progress_event(progress_file, event)
            decision = graph.process_signal(final_state["final_trade_decision"])
            append_progress_event(progress_file, tracker.build_run_completed_event())
        except Exception as exc:
            append_progress_event(progress_file, tracker.build_run_failed_event(str(exc)))
            raise
    else:
        final_state, decision = graph.propagate(ticker, resolved_analysis_date)
    summary = write_run_artifacts(
        final_state=final_state,
        ticker=ticker,
        analysis_date=resolved_analysis_date,
        decision=decision,
        config=config,
        started_at=started_at,
        ended_at=datetime.now().isoformat(),
    )
    return {
        "ticker": ticker,
        "analysis_date": resolved_analysis_date,
        "selected_analysts": resolved_analysts,
        "config": config,
        "final_state": final_state,
        "decision": decision,
        "run_summary": summary,
    }
