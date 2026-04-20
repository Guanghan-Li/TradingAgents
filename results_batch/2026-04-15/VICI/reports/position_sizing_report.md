**VICI Position Sizing**

- `Conviction`: Medium
- `Target size`: `4.0%` of portfolio
- `Starter size`: `2.0%`
- `Max loss budget`: `0.15%` of portfolio
- `Volatility context`: ATR is about `$0.50`, so a roughly `2 ATR` stop implies about `3.5%` to `4.0%` downside from the current `$28.13` area.

VICI supports a moderate income-oriented position size: valuation is undemanding, dividend yield is high at `6.29%`, beta is low at `0.728`, and margins are unusually strong for a REIT. The constraint is trend and balance-sheet sensitivity: shares remain below the `50-day` and `200-day` averages, and leverage is meaningful, so sizing should start smaller and only scale if the recent rebound continues. A practical plan is to initiate at `2%`, use a stop around `2 ATR` below entry or below the recent support zone, and add toward `4%` only if price keeps stabilizing above the recent recovery range.

```json
{
  "conviction": "medium",
  "target_weight_pct": 4.0,
  "initial_weight_pct": 2.0,
  "max_loss_pct": 0.15,
  "sizing_rationale": "VICI offers a favorable mix of low beta, strong profitability, reasonable valuation, and a 6.29% dividend yield, which supports a moderate allocation. However, shares are still below the 50-day and 200-day averages and the REIT structure carries leverage and rate sensitivity, so conviction is not high enough for an oversized position. With ATR near $0.50 and price near $28.13, a stop about 2 ATR below entry implies roughly 3.5% to 4.0% position downside, supporting a 2.0% starter position and a 4.0% full position while keeping total portfolio risk near 0.15% at max size."
}
```