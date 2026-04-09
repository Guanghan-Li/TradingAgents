import pytest

from cli.batch_progress import (
    DEFAULT_FIXED_AGENT_MILESTONES,
    BatchWorkerSlot,
    compute_progress_fraction,
    parse_progress_events,
    total_run_milestones,
)


def test_total_run_milestones_counts_selected_plus_fixed_agents():
    assert total_run_milestones(["market", "news"]) == 2 + len(
        DEFAULT_FIXED_AGENT_MILESTONES
    )


def test_parse_progress_events_skips_malformed_lines():
    events = parse_progress_events(
        '{"event":"agent_completed","agent":"Trader"}\nnot-json\n'
    )

    assert [event.event for event in events] == ["agent_completed"]


def test_compute_progress_fraction_uses_completed_agent_count():
    slot = BatchWorkerSlot(
        slot_index=1,
        ticker="MSFT",
        total_milestones=20,
        completed_agents={"Trader", "Chief Analyst"},
    )

    assert compute_progress_fraction(slot) == pytest.approx(0.10)
