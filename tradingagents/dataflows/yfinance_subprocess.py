from __future__ import annotations

from multiprocessing import get_context
import platform
from queue import Empty
import time
from typing import Any

import yfinance as yf
from yfinance.exceptions import YFRateLimitError


DEFAULT_YFINANCE_TIMEOUT_SECONDS = 30
DEFAULT_YFINANCE_RETRIES = 2


class YahooFinanceWorkerError(RuntimeError):
    """Raised when a subprocess-backed Yahoo Finance fetch fails."""


def _yf_retry(func, max_retries: int = DEFAULT_YFINANCE_RETRIES, base_delay: float = 2.0):
    for attempt in range(max_retries + 1):
        try:
            return func()
        except YFRateLimitError:
            if attempt >= max_retries:
                raise
            time.sleep(base_delay * (2 ** attempt))


def _worker(queue, operation: str, kwargs: dict[str, Any]) -> None:
    try:
        if operation == "ticker_history":
            ticker = yf.Ticker(kwargs["symbol"])
            timeout_seconds = kwargs.get("timeout_seconds", DEFAULT_YFINANCE_TIMEOUT_SECONDS)
            result = _yf_retry(
                lambda: ticker.history(
                    start=kwargs["start"],
                    end=kwargs["end"],
                    timeout=timeout_seconds,
                )
            )
        elif operation == "download":
            payload = dict(kwargs["download_kwargs"])
            timeout_seconds = payload.pop("timeout_seconds", DEFAULT_YFINANCE_TIMEOUT_SECONDS)
            result = _yf_retry(lambda: yf.download(timeout=timeout_seconds, **payload))
        elif operation == "ticker_info":
            result = _yf_retry(lambda: yf.Ticker(kwargs["symbol"]).info)
        elif operation == "ticker_attr":
            ticker = yf.Ticker(kwargs["symbol"])
            result = _yf_retry(lambda: getattr(ticker, kwargs["attr_name"]))
        elif operation == "ticker_news":
            ticker = yf.Ticker(kwargs["symbol"])
            result = _yf_retry(lambda: ticker.get_news(count=kwargs["count"]))
        elif operation == "search_news":
            search = yf.Search(
                query=kwargs["query"],
                news_count=kwargs["news_count"],
                enable_fuzzy_query=kwargs["enable_fuzzy_query"],
            )
            result = _yf_retry(lambda: search.news)
        else:
            raise ValueError(f"Unsupported Yahoo Finance operation: {operation}")

        queue.put(("ok", result))
    except Exception as exc:  # noqa: BLE001
        queue.put(("error", f"{exc.__class__.__name__}: {exc}"))


def _run_in_subprocess(
    operation: str,
    *,
    timeout_seconds: int = DEFAULT_YFINANCE_TIMEOUT_SECONDS,
    **kwargs,
):
    start_method = "fork" if platform.system() != "Windows" else "spawn"
    ctx = get_context(start_method)
    queue = ctx.Queue()
    process = ctx.Process(
        target=_worker,
        args=(queue, operation, kwargs),
        daemon=True,
    )
    process.start()
    process.join(timeout_seconds)

    if process.is_alive():
        process.terminate()
        process.join()
        raise TimeoutError(f"Yahoo Finance operation '{operation}' timed out after {timeout_seconds}s")

    try:
        status, payload = queue.get_nowait()
    except Empty as exc:
        raise YahooFinanceWorkerError(
            f"Yahoo Finance operation '{operation}' exited without returning data."
        ) from exc

    if status == "error":
        raise YahooFinanceWorkerError(payload)

    return payload


def fetch_ticker_history(
    symbol: str,
    *,
    start: str,
    end: str,
    timeout_seconds: int = DEFAULT_YFINANCE_TIMEOUT_SECONDS,
):
    return _run_in_subprocess(
        "ticker_history",
        timeout_seconds=timeout_seconds,
        symbol=symbol.upper(),
        start=start,
        end=end,
    )


def fetch_download_frame(
    symbols,
    timeout_seconds: int = DEFAULT_YFINANCE_TIMEOUT_SECONDS,
    **download_kwargs,
):
    payload = dict(download_kwargs)
    return _run_in_subprocess(
        "download",
        timeout_seconds=timeout_seconds,
        download_kwargs={
            "tickers": symbols,
            **payload,
            "timeout_seconds": timeout_seconds,
        },
    )


def fetch_ticker_info(symbol: str, timeout_seconds: int = DEFAULT_YFINANCE_TIMEOUT_SECONDS):
    return _run_in_subprocess(
        "ticker_info",
        timeout_seconds=timeout_seconds,
        symbol=symbol.upper(),
    )


def fetch_ticker_attr(
    symbol: str,
    attr_name: str,
    timeout_seconds: int = DEFAULT_YFINANCE_TIMEOUT_SECONDS,
):
    return _run_in_subprocess(
        "ticker_attr",
        timeout_seconds=timeout_seconds,
        symbol=symbol.upper(),
        attr_name=attr_name,
    )


def fetch_ticker_news(
    symbol: str,
    *,
    count: int = 20,
    timeout_seconds: int = DEFAULT_YFINANCE_TIMEOUT_SECONDS,
):
    return _run_in_subprocess(
        "ticker_news",
        timeout_seconds=timeout_seconds,
        symbol=symbol.upper(),
        count=count,
    )


def fetch_search_news(
    query: str,
    *,
    news_count: int = 20,
    enable_fuzzy_query: bool = True,
    timeout_seconds: int = DEFAULT_YFINANCE_TIMEOUT_SECONDS,
):
    return _run_in_subprocess(
        "search_news",
        timeout_seconds=timeout_seconds,
        query=query,
        news_count=news_count,
        enable_fuzzy_query=enable_fuzzy_query,
    )
