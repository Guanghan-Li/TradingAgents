import json
import subprocess


def test_write_run_artifacts_persists_reports_and_summary(tmp_path):
    from cli.automation import write_run_artifacts

    final_state = {
        "market_report": "Market setup looks constructive.",
        "news_report": "News flow is stable.",
        "investment_plan": "Research manager favors accumulation.",
        "trader_investment_plan": "Start with a small position.",
        "final_trade_decision": "BUY",
        "chief_analyst_report": "## Chief Analyst Summary\n\n### Verdict\n- Absolute Action: Buy\n- Relative Stance: Overweight",
        "chief_analyst_data": {
            "verdict": {
                "absolute_action": "Buy",
                "relative_stance": "Overweight",
                "summary": "Stage in.",
                "thesis": "Quality setup.",
            },
            "catalysts": [{"catalyst": "Earnings", "date_or_window": "2026-04-30"}],
            "tail_risk": {"risk_summary": "Watch support."},
        },
    }
    config = {
        "results_dir": str(tmp_path),
        "llm_provider": "openai",
        "backend_url": "https://api.itgpt.chat/v1",
        "quick_think_llm": "gpt-5.4",
        "deep_think_llm": "gpt-5.4",
        "openai_reasoning_effort": "high",
    }

    summary = write_run_artifacts(
        final_state=final_state,
        ticker="MSFT",
        analysis_date="2026-04-08",
        decision="BUY",
        config=config,
        started_at="2026-04-08T09:30:00",
        ended_at="2026-04-08T10:10:00",
    )

    run_dir = tmp_path / "MSFT" / "2026-04-08"
    report_dir = run_dir / "reports"
    payload = json.loads((run_dir / "run_summary.json").read_text())

    assert summary["ticker"] == "MSFT"
    assert (report_dir / "market_report.md").read_text() == "Market setup looks constructive."
    assert (report_dir / "chief_analyst_report.md").exists()
    assert (run_dir / "complete_report.md").exists()
    assert payload["analysis_date"] == "2026-04-08"
    assert payload["chief_action"] == "Buy"
    assert payload["chief_relative_stance"] == "Overweight"
    assert payload["decision"] == "BUY"
    assert payload["status"] == "completed"


def test_write_run_artifacts_supports_batch_date_first_layout(tmp_path):
    from cli.automation import write_run_artifacts

    final_state = {
        "market_report": "Market setup looks constructive.",
        "chief_analyst_report": "## Chief Analyst Summary\n\n### Verdict\n- Absolute Action: Buy\n- Relative Stance: Overweight",
        "chief_analyst_data": {
            "verdict": {
                "absolute_action": "Buy",
                "relative_stance": "Overweight",
                "summary": "Stage in.",
                "thesis": "Quality setup.",
            }
        },
    }
    config = {
        "results_dir": str(tmp_path / "results_batch"),
        "results_layout": "date_first",
        "llm_provider": "claude_code",
        "backend_url": "claude://local",
        "quick_think_llm": "claude-sonnet-4-6",
        "deep_think_llm": "claude-sonnet-4-6",
        "anthropic_effort": "medium",
    }

    summary = write_run_artifacts(
        final_state=final_state,
        ticker="MSFT",
        analysis_date="2026-04-13",
        decision="BUY",
        config=config,
        started_at="2026-04-13T09:30:00",
        ended_at="2026-04-13T10:10:00",
    )

    run_dir = tmp_path / "results_batch" / "2026-04-13" / "MSFT"
    assert summary["results_dir"] == str(run_dir)
    assert (run_dir / "complete_report.md").exists()
    assert (run_dir / "run_summary.json").exists()
    assert (run_dir / "reports" / "market_report.md").exists()


def test_summarize_runs_for_date_writes_json_and_markdown(tmp_path):
    from cli.automation import summarize_runs_for_date

    for ticker, action, relative, status in [
        ("MSFT", "Buy", "Overweight", "completed"),
        ("NVDA", "Buy", "Neutral", "completed"),
        ("MU", "Sell", "Underweight", "completed"),
        ("TSLA", "", "", "failed"),
    ]:
        run_dir = tmp_path / ticker / "2026-04-08"
        run_dir.mkdir(parents=True)
        (run_dir / "run_summary.json").write_text(
            json.dumps(
                {
                    "ticker": ticker,
                    "analysis_date": "2026-04-08",
                    "status": status,
                    "decision": action.upper() if action else "",
                    "chief_action": action,
                    "chief_relative_stance": relative if status == "completed" else "",
                    "chief_summary": f"{ticker} summary",
                    "risk_summary": f"{ticker} risk",
                }
            )
        )

    result = summarize_runs_for_date(
        results_dir=tmp_path,
        analysis_date="2026-04-08",
    )

    summary_dir = tmp_path / "daily_summaries" / "2026-04-08"
    payload = json.loads((summary_dir / "daily_summary.json").read_text())
    markdown = (summary_dir / "daily_summary.md").read_text()

    assert result["analysis_date"] == "2026-04-08"
    assert payload["counts"]["bullish"] == 2
    assert payload["counts"]["bearish"] == 1
    assert payload["counts"]["failed"] == 1
    assert "Strongest bullish ideas" in markdown
    assert "Bearish or avoid ideas" in markdown
    assert "Failed or incomplete runs" in markdown


def test_summarize_runs_for_date_supports_date_first_layout(tmp_path):
    from cli.automation import summarize_runs_for_date

    for ticker, action, relative, status in [
        ("MSFT", "Buy", "Overweight", "completed"),
        ("NVDA", "Buy", "Neutral", "completed"),
    ]:
        run_dir = tmp_path / "2026-04-13" / ticker
        run_dir.mkdir(parents=True)
        (run_dir / "run_summary.json").write_text(
            json.dumps(
                {
                    "ticker": ticker,
                    "analysis_date": "2026-04-13",
                    "status": status,
                    "decision": action.upper(),
                    "chief_action": action,
                    "chief_relative_stance": relative,
                    "chief_summary": f"{ticker} summary",
                }
            )
        )

    result = summarize_runs_for_date(results_dir=tmp_path, analysis_date="2026-04-13")

    assert result["counts"]["bullish"] == 2


def test_generate_final_allocation_artifacts_writes_markdown_and_pdf(tmp_path, monkeypatch):
    from cli.automation import generate_final_allocation_artifacts

    results_dir = tmp_path / "results_batch"
    date_dir = results_dir / "2026-04-13"

    for ticker in ("AAPL", "MSFT"):
        report_dir = date_dir / ticker / "reports"
        report_dir.mkdir(parents=True)
        (report_dir / "chief_analyst_report.md").write_text(
            f"## Chief Analyst Summary\n\n### Verdict\n- Rating: Buy\n- Summary: Buy {ticker}."
        )
        (date_dir / ticker / "run_summary.json").write_text(
            json.dumps(
                {
                    "ticker": ticker,
                    "analysis_date": "2026-04-13",
                    "status": "completed",
                    "chief_action": "Buy",
                    "chief_relative_stance": "Overweight",
                    "chief_summary": f"Buy {ticker}",
                }
            )
        )

    summary_dir = results_dir / "daily_summaries" / "2026-04-13"
    summary_dir.mkdir(parents=True)
    (summary_dir / "daily_summary.md").write_text("# Daily Summary: 2026-04-13\n\n- AAPL\n- MSFT")

    monkeypatch.setattr(
        "cli.automation.generate_final_allocation_markdown",
        lambda **kwargs: "# Final Allocation\n\n| Asset | Dollars |\n| --- | ---: |\n| AAPL | $120 |\n| MSFT | $80 |",
    )

    def fake_write_allocation_pdf(*, markdown_text, output_path, analysis_date):
        output_path.write_text(f"PDF {analysis_date}\n{markdown_text}")

    monkeypatch.setattr("cli.automation.write_allocation_pdf", fake_write_allocation_pdf)

    result = generate_final_allocation_artifacts(
        results_dir=results_dir,
        analysis_date="2026-04-13",
    )

    assert result["markdown_path"] == str(date_dir / "final_allocation.md")
    assert result["pdf_path"] == str(date_dir / "final_allocation.pdf")
    assert (date_dir / "final_allocation.md").exists()
    assert (date_dir / "final_allocation.pdf").exists()


def test_generate_final_allocation_artifacts_falls_back_after_scorer_timeout(tmp_path, monkeypatch):
    from cli.automation import generate_final_allocation_artifacts

    results_dir = tmp_path / "results_batch"
    date_dir = results_dir / "2026-04-13"

    for ticker, stance in (
        ("AAPL", "Overweight"),
        ("MSFT", "Overweight"),
        ("NVDA", "Neutral"),
        ("AMZN", "Neutral"),
    ):
        report_dir = date_dir / ticker / "reports"
        report_dir.mkdir(parents=True)
        (report_dir / "chief_analyst_report.md").write_text(
            f"## Chief Analyst Summary\n\n### Verdict\n- Rating: Buy\n- Summary: Buy {ticker}."
        )
        (date_dir / ticker / "run_summary.json").write_text(
            json.dumps(
                {
                    "ticker": ticker,
                    "analysis_date": "2026-04-13",
                    "status": "completed",
                    "chief_action": "Buy",
                    "chief_relative_stance": stance,
                    "chief_summary": f"{ticker} summary with clear support.",
                    "chief_thesis": f"{ticker} thesis with differentiated evidence.",
                    "risk_summary": f"{ticker} risk summary.",
                }
            )
        )

    summary_dir = results_dir / "daily_summaries" / "2026-04-13"
    summary_dir.mkdir(parents=True)
    (summary_dir / "daily_summary.md").write_text("# Daily Summary: 2026-04-13\n\n- AAPL\n- MSFT\n- NVDA\n- AMZN")

    class FakeLLM:
        def invoke(self, messages):
            raise subprocess.TimeoutExpired(["codex", "exec"], 180)

    class FakeClient:
        def get_llm(self):
            return FakeLLM()

    monkeypatch.setattr("cli.automation.create_llm_client", lambda **kwargs: FakeClient())

    def fake_write_allocation_pdf(*, markdown_text, output_path, analysis_date):
        output_path.write_text(f"PDF {analysis_date}\n{markdown_text}")

    monkeypatch.setattr("cli.automation.write_allocation_pdf", fake_write_allocation_pdf)

    result = generate_final_allocation_artifacts(
        results_dir=results_dir,
        analysis_date="2026-04-13",
    )

    markdown = (date_dir / "final_allocation.md").read_text()

    assert result["markdown_path"] == str(date_dir / "final_allocation.md")
    assert result["pdf_path"] == str(date_dir / "final_allocation.pdf")
    assert (date_dir / "final_allocation.md").exists()
    assert (date_dir / "final_allocation.pdf").exists()
    assert "Fallback allocation" in markdown
    assert "| AAPL |" in markdown
    assert "| MSFT |" in markdown
    assert "| NVDA |" in markdown


def test_build_allocation_packets_keeps_only_buy_and_overweight(tmp_path):
    from cli.automation import build_allocation_packets

    date_dir = tmp_path / "2026-04-13"
    for ticker, action, relative in [("AAPL", "BUY", "OVERWEIGHT"), ("MSFT", "HOLD", "NEUTRAL"), ("NVDA", "BUY", "OVERWEIGHT")]:
        stock_dir = date_dir / ticker
        stock_dir.mkdir(parents=True)
        (stock_dir / "run_summary.json").write_text(
            json.dumps(
                {
                    "ticker": ticker,
                    "analysis_date": "2026-04-13",
                    "decision": action,
                    "chief_action": action.title(),
                    "chief_relative_stance": relative.title(),
                    "chief_summary": f"{ticker} summary",
                    "chief_thesis": f"{ticker} thesis",
                    "risk_summary": f"{ticker} risk",
                }
            )
        )

    packets = build_allocation_packets(results_dir=tmp_path, analysis_date="2026-04-13")

    assert [packet["ticker"] for packet in packets] == ["AAPL", "NVDA"]


def test_build_decision_allocation_packets_keeps_only_completed_buys_and_collects_rich_fields(tmp_path):
    from cli.automation import build_decision_allocation_packets

    date_dir = tmp_path / "2026-04-16"
    for payload in [
        {
            "ticker": "AMZN",
            "analysis_date": "2026-04-16",
            "status": "completed",
            "decision": "BUY",
            "chief_action": "Buy",
            "chief_relative_stance": "Overweight",
            "chief_summary": "AMZN summary with clear top-line committee context.",
            "chief_thesis": "AMZN thesis with durable retail margin and AWS support.",
            "risk_summary": "AMZN risk is consumer slowdown.",
            "position_sizing": {
                "initial_position_size": "2%",
                "target_position_size": "4%",
                "sizing_rationale": "Scale from starter to target on execution.",
            },
            "scenario_analysis": {
                "base_case": "AWS acceleration supports re-rating.",
                "bull_case": "Retail margins inflect faster than expected.",
                "bear_case": "Consumer demand softens and spend decelerates.",
            },
            "catalysts": [
                {"catalyst": "Earnings", "date_or_window": "2026-04-30"},
            ],
            "invalidation": {
                "condition": "AWS growth stalls",
                "monitoring": "Watch enterprise demand revisions.",
            },
        },
        {
            "ticker": "CRM",
            "analysis_date": "2026-04-16",
            "status": "completed",
            "decision": "HOLD",
            "chief_action": "Hold",
            "chief_relative_stance": "Neutral",
            "chief_summary": "Hold name should be excluded.",
            "chief_thesis": "Hold thesis should be excluded.",
            "risk_summary": "Hold risk should be excluded.",
        },
        {
            "ticker": "MU",
            "analysis_date": "2026-04-16",
            "status": "completed",
            "decision": "BUY",
            "chief_action": "Buy",
            "chief_relative_stance": "Neutral",
            "chief_summary": "MU summary with memory cycle support.",
            "chief_thesis": "MU thesis with improving HBM pricing and demand.",
            "risk_summary": "MU risk is sharper memory price volatility.",
            "position_sizing": {
                "initial_position_size": "1.5%",
                "target_position_size": "3%",
            },
            "scenario_analysis": {
                "base_case": "HBM demand remains firm.",
            },
            "catalysts": [
                {"catalyst": "HBM supply update", "date_or_window": "next quarter"},
            ],
            "invalidation": {
                "condition": "Pricing rolls over",
            },
        },
        {
            "ticker": "NVDA",
            "analysis_date": "2026-04-16",
            "status": "completed",
            "decision": "BUY",
            "chief_action": "Buy",
            "chief_relative_stance": "Overweight",
            "chief_summary": "NVDA summary with strongest AI demand evidence.",
            "chief_thesis": "NVDA thesis with sustained datacenter demand leadership.",
            "risk_summary": "NVDA risk is valuation compression.",
            "position_sizing": {
                "initial_position_size": "3%",
                "target_position_size": "5%",
            },
            "scenario_analysis": {
                "base_case": "Demand stays above supply through the year.",
            },
            "catalysts": [
                {"catalyst": "Product launch cadence", "date_or_window": "H2 2026"},
            ],
            "invalidation": {
                "condition": "Large cloud capex pause",
            },
        },
        {
            "ticker": "SNOW",
            "analysis_date": "2026-04-16",
            "status": "failed",
            "decision": "BUY",
            "chief_action": "Buy",
            "chief_relative_stance": "Overweight",
            "chief_summary": "Failed run should be excluded.",
            "chief_thesis": "Failed thesis should be excluded.",
            "risk_summary": "Failed risk should be excluded.",
        },
        {
            "ticker": "TSLA",
            "analysis_date": "2026-04-15",
            "status": "completed",
            "decision": "BUY",
            "chief_action": "Buy",
            "chief_relative_stance": "Overweight",
            "chief_summary": "Prior-day run should be excluded.",
            "chief_thesis": "Prior-day thesis should be excluded.",
            "risk_summary": "Prior-day risk should be excluded.",
        },
    ]:
        stock_dir = date_dir / payload["ticker"]
        stock_dir.mkdir(parents=True, exist_ok=True)
        (stock_dir / "run_summary.json").write_text(json.dumps(payload))

    prior_day_dir = tmp_path / "2026-04-15" / "TSLA"
    prior_day_dir.mkdir(parents=True)
    (prior_day_dir / "run_summary.json").write_text(
        json.dumps(
            {
                "ticker": "TSLA",
                "analysis_date": "2026-04-15",
                "status": "completed",
                "decision": "BUY",
                "chief_action": "Buy",
                "chief_relative_stance": "Overweight",
                "chief_summary": "Prior-day run should be excluded.",
                "chief_thesis": "Prior-day thesis should be excluded.",
                "risk_summary": "Prior-day risk should be excluded.",
            }
        )
    )

    packets = build_decision_allocation_packets(results_dir=tmp_path, analysis_date="2026-04-16")

    assert [packet["ticker"] for packet in packets] == ["AMZN", "MU", "NVDA"]
    assert packets[0]["chief_summary"]
    assert packets[0]["chief_thesis"]
    assert packets[0]["risk_summary"]
    assert packets[0]["decision"] == "Buy"
    assert packets[0]["relative_stance"] == "Overweight"
    assert packets[0]["position_sizing"]["initial_position_size"] == "2%"
    assert packets[0]["scenario_analysis"]["base_case"]
    assert packets[0]["catalysts"][0]["catalyst"] == "Earnings"
    assert packets[0]["invalidation"]["condition"] == "AWS growth stalls"


def test_generate_final_allocation_scores_prompt_requires_buy_candidate_comparison(monkeypatch):
    from cli.automation import generate_final_allocation_scores

    captured = {}

    class FakeLLM:
        def invoke(self, messages):
            captured["system_prompt"] = messages[0].content
            captured["human_prompt"] = messages[1].content
            return type(
                "Response",
                (),
                {
                    "content": json.dumps(
                        {
                            "top_three": [
                                {
                                    "ticker": "TSM",
                                    "relative_weight_score": 95,
                                    "rationale": "strongest",
                                    "why_better_than_rest": "highest conviction",
                                },
                                {
                                    "ticker": "NVDA",
                                    "relative_weight_score": 90,
                                    "rationale": "second",
                                    "why_better_than_rest": "better sizing",
                                },
                                {
                                    "ticker": "MU",
                                    "relative_weight_score": 85,
                                    "rationale": "third",
                                    "why_better_than_rest": "better current earnings",
                                },
                            ],
                            "candidate_ranking": [
                                {
                                    "rank": 1,
                                    "ticker": "TSM",
                                    "reported_action": "Buy",
                                    "relative_stance": "Overweight",
                                    "relative_weight_score": 95,
                                    "sizing_evidence": "3% starter",
                                    "key_evidence": "strongest",
                                    "allocation_result": "selected $70",
                                },
                                {
                                    "rank": 2,
                                    "ticker": "NVDA",
                                    "reported_action": "Buy",
                                    "relative_stance": "Overweight",
                                    "relative_weight_score": 90,
                                    "sizing_evidence": "3% starter",
                                    "key_evidence": "second",
                                    "allocation_result": "selected $67",
                                },
                                {
                                    "rank": 3,
                                    "ticker": "MU",
                                    "reported_action": "Buy",
                                    "relative_stance": "Overweight",
                                    "relative_weight_score": 85,
                                    "sizing_evidence": "2% starter",
                                    "key_evidence": "third",
                                    "allocation_result": "selected $63",
                                },
                                {
                                    "rank": 4,
                                    "ticker": "MSFT",
                                    "reported_action": "Buy",
                                    "relative_stance": "Neutral",
                                    "relative_weight_score": 65,
                                    "sizing_evidence": "starter",
                                    "key_evidence": "neutral",
                                    "allocation_result": "rejected $0",
                                },
                            ],
                            "rejected_buy_candidates": [],
                            "thesis": [],
                            "risk_notes": [],
                        }
                    )
                },
            )()

    class FakeClient:
        def get_llm(self):
            return FakeLLM()

    monkeypatch.setattr("cli.automation.create_llm_client", lambda **kwargs: FakeClient())

    generate_final_allocation_scores(
        analysis_date="2026-04-15",
        daily_summary_markdown="# Daily Summary\n\nMSFT was a Buy.",
        stock_packets=[
            {"ticker": "TSM", "absolute_action": "Buy", "relative_stance": "Overweight"},
            {"ticker": "NVDA", "absolute_action": "Buy", "relative_stance": "Overweight"},
            {"ticker": "MU", "absolute_action": "Buy", "relative_stance": "Overweight"},
            {"ticker": "MSFT", "absolute_action": "Buy", "relative_stance": "Neutral"},
        ],
    )

    assert "candidate_ranking" in captured["system_prompt"]
    assert "relative_weight_score" in captured["system_prompt"]
    assert "must include exactly 4 entries" in captured["system_prompt"]
    assert "rejected_buy_candidates" in captured["system_prompt"]
    assert "compare every supplied Buy, Overweight, or investable candidate" in captured["system_prompt"]
    assert "No buy-rated candidate may be omitted" in captured["system_prompt"]
    assert "MSFT" in captured["human_prompt"]


def test_allocate_dollars_from_scores_keeps_only_top_three_and_sums_to_200():
    from cli.automation import allocate_dollars_from_scores

    allocations = allocate_dollars_from_scores(
        [
            {"ticker": "AAPL", "relative_weight_score": 92, "rationale": "strong"},
            {"ticker": "MSFT", "relative_weight_score": 61, "rationale": "good"},
            {"ticker": "NVDA", "relative_weight_score": 47, "rationale": "ok"},
            {"ticker": "AMZN", "relative_weight_score": 18, "rationale": "weaker"},
        ],
        total_dollars=200,
    )

    assert len(allocations) == 3
    assert [item["ticker"] for item in allocations] == ["AAPL", "MSFT", "NVDA"]
    assert sum(item["dollars"] for item in allocations) == 200
    assert allocations[0]["ticker"] == "AAPL"
    assert allocations[0]["dollars"] > allocations[1]["dollars"] > allocations[2]["dollars"]


def test_render_final_allocation_markdown_uses_scored_allocations():
    from cli.automation import render_final_allocation_markdown

    markdown = render_final_allocation_markdown(
        analysis_date="2026-04-13",
        allocations=[
            {
                "ticker": "AAPL",
                "score": 92,
                "dollars": 120,
                "weight_pct": 60.0,
                "rationale": "highest conviction",
                "why_better_than_rest": "AAPL had the clearest combination of quality and cleaner risk.",
            },
            {
                "ticker": "MSFT",
                "score": 61,
                "dollars": 80,
                "weight_pct": 40.0,
                "rationale": "second conviction",
                "why_better_than_rest": "MSFT beat the rest on durability and AI monetization quality.",
            },
        ],
        thesis_bullets=["AAPL and MSFT had the strongest research packets."],
        candidate_ranking=[
            {
                "rank": 1,
                "ticker": "AAPL",
                "reported_action": "Buy",
                "relative_stance": "Overweight",
                "relative_weight_score": 92,
                "sizing_evidence": "3% starter",
                "key_evidence": "highest conviction",
                "allocation_result": "selected $36",
            },
            {
                "rank": 3,
                "ticker": "NVDA",
                "reported_action": "Buy",
                "relative_stance": "Neutral",
                "relative_weight_score": 47,
                "sizing_evidence": "1.5% starter",
                "key_evidence": "good but lower conviction",
                "allocation_result": "$0 rejected",
            },
        ],
        rejected_buy_candidates=[
            {
                "ticker": "NVDA",
                "reported_action": "Buy",
                "relative_stance": "Neutral",
                "why_it_lost": "NVDA lagged the selected names on relative stance and sizing.",
                "what_would_change_decision": "A cleaner technical setup and higher target sizing.",
            }
        ],
        risk_bullets=["Concentration risk remains elevated in mega-cap tech."],
    )

    assert "# Final Allocation: 2026-04-13" in markdown
    assert "| AAPL | $120 | 60.0% | highest conviction |" in markdown
    assert "## Candidate Ranking" in markdown
    assert "Numeric Relative Weight Score" in markdown
    assert "| 1 | AAPL | Buy | Overweight | 92 | 3% starter | highest conviction | selected $120 |" in markdown
    assert "selected $120" in markdown
    assert "selected $36" not in markdown
    assert "NVDA lagged the selected names" in markdown
    assert "## Rejected Buy Candidates" in markdown
    assert "## Thesis" in markdown
    assert "## Why These Three Beat The Rest" in markdown
    assert "AAPL had the clearest combination of quality and cleaner risk." in markdown
    assert "## Risk Notes" in markdown
