import os


PM_DEFAULT_CONFIG = {
    "project_dir": os.path.abspath(os.path.join(os.path.dirname(__file__), ".")),
    "results_dir": os.getenv("TRADINGAGENTS_RESULTS_DIR", "./results"),
    "data_cache_dir": os.path.join(
        os.path.abspath(os.path.join(os.path.dirname(__file__), ".")),
        "data_cache",
    ),
    "llm_provider": "openai",
    "deep_think_llm": "gpt-5.2",
    "quick_think_llm": "gpt-5-mini",
    "backend_url": "https://api.openai.com/v1",
    "google_thinking_level": None,
    "openai_reasoning_effort": None,
    "anthropic_effort": None,
    "max_debate_rounds": 1,
    "max_risk_discuss_rounds": 1,
    "market_type": "polymarket",
}
