## XLE Position Sizing Summary

XLE supports a **medium-conviction** size rather than a full-risk allocation. The ETF is still above its **200-day average (47.73)**, but it has pulled back sharply from the **March 30, 2026 high of 63.46** and is now trading **56.58**, slightly below its **50-day average of 56.86**. That argues for a staged entry instead of immediate full size.

Using current **ATR of ~1.50**, a practical stop is about **2 ATR below entry**, near **53.6**, which is far enough to avoid routine noise but close enough to keep risk defined. With that stop width, a reasonable plan is:

- **Target size:** 10% portfolio weight
- **Starter size:** 5% portfolio weight
- **Max loss budget:** 0.6% of portfolio

Core rationale: XLE is a diversified sector ETF with acceptable valuation support (**P/B 1.09**, **2.44% yield**) and a still-intact longer-term trend, but recent price action shows momentum damage and elevated volatility after the failed breakout above 60. That combination supports building exposure in halves and only adding if price stabilizes and reclaims short-term trend support.

```json
{
  "conviction": "medium",
  "target_weight_pct": 10,
  "initial_weight_pct": 5,
  "max_loss_pct": 0.6,
  "sizing_rationale": "XLE remains above its 200-day average, which supports a constructive medium-term trend, but it has retraced materially from the March 30, 2026 peak and is trading around its 50-day average, indicating weaker short-term momentum. With ATR near 1.50, a roughly 2-ATR stop implies about 5% downside room from current levels, so a moderate 10% target weight with a 5% starter position keeps portfolio risk controlled while allowing room to add if the ETF bases and trend strength improves."
}
```