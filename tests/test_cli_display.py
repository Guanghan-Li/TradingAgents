import unittest

from cli.main import (
    MessageBuffer,
    get_progress_teams,
    normalize_selected_analyst_keys,
    update_analyst_statuses,
)


class CLIDisplayTests(unittest.TestCase):
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
