FINAL TRANSACTION PROPOSAL: **BUY**

## FCX Position Sizing
FCX supports a **medium-high conviction** sizing plan, but not a full-risk allocation. Fundamentals are solid for a cyclical miner: forward EPS implies a much cheaper forward multiple than trailing results, leverage looks manageable (`debt/equity 34.1`, `current ratio 2.29`), and the stock is trading well above its `50-day` and `200-day` averages. Price action is also constructive, with FCX recovering from the March drawdown and closing at `68.28` on `2026-04-16`, just below the `52-week high` of `69.75`.

Volatility argues for discipline. ATR is about `2.55`, or roughly `3.7%` of spot, and FCX has a `beta` of `1.47`, so this should be sized smaller than a lower-volatility large cap. A reasonable plan is a **2.0% starter position**, scaling to a **4.0% target weight** only if the breakout above the recent range holds. Keep **max portfolio loss budget at 0.75%**, which is consistent with a cyclical, high-beta name using an approximately `1.5x ATR` stop framework.

```json
{
  "conviction": "medium-high",
  "target_weight_pct": 4.0,
  "initial_weight_pct": 2.0,
  "max_loss_pct": 0.75,
  "sizing_rationale": "FCX shows supportive fundamentals for a cyclical long, including strong forward earnings improvement, positive free cash flow, manageable leverage, and price strength above the 50-day and 200-day averages near a 52-week high. However, beta of 1.47 and ATR of about 2.55 on a 68.28 stock indicate elevated volatility, so the position should start at half size and only scale to a 4.0% target if momentum persists. A 0.75% max portfolio loss budget fits a high-beta materials name with an approximately 1.5x ATR stop-loss framework."
}
```