import json


def test_write_run_artifacts_persists_reports_and_summary(tmp_path):
    from cli.automation import write_run_artifacts

    final_state = {
        "market_report": "Market setup looks constructive.",
        "news_report": "News flow is stable.",
        "investment_plan": "Research manager favors accumulation.",
        "trader_investment_plan": "Start with a small position.",
        "final_trade_decision": "BUY",
        "chief_analyst_report": "## Chief Analyst Summary\n\n### Verdict\n- Rating: Overweight",
        "chief_analyst_data": {
            "verdict": {
                "rating": "Overweight",
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
    assert payload["chief_rating"] == "Overweight"
    assert payload["decision"] == "BUY"
    assert payload["status"] == "completed"


def test_summarize_runs_for_date_writes_json_and_markdown(tmp_path):
    from cli.automation import summarize_runs_for_date

    for ticker, rating, status in [
        ("MSFT", "Overweight", "completed"),
        ("NVDA", "Buy", "completed"),
        ("MU", "Sell", "completed"),
        ("TSLA", "", "failed"),
    ]:
        run_dir = tmp_path / ticker / "2026-04-08"
        run_dir.mkdir(parents=True)
        (run_dir / "run_summary.json").write_text(
            json.dumps(
                {
                    "ticker": ticker,
                    "analysis_date": "2026-04-08",
                    "status": status,
                    "decision": rating.upper() if rating else "",
                    "chief_rating": rating,
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
