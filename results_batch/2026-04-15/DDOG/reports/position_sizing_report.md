## DDOG Position Sizing Summary

DDOG supports a `medium` conviction size, not a full-risk allocation. The quality anchors are solid revenue scale, strong free cash flow, and a healthy current ratio, but GAAP profitability remains thin and valuation is still demanding with a forward P/E near 46 and a trailing P/E near 391.

Recent trading also argues for restraint. DDOG closed at `121.06` on `2026-04-15`, slightly above its 50-day average (`119.29`) but still below its 200-day average (`138.74`). The stock has been highly directional over the last 60 days, falling to `102.61` in late February, rebounding above `131`, then dropping back near `105` before the latest bounce. With ATR around `7.17`, daily volatility is roughly `5.9%` of price, so stops need room and position size should be moderated.

A disciplined plan is to start at `1.25%` and only build toward a `3.0%` target weight if DDOG holds the recent rebound and volatility does not expand further. Keep max portfolio loss budget around `0.6%`, which fits a roughly `1.5x-2.0x ATR` stop framework without forcing an oversized position.

```json
{
  "conviction": "medium",
  "target_weight_pct": 3.0,
  "initial_weight_pct": 1.25,
  "max_loss_pct": 0.6,
  "sizing_rationale": "DDOG merits a medium-conviction position because fundamentals show strong revenue scale, solid free cash flow, and good liquidity, but thin operating margins and a still-rich valuation limit aggressiveness. Price action is volatile and trend quality is mixed: shares are back above the 50-day average but remain below the 200-day average after multiple 10%+ swings over the last two months. With ATR near 7.17, a phased entry is more appropriate than full size, using a 1.5x-2.0x ATR risk framework and capping portfolio loss near 0.6%."
}
```