import json

from tradingagents.dataflows.alpha_vantage_common import _make_api_request


def test_make_api_request_passes_timeout(monkeypatch):
    captured = {}

    class FakeResponse:
        text = json.dumps({"ok": True})

        def raise_for_status(self):
            return None

    def fake_get(url, params, timeout):
        captured["url"] = url
        captured["params"] = params
        captured["timeout"] = timeout
        return FakeResponse()

    monkeypatch.setattr(
        "tradingagents.dataflows.alpha_vantage_common.get_api_key",
        lambda: "test-key",
    )
    monkeypatch.setattr(
        "tradingagents.dataflows.alpha_vantage_common.requests.get",
        fake_get,
    )

    response = _make_api_request("TIME_SERIES_DAILY", {"symbol": "MSFT"})

    assert response == json.dumps({"ok": True})
    assert captured["timeout"] == 30
    assert captured["params"]["function"] == "TIME_SERIES_DAILY"
    assert captured["params"]["apikey"] == "test-key"
