from run_itgpt import build_config, parse_args


def test_parse_args_defaults():
    args = parse_args([])

    assert args.ticker == "AAPL"
    assert args.date is None
    assert args.analysts == ["market"]
    assert args.debug is False


def test_build_config_uses_itgpt_gpt54_defaults():
    config = build_config()

    assert config["llm_provider"] == "openai"
    assert config["backend_url"] == "https://api.itgpt.chat/v1"
    assert config["deep_think_llm"] == "gpt-5.4"
    assert config["quick_think_llm"] == "gpt-5-mini"
    assert config["openai_reasoning_effort"] == "xhigh"
    assert config["max_debate_rounds"] == 1
    assert config["max_risk_discuss_rounds"] == 1
    assert config["llm_routing"]["default"]["model"] == "gpt-5-mini"
    assert config["llm_routing"]["roles"]["chief_analyst"]["model"] == "gpt-5.4"
