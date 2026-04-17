## Sizing Summary
TSLA merits a modest, volatility-adjusted size rather than a full-risk position. Fundamentals are not strong enough for aggressive sizing: valuation is very stretched (359.6x trailing P/E, 17.9x price/book), profitability is thin (4.0% net margin), and beta is high at 1.915. Price action improved sharply on 2026-04-15 with a close at 391.95 on very heavy volume, reclaiming the 50-day average, but shares are still only around the 200-day average after a sharp March-April drawdown.

Using the current ATR of 15.59, a practical stop is about 2 ATR below entry at roughly 360.8, or about 8.0% below 391.95. That supports a `2.0%` target weight, started at `0.75%`, with a `0.16%` max portfolio loss budget. The sizing plan is to start small after the large one-day rebound, add only if TSLA holds above the 50-day average and confirms through the 200-day average, and avoid oversized exposure because volatility and valuation both remain elevated.

```json
{
  "conviction": "medium-low",
  "target_weight_pct": 2.0,
  "initial_weight_pct": 0.75,
  "max_loss_pct": 0.16,
  "sizing_rationale": "TSLA shows improving momentum after a high-volume rebound to 391.95 on 2026-04-15, but conviction is capped by stretched valuation, thin margins, and high beta. With ATR near 15.59, a roughly 2 ATR stop implies about 8% price risk, so position size should stay modest. A 2.0% target weight and 0.75% starter size keep portfolio risk contained while allowing adds only if price holds the 50-day average and reclaims the 200-day average."
}
```