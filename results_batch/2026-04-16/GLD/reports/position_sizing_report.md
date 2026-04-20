## GLD Position Sizing

GLD supports a **medium-conviction** sizing plan: it remains well above its 200-day average (`440.08` vs `384.09`) and has recovered materially from the late-March drawdown, but it is still below its 50-day average (`450.24`), which argues against a full-size entry. Recent ATR is about `10.07`, so a disciplined stop roughly `2 x ATR` below spot implies a stop zone near `419.9` to `420.0`, or about `4.6%` downside from current price.

For that setup, a reasonable portfolio expression is a **5.0% target weight**, entered as a **2.5% starter**, with a **0.75% max portfolio loss budget**. The logic is that GLD is a highly liquid macro hedge with strong trend support over the intermediate term, but the last 60 days show sharp swings from `481` down to `400` and back to `440`, so scaling in is more appropriate than opening at full size immediately.

```json
{
  "conviction": "medium",
  "target_weight_pct": 5.0,
  "initial_weight_pct": 2.5,
  "max_loss_pct": 0.75,
  "sizing_rationale": "GLD has large-cap ETF liquidity, remains above its 200-day moving average, and has rebounded from a sharp March selloff, which supports a moderate allocation. However, price is still below the 50-day average and 60-day trading has been volatile, with ATR near 10 points and a recent range from about 400 to 481. That volatility supports using a 2x ATR stop near 420 and entering with a half-size starter before scaling to a 5% target only if trend confirmation continues."
}
```