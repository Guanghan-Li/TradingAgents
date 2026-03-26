from unittest.mock import patch

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
