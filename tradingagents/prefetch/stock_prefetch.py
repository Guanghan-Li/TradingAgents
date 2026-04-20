from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta
import logging
import time

from tradingagents.dataflows.interface import route_to_vendor
from tradingagents.dataflows.peer_comparison import (
    get_peer_comparison_report,
    get_sector_relative_report,
)


MARKET_INDICATORS = [
    ("close_10_ema", 90),
    ("close_50_sma", 180),
    ("close_200_sma", 250),
    ("macd", 90),
    ("rsi", 60),
    ("boll_ub", 60),
    ("boll_lb", 60),
    ("atr", 60),
]
logger = logging.getLogger(__name__)


def _safe_fetch(name: str, fetcher):
    start = time.time()
    try:
        result = fetcher()
        logger.info("prefetch[%s] ok in %.2fs", name, time.time() - start)
        return result
    except Exception as exc:  # noqa: BLE001
        logger.warning("prefetch[%s] failed in %.2fs: %s", name, time.time() - start, exc)
        return f"Error during prefetch: {exc}"


def _date_window(curr_date: str, days_back: int) -> tuple[str, str]:
    current_dt = datetime.strptime(curr_date, "%Y-%m-%d")
    start_date = (current_dt - timedelta(days=days_back)).strftime("%Y-%m-%d")
    return start_date, curr_date


def build_prefetched_stock_context(
    *,
    ticker: str,
    analysis_date: str,
    selected_analysts: list[str],
) -> dict[str, str]:
    selected = set(selected_analysts)
    prefetched: dict[str, str] = {}

    company_news_start, company_news_end = _date_window(analysis_date, 10)
    sizing_start, sizing_end = _date_window(analysis_date, 60)

    jobs = {}
    with ThreadPoolExecutor(max_workers=8) as executor:
        if {"market", "position_sizing"} & selected:
            jobs["stock_data"] = executor.submit(
                _safe_fetch,
                "stock_data",
                lambda: route_to_vendor(
                    "get_stock_data",
                    symbol=ticker,
                    start_date=sizing_start,
                    end_date=sizing_end,
                ),
            )
        if {"market", "position_sizing"} & selected:
            jobs["atr"] = executor.submit(
                _safe_fetch,
                "atr",
                lambda: route_to_vendor(
                    "get_indicators",
                    symbol=ticker,
                    indicator="atr",
                    curr_date=analysis_date,
                    look_back_days=60,
                ),
            )
        if "market" in selected:
            for indicator, lookback in MARKET_INDICATORS:
                jobs[f"indicator:{indicator}"] = executor.submit(
                    _safe_fetch,
                    f"indicator:{indicator}",
                    lambda ind=indicator, lb=lookback: route_to_vendor(
                        "get_indicators",
                        symbol=ticker,
                        indicator=ind,
                        curr_date=analysis_date,
                        look_back_days=lb,
                    ),
                )
        if {"fundamentals", "valuation", "segment", "scenario", "position_sizing"} & selected:
            jobs["fundamentals"] = executor.submit(
                _safe_fetch,
                "fundamentals",
                lambda: route_to_vendor(
                    "get_fundamentals",
                    ticker=ticker,
                    curr_date=analysis_date,
                ),
            )
        if {"fundamentals", "segment"} & selected:
            jobs["income_statement"] = executor.submit(
                _safe_fetch,
                "income_statement",
                lambda: route_to_vendor(
                    "get_income_statement",
                    ticker=ticker,
                    freq="quarterly",
                    curr_date=analysis_date,
                ),
            )
            jobs["balance_sheet"] = executor.submit(
                _safe_fetch,
                "balance_sheet",
                lambda: route_to_vendor(
                    "get_balance_sheet",
                    ticker=ticker,
                    freq="quarterly",
                    curr_date=analysis_date,
                ),
            )
            jobs["cashflow"] = executor.submit(
                _safe_fetch,
                "cashflow",
                lambda: route_to_vendor(
                    "get_cashflow",
                    ticker=ticker,
                    freq="quarterly",
                    curr_date=analysis_date,
                ),
            )
        if {"social", "news", "segment", "scenario"} & selected:
            jobs["company_news"] = executor.submit(
                _safe_fetch,
                "company_news",
                lambda: route_to_vendor(
                    "get_news",
                    query=ticker,
                    start_date=company_news_start,
                    end_date=company_news_end,
                ),
            )
        if "news" in selected:
            jobs["global_news"] = executor.submit(
                _safe_fetch,
                "global_news",
                lambda: route_to_vendor(
                    "get_global_news",
                    curr_date=analysis_date,
                    look_back_days=7,
                    limit=10,
                ),
            )
        if {"macro", "scenario"} & selected:
            jobs["macro_indicators"] = executor.submit(
                _safe_fetch,
                "macro_indicators",
                lambda: route_to_vendor(
                    "get_economic_indicators",
                    curr_date=analysis_date,
                    lookback_days=120,
                ),
            )
            jobs["yield_curve"] = executor.submit(
                _safe_fetch,
                "yield_curve",
                lambda: route_to_vendor(
                    "get_yield_curve",
                    curr_date=analysis_date,
                ),
            )
            jobs["fed_calendar"] = executor.submit(
                _safe_fetch,
                "fed_calendar",
                lambda: route_to_vendor(
                    "get_fed_calendar",
                    curr_date=analysis_date,
                ),
            )
        if "fundamentals" in selected:
            jobs["peer_report"] = executor.submit(
                _safe_fetch,
                "peer_report",
                lambda: get_peer_comparison_report(ticker, analysis_date),
            )
            jobs["sector_report"] = executor.submit(
                _safe_fetch,
                "sector_report",
                lambda: get_sector_relative_report(ticker, analysis_date),
            )

        results = {name: future.result() for name, future in jobs.items()}

    if "macro" in selected:
        prefetched["macro"] = "\n\n".join(
            [
                "## Prefetched macro context",
                results.get("macro_indicators", ""),
                results.get("yield_curve", ""),
                results.get("fed_calendar", ""),
            ]
        )
    if "market" in selected:
        indicator_sections = [results.get(f"indicator:{indicator}", "") for indicator, _ in MARKET_INDICATORS]
        prefetched["market"] = "\n\n".join(
            [
                "## Prefetched market context",
                results.get("stock_data", ""),
                *indicator_sections,
                prefetched.get("macro", ""),
            ]
        )
    if "social" in selected:
        prefetched["social"] = "\n\n".join(
            [
                "## Prefetched social/news context",
                results.get("company_news", ""),
            ]
        )
    if "news" in selected:
        prefetched["news"] = "\n\n".join(
            [
                "## Prefetched news context",
                results.get("company_news", ""),
                results.get("global_news", ""),
            ]
        )
    if "fundamentals" in selected:
        prefetched["fundamentals"] = "\n\n".join(
            [
                "## Prefetched fundamentals context",
                results.get("fundamentals", ""),
                results.get("income_statement", ""),
                results.get("balance_sheet", ""),
                results.get("cashflow", ""),
                results.get("peer_report", ""),
                results.get("sector_report", ""),
                prefetched.get("macro", ""),
            ]
        )
    if "valuation" in selected:
        prefetched["valuation"] = "\n\n".join(
            ["## Prefetched valuation context", results.get("fundamentals", "")]
        )
    if "segment" in selected:
        prefetched["segment"] = "\n\n".join(
            [
                "## Prefetched segment context",
                results.get("fundamentals", ""),
                results.get("income_statement", ""),
                results.get("company_news", ""),
            ]
        )
    if "scenario" in selected:
        prefetched["scenario"] = "\n\n".join(
            [
                "## Prefetched scenario context",
                results.get("fundamentals", ""),
                results.get("company_news", ""),
                prefetched.get("macro", ""),
            ]
        )
    if "position_sizing" in selected:
        prefetched["position_sizing"] = "\n\n".join(
            [
                "## Prefetched position sizing context",
                results.get("fundamentals", ""),
                results.get("stock_data", ""),
                results.get("atr", ""),
            ]
        )

    return prefetched
