from __future__ import annotations

from dataclasses import dataclass, field
import json
from pathlib import Path

from rich.console import Group
from rich.panel import Panel
from rich.progress_bar import ProgressBar
from rich.table import Table
from rich.text import Text


ANALYST_STATUS_ORDER = [
    "macro",
    "market",
    "social",
    "news",
    "fundamentals",
    "factor_rules",
    "valuation",
    "segment",
    "scenario",
    "position_sizing",
]

ANALYST_AGENT_NAMES = {
    "macro": "Macro Analyst",
    "market": "Market Analyst",
    "social": "Social Analyst",
    "news": "News Analyst",
    "fundamentals": "Fundamentals Analyst",
    "factor_rules": "Factor Rules Analyst",
    "valuation": "Valuation Analyst",
    "segment": "Segment Analyst",
    "scenario": "Scenario Analyst",
    "position_sizing": "Position Sizing Analyst",
}

ANALYST_REPORT_MAP = {
    "macro": "macro_report",
    "market": "market_report",
    "social": "sentiment_report",
    "news": "news_report",
    "fundamentals": "fundamentals_report",
    "factor_rules": "factor_rules_report",
    "valuation": "valuation_data",
    "segment": "segment_report",
    "scenario": "scenario_catalyst_report",
    "position_sizing": "position_sizing_report",
}


DEFAULT_FIXED_AGENT_MILESTONES = [
    "Bull Researcher",
    "Bear Researcher",
    "Research Manager",
    "Trader",
    "Aggressive Analyst",
    "Conservative Analyst",
    "Neutral Analyst",
    "Portfolio Manager",
    "Chief Analyst",
]


@dataclass(frozen=True)
class BatchProgressEvent:
    event: str
    agent: str | None = None
    ticker: str | None = None
    analysis_date: str | None = None
    total_milestones: int | None = None
    completed_milestones: int | None = None
    error: str | None = None


@dataclass
class BatchWorkerSlot:
    slot_index: int
    ticker: str | None = None
    status: str = "idle"
    active_agent: str | None = None
    total_milestones: int = 0
    completed_agents: set[str] = field(default_factory=set)
    progress_file: str | None = None
    progress_offset: int = 0
    error: str | None = None

    def assign(self, *, ticker: str, progress_file: str | None = None) -> None:
        self.ticker = ticker
        self.status = "starting"
        self.active_agent = None
        self.total_milestones = 0
        self.completed_agents.clear()
        self.progress_file = progress_file
        self.progress_offset = 0
        self.error = None

    def snapshot(self) -> dict:
        return {
            "slot_index": self.slot_index,
            "ticker": self.ticker,
            "status": self.status,
            "active_agent": self.active_agent,
            "total_milestones": self.total_milestones,
            "completed_agents": sorted(self.completed_agents),
            "progress_fraction": compute_progress_fraction(self),
            "error": self.error,
        }


@dataclass
class BatchDashboardState:
    total_jobs: int
    slots: list[BatchWorkerSlot]
    completed_jobs: int = 0
    failed_jobs: int = 0

    def snapshot(self) -> dict:
        active_jobs = sum(
            1
            for slot in self.slots
            if slot.ticker and slot.status not in {"idle", "completed", "failed"}
        )
        return {
            "total_jobs": self.total_jobs,
            "completed_jobs": self.completed_jobs,
            "failed_jobs": self.failed_jobs,
            "finished_jobs": self.completed_jobs + self.failed_jobs,
            "active_jobs": active_jobs,
            "queued_jobs": max(
                self.total_jobs - self.completed_jobs - self.failed_jobs - active_jobs,
                0,
            ),
            "slots": [slot.snapshot() for slot in self.slots],
        }


class RunProgressTracker:
    def __init__(self, selected_analysts: list[str], *, ticker: str, analysis_date: str):
        self.selected_analysts = [analyst.lower() for analyst in selected_analysts]
        self.ticker = ticker
        self.analysis_date = analysis_date
        self.total_milestones = total_run_milestones(self.selected_analysts)
        self.completed_agents: set[str] = set()
        self.started_agents: set[str] = set()
        self.report_sections = {
            report_key: None
            for analyst_key, report_key in ANALYST_REPORT_MAP.items()
            if analyst_key in self.selected_analysts
        }

    def update_from_chunk(self, chunk: dict) -> list[dict]:
        events: list[dict] = []

        for analyst_key in ANALYST_STATUS_ORDER:
            if analyst_key not in self.selected_analysts:
                continue

            report_key = ANALYST_REPORT_MAP[analyst_key]
            if report_key in chunk and has_meaningful_report_content(chunk[report_key]):
                self.report_sections[report_key] = chunk[report_key]

            if has_meaningful_report_content(self.report_sections.get(report_key)):
                events.extend(self._complete_agent(ANALYST_AGENT_NAMES[analyst_key]))

        debate_state = chunk.get("investment_debate_state") or {}
        if debate_state.get("bull_history", "").strip():
            events.extend(self._complete_agent("Bull Researcher"))
        if debate_state.get("bear_history", "").strip():
            events.extend(self._complete_agent("Bear Researcher"))
        if debate_state.get("judge_decision", "").strip():
            events.extend(self._complete_agent("Research Manager"))

        if has_meaningful_report_content(chunk.get("trader_investment_plan")):
            events.extend(self._complete_agent("Trader"))

        risk_state = chunk.get("risk_debate_state") or {}
        if risk_state.get("aggressive_history", "").strip():
            events.extend(self._complete_agent("Aggressive Analyst"))
        if risk_state.get("conservative_history", "").strip():
            events.extend(self._complete_agent("Conservative Analyst"))
        if risk_state.get("neutral_history", "").strip():
            events.extend(self._complete_agent("Neutral Analyst"))
        if risk_state.get("judge_decision", "").strip():
            events.extend(self._complete_agent("Portfolio Manager"))

        if has_meaningful_report_content(chunk.get("chief_analyst_report")):
            events.extend(self._complete_agent("Chief Analyst"))

        return events

    def build_run_started_event(self) -> dict:
        return self._build_event("run_started")

    def build_run_completed_event(self) -> dict:
        return self._build_event("run_completed")

    def build_run_failed_event(self, error: str) -> dict:
        payload = self._build_event("run_failed")
        payload["error"] = error
        return payload

    def _complete_agent(self, agent: str) -> list[dict]:
        if agent in self.completed_agents:
            return []

        events = []
        if agent not in self.started_agents:
            self.started_agents.add(agent)
            events.append(self._build_event("agent_started", agent=agent))

        self.completed_agents.add(agent)
        events.append(self._build_event("agent_completed", agent=agent))
        return events

    def _build_event(self, event: str, *, agent: str | None = None) -> dict:
        return {
            "event": event,
            "agent": agent,
            "ticker": self.ticker,
            "analysis_date": self.analysis_date,
            "total_milestones": self.total_milestones,
            "completed_milestones": len(self.completed_agents),
        }


def total_run_milestones(selected_analysts: list[str]) -> int:
    return len(selected_analysts) + len(DEFAULT_FIXED_AGENT_MILESTONES)


def compute_progress_fraction(slot: BatchWorkerSlot) -> float:
    if slot.status == "completed":
        return 1.0
    if slot.total_milestones <= 0:
        return 0.0
    return min(len(slot.completed_agents) / slot.total_milestones, 1.0)


def append_progress_event(path, payload: dict) -> None:
    progress_path = Path(path)
    progress_path.parent.mkdir(parents=True, exist_ok=True)
    with progress_path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, sort_keys=True))
        handle.write("\n")


def parse_progress_events(text: str) -> list[BatchProgressEvent]:
    events: list[BatchProgressEvent] = []
    for line in text.splitlines():
        if not line.strip():
            continue
        try:
            payload = json.loads(line)
        except json.JSONDecodeError:
            continue
        events.append(
            BatchProgressEvent(
                event=str(payload.get("event", "")),
                agent=payload.get("agent"),
                ticker=payload.get("ticker"),
                analysis_date=payload.get("analysis_date"),
                total_milestones=payload.get("total_milestones"),
                completed_milestones=payload.get("completed_milestones"),
                error=payload.get("error"),
            )
        )
    return events


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


def read_progress_events(path: str | Path, offset: int = 0) -> tuple[list[BatchProgressEvent], int]:
    progress_path = Path(path)
    if not progress_path.exists():
        return [], offset

    with progress_path.open("r", encoding="utf-8") as handle:
        handle.seek(offset)
        chunk = handle.read()
        new_offset = handle.tell()

    return parse_progress_events(chunk), new_offset


def apply_progress_event(slot: BatchWorkerSlot, event: BatchProgressEvent) -> None:
    if event.total_milestones:
        slot.total_milestones = event.total_milestones

    if event.event == "run_started":
        slot.status = "running"
        return

    if event.event == "agent_started":
        slot.status = "running"
        slot.active_agent = event.agent
        return

    if event.event == "agent_completed":
        if event.agent:
            slot.completed_agents.add(event.agent)
            if slot.active_agent == event.agent:
                slot.active_agent = None
        slot.status = "running"
        return

    if event.event == "run_completed":
        slot.status = "completed"
        slot.active_agent = None
        return

    if event.event == "run_failed":
        slot.status = "failed"
        slot.active_agent = None
        slot.error = event.error


def render_batch_dashboard(state: BatchDashboardState):
    snapshot = state.snapshot()

    summary = Table.grid(expand=True)
    summary.add_column(ratio=1)
    summary.add_row(
        Text(
            " | ".join(
                [
                    f"Done {snapshot['completed_jobs']}/{snapshot['total_jobs']}",
                    f"Failed {snapshot['failed_jobs']}",
                    f"Active {snapshot['active_jobs']}",
                    f"Queued {snapshot['queued_jobs']}",
                ]
            ),
            style="bold cyan",
        )
    )
    summary.add_row(
        ProgressBar(
            total=max(snapshot["total_jobs"], 1),
            completed=snapshot["finished_jobs"],
        )
    )

    worker_group = Group(*(render_worker_slot(slot) for slot in snapshot["slots"]))
    return Group(
        Panel(summary, title="Batch Progress", border_style="cyan"),
        Panel(worker_group, title="Workers", border_style="blue"),
    )


def render_worker_slot(slot_snapshot: dict) -> Panel:
    status = slot_snapshot["status"]
    status_style = {
        "idle": "dim",
        "starting": "yellow",
        "running": "cyan",
        "completed": "green",
        "failed": "red",
    }.get(status, "white")

    title = f"Worker #{slot_snapshot['slot_index']}"
    ticker = slot_snapshot["ticker"] or "Waiting for next job"
    active_agent = slot_snapshot["active_agent"] or "Waiting"
    completed = len(slot_snapshot["completed_agents"])
    total = slot_snapshot["total_milestones"] or 1
    progress_completed = completed
    if status == "completed":
        progress_completed = total

    body = Table.grid(expand=True)
    body.add_column(ratio=1)
    body.add_row(Text(ticker, style="bold white"))
    body.add_row(Text(f"Status: {status}", style=status_style))
    body.add_row(Text(f"Current: {active_agent}", style="white"))
    body.add_row(ProgressBar(total=total, completed=progress_completed))
    body.add_row(
        Text(
            f"Milestones: {completed}/{slot_snapshot['total_milestones'] or 0}",
            style="dim",
        )
    )
    if slot_snapshot.get("error"):
        body.add_row(Text(f"Error: {slot_snapshot['error']}", style="red"))
    return Panel(body, title=title, border_style=status_style)
