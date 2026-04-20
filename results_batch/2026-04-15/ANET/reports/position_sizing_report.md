## ANET Position Sizing
ANET supports a `medium-high` conviction size, but not an aggressive one. Fundamentals are strong: ~39.0% profit margin, ~41.5% operating margin, strong free cash flow, low balance-sheet stress, and forward EPS implies valuation compression versus trailing earnings. The constraint is risk: `ANET` is trading at `154.33`, has `beta 1.475`, ATR is about `6.16` (`~4.0%` of price), and the stock has already rebounded sharply from the late-March low near `116` to the mid-`150s`, so chasing full size immediately is not disciplined.

Sizing plan: start with `1.5%` portfolio weight, scale to `4.0%` only if the recent breakout holds and volatility stays controlled. Use a stop roughly `1.75x-2.0x ATR` below entry (`~7-8%` price risk). Keep portfolio-level max loss budget at `0.6%`; if the setup fails, exit rather than average down.

```json
{
  "conviction": "medium-high",
  "target_weight_pct": 4.0,
  "initial_weight_pct": 1.5,
  "max_loss_pct": 0.6,
  "sizing_rationale": "ANET combines elite profitability, strong free cash flow, solid liquidity, and modest leverage with continued earnings growth, which supports owning the name. Position size should still be capped because valuation remains rich, beta is elevated, ATR is about 4% of price, and the stock has already moved sharply higher over the last two weeks. A staged entry reduces timing risk, while a roughly 1.75x-2.0x ATR stop keeps the trade risk-defined and consistent with a moderate-conviction growth position."
}
```