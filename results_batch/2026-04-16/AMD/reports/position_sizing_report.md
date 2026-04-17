## AMD Position Sizing

AMD supports a `medium-high` conviction size, but not a full-risk allocation immediately. Fundamentals are solid enough for a bullish thesis, with strong forward EPS support, positive free cash flow, and price trading above both the 50-day and 200-day averages. The restraint comes from risk: beta is `1.963`, ATR is about `10.44`, and the stock has become very extended after a sharp run to a fresh 52-week high on `2026-04-16`.

A disciplined plan is to target a `6.5%` full position, start with `2.5%`, and cap portfolio loss at `0.5%`. That implies using a relatively wide stop, roughly `1.8-2.0 ATR` below entry, near the recent breakout zone around the mid-`250s`. The logic is straightforward: strong trend and improving earnings outlook justify meaningful exposure, but the recent vertical move and high volatility argue for scaling in rather than entering full size at once.

```json
{
  "conviction": "medium-high",
  "target_weight_pct": 6.5,
  "initial_weight_pct": 2.5,
  "max_loss_pct": 0.5,
  "sizing_rationale": "AMD merits a medium-high conviction size because forward earnings and cash generation support the thesis, and price is in a strong uptrend above major moving averages. However, the stock is highly volatile, with beta near 1.96 and ATR around 10.44, and it is extended after a rapid breakout to a new 52-week high. A 6.5% target weight with a 2.5% starter balances upside participation with gap and pullback risk, while a 0.5% max loss budget keeps portfolio risk controlled if a stop near 1.8-2.0 ATR below entry is hit."
}
```