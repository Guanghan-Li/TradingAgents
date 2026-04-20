## MSFT Position Sizing
MSFT supports a **medium-high conviction** size, but not a full-risk allocation yet. Fundamentals remain strong: very high margins, ROE near 34%, positive forward EPS growth, and a reasonable forward P/E for a mega-cap quality compounder. Price action also improved materially, with shares rebounding from the late-March low near **356.77** to **420.26** on 2026-04-16, now above the **50-day average (391.9)**.

The main constraint is trend quality at the higher timeframe: MSFT is still below its **200-day average (472.7)** after a sharp drawdown from the 52-week high, so this looks more like a recovery trend than a fully re-established uptrend. With **ATR near 9.75**, daily volatility is about **2.3%** of spot; a practical stop is roughly **1.75 to 2.0 ATR** below entry, which argues for a measured starter.

Suggested sizing plan:
- **Target size:** **4.0%** portfolio weight
- **Starter size:** **2.0%** portfolio weight
- **Max loss budget:** **0.75%** of portfolio capital
- **Risk logic:** Start half-sized, then add only if MSFT holds the recent breakout area and volatility stays controlled. Keep the stop wide enough to respect ATR, rather than forcing a larger size with a tight stop.

```json
{
  "conviction": "medium-high",
  "target_weight_pct": 4.0,
  "initial_weight_pct": 2.0,
  "max_loss_pct": 0.75,
  "sizing_rationale": "MSFT combines strong large-cap fundamentals with improving short-term momentum, but the stock remains below its 200-day average after a meaningful correction, so sizing should be constructive rather than aggressive. Current ATR near 9.75 implies moderate absolute volatility, supporting a staged entry with an initial 2.0% weight and a 4.0% target if price confirms. A 0.75% max portfolio loss budget keeps downside contained while allowing room for an ATR-based stop."
}
```