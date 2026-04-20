FINAL TRANSACTION PROPOSAL: **BUY**

### AVGO Position Sizing Summary
AVGO supports a moderately aggressive long size, but not a full one. Fundamentals are strong: ~36.6% net margin, ~44.9% operating margin, robust free cash flow, and forward P/E (~22.1) is far more reasonable than trailing P/E (~77.8), which suggests earnings growth is doing real work. Price action is also constructive, with AVGO rebounding from the late-March low near 293 to 398.47 on 2026-04-16, but the stock is now materially extended above both the 50-day (~329.9) and 200-day (~331.9) averages.

Given that setup, the sizing plan should respect momentum but account for extension and volatility. ATR is about 12.6, or roughly 3.2% of spot, so a practical stop is around 2 ATR below entry, near 373, which implies about 6% to 6.5% downside from current levels. That supports a `target_weight_pct` of **4.0%**, entered with an `initial_weight_pct` of **2.0%** and only scaled if the breakout holds or pulls back constructively. Keep portfolio `max_loss_pct` at **0.6%** to avoid letting a fast semiconductor reversal do disproportionate damage.

```json
{
  "conviction": "medium-high",
  "target_weight_pct": 4.0,
  "initial_weight_pct": 2.0,
  "max_loss_pct": 0.6,
  "sizing_rationale": "AVGO combines strong profitability, cash generation, and forward earnings support with strong recent momentum, but the stock is extended well above its 50-day and 200-day averages and carries meaningful volatility and leverage risk. ATR near 12.6 suggests roughly 3.2% daily volatility, so sizing should be constructive but disciplined: start at 2.0%, scale toward 4.0% only if price confirms, and cap portfolio loss budget at 0.6% using an approximate 2x ATR stop."
}
```