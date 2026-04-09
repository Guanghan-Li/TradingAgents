from __future__ import annotations

from dataclasses import dataclass, field
import json


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


@dataclass
class BatchWorkerSlot:
    slot_index: int
    ticker: str | None = None
    total_milestones: int = 0
    completed_agents: set[str] = field(default_factory=set)


def total_run_milestones(selected_analysts: list[str]) -> int:
    return len(selected_analysts) + len(DEFAULT_FIXED_AGENT_MILESTONES)


def compute_progress_fraction(slot: BatchWorkerSlot) -> float:
    if slot.total_milestones <= 0:
        return 0.0
    return min(len(slot.completed_agents) / slot.total_milestones, 1.0)


def append_progress_event(path, payload: dict) -> None:
    with open(path, "a") as handle:
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
            )
        )
    return events
