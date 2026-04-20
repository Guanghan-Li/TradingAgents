import unittest
from pathlib import Path

from cli.main import (
    MessageBuffer,
    _extract_task_name_from_traceback,
    build_run_log_paths,
    get_progress_teams,
    normalize_selected_analyst_keys,
    prepare_run_output_dirs,
    update_analyst_statuses,
)


class CLIDisplayTests(unittest.TestCase):
    def test_extract_task_name_from_traceback_prefers_langgraph_note(self):
        trace_text = (
            "Traceback ...\n"
            "InternalServerError: Gateway time-out\n"
            "During task with name 'Macro Analyst' and id 'abc123'\n"
        )

        self.assertEqual(_extract_task_name_from_traceback(trace_text), "Macro Analyst")

    def test_build_run_log_paths_includes_timestamp_in_filenames(self):
        paths = build_run_log_paths(
            Path("/tmp/results/SOFI/2026-04-09"),
            "20260410_033012",
        )

        self.assertEqual(
            paths["message_tool_log"],
            Path("/tmp/results/SOFI/2026-04-09/message_tool_20260410_033012.log"),
        )
        self.assertEqual(
            paths["error_log"],
            Path("/tmp/results/SOFI/2026-04-09/error_20260410_033012.log"),
        )

    def test_prepare_run_output_dirs_clears_stale_reports_but_keeps_logs(self):
        base_dir = Path(self.id().replace(".", "_"))
        results_root = Path("/tmp") / base_dir
        results_dir = results_root / "MSFT" / "2026-04-12"
        report_dir = results_dir / "reports"
        report_dir.mkdir(parents=True, exist_ok=True)
        (report_dir / "macro_report.md").write_text("stale macro")
        (results_dir / "complete_report.md").write_text("stale complete")
        (results_dir / "run_summary.json").write_text("{}")
        old_log = results_dir / "message_tool_20260412_140000.log"
        old_log.write_text("keep me")

        prepared_results_dir, prepared_report_dir, log_paths = prepare_run_output_dirs(
            results_root,
            "MSFT",
            "2026-04-12",
            "20260412_150000",
        )

        self.assertEqual(prepared_results_dir, results_dir)
        self.assertEqual(prepared_report_dir, report_dir)
        self.assertFalse((report_dir / "macro_report.md").exists())
        self.assertFalse((results_dir / "complete_report.md").exists())
        self.assertFalse((results_dir / "run_summary.json").exists())
        self.assertTrue(old_log.exists())
        self.assertEqual(
            log_paths["message_tool_log"],
            results_dir / "message_tool_20260412_150000.log",
        )

    def test_normalize_selected_analyst_keys_returns_values_in_cli_order(self):
        selected = {
            "macro",
            "market",
            "news",
        }

        self.assertEqual(
            normalize_selected_analyst_keys(selected),
            ["market", "news", "macro"],
        )

    def test_macro_report_updates_current_report_without_key_error(self):
        message_buffer = MessageBuffer()
        message_buffer.init_for_analysis(["macro"])

        message_buffer.update_report_section("macro_report", "Macro body")

        self.assertEqual(message_buffer.current_report, "### Macro Analysis\nMacro body")

    def test_progress_teams_include_all_stock_analysts_and_chief_when_active(self):
        message_buffer = MessageBuffer()
        message_buffer.init_for_analysis(
            [
                "market",
                "social",
                "news",
                "fundamentals",
                "macro",
                "factor_rules",
                "valuation",
                "segment",
                "scenario",
                "position_sizing",
            ]
        )

        teams = get_progress_teams(message_buffer.agent_status)

        self.assertEqual(
            teams["Analyst Team"],
            [
                "Market Analyst",
                "Social Analyst",
                "News Analyst",
                "Fundamentals Analyst",
                "Macro Analyst",
                "Factor Rules Analyst",
                "Valuation Analyst",
                "Segment Analyst",
                "Scenario Analyst",
                "Position Sizing Analyst",
            ],
        )
        self.assertEqual(
            teams["Portfolio Management"],
            ["Portfolio Manager", "Chief Analyst"],
        )

    def test_structured_valuation_data_is_rendered_in_current_report(self):
        message_buffer = MessageBuffer()
        message_buffer.init_for_analysis(["valuation"])

        message_buffer.update_report_section(
            "valuation_data",
            {
                "fair_value_range": {"low": 150.0, "high": 180.0},
                "primary_method": "dcf",
            },
        )

        self.assertIn("### Valuation Summary", message_buffer.current_report)
        self.assertIn('"primary_method": "dcf"', message_buffer.current_report)

    def test_default_valuation_data_does_not_mark_analyst_complete(self):
        message_buffer = MessageBuffer()
        message_buffer.init_for_analysis(["valuation"])

        update_analyst_statuses(
            message_buffer,
            {
                "valuation_data": {
                    "fair_value_range": {"low": None, "high": None},
                    "expected_return_pct": None,
                    "primary_method": "",
                    "thesis": "",
                }
            },
        )

        self.assertEqual(message_buffer.agent_status["Valuation Analyst"], "in_progress")
        self.assertIsNone(message_buffer.current_report)


if __name__ == "__main__":
    unittest.main()
