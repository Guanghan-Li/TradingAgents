## VWO Position Sizing
VWO supports a **moderate** sizing posture. It is a diversified emerging-markets ETF rather than a single-stock idiosyncratic bet, fundamentals are reasonable for the asset class (`P/E ~17`, `P/B ~1.21`, `yield 2.71%`), and price is trading above both the 50-day and 200-day averages while sitting just below the 52-week high. Recent tape also shows a sharp late-March drawdown followed by a strong recovery into mid-April, which argues for participating but not entering at full size immediately.

With spot near `58.21` and ATR near `0.95`, a practical initial risk framework is a stop roughly `2 x ATR` below entry, or about `1.90` points (`~3.3%`) of price risk. That supports a **target weight of 6.0%**, entered as a **starter size of 3.0%**, with a **max portfolio loss budget of 0.75%**. The staggered entry is appropriate because momentum is constructive, but VWO is also near range highs and emerging-markets exposure can gap on macro, FX, and policy headlines.

```json
{
  "conviction": "moderate",
  "target_weight_pct": 6.0,
  "initial_weight_pct": 3.0,
  "max_loss_pct": 0.75,
  "sizing_rationale": "VWO offers diversified emerging-markets exposure with reasonable valuation, positive trend versus 50-day and 200-day averages, and a rebound from the late-March pullback back toward its 52-week high. ATR around 0.95 implies moderate day-to-day volatility, so a staged entry is preferable: start at 3.0% and build toward 6.0% if price action remains constructive. A roughly 2x ATR stop equates to about 3.3% position risk from entry, keeping overall portfolio loss budget contained at 0.75% while acknowledging macro and currency sensitivity typical of emerging-markets ETFs."
}
```