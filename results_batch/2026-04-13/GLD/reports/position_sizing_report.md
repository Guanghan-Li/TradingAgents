# Position Sizing Analysis: GLD

## Market Context
GLD has experienced significant volatility over the past two months, declining ~18% from its early March peak of $490 to a low of $400 by late March, before recovering to $435. Current ATR of 10.94 reflects elevated volatility compared to the instrument's typical range.

## Sizing Rationale
Gold ETFs serve as portfolio hedges and safe-haven allocations. The recent drawdown suggests macro uncertainty (likely geopolitical or monetary policy shifts). The recovery from $400 to $435 shows stabilization but volatility remains elevated.

**Conviction**: Moderate. Gold's defensive characteristics are intact, but the sharp selloff and elevated ATR warrant caution.

**Target Weight**: 8% of portfolio  
**Initial Weight**: 4% (scale in given volatility)  
**Max Loss Budget**: 2% of portfolio (tight risk control given uncertainty)

**Stop Placement**: Using 2× ATR (~$22) below entry suggests a stop near $413, just above the recent low of $400. This provides breathing room while protecting capital.

**Scaling Plan**: Start with half position (4%), add remaining 4% if price holds above $420 and ATR compresses below 9.0, signaling reduced volatility.

```json
{
  "conviction": "Moderate - defensive asset with elevated volatility",
  "target_weight_pct": 8.0,
  "initial_weight_pct": 4.0,
  "max_loss_pct": 2.0,
  "sizing_rationale": "GLD serves as portfolio hedge. Recent 18% drawdown from $490 to $400 shows macro stress, but recovery to $435 suggests stabilization. ATR of 10.94 remains elevated, warranting scaled entry. Start 4%, add 4% on confirmation (hold above $420, ATR compression). Stop at $413 (2×ATR buffer) limits risk to 2% portfolio loss. Defensive allocation sized for volatility regime."
}
```