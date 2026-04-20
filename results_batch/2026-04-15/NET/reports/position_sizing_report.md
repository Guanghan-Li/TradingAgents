## NET Position Sizing

- Conviction: Medium
- Target size: 2.5% portfolio weight
- Starter size: 1.0% portfolio weight
- Max loss budget: 0.5% of portfolio NAV

NET merits a non-zero position because fundamentals still show meaningful scale and quality in the model: roughly $2.17B TTM revenue, strong gross profit, and positive free cash flow. But sizing should stay restrained because valuation is still rich (about 131.9x forward P/E, 45.8x price/book), profitability remains negative on a TTM basis, leverage is elevated, and the stock is highly volatile. Recent price action also argues for caution: NET fell from the low-$220s to $166.99 in two sessions before rebounding to $190.13, while ATR sits near $13.86, or about 7.3% of spot. That combination supports a smaller-than-core initial allocation, with adds only after price confirms stability and volatility cools.

A practical framework is to start at 1.0% and only scale toward 2.5% if NET holds the rebound and reclaims trend strength versus the 50-day and 200-day areas. Using an ATR-aware stop roughly 1.0-1.25x ATR below entry keeps the expected realized loss per attempt contained, while the 0.5% portfolio loss cap prevents the name from becoming oversized relative to its current volatility.

```json
{
  "conviction": "medium",
  "target_weight_pct": 2.5,
  "initial_weight_pct": 1.0,
  "max_loss_pct": 0.5,
  "sizing_rationale": "NET combines strong top-line scale, gross profit generation, and positive free cash flow with negative TTM earnings, elevated leverage, premium valuation, and high volatility. Current ATR near 13.86 and the sharp April drawdown/rebound support a smaller-than-core position. Start at 1.0% and scale only on continued price stabilization; cap total portfolio loss at 0.5% using an ATR-based stop discipline."
}
```