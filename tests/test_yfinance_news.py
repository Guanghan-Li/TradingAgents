from tradingagents.dataflows.yfinance_news import get_news_yfinance


def test_get_news_yfinance_accepts_query_search(monkeypatch):
    def fake_fetch_search_news(query, news_count=20, enable_fuzzy_query=True):
        return [
            {
                "title": f"{query} headline",
                "publisher": "Example",
                "link": "https://example.com/story",
            }
        ]

    monkeypatch.setattr("tradingagents.dataflows.yfinance_news.fetch_search_news", fake_fetch_search_news)

    result = get_news_yfinance(
        query="AAPL product launch catalyst",
        start_date="2026-03-01",
        end_date="2026-03-24",
    )

    assert "AAPL product launch catalyst headline" in result


def test_get_news_yfinance_accepts_ticker_lookup(monkeypatch):
    def fake_fetch_ticker_news(ticker, count=20):
        return [
            {
                "title": f"{ticker} headline",
                "publisher": "Example",
                "link": "https://example.com/story",
            }
        ]

    monkeypatch.setattr("tradingagents.dataflows.yfinance_news.fetch_ticker_news", fake_fetch_ticker_news)

    result = get_news_yfinance(
        ticker="AAPL",
        start_date="2026-03-01",
        end_date="2026-03-24",
    )

    assert "AAPL headline" in result
