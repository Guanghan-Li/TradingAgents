#!/usr/bin/env python3

import argparse
import os
import sys
from datetime import date
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent
DEFAULT_ENV_PYTHON = Path.home() / "anaconda3" / "envs" / "tradingagents" / "bin" / "python"


def resolve_target_python() -> Path:
    override = os.environ.get("TRADINGAGENTS_PYTHON")
    if override:
        return Path(override).expanduser()
    return DEFAULT_ENV_PYTHON


def ensure_runtime_python(argv: list[str] | None = None) -> None:
    argv = argv if argv is not None else sys.argv[1:]
    target_python = resolve_target_python()

    if not target_python.exists():
        raise SystemExit(
            f"TradingAgents Python not found at {target_python}. "
            "Create the conda env first or set TRADINGAGENTS_PYTHON."
        )

    if Path(sys.executable).resolve() != target_python.resolve():
        os.execv(str(target_python), [str(target_python), str(Path(__file__).resolve()), *argv])


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run TradingAgents against api.itgpt.chat with gpt-5.4 defaults."
    )
    parser.add_argument("--ticker", default="AAPL", help="Ticker symbol to analyze.")
    parser.add_argument(
        "--date",
        dest="date",
        default=None,
        help="Analysis date in YYYY-MM-DD format. Defaults to today.",
    )
    parser.add_argument(
        "--analyst",
        dest="analysts",
        action="append",
        help="Analyst to include. Repeat to add more. Defaults to: market",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable TradingAgents debug mode.",
    )
    parser.add_argument(
        "--max-debate-rounds",
        type=int,
        default=1,
        help="Number of investment debate rounds.",
    )
    parser.add_argument(
        "--max-risk-discuss-rounds",
        type=int,
        default=1,
        help="Number of risk discussion rounds.",
    )
    args = parser.parse_args(argv)
    args.analysts = args.analysts or ["market"]
    return args


def build_config(
    *,
    max_debate_rounds: int = 1,
    max_risk_discuss_rounds: int = 1,
) -> dict:
    from tradingagents.default_config import DEFAULT_CONFIG

    config = DEFAULT_CONFIG.copy()
    config.update(
        {
            "llm_provider": "openai",
            "backend_url": "https://api.itgpt.chat/v1",
            "deep_think_llm": "gpt-5.4",
            "quick_think_llm": "gpt-5.4",
            "openai_reasoning_effort": "xhigh",
            "max_debate_rounds": max_debate_rounds,
            "max_risk_discuss_rounds": max_risk_discuss_rounds,
        }
    )
    return config


def run_analysis(args: argparse.Namespace) -> str:
    from tradingagents.env import load_project_dotenv
    from tradingagents.graph.trading_graph import TradingAgentsGraph

    load_project_dotenv(start_dir=REPO_ROOT)

    config = build_config(
        max_debate_rounds=args.max_debate_rounds,
        max_risk_discuss_rounds=args.max_risk_discuss_rounds,
    )
    analysis_date = args.date or date.today().isoformat()

    graph = TradingAgentsGraph(
        selected_analysts=args.analysts,
        debug=args.debug,
        config=config,
    )
    _, decision = graph.propagate(args.ticker, analysis_date)
    return decision


def main(argv: list[str] | None = None) -> int:
    ensure_runtime_python(argv)
    args = parse_args(argv)
    decision = run_analysis(args)
    print(decision)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
