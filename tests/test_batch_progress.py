import pytest
from rich.console import Console

from cli.batch_progress import (
    DEFAULT_FIXED_AGENT_MILESTONES,
    BatchWorkerSlot,
    apply_progress_event,
    BatchProgressEvent,
    compute_progress_fraction,
    parse_progress_events,
    render_worker_slot,
    total_run_milestones,
)


def test_total_run_milestones_counts_selected_plus_fixed_agents():
    assert total_run_milestones(["market", "news"]) == 2 + len(
        DEFAULT_FIXED_AGENT_MILESTONES
    )


def test_parse_progress_events_skips_malformed_lines():
    events = parse_progress_events(
        '{"event":"agent_completed","agent":"Trader"}\n'
        '{"event":"run_failed","error":"Claude CLI failed"}\n'
        'not-json\n'
    )

    assert [event.event for event in events] == ["agent_completed", "run_failed"]
    assert events[1].error == "Claude CLI failed"


def test_compute_progress_fraction_uses_completed_agent_count():
    slot = BatchWorkerSlot(
        slot_index=1,
        ticker="MSFT",
        total_milestones=20,
        completed_agents={"Trader", "Chief Analyst"},
    )

    assert compute_progress_fraction(slot) == pytest.approx(0.10)


def test_apply_progress_event_stores_run_failure_error():
    slot = BatchWorkerSlot(slot_index=1, ticker="MSFT")

    apply_progress_event(
        slot,
        BatchProgressEvent(event="run_failed", error="Claude CLI failed with exit code 1"),
    )

    assert slot.status == "failed"
    assert slot.error == "Claude CLI failed with exit code 1"


def test_render_worker_slot_includes_error_detail():
    panel = render_worker_slot(
        {
            "slot_index": 1,
            "ticker": "MSFT",
            "status": "failed",
            "active_agent": None,
            "completed_agents": ["Macro Analyst"],
            "total_milestones": 19,
            "progress_fraction": 0.05,
            "error": "Claude CLI failed with exit code 1",
        }
    )

    console = Console(record=True, width=120)
    console.print(panel)
    rendered = console.export_text()
    assert "Claude CLI failed with exit code 1" in rendered
