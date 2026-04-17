# Position Sizing Analysis: MSFT

## Market Context
Microsoft closed at **$370.87** on 2026-04-10, down **33% from its 52-week high** of $555.45 and sitting well below both the 50-day ($393.88) and 200-day ($474.17) moving averages. The stock has experienced significant volatility, with ATR currently at **~$8.47**, representing roughly **2.3% daily volatility**.

## Fundamental Anchor
MSFT remains a **high-quality compounder** with:
- **39% net margin** and **34% ROE** – best-in-class profitability
- **$53.6B free cash flow** supporting the dividend and buybacks
- Trading at **23.2x trailing P/E** and **19.7x forward P/E** – reasonable for quality
- Modest **31.5% debt-to-equity** and healthy **1.39x current ratio**

The recent drawdown appears **technically driven** rather than fundamentally justified. The forward P/E compression suggests the market is pricing in growth concerns, but the underlying business remains robust.

## Sizing Rationale
Given the **technical weakness** but **fundamental strength**, this warrants a **scaled entry approach**:

- **Target weight:** 8% (full conviction position for a quality name at a discount)
- **Initial entry:** 3% (starter position to manage volatility risk)
- **Max loss budget:** 1.5% of portfolio (tight risk control given recent volatility)

**Stop placement:** Use 2x ATR (~$17) below entry for a stop around **$354**, just above the March low of $356.77. This respects recent support while limiting downside to ~4.5% on the position.

**Scale-in plan:** Add 2.5% on a break above $385 (reclaiming the 50-day MA), and final 2.5% on a break above $410 (confirming trend reversal). This structure caps initial risk while allowing participation in a recovery.

```json
{
  "conviction": "HIGH - Quality compounder at technical discount; fundamentals intact despite 33% drawdown from highs",
  "target_weight_pct": 8.0,
  "initial_weight_pct": 3.0,
  "max_loss_pct": 1.5,
  "sizing_rationale": "Scaled entry using 2x ATR stop (~$354) limits initial risk to 1.5% of portfolio. Starter 3% position allows for 2-stage scale-in at $385 and $410 resistance levels. Target 8% reflects high conviction in MSFT's 39% margins, 34% ROE, and $53B FCF, with current 19.7x forward P/E offering value. Recent volatility (ATR $8.47) justifies conservative initial sizing despite strong fundamentals."
}
```