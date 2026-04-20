# ruff: noqa: E402

from copy import deepcopy
from collections import deque
from concurrent.futures import FIRST_COMPLETED, ThreadPoolExecutor, wait
from contextlib import nullcontext
from datetime import date, datetime
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time
from typing import Optional

from langchain_core.messages import HumanMessage, SystemMessage
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
from tradingagents.env import load_project_dotenv
from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.llm_clients import create_llm_client
from tradingagents.agents.utils.analyst_resilience import build_degraded_stock_final_state
from tradingagents.prefetch.stock_prefetch import build_prefetched_stock_context


load_project_dotenv(override=True)

from cli.utils import (
    ANALYST_ORDER,
    build_llm_routing_config,
    normalize_provider_key,
    resolve_gateway_model_pair,
)


DEFAULT_BATCH_PROVIDER = "anthropic"
DEFAULT_BATCH_BACKEND_URL = "https://api.routeai.cc"
DEFAULT_BATCH_MODEL = "claude-sonnet-4-6"
DEFAULT_REASONING_EFFORT = "medium"
DEFAULT_DEPTH_PRESET = "medium"
DEFAULT_BATCH_LAUNCH_STAGGER_SECONDS = 0.0
BATCH_CODEX_AGENT_CLI = "codex"
BATCH_CLAUDE_AGENT_CLI = "claude"
DEFAULT_BATCH_AGENT_CLI = BATCH_CODEX_AGENT_CLI
BATCH_CODEX_PROVIDER = "openai"
BATCH_CODEX_BACKEND_URL = "https://api.routeai.cc"
BATCH_CODEX_MODEL = "gpt-5.4"
BATCH_CODEX_REASONING_EFFORT = "high"
BATCH_CODEX_FINAL_REASONING_EFFORT = "xhigh"
BATCH_CLAUDE_PROVIDER = "anthropic"
BATCH_CLAUDE_BACKEND_URL = "https://api.routeai.cc"
BATCH_CLAUDE_MODEL = "claude-sonnet-4-6"
BATCH_CLAUDE_REASONING_EFFORT = "high"
BATCH_RESULTS_DIR = "results_batch"
BATCH_RESULTS_LAYOUT = "date_first"
DEPTH_PRESET_TO_ROUNDS = {
    "shallow": 1,
    "medium": 2,
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


def resolve_batch_agent_preset(agent_cli: Optional[str] = None) -> dict:
    normalized = (agent_cli or DEFAULT_BATCH_AGENT_CLI).lower()
    if normalized == BATCH_CODEX_AGENT_CLI:
        return {
            "agent_cli": BATCH_CODEX_AGENT_CLI,
            "provider": BATCH_CODEX_PROVIDER,
            "backend_url": BATCH_CODEX_BACKEND_URL,
            "model": BATCH_CODEX_MODEL,
            "quick_model": BATCH_CODEX_MODEL,
            "deep_model": BATCH_CODEX_MODEL,
            "reasoning_effort": BATCH_CODEX_REASONING_EFFORT,
            "final_reasoning_effort": BATCH_CODEX_FINAL_REASONING_EFFORT,
        }
    if normalized == BATCH_CLAUDE_AGENT_CLI:
        return {
            "agent_cli": BATCH_CLAUDE_AGENT_CLI,
            "provider": BATCH_CLAUDE_PROVIDER,
            "backend_url": BATCH_CLAUDE_BACKEND_URL,
            "model": BATCH_CLAUDE_MODEL,
            "quick_model": BATCH_CLAUDE_MODEL,
            "deep_model": BATCH_CLAUDE_MODEL,
            "reasoning_effort": BATCH_CLAUDE_REASONING_EFFORT,
            "final_reasoning_effort": BATCH_CLAUDE_REASONING_EFFORT,
        }
    raise ValueError("agent_cli must be either 'codex' or 'claude'")


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
    results_layout: Optional[str] = None,
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
        if results_layout is not None:
            merged["results_layout"] = results_layout
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
        "results_layout": "--results-layout",
        "progress_file": "--progress-file",
    }
    for key, flag in flag_map.items():
        value = job.get(key)
        if value:
            argv.extend([flag, str(value)])
    return argv


def run_cli_stock_job(job: dict) -> dict:
    log_dir = build_job_run_dir(job) / "_batch_logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    attempt = int(job.get("_attempt", 1))
    stdout_path = log_dir / f"attempt_{attempt}.stdout.log"
    stderr_path = log_dir / f"attempt_{attempt}.stderr.log"

    env = os.environ.copy()
    env.setdefault("PYTHONUNBUFFERED", "1")

    with stdout_path.open("w", buffering=1) as out_f, stderr_path.open("w", buffering=1) as err_f:
        completed = subprocess.run(
            build_run_stock_argv(job),
            stdout=out_f,
            stderr=err_f,
            text=True,
            check=False,
            env=env,
        )

    try:
        stdout_text = stdout_path.read_text()
    except OSError:
        stdout_text = ""
    try:
        stderr_text = stderr_path.read_text()
    except OSError:
        stderr_text = ""

    return {
        "ticker": job["ticker"],
        "status": "completed" if completed.returncode == 0 else "failed",
        "returncode": completed.returncode,
        "stdout": stdout_text,
        "stderr": stderr_text,
        "_streamed_logs": True,
    }


def build_job_run_dir(job: dict) -> Path:
    results_root = Path(job.get("results_dir") or BATCH_RESULTS_DIR)
    analysis_date = job.get("analysis_date") or resolve_analysis_date()
    if job.get("results_layout") == "date_first":
        return results_root / analysis_date / job["ticker"]
    return results_root / job["ticker"] / analysis_date


def write_batch_attempt_logs(job: dict, *, attempt: int, result: dict) -> None:
    log_dir = build_job_run_dir(job) / "_batch_logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    (log_dir / f"attempt_{attempt}.stdout.log").write_text(result.get("stdout") or "")
    (log_dir / f"attempt_{attempt}.stderr.log").write_text(result.get("stderr") or "")


def run_cli_stock_job_with_retry(job: dict, *, max_attempts: int = 2) -> dict:
    last_result = None
    for attempt in range(1, max_attempts + 1):
        job["_attempt"] = attempt
        result = run_cli_stock_job(job)
        if not result.get("_streamed_logs"):
            write_batch_attempt_logs(job, attempt=attempt, result=result)
        last_result = result
        if result["returncode"] == 0:
            result["attempts"] = attempt
            return result
    if last_result is None:
        raise RuntimeError("run_cli_stock_job_with_retry completed without attempts")
    last_result["attempts"] = max_attempts
    return last_result


def summarize_batch_failure(result: dict) -> str:
    stderr = (result.get("stderr") or "").strip()
    stdout = (result.get("stdout") or "").strip()
    detail = stderr or stdout or f"child process exited with code {result.get('returncode')}"
    if "Traceback" in detail:
        lines = [line.strip() for line in detail.splitlines() if line.strip()]
        for line in reversed(lines):
            if line.startswith("File "):
                continue
            if line.startswith("^"):
                continue
            if line.startswith("Traceback"):
                continue
            detail = line
            break
    compact = " ".join(detail.split())
    return compact[:240]


def build_run_dir(*, config: dict, ticker: str, analysis_date: str) -> Path:
    results_root = Path(config["results_dir"])
    if config.get("results_layout") == "date_first":
        return results_root / analysis_date / ticker
    return results_root / ticker / analysis_date


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
    agent_cli: Optional[str] = None,
) -> dict:
    if cap < 1:
        raise ValueError("cap must be at least 1")

    preset = resolve_batch_agent_preset(agent_cli)
    resolved_results_dir = results_dir or BATCH_RESULTS_DIR
    jobs = build_batch_jobs(
        watchlist_path=watchlist_path,
        analysis_date=analysis_date,
        provider=preset["provider"],
        backend_url=preset["backend_url"],
        model=preset["model"],
        quick_model=preset["quick_model"],
        deep_model=preset["deep_model"],
        reasoning_effort=preset["reasoning_effort"],
        depth=depth,
        results_dir=resolved_results_dir,
        results_layout=BATCH_RESULTS_LAYOUT,
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
            else:
                slot.assign(ticker=job["ticker"], progress_file=None)
            future = executor.submit(run_cli_stock_job_with_retry, job)
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
                    if result["returncode"] != 0:
                        slot.error = summarize_batch_failure(result)
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
    resolved_analysis_date = jobs[0].get("analysis_date") or resolve_analysis_date()
    summarize_runs_for_date(
        results_dir=resolved_results_dir,
        analysis_date=resolved_analysis_date,
    )
    final_allocation = generate_final_allocation_artifacts(
        results_dir=resolved_results_dir,
        analysis_date=resolved_analysis_date,
        provider=preset["provider"],
        backend_url=preset["backend_url"],
        model=preset["model"],
        reasoning_effort=preset["final_reasoning_effort"],
    )
    return {
        "jobs": jobs,
        "results": [results_by_ticker[job["ticker"]] for job in jobs],
        "completed": completed,
        "failed": failed,
        "final_allocation": final_allocation,
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
    results_layout: str = "ticker_first",
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
    config["llm_provider"] = normalize_provider_key(provider)
    config["backend_url"] = backend_url
    config["quick_think_llm"] = resolved_quick_model
    config["deep_think_llm"] = resolved_deep_model
    config["openai_reasoning_effort"] = None
    config["anthropic_effort"] = None
    if config["llm_provider"] in {"openai", "codex_cli"}:
        config["openai_reasoning_effort"] = reasoning_effort
    elif config["llm_provider"] == "anthropic":
        config["anthropic_effort"] = reasoning_effort
    elif config["llm_provider"] == "claude_code":
        # Local Claude runs can exceed the generic 180s floor on long analyst steps.
        config["llm_timeout_seconds"] = max(config.get("llm_timeout_seconds", 60), 90)
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
    config["results_layout"] = results_layout
    return config


def probe_llm_backend(config: dict) -> str | None:
    provider = config.get("llm_provider")
    if provider != "anthropic":
        return

    client_kwargs = {
        "timeout": 20,
        "max_retries": 0,
        "max_tokens": 16,
    }
    effort = config.get("anthropic_effort")
    if effort:
        client_kwargs["effort"] = effort

    llm = create_llm_client(
        provider=provider,
        model=config.get("quick_think_llm"),
        base_url=config.get("backend_url"),
        **client_kwargs,
    ).get_llm()

    try:
        llm.invoke("Reply with exactly OK")
    except Exception as exc:
        return f"Anthropic backend preflight failed: {str(exc).strip() or exc.__class__.__name__}"
    return None


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
    chief_action = verdict.get("absolute_action", "")
    chief_relative_stance = verdict.get("relative_stance", "")
    return {
        "ticker": ticker,
        "analysis_date": analysis_date,
        "status": status,
        "decision": decision,
        "chief_action": chief_action,
        "chief_relative_stance": chief_relative_stance,
        "chief_rating": chief_relative_stance or chief_action,
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
        "anthropic_effort": config.get("anthropic_effort"),
        "results_dir": str(build_run_dir(config=config, ticker=ticker, analysis_date=analysis_date)),
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
    run_dir = build_run_dir(config=config, ticker=ticker, analysis_date=analysis_date)
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


def _normalize_summary_action(value: str) -> str:
    normalized = (value or "").strip().upper()
    if normalized in {"BUY", "HOLD", "SELL"}:
        return normalized
    if normalized == "OVERWEIGHT":
        return "BUY"
    if normalized == "UNDERWEIGHT":
        return "SELL"
    return ""


def _normalize_summary_relative_stance(value: str) -> str:
    normalized = (value or "").strip().upper()
    if normalized in {"OVERWEIGHT", "UNDERWEIGHT"}:
        return normalized.title()
    if normalized in {"NEUTRAL", "HOLD"}:
        return "Neutral"
    return ""


def collect_run_summaries(*, results_dir: str | Path, analysis_date: str) -> list[dict]:
    base_dir = Path(results_dir)
    summaries = []
    seen_paths = set()
    for pattern in (
        f"*/{analysis_date}/run_summary.json",
        f"{analysis_date}/*/run_summary.json",
    ):
        for summary_path in sorted(base_dir.glob(pattern)):
            if summary_path in seen_paths:
                continue
            seen_paths.add(summary_path)
            summaries.append(json.loads(summary_path.read_text()))
    return summaries


def classify_summary(summary: dict) -> str:
    action = _normalize_summary_action(
        summary.get("chief_action") or summary.get("decision") or summary.get("chief_rating") or ""
    ).lower()
    status = (summary.get("status") or "").strip().lower()
    if status != "completed":
        return "failed"
    if action == "buy":
        return "bullish"
    if action == "sell":
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
            display_action = _normalize_summary_action(
                item.get("chief_action") or item.get("decision") or item.get("chief_rating") or ""
            )
            relative_stance = _normalize_summary_relative_stance(
                item.get("chief_relative_stance") or item.get("chief_rating") or ""
            )
            label = display_action or item.get("status", "")
            if relative_stance:
                label = f"{label} / {relative_stance}"
            lines.append(
                f"- {item['ticker']}: {label} - {item.get('chief_summary', '')}"
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


def _extract_json_object_from_text(text: str) -> dict | None:
    stripped = text.strip()
    if not stripped:
        return None
    try:
        payload = json.loads(stripped)
        return payload if isinstance(payload, dict) else None
    except json.JSONDecodeError:
        start = stripped.find("{")
        end = stripped.rfind("}")
        if start == -1 or end == -1 or end <= start:
            return None
        try:
            payload = json.loads(stripped[start : end + 1])
        except json.JSONDecodeError:
            return None
        return payload if isinstance(payload, dict) else None


def build_allocation_packets(
    *,
    results_dir: str | Path,
    analysis_date: str,
) -> list[dict]:
    results_root = Path(results_dir)
    packets = []
    for run_summary_path in sorted((results_root / analysis_date).glob("*/run_summary.json")):
        payload = json.loads(run_summary_path.read_text())
        absolute_action = _normalize_summary_action(
            payload.get("chief_action") or payload.get("decision") or payload.get("chief_rating") or ""
        )
        if absolute_action != "BUY":
            continue
        relative_stance = _normalize_summary_relative_stance(
            payload.get("chief_relative_stance") or payload.get("chief_rating") or ""
        )
        chief_summary = (payload.get("chief_summary", "") or "").strip()
        chief_thesis = (payload.get("chief_thesis", "") or "").strip()
        risk_summary = (payload.get("risk_summary", "") or "").strip()
        packets.append(
            {
                "ticker": payload.get("ticker", run_summary_path.parent.name),
                "absolute_action": absolute_action,
                "relative_stance": relative_stance,
                "chief_summary": chief_summary[:120],
                "chief_thesis": chief_thesis[:160],
                "risk_summary": risk_summary[:100],
            }
        )
    return packets


def build_decision_allocation_packets(
    *,
    results_dir: str | Path,
    analysis_date: str,
) -> list[dict]:
    packets = []
    for payload in collect_run_summaries(results_dir=results_dir, analysis_date=analysis_date):
        if (payload.get("analysis_date") or "").strip() != analysis_date:
            continue
        if (payload.get("status") or "").strip().lower() != "completed":
            continue

        absolute_action = _normalize_summary_action(
            payload.get("chief_action") or payload.get("decision") or ""
        )
        if absolute_action != "BUY":
            continue

        packets.append(
            {
                "ticker": payload.get("ticker", ""),
                "analysis_date": analysis_date,
                "decision": absolute_action.title(),
                "relative_stance": _normalize_summary_relative_stance(
                    payload.get("chief_relative_stance") or payload.get("chief_rating") or ""
                ),
                "chief_summary": (payload.get("chief_summary") or "").strip(),
                "chief_thesis": (payload.get("chief_thesis") or "").strip(),
                "risk_summary": (payload.get("risk_summary") or "").strip(),
                "position_sizing": payload.get("position_sizing") or {},
                "scenario_analysis": payload.get("scenario_analysis") or {},
                "catalysts": payload.get("catalysts") or [],
                "invalidation": payload.get("invalidation") or {},
            }
        )
    return packets


def _extract_decision_grade_allocation_payload(payload: dict) -> dict:
    required_top_level = {
        "executive_decision",
        "selected_positions",
        "rejected_close_alternatives",
        "portfolio_risks",
        "decision_quality",
    }
    missing = sorted(required_top_level - set(payload))
    if missing:
        raise ValueError(f"Decision-grade allocation payload missing keys: {missing}")

    selected_positions = payload.get("selected_positions")
    if not isinstance(selected_positions, list) or len(selected_positions) != 3:
        raise ValueError("Decision-grade allocation must contain exactly 3 selected positions.")

    executive_decision = payload.get("executive_decision")
    if not isinstance(executive_decision, dict):
        raise ValueError("Decision-grade allocation must include an executive_decision object.")

    total_allocated_dollars = executive_decision.get("total_allocated_dollars")
    if total_allocated_dollars != 200:
        raise ValueError("Decision-grade allocation must allocate exactly $200.")

    return payload


def _non_empty_value(value) -> bool:
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, (list, tuple, set, dict)):
        return bool(value)
    return value is not None


def verify_decision_grade_allocation(payload: dict, *, eligible_packets: list[dict]) -> dict:
    payload = _extract_decision_grade_allocation_payload(payload)
    selected_positions = payload["selected_positions"]
    selected_tickers = [
        str(item.get("ticker", "")).strip().upper()
        for item in selected_positions
    ]
    if len(set(selected_tickers)) != 3:
        raise ValueError("Decision-grade allocation selected positions must be unique.")

    eligible_tickers = {
        str(packet.get("ticker", "")).strip().upper()
        for packet in eligible_packets
        if str(packet.get("ticker", "")).strip()
    }
    selected_ticker_set = set(selected_tickers)
    for ticker in selected_tickers:
        if ticker not in eligible_tickers:
            raise ValueError(f"Selected ticker {ticker} is not an eligible Buy.")

    rejected_alternatives = payload.get("rejected_close_alternatives") or []
    rejected_tickers = {
        str(item.get("ticker", "")).strip().upper()
        for item in rejected_alternatives
        if str(item.get("ticker", "")).strip()
    }
    invalid_rejected = sorted(rejected_tickers - eligible_tickers)
    if invalid_rejected:
        raise ValueError(f"Decision-grade allocation includes invalid rejected Buy alternatives: {invalid_rejected}")
    rejected_selected_overlap = sorted(rejected_tickers & selected_ticker_set)
    if rejected_selected_overlap:
        raise ValueError(f"Rejected Buy alternatives include selected tickers: {rejected_selected_overlap}")

    required_position_fields = {
        "ticker",
        "allocated_dollars",
        "weight_pct",
        "selection_role",
        "core_thesis",
        "key_supporting_evidence",
        "key_disconfirming_evidence",
        "entry_quality_assessment",
        "why_it_beats_closest_rejected_buy",
        "risk_controls_and_invalidation",
        "confidence",
    }
    total_allocated = 0
    for position in selected_positions:
        missing = [
            field
            for field in sorted(required_position_fields)
            if not _non_empty_value(position.get(field))
        ]
        if missing:
            raise ValueError(f"Selected position {position.get('ticker', '')} missing required fields: {missing}")
        allocated_dollars = position.get("allocated_dollars")
        if not isinstance(allocated_dollars, int) or allocated_dollars <= 0:
            raise ValueError("Each selected position must have a positive dollar allocation.")
        total_allocated += allocated_dollars
        comparison = str(position.get("why_it_beats_closest_rejected_buy", "")).upper()
        if not any(ticker and ticker in comparison for ticker in rejected_tickers):
            raise ValueError("Each selected position must include a named rejected Buy comparison.")

    if total_allocated != 200:
        raise ValueError("Selected position allocations must sum to $200.")

    executive_total = payload["executive_decision"].get("total_allocated_dollars")
    if executive_total != total_allocated:
        raise ValueError("Executive decision total must match selected position allocations.")

    return payload


def generate_decision_grade_allocation(
    *,
    analysis_date: str,
    daily_summary_markdown: str,
    stock_packets: list[dict],
    provider: str = BATCH_CODEX_PROVIDER,
    backend_url: str = BATCH_CODEX_BACKEND_URL,
    model: str = BATCH_CODEX_MODEL,
    reasoning_effort: str = BATCH_CODEX_FINAL_REASONING_EFFORT,
) -> dict:
    if not stock_packets:
        raise ValueError("Decision-grade allocation requires at least 3 Buy candidates.")

    summary_excerpt = daily_summary_markdown.strip()
    if len(summary_excerpt) > 2500:
        summary_excerpt = summary_excerpt[:2500] + "\n\n[truncated]"

    eligible_tickers = [
        str(packet.get("ticker", "")).strip()
        for packet in stock_packets
        if str(packet.get("ticker", "")).strip()
    ]

    system_prompt = (
        "You are an investment committee decision writer preparing a decision-grade allocation memo for a hypothetical paper portfolio. "
        "This is not investment advice. "
        "Use only the supplied daily summary and rich Buy-only stock packets. "
        "Choose exactly 3 names, all of which must already be explicit Buy decisions in the supplied evidence. "
        "Allocate exactly $200 across the 3 selected names, with all 3 positions receiving positive dollars. "
        "Do not output a ranking-sheet response. Write a committee-quality decision payload that defends why these 3 names won and why the closest rejected Buy names lost. "
        "You must explain weighting differences, discuss both business quality and entry quality, and name specific rejected alternatives. "
        "Avoid generic filler such as 'stronger support', 'better profile', or 'the rest' unless followed by concrete evidence. "
        "Return JSON only with this exact shape: "
        "{"
        "\"executive_decision\":{\"summary\":\"text\",\"why_this_portfolio\":\"text\",\"weighting_principle\":\"text\",\"total_allocated_dollars\":200},"
        "\"selected_positions\":[{\"ticker\":\"TICKER\",\"allocated_dollars\":1,\"weight_pct\":0,\"selection_role\":\"text\",\"core_thesis\":\"text\",\"key_supporting_evidence\":\"text\",\"key_disconfirming_evidence\":\"text\",\"entry_quality_assessment\":\"text\",\"why_it_beats_closest_rejected_buy\":\"text\",\"risk_controls_and_invalidation\":\"text\",\"confidence\":\"low|medium|medium-high|high\"}],"
        "\"rejected_close_alternatives\":[{\"ticker\":\"TICKER\",\"why_it_was_close\":\"text\",\"why_it_lost\":\"text\",\"what_would_have_changed_the_decision\":\"text\"}],"
        "\"portfolio_risks\":{\"top_risks\":[\"text\"],\"concentration_notes\":\"text\",\"macro_notes\":\"text\",\"timing_notes\":\"text\"},"
        "\"decision_quality\":{\"evidence_quality\":\"text\",\"main_assumptions\":[\"text\"],\"known_weak_points\":[\"text\"],\"internal_consistency_check\":\"text\"}"
        "}. "
        "The selected_positions array must contain exactly 3 objects and no duplicate tickers. "
        "The total_allocated_dollars field must equal 200."
    )
    human_prompt = (
        f"Date: {analysis_date}\n\n"
        "Eligible Buy tickers:\n\n"
        f"{json.dumps(eligible_tickers)}\n\n"
        "Daily summary:\n\n"
        f"{summary_excerpt}\n\n"
        "Rich stock packets (JSON):\n\n"
        f"{json.dumps(stock_packets, indent=2)}"
    )

    client = create_llm_client(
        provider=provider,
        model=model,
        base_url=backend_url,
        reasoning_effort=reasoning_effort if provider in {"codex_cli", "openai"} else None,
        effort=reasoning_effort if provider in {"claude_code", "anthropic"} else None,
        timeout=90,
    )
    response = client.get_llm().invoke(
        [
            SystemMessage(content=system_prompt),
            HumanMessage(content=human_prompt),
        ]
    )
    content = format_report_content(response.content).strip()
    payload = _extract_json_object_from_text(content)
    if not payload:
        raise ValueError("Decision-grade allocation scorer did not return valid JSON.")
    return verify_decision_grade_allocation(payload, eligible_packets=stock_packets)


def _retry_reasoning_effort(reasoning_effort: str) -> str:
    if reasoning_effort == "xhigh":
        return "high"
    if reasoning_effort == "high":
        return "medium"
    return reasoning_effort


def generate_decision_grade_allocation_with_retry(
    *,
    analysis_date: str,
    daily_summary_markdown: str,
    stock_packets: list[dict],
    provider: str = BATCH_CODEX_PROVIDER,
    backend_url: str = BATCH_CODEX_BACKEND_URL,
    model: str = BATCH_CODEX_MODEL,
    reasoning_effort: str = BATCH_CODEX_FINAL_REASONING_EFFORT,
) -> dict:
    try:
        return generate_decision_grade_allocation(
            analysis_date=analysis_date,
            daily_summary_markdown=daily_summary_markdown,
            stock_packets=stock_packets,
            provider=provider,
            backend_url=backend_url,
            model=model,
            reasoning_effort=reasoning_effort,
        )
    except (subprocess.TimeoutExpired, RuntimeError, ValueError):
        return generate_decision_grade_allocation(
            analysis_date=analysis_date,
            daily_summary_markdown=daily_summary_markdown,
            stock_packets=stock_packets,
            provider=provider,
            backend_url=backend_url,
            model=model,
            reasoning_effort=_retry_reasoning_effort(reasoning_effort),
        )


def _decision_packet_sort_key(packet: dict) -> tuple[int, int, str]:
    stance_rank = _fallback_relative_stance_rank(packet.get("relative_stance", ""))
    support_words = len(
        (
            f"{packet.get('chief_summary', '')} {packet.get('chief_thesis', '')}"
        ).split()
    )
    return (-stance_rank, -support_words, str(packet.get("ticker", "")).strip().upper())


def _allocate_exact_200_for_three(ranked_packets: list[dict]) -> list[int]:
    scores = []
    for idx, packet in enumerate(ranked_packets[:3]):
        stance_rank = _fallback_relative_stance_rank(packet.get("relative_stance", ""))
        base_score = 92 if stance_rank == 2 else 78 if stance_rank == 1 else 64
        scores.append(max(base_score - idx * 4, 1))
    total_score = sum(scores)
    raw_amounts = [score / total_score * 200 for score in scores]
    dollars = [int(amount) for amount in raw_amounts]
    remainder = 200 - sum(dollars)
    order = sorted(
        range(len(dollars)),
        key=lambda idx: (raw_amounts[idx] - dollars[idx], scores[idx]),
        reverse=True,
    )
    for idx in order[:remainder]:
        dollars[idx] += 1
    return dollars


def build_fallback_decision_grade_allocation(*, stock_packets: list[dict], error: Exception) -> dict:
    eligible_packets = [
        packet
        for packet in stock_packets
        if _normalize_summary_action(packet.get("decision") or packet.get("chief_action") or "") == "BUY"
    ]
    if len(eligible_packets) < 3:
        raise ValueError("Fallback allocation requires at least 3 eligible Buy candidates.")

    ranked_packets = sorted(eligible_packets, key=_decision_packet_sort_key)
    selected_packets = ranked_packets[:3]
    rejected_packets = ranked_packets[3:]
    dollars = _allocate_exact_200_for_three(selected_packets)
    fallback_reason = _fallback_allocation_reason(error)
    rejected_names = [
        str(packet.get("ticker", "")).strip().upper()
        for packet in rejected_packets[:3]
        if str(packet.get("ticker", "")).strip()
    ]
    closest_rejected = rejected_names[0] if rejected_names else "the next eligible Buy candidate"

    selected_positions = []
    for packet, allocated_dollars in zip(selected_packets, dollars):
        ticker = str(packet.get("ticker", "")).strip().upper()
        rationale = _fallback_packet_snippet(packet, max_length=160)
        selected_positions.append(
            {
                "ticker": ticker,
                "allocated_dollars": allocated_dollars,
                "weight_pct": round(allocated_dollars / 200 * 100, 1),
                "selection_role": "Fallback-selected eligible Buy candidate",
                "core_thesis": rationale,
                "key_supporting_evidence": rationale,
                "key_disconfirming_evidence": str(packet.get("risk_summary") or "Fallback path did not complete full comparative review.").strip(),
                "entry_quality_assessment": "Fallback memo did not complete the preferred entry-quality committee review.",
                "why_it_beats_closest_rejected_buy": f"{ticker} ranked ahead of {closest_rejected} under the fallback continuity rules; this is not a full committee comparison.",
                "risk_controls_and_invalidation": str(packet.get("risk_summary") or "Review the source run before acting on this fallback allocation.").strip(),
                "confidence": "fallback-limited",
            }
        )

    rejected_close_alternatives = []
    for packet in rejected_packets[:3]:
        ticker = str(packet.get("ticker", "")).strip().upper()
        rejected_close_alternatives.append(
            {
                "ticker": ticker,
                "why_it_was_close": _fallback_packet_snippet(packet, max_length=120),
                "why_it_lost": "It ranked below the selected names under fallback continuity rules.",
                "what_would_have_changed_the_decision": "A successful decision-grade scorer pass is required for a full comparative conclusion.",
            }
        )

    payload = {
        "fallback": {
            "used": True,
            "title": "Fallback Allocation Memo",
            "reason": fallback_reason,
            "limitations": "This continuity artifact is rule-compliant but not the preferred decision-grade committee memo.",
        },
        "executive_decision": {
            "summary": f"Fallback allocation generated because {fallback_reason}.",
            "why_this_portfolio": "The selected names were chosen by deterministic continuity rules from eligible Buy candidates.",
            "weighting_principle": "Fallback weights are score-normalized from relative stance and available supporting detail.",
            "total_allocated_dollars": 200,
        },
        "selected_positions": selected_positions,
        "rejected_close_alternatives": rejected_close_alternatives,
        "portfolio_risks": {
            "top_risks": [
                "Fallback allocation did not complete the preferred decision-grade comparative review.",
                "Review the source reports before relying on this output.",
            ],
            "concentration_notes": "Fallback path does not perform full concentration analysis.",
            "macro_notes": "Use the underlying reports for macro-specific risk details.",
            "timing_notes": "Fallback path does not replace the preferred entry-quality assessment.",
        },
        "decision_quality": {
            "evidence_quality": "fallback-limited",
            "main_assumptions": ["Eligible Buy source reports are internally reliable."],
            "known_weak_points": ["No full committee scorer result was available."],
            "internal_consistency_check": "Fallback selected exactly 3 eligible Buy names and allocated exactly $200.",
        },
    }
    return verify_decision_grade_allocation(payload, eligible_packets=eligible_packets)


def _fallback_allocation_reason(error: Exception) -> str:
    if isinstance(error, subprocess.TimeoutExpired):
        return "the automated final-allocation scorer timed out"
    if isinstance(error, ValueError):
        return "the automated final-allocation scorer returned incomplete structured output"
    if isinstance(error, RuntimeError):
        return "the automated final-allocation scorer process failed"
    return "the automated final-allocation scorer failed"


def _fallback_relative_stance_rank(value: str) -> int:
    normalized = (value or "").strip().lower()
    if normalized == "overweight":
        return 2
    if normalized == "neutral":
        return 1
    return 0


def _fallback_packet_snippet(packet: dict, *, max_length: int = 120) -> str:
    text = (
        (packet.get("chief_thesis") or "").strip()
        or (packet.get("chief_summary") or "").strip()
        or (packet.get("risk_summary") or "").strip()
    )
    if not text:
        return "Limited supporting detail was available in the completed packet."
    if len(text) <= max_length:
        return text
    return text[: max_length - 3].rstrip() + "..."


def _build_fallback_allocation_scores(*, stock_packets: list[dict], error: Exception) -> dict:
    if not stock_packets:
        return {
            "top_three": [],
            "thesis": ["No completed stock packets were available."],
            "risk_notes": ["Hold cash when no same-day research packets are complete."],
        }

    ranked_packets = []
    for packet in stock_packets:
        stance_rank = _fallback_relative_stance_rank(packet.get("relative_stance", ""))
        support_words = len(
            (
                f"{packet.get('chief_summary', '')} {packet.get('chief_thesis', '')}"
            ).split()
        )
        ranked_packets.append(
            {
                "ticker": str(packet.get("ticker", "")).strip().upper(),
                "reported_action": str(packet.get("absolute_action", "Buy")).strip().title() or "Buy",
                "relative_stance": str(packet.get("relative_stance", "")).strip() or "Neutral",
                "summary_snippet": _fallback_packet_snippet(packet),
                "risk_summary": str(packet.get("risk_summary", "")).strip(),
                "stance_rank": stance_rank,
                "support_words": support_words,
            }
        )

    ranked_packets.sort(
        key=lambda item: (
            -item["stance_rank"],
            -item["support_words"],
            item["ticker"],
        )
    )

    top_three = []
    candidate_ranking = []
    rejected_buy_candidates = []

    for idx, item in enumerate(ranked_packets):
        stance_rank = item["stance_rank"]
        base_score = 92 if stance_rank == 2 else 78 if stance_rank == 1 else 64
        score = max(base_score - idx * 4, 1)
        selected = idx < 3
        if stance_rank == 2:
            comparative = "It outranked lower candidates on stronger relative stance and denser report support."
            sizing = "Fallback heuristic favored Buy / Overweight packets with fuller supporting notes."
        elif stance_rank == 1:
            comparative = "It remained investable, but it trailed overweight names on relative stance."
            sizing = "Fallback heuristic kept Buy / Neutral packets below overweight names unless support was clearly stronger."
        else:
            comparative = "It stayed behind names with clearer reported conviction."
            sizing = "Fallback heuristic penalized packets without explicit overweight support."

        candidate_ranking.append(
            {
                "rank": idx + 1,
                "ticker": item["ticker"],
                "reported_action": item["reported_action"],
                "relative_stance": item["relative_stance"],
                "relative_weight_score": score,
                "sizing_evidence": sizing,
                "key_evidence": item["summary_snippet"],
                "allocation_result": "selected pending sizing" if selected else "rejected $0",
            }
        )

        if selected:
            top_three.append(
                {
                    "ticker": item["ticker"],
                    "relative_weight_score": score,
                    "rationale": item["summary_snippet"],
                    "why_better_than_rest": comparative,
                }
            )
        else:
            rejected_buy_candidates.append(
                {
                    "ticker": item["ticker"],
                    "reported_action": item["reported_action"],
                    "relative_stance": item["relative_stance"],
                    "why_it_lost": comparative,
                    "what_would_change_decision": "A stronger relative stance or more differentiated supporting evidence in the report stack.",
                }
            )

    fallback_reason = _fallback_allocation_reason(error)
    thesis = [
        f"Fallback allocation generated because {fallback_reason}.",
        "Ranking used Buy eligibility first, then relative stance, then the amount of supporting detail in each completed packet.",
    ]
    thesis.extend(
        [
            f"{item['ticker']}: {item['summary_snippet']}"
            for item in ranked_packets[:3]
        ]
    )

    risk_notes = [
        "Review the selected names manually if the automated scorer continues to fail; this allocation used deterministic heuristics.",
    ]
    risk_notes.extend(
        [
            f"{item['ticker']}: {item['risk_summary']}"
            for item in ranked_packets[:3]
            if item["risk_summary"]
        ]
    )

    return {
        "top_three": top_three,
        "candidate_ranking": candidate_ranking,
        "rejected_buy_candidates": rejected_buy_candidates,
        "thesis": thesis,
        "risk_notes": risk_notes,
    }


def generate_final_allocation_scores(
    *,
    analysis_date: str,
    daily_summary_markdown: str,
    stock_packets: list[dict],
    provider: str = BATCH_CODEX_PROVIDER,
    backend_url: str = BATCH_CODEX_BACKEND_URL,
    model: str = BATCH_CODEX_MODEL,
    reasoning_effort: str = BATCH_CODEX_FINAL_REASONING_EFFORT,
) -> dict:
    if not stock_packets:
        return {
            "top_three": [],
            "thesis": ["No completed stock packets were available."],
            "risk_notes": ["Hold cash when no same-day research packets are complete."],
        }

    summary_excerpt = daily_summary_markdown.strip()
    if len(summary_excerpt) > 2500:
        summary_excerpt = summary_excerpt[:2500] + "\n\n[truncated]"

    expected_rank_count = len(stock_packets)
    expected_tickers = [str(packet.get("ticker", "")).strip() for packet in stock_packets if str(packet.get("ticker", "")).strip()]

    system_prompt = (
        "You are an educational portfolio ranking assistant for a hypothetical paper portfolio. "
        "This is not investment advice. "
        "Use only the supplied daily summary and compact stock packets. "
        "Each packet already includes the absolute action and relative stance from the report stack. "
        "Treat absolute_action=BUY as the eligibility gate, and use relative_stance plus summary quality to rank the strongest 3 names. "
        "Your job is not just to pick winners; it is to prove why the chosen assets are better than the other investable packets. "
        "You must compare every supplied Buy, Overweight, or investable candidate before final allocation. "
        "No buy-rated candidate may be omitted, even if it receives $0. "
        "For every buy-rated candidate that receives $0, name the asset and explain why the selected assets beat it. "
        "Do not hide rejected candidates behind phrases like 'the rest' or 'other names'; use the ticker symbols. "
        "Base comparisons on reported evidence such as absolute action, relative stance, initial and target sizing, "
        "scenario probabilities, catalysts, risk budgets, technical setup, valuation quality, and thesis confidence. "
        "Choose exactly 3 strongest names from the supplied tickers. "
        "For those 3 only, assign distinct relative_weight_score integers from 1 to 100, where higher means more conviction. "
        "Scores should not be equal unless there is an exceptional reason, and ties should be avoided. "
        "Return JSON only with this exact shape: "
        "{"
        "\"top_three\":[{\"ticker\":\"TICKER\",\"relative_weight_score\":1-100,\"rationale\":\"short reason\",\"why_better_than_rest\":\"short comparison\"}],"
        "\"candidate_ranking\":[{\"rank\":1,\"ticker\":\"TICKER\",\"reported_action\":\"Buy\",\"relative_stance\":\"Overweight/Neutral/etc\",\"relative_weight_score\":1-100,\"sizing_evidence\":\"starter/target/risk evidence\",\"key_evidence\":\"why ranked here\",\"allocation_result\":\"selected $X or rejected $0\"}],"
        "\"rejected_buy_candidates\":[{\"ticker\":\"TICKER\",\"reported_action\":\"Buy\",\"relative_stance\":\"Overweight/Neutral/etc\",\"why_it_lost\":\"specific comparison versus selected names\",\"what_would_change_decision\":\"evidence that would move it into top three\"}],"
        "\"thesis\":[\"bullet\",...],"
        "\"risk_notes\":[\"bullet\",...]"
        "}. "
        "The top_three array must contain exactly 3 tickers and no duplicates. "
        f"The candidate_ranking array must include every supplied Buy, Overweight, or investable candidate in rank order and must include exactly {expected_rank_count} entries. "
        "The rejected_buy_candidates array must include every buy-rated or investable candidate assigned $0. "
        "Keep rationales concise and comparative."
    )
    human_prompt = (
        f"Date: {analysis_date}\n\n"
        "Daily summary:\n\n"
        f"{summary_excerpt}\n\n"
        "Expected ranked ticker set:\n\n"
        f"{json.dumps(expected_tickers)}\n\n"
        "Compact stock packets (JSON):\n\n"
        f"{json.dumps(stock_packets, indent=2)}"
    )

    client = create_llm_client(
        provider=provider,
        model=model,
        base_url=backend_url,
        reasoning_effort=reasoning_effort if provider in {"codex_cli", "openai"} else None,
        effort=reasoning_effort if provider in {"claude_code", "anthropic"} else None,
        timeout=90,
    )
    response = client.get_llm().invoke(
        [
            SystemMessage(content=system_prompt),
            HumanMessage(content=human_prompt),
        ]
    )
    content = format_report_content(response.content).strip()
    payload = _extract_json_object_from_text(content)
    if not payload:
        raise ValueError("Final allocation scorer did not return valid JSON.")
    candidate_ranking = payload.get("candidate_ranking") or []
    returned_tickers = {
        str(item.get("ticker") or item.get("asset") or "").strip()
        for item in candidate_ranking
        if str(item.get("ticker") or item.get("asset") or "").strip()
    }
    expected_ticker_set = set(expected_tickers)
    missing_tickers = sorted(expected_ticker_set - returned_tickers)
    extra_tickers = sorted(returned_tickers - expected_ticker_set)
    if len(candidate_ranking) != expected_rank_count or missing_tickers or extra_tickers:
        raise ValueError(
            "Final allocation scorer returned an incomplete candidate ranking: "
            f"expected {expected_rank_count}, got {len(candidate_ranking)}, "
            f"missing={missing_tickers}, extra={extra_tickers}"
        )
    return payload


def allocate_dollars_from_scores(
    scored_allocations: list[dict],
    *,
    total_dollars: int = 200,
) -> list[dict]:
    normalized = []
    for item in scored_allocations:
        score = item.get("relative_weight_score", item.get("score", 0))
        try:
            score_value = max(float(score), 0.0)
        except (TypeError, ValueError):
            score_value = 0.0
        normalized.append(
            {
                "ticker": str(item.get("ticker", "")).strip(),
                "score": score_value,
                "rationale": str(item.get("rationale", "")).strip(),
                "why_better_than_rest": str(item.get("why_better_than_rest", "")).strip(),
            }
        )

    normalized = [item for item in normalized if item["ticker"]]
    normalized.sort(key=lambda item: (-item["score"], item["ticker"]))
    normalized = normalized[:3]
    total_score = sum(item["score"] for item in normalized)
    if total_score <= 0:
        return [
            {
                "ticker": "CASH",
                "score": 0.0,
                "dollars": total_dollars,
                "weight_pct": 100.0,
                "rationale": "No ticker received a positive conviction score.",
                "why_better_than_rest": "No equity candidate cleared the conviction threshold.",
            }
        ]

    raw_amounts = [item["score"] / total_score * total_dollars for item in normalized]
    floored = [int(amount) for amount in raw_amounts]
    remainder = total_dollars - sum(floored)
    order = sorted(
        range(len(normalized)),
        key=lambda idx: (raw_amounts[idx] - floored[idx], normalized[idx]["score"]),
        reverse=True,
    )
    for idx in order[:remainder]:
        floored[idx] += 1

    allocations = []
    for item, dollars in zip(normalized, floored):
        allocations.append(
            {
                "ticker": item["ticker"],
                "score": item["score"],
                "dollars": dollars,
                "weight_pct": round(dollars / total_dollars * 100, 1),
                "rationale": item["rationale"],
                "why_better_than_rest": item["why_better_than_rest"],
            }
        )

    allocations.sort(key=lambda item: (-item["dollars"], -item["score"], item["ticker"]))
    return allocations


def render_decision_grade_allocation_markdown(payload: dict, *, analysis_date: str) -> str:
    def cell(value) -> str:
        cleaned = str(value or "").replace("\n", " ").replace("|", "/").strip()
        return cleaned or " "

    lines = [f"# Final Allocation: {analysis_date}", ""]

    fallback = payload.get("fallback") or {}
    if fallback.get("used"):
        lines.extend(
            [
                f"## {cell(fallback.get('title') or 'Fallback Allocation Memo')}",
                "",
                f"- Reason: {cell(fallback.get('reason'))}",
                f"- Limitations: {cell(fallback.get('limitations'))}",
                "",
            ]
        )

    executive = payload.get("executive_decision") or {}
    lines.extend(
        [
            "## Executive Decision",
            "",
            f"- Summary: {cell(executive.get('summary'))}",
            f"- Why this portfolio: {cell(executive.get('why_this_portfolio'))}",
            f"- Weighting principle: {cell(executive.get('weighting_principle'))}",
            f"- Total allocated: ${cell(executive.get('total_allocated_dollars'))}",
            "",
            "## Selected Positions and Allocations",
            "",
            "| Asset | Dollars | Weight | Role |",
            "| --- | ---: | ---: | --- |",
        ]
    )
    for position in payload.get("selected_positions") or []:
        lines.append(
            f"| {cell(position.get('ticker'))} | "
            f"${cell(position.get('allocated_dollars'))} | "
            f"{cell(position.get('weight_pct'))}% | "
            f"{cell(position.get('selection_role'))} |"
        )

    lines.extend(
        [
            "",
            "## Why This Portfolio, Not The Next-Best Portfolio",
            "",
            cell(executive.get("why_this_portfolio")),
            "",
            "## Position Memos",
            "",
        ]
    )
    for position in payload.get("selected_positions") or []:
        lines.extend(
            [
                f"### {cell(position.get('ticker'))}",
                "",
                f"- Role: {cell(position.get('selection_role'))}",
                f"- Core thesis: {cell(position.get('core_thesis'))}",
                f"- Supporting evidence: {cell(position.get('key_supporting_evidence'))}",
                f"- Disconfirming evidence: {cell(position.get('key_disconfirming_evidence'))}",
                f"- Entry quality: {cell(position.get('entry_quality_assessment'))}",
                f"- Why it beat a close rejected Buy: {cell(position.get('why_it_beats_closest_rejected_buy'))}",
                f"- Risk controls and invalidation: {cell(position.get('risk_controls_and_invalidation'))}",
                f"- Confidence: {cell(position.get('confidence'))}",
                "",
            ]
        )

    lines.extend(
        [
            "## Closest Rejected Buy Alternatives",
            "",
            "| Asset | Why It Was Close | Why It Lost | What Would Change The Decision |",
            "| --- | --- | --- | --- |",
        ]
    )
    for rejected in payload.get("rejected_close_alternatives") or []:
        lines.append(
            f"| {cell(rejected.get('ticker'))} | "
            f"{cell(rejected.get('why_it_was_close'))} | "
            f"{cell(rejected.get('why_it_lost'))} | "
            f"{cell(rejected.get('what_would_have_changed_the_decision'))} |"
        )

    risks = payload.get("portfolio_risks") or {}
    lines.extend(["", "## Portfolio Risks", ""])
    top_risks = risks.get("top_risks") or []
    if top_risks:
        lines.extend(f"- {cell(risk)}" for risk in top_risks)
    lines.extend(
        [
            f"- Concentration: {cell(risks.get('concentration_notes'))}",
            f"- Macro: {cell(risks.get('macro_notes'))}",
            f"- Timing: {cell(risks.get('timing_notes'))}",
            "",
            "## Decision Quality and Key Assumptions",
            "",
        ]
    )

    quality = payload.get("decision_quality") or {}
    lines.append(f"- Evidence quality: {cell(quality.get('evidence_quality'))}")
    for assumption in quality.get("main_assumptions") or []:
        lines.append(f"- Assumption: {cell(assumption)}")
    for weak_point in quality.get("known_weak_points") or []:
        lines.append(f"- Known weak point: {cell(weak_point)}")
    lines.append(f"- Internal consistency: {cell(quality.get('internal_consistency_check'))}")

    return "\n".join(lines)


def render_final_allocation_markdown(
    *,
    analysis_date: str,
    allocations: list[dict],
    thesis_bullets: list[str],
    risk_bullets: list[str],
    candidate_ranking: Optional[list[dict]] = None,
    rejected_buy_candidates: Optional[list[dict]] = None,
) -> str:
    def cell(value) -> str:
        cleaned = str(value or "").replace("\n", " ").replace("|", "/").strip()
        return cleaned or " "

    selected_dollars = {
        str(item.get("ticker", "")).upper(): item.get("dollars")
        for item in allocations
        if item.get("ticker") and item.get("ticker") != "CASH"
    }

    lines = [
        f"# Final Allocation: {analysis_date}",
        "",
        "## Allocation Table",
        "",
        "| Asset | Dollars | Weight | Why |",
        "| --- | ---: | ---: | --- |",
    ]
    for item in allocations:
        lines.append(
            f"| {cell(item['ticker'])} | ${item['dollars']} | {item['weight_pct']}% | {cell(item['rationale'])} |"
        )

    lines.extend(["", "## Candidate Ranking", ""])
    if candidate_ranking:
        lines.extend(
            [
                "| Rank | Asset | Reported Action | Relative Stance | Numeric Relative Weight Score | Sizing Evidence | Key Evidence | Allocation Result |",
                "| ---: | --- | --- | --- | ---: | --- | --- | --- |",
            ]
        )
        for item in candidate_ranking:
            ticker = item.get("ticker") or item.get("asset")
            dollars = selected_dollars.get(str(ticker or "").upper())
            allocation_result = f"selected ${dollars}" if dollars is not None else item.get("allocation_result")
            lines.append(
                f"| {cell(item.get('rank'))} | {cell(ticker)} | "
                f"{cell(item.get('reported_action'))} | {cell(item.get('relative_stance'))} | "
                f"{cell(item.get('relative_weight_score'))} | "
                f"{cell(item.get('sizing_evidence'))} | {cell(item.get('key_evidence'))} | "
                f"{cell(allocation_result)} |"
            )
    else:
        lines.append("- No candidate ranking was returned.")

    lines.extend(["", "## Thesis", ""])
    if thesis_bullets:
        lines.extend(f"- {cell(bullet)}" for bullet in thesis_bullets)
    else:
        lines.append("- No thesis bullets were returned.")

    lines.extend(["", "## Why These Three Beat The Rest", ""])
    for item in allocations:
        comparison = item.get("why_better_than_rest") or item["rationale"]
        lines.append(f"- **{cell(item['ticker'])}**: {cell(comparison)}")

    lines.extend(["", "## Rejected Buy Candidates", ""])
    if rejected_buy_candidates:
        lines.extend(
            [
                "| Asset | Reported Action | Relative Stance | Why It Lost | What Would Change The Decision |",
                "| --- | --- | --- | --- | --- |",
            ]
        )
        for item in rejected_buy_candidates:
            lines.append(
                f"| {cell(item.get('ticker') or item.get('asset'))} | "
                f"{cell(item.get('reported_action'))} | {cell(item.get('relative_stance'))} | "
                f"{cell(item.get('why_it_lost'))} | {cell(item.get('what_would_change_decision'))} |"
            )
    else:
        lines.append("- No rejected buy candidates were returned.")

    lines.extend(["", "## Risk Notes", ""])
    if risk_bullets:
        lines.extend(f"- {cell(bullet)}" for bullet in risk_bullets)
    else:
        lines.append("- No risk notes were returned.")
    return "\n".join(lines)


def generate_final_allocation_markdown(
    *,
    analysis_date: str,
    daily_summary_markdown: str,
    stock_packets: list[dict],
    provider: str = BATCH_CODEX_PROVIDER,
    backend_url: str = BATCH_CODEX_BACKEND_URL,
    model: str = BATCH_CODEX_MODEL,
    reasoning_effort: str = BATCH_CODEX_FINAL_REASONING_EFFORT,
) -> str:
    try:
        scored = generate_final_allocation_scores(
            analysis_date=analysis_date,
            daily_summary_markdown=daily_summary_markdown,
            stock_packets=stock_packets,
            provider=provider,
            backend_url=backend_url,
            model=model,
            reasoning_effort=reasoning_effort,
        )
    except (subprocess.TimeoutExpired, RuntimeError, ValueError) as exc:
        scored = _build_fallback_allocation_scores(stock_packets=stock_packets, error=exc)
    allocations = allocate_dollars_from_scores(scored.get("top_three", []), total_dollars=200)
    return render_final_allocation_markdown(
        analysis_date=analysis_date,
        allocations=allocations,
        thesis_bullets=[str(item).strip() for item in (scored.get("thesis") or []) if str(item).strip()],
        candidate_ranking=scored.get("candidate_ranking") or [],
        rejected_buy_candidates=scored.get("rejected_buy_candidates") or [],
        risk_bullets=[str(item).strip() for item in (scored.get("risk_notes") or []) if str(item).strip()],
    )


def write_allocation_pdf(
    *,
    markdown_text: str,
    output_path: Path,
    analysis_date: str,
) -> None:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
    from reportlab.lib.units import inch
    from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "AllocationTitle",
        parent=styles["Title"],
        fontName="Helvetica-Bold",
        fontSize=18,
        leading=23,
        spaceAfter=12,
        textColor=colors.HexColor("#102A43"),
    )
    heading_style = ParagraphStyle(
        "AllocationHeading",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=12.5,
        leading=16,
        spaceBefore=10,
        spaceAfter=6,
        textColor=colors.HexColor("#1D4E89"),
    )
    body_style = ParagraphStyle(
        "AllocationBody",
        parent=styles["BodyText"],
        fontName="Helvetica",
        fontSize=10.5,
        leading=14,
        spaceAfter=5,
        textColor=colors.HexColor("#1F2933"),
    )
    bullet_style = ParagraphStyle(
        "AllocationBullet",
        parent=body_style,
        leftIndent=14,
        bulletIndent=2,
    )
    cell_style = ParagraphStyle(
        "AllocationCell",
        parent=body_style,
        fontSize=9.5,
        leading=12,
    )

    doc = SimpleDocTemplate(
        str(output_path),
        pagesize=letter,
        rightMargin=0.7 * inch,
        leftMargin=0.7 * inch,
        topMargin=0.7 * inch,
        bottomMargin=0.7 * inch,
        title=f"Final Allocation {analysis_date}",
    )
    story = [Paragraph(f"Final Allocation - {analysis_date}", title_style)]

    def flush_table(table_lines: list[str]) -> None:
        if not table_lines:
            return
        rows = []
        for line in table_lines:
            if set(line.replace("|", "").replace(" ", "")) <= {"-", ":"}:
                continue
            cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
            rows.append([Paragraph(cell or " ", cell_style) for cell in cells])
        if not rows:
            return
        table = Table(rows, repeatRows=1, hAlign="LEFT")
        table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#D9EAF7")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#102A43")),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#BCCCDC")),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FBFD")]),
                    ("LEFTPADDING", (0, 0), (-1, -1), 6),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                    ("TOPPADDING", (0, 0), (-1, -1), 5),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                ]
            )
        )
        story.append(table)
        story.append(Spacer(1, 10))

    table_lines: list[str] = []
    for raw_line in markdown_text.splitlines():
        line = raw_line.rstrip()
        if line.strip().startswith("|"):
            table_lines.append(line)
            continue
        flush_table(table_lines)
        table_lines = []

        stripped = line.strip()
        if not stripped:
            story.append(Spacer(1, 5))
            continue
        if stripped.startswith("# "):
            continue
        if stripped.startswith("## "):
            story.append(Paragraph(stripped[3:].strip(), heading_style))
            continue
        if stripped.startswith("- "):
            story.append(Paragraph(stripped[2:].strip(), bullet_style, bulletText="•"))
            continue
        story.append(Paragraph(stripped, body_style))
    flush_table(table_lines)

    def add_page_number(canvas, doc_obj):
        canvas.saveState()
        canvas.setFont("Helvetica", 9)
        canvas.setFillColor(colors.HexColor("#486581"))
        canvas.drawRightString(doc_obj.pagesize[0] - 0.7 * inch, 0.45 * inch, f"Page {doc_obj.page}")
        canvas.restoreState()

    doc.build(story, onFirstPage=add_page_number, onLaterPages=add_page_number)


def generate_final_allocation_artifacts(
    *,
    results_dir: str | Path,
    analysis_date: str,
    provider: str = BATCH_CODEX_PROVIDER,
    backend_url: str = BATCH_CODEX_BACKEND_URL,
    model: str = BATCH_CODEX_MODEL,
    reasoning_effort: str = BATCH_CODEX_FINAL_REASONING_EFFORT,
) -> dict:
    results_root = Path(results_dir)
    date_dir = results_root / analysis_date
    summary_path = results_root / "daily_summaries" / analysis_date / "daily_summary.md"
    daily_summary_markdown = summary_path.read_text() if summary_path.exists() else ""
    stock_packets = build_decision_allocation_packets(
        results_dir=results_root,
        analysis_date=analysis_date,
    )

    try:
        allocation_payload = generate_decision_grade_allocation_with_retry(
            analysis_date=analysis_date,
            daily_summary_markdown=daily_summary_markdown,
            stock_packets=stock_packets,
            provider=provider,
            backend_url=backend_url,
            model=model,
            reasoning_effort=reasoning_effort,
        )
    except (subprocess.TimeoutExpired, RuntimeError, ValueError) as exc:
        allocation_payload = build_fallback_decision_grade_allocation(
            stock_packets=stock_packets,
            error=exc,
        )

    markdown_text = render_decision_grade_allocation_markdown(
        allocation_payload,
        analysis_date=analysis_date,
    )
    markdown_path = date_dir / "final_allocation.md"
    markdown_path.write_text(markdown_text)

    pdf_path = date_dir / "final_allocation.pdf"
    write_allocation_pdf(
        markdown_text=markdown_text,
        output_path=pdf_path,
        analysis_date=analysis_date,
    )
    return {
        "markdown_path": str(markdown_path),
        "pdf_path": str(pdf_path),
    }


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
    results_layout: str = "ticker_first",
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
        results_layout=results_layout,
    )
    preflight_error = probe_llm_backend(config)
    if preflight_error:
        final_state, decision = build_degraded_stock_final_state(
            ticker=ticker,
            analysis_date=resolved_analysis_date,
            selected_analysts=resolved_analysts,
            backend_detail=preflight_error,
        )
        started_at = datetime.now().isoformat()
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

    prefetched_context = build_prefetched_stock_context(
        ticker=ticker,
        analysis_date=resolved_analysis_date,
        selected_analysts=resolved_analysts,
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
        init_agent_state["prefetched_context"] = prefetched_context
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
        final_state, decision = graph.propagate(
            ticker,
            resolved_analysis_date,
            prefetched_context=prefetched_context,
        )
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
