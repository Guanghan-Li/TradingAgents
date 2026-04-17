import csv
from io import StringIO

from langchain_core.messages import BaseMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from tradingagents.agents.utils.agent_utils import (
    add_educational_use_context,
    build_instrument_context,
    get_indicators,
    get_stock_data,
)
from tradingagents.dataflows.macro_regime import classify_macro_regime, format_macro_report

MARKET_RECENT_PRICE_ROWS = 5
MARKET_RECENT_INDICATOR_POINTS = 5


def _merge_macro_context(upstream_macro_report: str, macro_regime_report: str) -> str:
    macro_report = macro_regime_report
    if not upstream_macro_report:
        return macro_report

    return (
        f"{upstream_macro_report.strip()}\n\n## Medium-Term Macro Regime Overlay\n\n"
        f"{macro_regime_report}"
    )


def _safe_float(value: str) -> float | None:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _format_pct_change(start: float | None, end: float | None) -> str:
    if start in (None, 0) or end is None:
        return "N/A"
    return f"{((end - start) / start) * 100:+.2f}%"


def _compress_stock_data_message(content: str) -> str:
    if not content.startswith("# Stock data for "):
        return content

    _, _, csv_payload = content.partition("\n\n")
    rows = list(csv.DictReader(StringIO(csv_payload)))
    if not rows:
        return content

    latest = rows[-1]
    oldest = rows[0]
    latest_close = _safe_float(latest.get("Close"))
    oldest_close = _safe_float(oldest.get("Close"))
    window_high = max(
        (value for value in (_safe_float(row.get("High")) for row in rows) if value is not None),
        default=None,
    )
    window_low = min(
        (value for value in (_safe_float(row.get("Low")) for row in rows) if value is not None),
        default=None,
    )
    recent_rows = rows[-MARKET_RECENT_PRICE_ROWS:]
    recent_preview = "\n".join(
        f"{row['Date']}: close={row.get('Close', 'N/A')}, high={row.get('High', 'N/A')}, "
        f"low={row.get('Low', 'N/A')}, volume={row.get('Volume', 'N/A')}"
        for row in recent_rows
    )

    return (
        f"{content.splitlines()[0]}\n"
        f"## Market data summary for analyst context\n"
        f"- Window start close ({oldest['Date']}): {oldest.get('Close', 'N/A')}\n"
        f"- Latest close ({latest['Date']}): {latest.get('Close', 'N/A')}\n"
        f"- Close change over provided window: {_format_pct_change(oldest_close, latest_close)}\n"
        f"- Window high: {window_high if window_high is not None else 'N/A'}\n"
        f"- Window low: {window_low if window_low is not None else 'N/A'}\n"
        f"- Recent {len(recent_rows)} trading rows:\n{recent_preview}"
    )


def _compress_indicator_message(content: str) -> str:
    if not content.startswith("## ") or " values from " not in content:
        return content

    lines = [line.strip() for line in content.splitlines()]
    header = lines[0]
    try:
        indicator_name = header.split()[1]
    except IndexError:
        return content

    data_points: list[tuple[str, str]] = []
    description_lines: list[str] = []
    in_description = False
    for line in lines[1:]:
        if not line:
            continue
        if in_description:
            description_lines.append(line)
            continue
        if ": " in line and line[:4].isdigit():
            date_str, value = line.split(": ", 1)
            data_points.append((date_str, value))
            continue
        if not line.startswith("## Showing latest"):
            in_description = True
            description_lines.append(line)

    if not data_points:
        return content

    valid_points = [(date_str, value) for date_str, value in data_points if "N/A" not in value]
    recent_points = valid_points[:MARKET_RECENT_INDICATOR_POINTS] or data_points[:MARKET_RECENT_INDICATOR_POINTS]
    latest_value = recent_points[0][1]
    previous_value = recent_points[1][1] if len(recent_points) > 1 else None
    latest_float = _safe_float(latest_value)
    previous_float = _safe_float(previous_value) if previous_value is not None else None

    trend = "flat"
    if latest_float is not None and previous_float is not None:
        if latest_float > previous_float:
            trend = "up"
        elif latest_float < previous_float:
            trend = "down"

    recent_preview = "\n".join(f"- {date_str}: {value}" for date_str, value in recent_points)
    description = " ".join(description_lines).strip()

    return (
        f"## {indicator_name} summary for analyst context\n"
        f"- Latest valid reading: {recent_points[0][0]} = {latest_value}\n"
        f"- Short-term direction: {trend}\n"
        f"- Recent {len(recent_points)} points:\n{recent_preview}\n"
        f"- Reference: {description}"
    )


def _compress_market_context_messages(messages):
    compressed_messages = []
    for message in messages:
        if isinstance(message, tuple):
            compressed_messages.append(message)
            continue

        if not isinstance(message, BaseMessage) or not isinstance(message.content, str):
            compressed_messages.append(message)
            continue

        compressed_content = _compress_indicator_message(
            _compress_stock_data_message(message.content)
        )
        compressed_messages.append(message.model_copy(update={"content": compressed_content}))

    return compressed_messages


def create_market_analyst(llm):

    def market_analyst_node(state):
        current_date = state["trade_date"]
        instrument_context = build_instrument_context(state["company_of_interest"])
        prefetched_context = (state.get("prefetched_context") or {}).get("market", "").strip()
        macro_regime_report = format_macro_report(classify_macro_regime(current_date))
        upstream_macro_report = state.get("macro_report", "")
        macro_report = _merge_macro_context(upstream_macro_report, macro_regime_report)

        tools = [
            get_stock_data,
            get_indicators,
        ]

        # Static analyst prompt text; Bandit can misread the word "select" as SQL.
        system_message = """You are a trading assistant tasked with analyzing financial markets. Your role is to select the **most relevant indicators** for a given market condition or trading strategy from the following list. The goal is to choose up to **8 indicators** that provide complementary insights without redundancy. Categories and each category's indicators are:

Moving Averages:
- close_50_sma: 50 SMA: A medium-term trend indicator. Usage: Identify trend direction and serve as dynamic support/resistance. Tips: It lags price; combine with faster indicators for timely signals.
- close_200_sma: 200 SMA: A long-term trend benchmark. Usage: Confirm overall market trend and identify golden/death cross setups. Tips: It reacts slowly; best for strategic trend confirmation rather than frequent trading entries.
- close_10_ema: 10 EMA: A responsive short-term average. Usage: Capture quick shifts in momentum and potential entry points. Tips: Prone to noise in choppy markets; use alongside longer averages for filtering false signals.

MACD Related:
- macd: MACD: Computes momentum via differences of EMAs. Usage: Look for crossovers and divergence as signals of trend changes. Tips: Confirm with other indicators in low-volatility or sideways markets.
- macds: MACD Signal: An EMA smoothing of the MACD line. Usage: Use crossovers with the MACD line to trigger trades. Tips: Should be part of a broader strategy to avoid false positives.
- macdh: MACD Histogram: Shows the gap between the MACD line and its signal. Usage: Visualize momentum strength and spot divergence early. Tips: Can be volatile; complement with additional filters in fast-moving markets.

Momentum Indicators:
- rsi: RSI: Measures momentum to flag overbought/oversold conditions. Usage: Apply 70/30 thresholds and watch for divergence to signal reversals. Tips: In strong trends, RSI may remain extreme; always cross-check with trend analysis.

Volatility Indicators:
- boll: Bollinger Middle: A 20 SMA serving as the basis for Bollinger Bands. Usage: Acts as a dynamic benchmark for price movement. Tips: Combine with the upper and lower bands to effectively spot breakouts or reversals.
- boll_ub: Bollinger Upper Band: Typically 2 standard deviations above the middle line. Usage: Signals potential overbought conditions and breakout zones. Tips: Confirm signals with other tools; prices may ride the band in strong trends.
- boll_lb: Bollinger Lower Band: Typically 2 standard deviations below the middle line. Usage: Indicates potential oversold conditions. Tips: Use additional analysis to avoid false reversal signals.
- atr: ATR: Averages true range to measure volatility. Usage: Set stop-loss levels and adjust position sizes based on current market volatility. Tips: It's a reactive measure, so use it as part of a broader risk management strategy.

Volume-Based Indicators:
- vwma: VWMA: A moving average weighted by volume. Usage: Confirm trends by integrating price action with volume data. Tips: Watch for skewed results from volume spikes; use in combination with other volume analyses.

- Select indicators that provide diverse and complementary information. Avoid redundancy (e.g., do not select both rsi and stochrsi). Also briefly explain why they are suitable for the given market context. When you tool call, please use the exact name of the indicators provided above as they are defined parameters, otherwise your call will fail. Please make sure to call get_stock_data first to retrieve the CSV that is needed to generate indicators. Then use get_indicators with the specific indicator names. Write a very detailed and nuanced report of the trends you observe. Provide specific, actionable insights with supporting evidence to help traders make informed decisions."""  # nosec
        system_message = add_educational_use_context(system_message)
        system_message += f"\n\nUse this macro regime context to frame the technical read:\n{macro_report}"
        system_message += """ Make sure to append a Markdown table at the end of the report to organize key points in the report, organized and easy to read."""

        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "You are a helpful AI assistant, collaborating with other assistants."
                    " Use the provided tools to progress towards answering the question."
                    " If you are unable to fully answer, that's OK; another assistant with different tools"
                    " will help where you left off. Execute what you can to make progress."
                    " If you or any other assistant has the FINAL TRANSACTION PROPOSAL: **BUY/HOLD/SELL** or deliverable,"
                    " prefix your response with FINAL TRANSACTION PROPOSAL: **BUY/HOLD/SELL** so the team knows to stop."
                    " You have access to the following tools: {tool_names}.\n{system_message}"
                    "For your reference, the current date is {current_date}. {instrument_context}",
                ),
                MessagesPlaceholder(variable_name="messages"),
            ]
        )

        prompt = prompt.partial(system_message=system_message)
        prompt = prompt.partial(tool_names=", ".join([tool.name for tool in tools]))
        prompt = prompt.partial(current_date=current_date)
        prompt = prompt.partial(instrument_context=instrument_context)

        if prefetched_context:
            prompt = prompt.partial(
                system_message=system_message
                + f"\n\nUse this prefetched live market context as your primary evidence.\n\n{prefetched_context}"
            )
            chain = prompt | llm
            result = chain.invoke(state["messages"])
        else:
            chain = prompt | llm.bind_tools(tools)
            result = chain.invoke(_compress_market_context_messages(state["messages"]))

        report = ""

        if len(result.tool_calls) == 0:
            report = result.content

        return {
            "messages": [result],
            "market_report": report,
        }

    return market_analyst_node
