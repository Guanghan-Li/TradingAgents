import unittest

from cli.main import MessageBuffer, get_progress_teams


class CLIDisplayTests(unittest.TestCase):
    def test_macro_report_updates_current_report_without_key_error(self):
        message_buffer = MessageBuffer()
        message_buffer.init_for_analysis(["macro"])

        message_buffer.update_report_section("macro_report", "Macro body")

        self.assertEqual(message_buffer.current_report, "### Macro Analysis\nMacro body")

    def test_progress_teams_include_macro_and_chief_when_active(self):
        message_buffer = MessageBuffer()
        message_buffer.init_for_analysis(["market", "social", "news", "fundamentals", "macro"])

        teams = get_progress_teams(message_buffer.agent_status)

        self.assertEqual(
            teams["Analyst Team"],
            [
                "Market Analyst",
                "Social Analyst",
                "News Analyst",
                "Fundamentals Analyst",
                "Macro Analyst",
            ],
        )
        self.assertEqual(
            teams["Portfolio Management"],
            ["Portfolio Manager", "Chief Analyst"],
        )


if __name__ == "__main__":
    unittest.main()
