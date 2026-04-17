## PLTR Position Sizing
PLTR supports a `medium` conviction size, not a full-risk allocation. Fundamentals are strong enough to justify exposure: high margins, positive net income, strong free cash flow, and low balance-sheet stress. The constraint is valuation and volatility: `226.6x` trailing P/E, `46.2x` price/book, `1.67` beta, and current ATR near `7.5`, which is about `5.3%` of the stock price.

Recent price action argues for scaling in. PLTR rebounded from the `2026-04-10` low near `122.68` back to `142.76` on `2026-04-16`, but it is still below the `50-day` average (`143.61`) and well below the `200-day` average (`164.12`). That setup supports a starter position first, then adding only if the rebound holds. A practical stop is roughly `1.5x ATR` below entry, near the low `130s`, which keeps the risk framework aligned with the recent support zone.

Sizing plan: target weight `3.5%`, start with `1.5%`, and cap max portfolio loss on the idea at `0.4%`. This keeps PLTR sized as a high-quality but expensive, high-volatility growth name rather than a core low-volatility holding.

```json
{"conviction":"medium","target_weight_pct":3.5,"initial_weight_pct":1.5,"max_loss_pct":0.4,"sizing_rationale":"PLTR has strong profitability, free cash flow, and balance-sheet quality, which supports owning it, but valuation is very rich and recent volatility is elevated. With ATR around 7.5 and beta near 1.67, position size should stay moderate. Recent price action shows a rebound off the April selloff, but the stock remains below its 50-day and 200-day averages, so scaling in is more prudent than entering full size immediately. A target 3.5% weight with a 1.5% starter and a portfolio loss cap of 0.4% balances upside participation with disciplined risk control."}
```