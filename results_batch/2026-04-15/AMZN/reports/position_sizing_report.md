## AMZN Position Sizing
AMZN supports a `moderate` conviction size, not a max-size entry. Fundamentals are high quality for a mega-cap growth name: forward P/E (`26.4`) is more reasonable than trailing (`34.7`), profitability is strong, and returns on capital are healthy. Price action is also constructive, with a sharp recovery from late March and the stock closing at `248.50`, near its 52-week high.

The constraint is extension and volatility. AMZN is now well above its 50-day average (`213.56`), beta is elevated (`1.38`), and ATR is about `6.66`, or roughly `2.7%` of spot. After a fast run from roughly `199` to `249` in under three weeks, chasing full size immediately is not disciplined. A better plan is to start smaller and only scale toward target if the breakout holds and the stock digests gains without losing trend support.

Sizing plan: target weight `4.0%`, starter weight `2.0%`, and max portfolio loss budget `0.8%`. That lines up with a stop framework around `1.5-2.0x ATR` below entry or below a nearby trend support zone, while leaving room to add only if price confirms rather than reverses.

```json
{
  "conviction": "moderate",
  "target_weight_pct": 4.0,
  "initial_weight_pct": 2.0,
  "max_loss_pct": 0.8,
  "sizing_rationale": "AMZN combines strong large-cap fundamentals, improving forward earnings valuation, and strong recent momentum, but the stock is extended after a rapid advance and carries above-market beta. With ATR near 6.66, volatility is meaningful enough to avoid an immediate full-size position. A half-size starter controls timing risk, with room to build toward 4% only if the breakout holds and price action remains orderly."
}
```