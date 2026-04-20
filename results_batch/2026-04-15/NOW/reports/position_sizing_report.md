### NOW Position Sizing Summary
Conviction is **medium**. ServiceNow still has strong underlying business quality for `NOW` with solid free cash flow, healthy margins, and a much lower forward P/E than trailing P/E, but the tape is materially damaged: price is well below both the 50-day average (`106.64`) and 200-day average (`156.88`), and current ATR is elevated at about `5.72`, or roughly `6.1%` of spot.

A disciplined plan is to keep the position modest until price action stabilizes. I would size `NOW` at a **3.0% target weight**, start with an **initial 1.0% weight**, and cap **max loss at 0.50%** of portfolio NAV. That framework fits a stop roughly `1.5 x ATR` below entry, which is wide enough for current volatility but still keeps downside controlled. The core logic is simple: good company, weak trend, high volatility, so start small and only scale if the rebound proves durable.

```json
{
  "conviction": "medium",
  "target_weight_pct": 3.0,
  "initial_weight_pct": 1.0,
  "max_loss_pct": 0.5,
  "sizing_rationale": "NOW has solid business quality, free cash flow, and forward earnings support, but recent price action is weak and volatility is elevated. Shares are trading below the 50-day and 200-day averages, and ATR near 5.72 implies wide daily movement. A smaller starter position limits risk while allowing participation if the rebound continues; scaling toward the full target should wait for improved trend confirmation."
}
```