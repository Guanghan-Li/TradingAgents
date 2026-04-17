FINAL TRANSACTION PROPOSAL: **BUY**

### ASML Position Sizing
ASML supports a `moderate-high` conviction size, but not a full-risk entry. Fundamentals are strong: ~29.4% net margin, ~35.3% operating margin, strong free cash flow, and forward EPS implies meaningful earnings growth versus the current trailing multiple. Price action is also constructive, with a sharp recovery from late-March lows and the stock trading well above its 200-day average.

The constraint is volatility and valuation. ATR is about `58.4`, or roughly `3.9%` of price, beta is `1.38`, and the stock is near the top of its 52-week range after a fast rebound. That argues for scaling in rather than entering full size immediately.

Target size: `4.0%` portfolio weight  
Starter size: `1.5%` portfolio weight  
Max loss budget: `0.75%` of portfolio NAV  
Sizing logic: begin with a smaller tranche, use a stop around `1.75-2.0x ATR` below entry, and only build toward target if momentum holds and volatility does not expand materially.

```json
{
  "conviction": "moderate-high",
  "target_weight_pct": 4.0,
  "initial_weight_pct": 1.5,
  "max_loss_pct": 0.75,
  "sizing_rationale": "ASML combines high-quality semiconductor equipment fundamentals, strong profitability, and positive medium-term price structure, supporting a meaningful but not maximum allocation. Current risk is elevated because ATR is about 58.4, beta is 1.38, and the stock is trading near its 52-week high after a rapid rebound. A scale-in approach is appropriate: start at 1.5%, use a roughly 1.75-2.0 ATR stop framework, and add only if the trend remains intact and volatility stays controlled, with an eventual cap around 4.0% portfolio weight."
}
```