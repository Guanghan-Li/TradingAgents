from tradingagents.graph.signal_processing import SignalProcessor


def test_signal_processor_extracts_final_transaction_proposal_without_llm():
    processor = SignalProcessor(quick_thinking_llm=None)

    decision = processor.process_signal(
        "Some text\nFINAL TRANSACTION PROPOSAL: **BUY**\nMore text"
    )

    assert decision == "BUY"


def test_signal_processor_extracts_absolute_action_section_without_llm():
    processor = SignalProcessor(quick_thinking_llm=None)

    decision = processor.process_signal(
        "**Absolute Action**: Buy\n\n**Relative Stance**: Overweight\n\nExecutive Summary: Add on weakness."
    )

    assert decision == "BUY"


def test_signal_processor_maps_legacy_overweight_rating_to_buy():
    processor = SignalProcessor(quick_thinking_llm=None)

    decision = processor.process_signal(
        "**Rating**: Overweight\n\nExecutive Summary: Add on weakness."
    )

    assert decision == "BUY"


def test_signal_processor_falls_back_to_hold_when_no_rating_found():
    processor = SignalProcessor(quick_thinking_llm=None)

    decision = processor.process_signal("No explicit decision here.")

    assert decision == "HOLD"
