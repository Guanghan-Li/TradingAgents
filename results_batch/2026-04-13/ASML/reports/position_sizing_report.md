# Position Sizing Analysis: ASML

**Conviction Level:** Medium-High  
**Target Weight:** 4.0%  
**Initial/Starter Weight:** 2.0%  
**Max Loss Budget:** 1.0% of portfolio

## Rationale

ASML demonstrates exceptional fundamentals—50% ROE, 29% profit margin, and dominant positioning in semiconductor lithography equipment. The company's forward PE of 32.9 (vs TTM 51.5) suggests earnings growth expectations are intact despite recent volatility.

However, recent price action warrants caution. The stock experienced a sharp drawdown from $1,547 (Feb 25) to $1,254 (Mar 30)—a 19% decline—before recovering to current levels around $1,485. Current ATR of $55.56 represents ~3.7% daily volatility, elevated relative to typical large-cap tech.

**Sizing Logic:**
- Start with 2% position to establish exposure while volatility remains elevated
- Scale to 4% target if price consolidates above $1,450-$1,500 range with declining ATR
- Stop loss at 2x ATR (~$110) below entry = ~7.4% position risk
- 2% initial × 7.4% stop = 0.15% portfolio risk; allows room to average up
- Max portfolio loss capped at 1.0% (full 4% position stopped out at -25%)

The phased approach respects both the quality thesis and the current volatility regime. Strong fundamentals justify the 4% target, but recent price instability argues for building the position incrementally rather than committing full size immediately.

```json
{
  "conviction": "Medium-High",
  "target_weight_pct": 4.0,
  "initial_weight_pct": 2.0,
  "max_loss_pct": 1.0,
  "sizing_rationale": "Strong fundamentals (50% ROE, 29% margin, semiconductor equipment leader) support 4% target weight, but elevated volatility (ATR $55.56 = 3.7% daily) and recent 19% drawdown warrant phased entry. Start 2%, scale to 4% on consolidation above $1,450. Stop at 2x ATR (~$110 or 7.4%) limits initial risk to 0.15% of portfolio, with 1% max portfolio loss budget at full size."
}
```