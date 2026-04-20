from unittest.mock import patch

import pandas as pd


def test_get_fundamentals_uses_subprocess_info_fetch(monkeypatch):
    from tradingagents.dataflows import y_finance

    monkeypatch.setattr(
        y_finance,
        "fetch_ticker_info",
        lambda symbol, timeout_seconds=30: {
            "longName": "Microsoft Corp",
            "sector": "Technology",
            "marketCap": 123,
        },
    )

    report = y_finance.get_fundamentals("MSFT")

    assert "Company Fundamentals for MSFT" in report
    assert "Name: Microsoft Corp" in report
    assert "Sector: Technology" in report


def test_get_news_yfinance_uses_subprocess_ticker_news_fetch(monkeypatch):
    from tradingagents.dataflows import yfinance_news

    monkeypatch.setattr(
        yfinance_news,
        "fetch_ticker_news",
        lambda ticker, count=20, timeout_seconds=30: [
            {
                "content": {
                    "title": "MSFT headline",
                    "summary": "MSFT summary",
                    "provider": {"displayName": "Example"},
                    "canonicalUrl": {"url": "https://example.test"},
                    "pubDate": "2026-04-10T12:00:00Z",
                }
            }
        ],
    )

    report = yfinance_news.get_news_yfinance(
        ticker="MSFT",
        start_date="2026-04-09",
        end_date="2026-04-11",
    )

    assert "MSFT headline" in report
    assert "MSFT summary" in report


def test_get_sector_peers_uses_subprocess_info_fetch(monkeypatch):
    from tradingagents.dataflows import peer_comparison

    monkeypatch.setattr(
        peer_comparison,
        "fetch_ticker_info",
        lambda ticker, timeout_seconds=30: {"sector": "Technology"},
    )

    sector_display, sector_key, peers = peer_comparison.get_sector_peers("MSFT")

    assert sector_display == "Technology"
    assert sector_key == "technology"
    assert "AAPL" in peers


def test_fetch_download_frame_returns_dataframe():
    from tradingagents.dataflows.yfinance_subprocess import fetch_download_frame

    with patch(
        "tradingagents.dataflows.yfinance_subprocess._run_in_subprocess",
        return_value=pd.DataFrame({"Close": [1.0]}),
    ) as mock_run:
        frame = fetch_download_frame(["AAPL"], period="1mo", timeout_seconds=1)

    assert not frame.empty
    assert list(frame["Close"]) == [1.0]
    mock_run.assert_called_once()
