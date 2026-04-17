# Position Sizing Analysis: MSFT

## Market Context
Microsoft is trading at **$381.75** as of April 13, 2026, down ~31% from its 52-week high of $555.45. The stock sits below both its 50-day MA ($393.88) and 200-day MA ($474.17), confirming a technical downtrend despite strong fundamental quality.

## Fundamental Anchor
- **Quality Score: High** – Profit margin 39%, ROE 34%, $53.6B free cash flow
- **Valuation: Reasonable** – Forward PE 20.2x with continued growth expected
- **Balance Sheet: Solid** – Current ratio 1.39, manageable leverage

## Volatility & Risk Parameters
- **ATR (14-day): $8.47** (~2.3% of price)
- **Suggested stop: 2.5x ATR = ~$21 below entry** → Stop at $360
- **Risk per share: ~5.5%**

## Sizing Recommendation

**Conviction: Medium** – Strong fundamentals meet weak technicals. The discount is real, but the trend remains down.

- **Target Weight: 4.0%** of portfolio (full position if thesis plays out)
- **Initial Weight: 2.0%** (starter position given downtrend)
- **Max Loss Budget: 0.5%** of portfolio (tight risk control on initial tranche)

### Rationale
Scale in with a 2% starter while price is below key moving averages. If MSFT reclaims the 50-day MA (~$394) with volume, add another 1-2%. The 2.5x ATR stop at $360 protects against further breakdown while allowing normal volatility. Strong fundamentals justify the position; weak technicals justify the caution.

```json
{
  "conviction": "Medium",
  "target_weight_pct": 4.0,
  "initial_weight_pct": 2.0,
  "max_loss_pct": 0.5,
  "sizing_rationale": "Quality company at 31% discount from highs, but trading below both 50-day and 200-day MAs. Start with 2% position using 2.5x ATR stop (~$360). Scale to 4% target if price reclaims $394 (50-day MA). Strong fundamentals (39% margin, 34% ROE, $54B FCF) support medium conviction despite technical weakness."
}
```