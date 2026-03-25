from tradingagents.dataflows.yfinance_news import get_news_yfinance


class _FakeSearch:
    def __init__(self, query, news_count=20, enable_fuzzy_query=True):
        self.query = query
        self.news = [
            {
                "title": f"{query} headline",
                "publisher": "Example",
                "link": "https://example.com/story",
            }
        ]


class _FakeTicker:
    def __init__(self, ticker):
        self.ticker = ticker

    def get_news(self, count=20):
        return [
            {
                "title": f"{self.ticker} headline",
                "publisher": "Example",
                "link": "https://example.com/story",
            }
        ]


def test_get_news_yfinance_accepts_query_search(monkeypatch):
    monkeypatch.setattr("tradingagents.dataflows.yfinance_news.yf.Search", _FakeSearch)

    result = get_news_yfinance(
        query="AAPL product launch catalyst",
        start_date="2026-03-01",
        end_date="2026-03-24",
    )

    assert "AAPL product launch catalyst headline" in result


def test_get_news_yfinance_accepts_ticker_lookup(monkeypatch):
    monkeypatch.setattr("tradingagents.dataflows.yfinance_news.yf.Ticker", _FakeTicker)

    result = get_news_yfinance(
        ticker="AAPL",
        start_date="2026-03-01",
        end_date="2026-03-24",
    )

    assert "AAPL headline" in result
