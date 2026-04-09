from tradingagents.prediction_market.dataflows.polymarket import _cache_key


def test_cache_key_is_deterministic_and_uses_strong_hash():
    first = _cache_key("gamma", endpoint="/markets/1", params={"slug": "msft"})
    second = _cache_key("gamma", endpoint="/markets/1", params={"slug": "msft"})
    different = _cache_key("gamma", endpoint="/markets/2", params={"slug": "nvda"})

    assert first == second
    assert first != different
    assert len(first) == 64
