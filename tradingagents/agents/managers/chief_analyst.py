import re

from tradingagents.agents.utils.agent_states import build_chief_analyst_data_defaults


PORTFOLIO_MANAGER_SECTIONS = [
    "Rating",
    "Executive Summary",
    "Investment Thesis",
]


def _section_heading_pattern() -> re.Pattern[str]:
    section_union = "|".join(re.escape(section) for section in PORTFOLIO_MANAGER_SECTIONS)
    return re.compile(
        rf"^\s*(?:\d+\.\s*)?(?:\*\*(?P<label>{section_union})\*\*|(?P<plain>{section_union}))\s*(?::\s*(?P<inline>.*?))?\s*$",
        re.IGNORECASE | re.MULTILINE,
    )


def _extract_section_body(text: str, label: str) -> str:
    matches = list(_section_heading_pattern().finditer(text or ""))
    for index, match in enumerate(matches):
        matched_label = match.group("label") or match.group("plain") or ""
        if matched_label.lower() != label.lower():
            continue

        inline = (match.group("inline") or "").strip()
        section_end = matches[index + 1].start() if index + 1 < len(matches) else len(text or "")
        trailing = (text or "")[match.end():section_end].strip()

        if inline and trailing:
            return f"{inline}\n\n{trailing}".strip()
        if inline:
            return inline
        return trailing
    return ""


def _extract_section(text: str, label: str) -> str:
    return _extract_section_body(text, label)


def _extract_rating(text: str) -> str:
    rating_body = _extract_section_body(text, "Rating")
    if not rating_body:
        return ""
    return rating_body.splitlines()[0].strip().strip("*").strip()


def _scenario_fair_value_map(scenario_catalyst_data: dict) -> dict:
    fair_value = {
        "bull_case": "",
        "base_case": "",
        "bear_case": "",
    }
    scenario_map = scenario_catalyst_data.get("scenario_map", [])
    for scenario in scenario_map:
        scenario_name = str(scenario.get("name", "")).strip().lower()
        valuation_implication = scenario.get("valuation_implication", "")
        if scenario_name in {"bull", "base", "bear"} and valuation_implication:
            fair_value[f"{scenario_name}_case"] = valuation_implication
    return fair_value


def _variant_perception(segment_data: dict) -> dict:
    business_segments = [
        segment["segment"]
        for segment in segment_data.get("business_unit_decomposition", [])
        if isinstance(segment, dict) and segment.get("segment")
    ]
    value_drivers = [
        driver["driver"]
        for driver in segment_data.get("value_driver_map", [])
        if isinstance(driver, dict) and driver.get("driver")
    ]
    return {
        "business_segments": business_segments,
        "value_drivers": value_drivers,
    }


def _format_chief_analyst_report(chief_analyst_data: dict) -> str:
    verdict = chief_analyst_data["verdict"]
    fair_value = chief_analyst_data["fair_value"]
    execution = chief_analyst_data["execution"]
    tail_risk = chief_analyst_data["tail_risk"]
    variant = chief_analyst_data["variant_perception"]
    catalysts = chief_analyst_data["catalysts"]

    fair_value_lines = [
        f"- Bull case: {fair_value.get('bull_case', 'Not provided') or 'Not provided'}",
        f"- Base case: {fair_value.get('base_case', 'Not provided') or 'Not provided'}",
        f"- Bear case: {fair_value.get('bear_case', 'Not provided') or 'Not provided'}",
    ]
    catalyst_lines = [
        f"- {item['date_or_window']}: {item['catalyst']} ({item['expected_impact']})"
        for item in catalysts
    ] or ["- None captured"]
    risk_lines = [
        f"- {item['trigger']} ({item.get('severity', 'unspecified')})"
        for item in tail_risk["invalidation_triggers"]
    ] or ["- None captured"]
    segment_line = ", ".join(variant["business_segments"]) or "None captured"
    driver_line = ", ".join(variant["value_drivers"]) or "None captured"

    return "\n".join(
        [
            "## Chief Analyst Summary",
            "",
            "### Verdict",
            f"- Rating: {verdict['rating']}",
            f"- Summary: {verdict['summary']}",
            f"- Thesis: {verdict['thesis']}",
            "",
            "### Fair Value",
            *fair_value_lines,
            "",
            "### Catalysts",
            *catalyst_lines,
            "",
            "### Execution",
            f"- Research plan: {execution['research_plan']}",
            f"- Trader plan: {execution['trader_plan']}",
            f"- Portfolio manager guidance: {execution['portfolio_manager_guidance']}",
            "",
            "### Tail Risk",
            f"- Risk summary: {tail_risk['risk_summary']}",
            *risk_lines,
            "",
            "### Variant Perception",
            f"- Business segments: {segment_line}",
            f"- Value drivers: {driver_line}",
        ]
    )


def create_chief_analyst(llm, memory=None):
    def chief_analyst_node(state) -> dict:
        _ = llm
        _ = memory

        final_trade_decision = state.get("final_trade_decision", "")
        risk_debate_state = state.get("risk_debate_state", {})
        segment_data = state.get("segment_data", {})
        scenario_catalyst_data = state.get("scenario_catalyst_data", {})

        chief_analyst_data = build_chief_analyst_data_defaults(
            ticker=state.get("company_of_interest", ""),
            analysis_date=state.get("trade_date", ""),
        )
        chief_analyst_data["verdict"] = {
            "rating": _extract_rating(final_trade_decision),
            "summary": _extract_section(final_trade_decision, "Executive Summary"),
            "thesis": _extract_section(final_trade_decision, "Investment Thesis"),
        }
        chief_analyst_data["fair_value"] = _scenario_fair_value_map(
            scenario_catalyst_data
        )
        chief_analyst_data["catalysts"] = [
            {
                "catalyst": catalyst.get("catalyst", ""),
                "date_or_window": catalyst.get("date_or_window", ""),
                "expected_impact": catalyst.get("expected_impact", ""),
            }
            for catalyst in scenario_catalyst_data.get("dated_catalyst_map", [])
            if isinstance(catalyst, dict)
        ]
        chief_analyst_data["execution"] = {
            "research_plan": state.get("investment_plan", ""),
            "trader_plan": state.get("trader_investment_plan", ""),
            "portfolio_manager_guidance": chief_analyst_data["verdict"]["summary"],
        }
        chief_analyst_data["tail_risk"] = {
            "risk_summary": risk_debate_state.get("judge_decision", ""),
            "invalidation_triggers": [
                {
                    "trigger": trigger.get("trigger", ""),
                    "severity": trigger.get("severity", ""),
                }
                for trigger in scenario_catalyst_data.get("invalidation_triggers", [])
                if isinstance(trigger, dict)
            ],
        }
        chief_analyst_data["variant_perception"] = _variant_perception(segment_data)

        return {
            "chief_analyst_data": chief_analyst_data,
            "chief_analyst_report": _format_chief_analyst_report(chief_analyst_data),
        }

    return chief_analyst_node
