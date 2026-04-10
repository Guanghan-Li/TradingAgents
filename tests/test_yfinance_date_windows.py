from unittest.mock import patch
from datetime import datetime, timedelta

import pandas as pd


def _make_ohlcv_frame(dates: list[str]) -> pd.DataFrame:
    index = pd.to_datetime(dates)
    return pd.DataFrame(
        {
            "Open": [100.0 + idx for idx, _ in enumerate(index)],
            "High": [101.0 + idx for idx, _ in enumerate(index)],
            "Low": [99.0 + idx for idx, _ in enumerate(index)],
            "Close": [100.5 + idx for idx, _ in enumerate(index)],
            "Adj Close": [100.5 + idx for idx, _ in enumerate(index)],
            "Volume": [1_000_000 + idx for idx, _ in enumerate(index)],
        },
        index=index,
    )


def test_get_yfin_data_online_treats_end_date_as_inclusive():
    calls = []
    history = _make_ohlcv_frame(["2026-03-25", "2026-03-26"])

    def fake_history(**kwargs):
        calls.append(kwargs)
        return history

    with patch("tradingagents.dataflows.y_finance.yf.Ticker") as mock_ticker:
        mock_ticker.return_value.history.side_effect = fake_history

        from tradingagents.dataflows.y_finance import get_YFin_data_online

        report = get_YFin_data_online("AAPL", "2026-03-25", "2026-03-26")

    assert calls[0]["start"] == "2026-03-25"
    assert calls[0]["end"] == "2026-03-27"
    assert "2026-03-26" in report


def test_get_yfin_data_online_truncates_large_history_for_llm_output():
    history = _make_ohlcv_frame(
        pd.date_range("2025-01-01", periods=100, freq="B").strftime("%Y-%m-%d").tolist()
    )

    with patch("tradingagents.dataflows.y_finance.yf.Ticker") as mock_ticker:
        mock_ticker.return_value.history.return_value = history

        from tradingagents.dataflows.y_finance import get_YFin_data_online

        report = get_YFin_data_online("AAPL", "2025-01-01", "2025-05-31")

    assert "# Displaying latest 40 records for LLM context" in report
    assert "\n2025-01-01," not in report
    assert "\n2025-05-20," in report


def test_stockstats_indicator_window_truncates_old_history():
    from tradingagents.dataflows import y_finance as yf_module

    curr_date = datetime(2026, 4, 9)
    indicator_data = {
        (curr_date - timedelta(days=offset)).strftime("%Y-%m-%d"): str(offset)
        for offset in range(40)
    }

    with patch.object(yf_module, "_get_stock_stats_bulk", return_value=indicator_data):
        report = yf_module.get_stock_stats_indicators_window(
            "AAPL",
            "rsi",
            "2026-04-09",
            40,
        )

    assert "## Showing latest 20 dates for LLM context" in report
    assert "2026-04-09: 0" in report
    assert "2026-03-01: 39" not in report


def test_stockstats_uses_next_day_exclusive_end_for_requested_trade_date(tmp_path):
    calls = []
    history = _make_ohlcv_frame(["2026-03-25", "2026-03-26"]).reset_index(names="Date")

    def fake_download(symbol, **kwargs):
        calls.append(kwargs)
        return history.set_index("Date")

    with patch(
        "tradingagents.dataflows.stockstats_utils.get_config",
        return_value={"data_cache_dir": str(tmp_path)},
    ), patch(
        "tradingagents.dataflows.stockstats_utils.os.path.exists",
        return_value=False,
    ), patch(
        "tradingagents.dataflows.stockstats_utils.pd.Timestamp.today",
        return_value=pd.Timestamp("2026-03-26"),
    ), patch(
        "tradingagents.dataflows.stockstats_utils.yf.download",
        side_effect=fake_download,
    ):
        from tradingagents.dataflows.stockstats_utils import StockstatsUtils

        value = StockstatsUtils.get_stock_stats("AAPL", "close", "2026-03-26")

    assert calls[0]["end"] == "2026-03-27"
    assert value == 101.5
