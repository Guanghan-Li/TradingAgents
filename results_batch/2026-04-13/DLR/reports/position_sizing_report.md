# Position Sizing Analysis: DLR (Digital Realty Trust)

## Market Context
DLR closed at **$190.86** on 2026-04-13, up significantly from the late-March low of ~$173. The stock has rallied **+10%** in approximately two weeks, showing strong momentum. Current ATR sits at **3.82** (~2% of price), indicating moderate but manageable volatility for a large-cap REIT.

## Fundamental Anchor
Digital Realty is a **$66.7B data center REIT** with solid operating metrics: 21.5% profit margin, $1.96B free cash flow, and a 2.58% dividend yield. However, the **PE ratio of 53.16** is elevated for a REIT, suggesting the market is pricing in significant AI infrastructure growth expectations. The recent price surge may have front-run some of this optimism.

## Sizing Rationale
**Conviction: MODERATE** – The thesis is sound (data center demand, AI tailwinds, quality operator), but valuation and recent momentum create near-term risk. This warrants a **scaled entry** rather than full position immediately.

- **Target Weight:** 4.0% of portfolio (meaningful exposure to data center theme)
- **Initial Weight:** 2.0% (half position to start, allowing room to add on pullback)
- **Max Loss Budget:** 1.5% of portfolio (tight risk control given valuation stretch)

## Stop Placement & Risk Management
Using **2x ATR** for stop distance: 2 × 3.82 = **$7.64** below entry. Initial stop at **~$183.20** (3.8% below current price). This translates to a **1.5% portfolio loss** on the 2% initial position if stopped out.

**Scale-in plan:** Add remaining 2% if DLR consolidates above $185 or pulls back to $180-182 support zone with ATR stabilizing.

```json
{
  "conviction": "MODERATE",
  "target_weight_pct": 4.0,
  "initial_weight_pct": 2.0,
  "max_loss_pct": 1.5,
  "sizing_rationale": "DLR offers solid data center REIT exposure with AI infrastructure tailwinds, but the PE of 53 and recent 10% rally warrant a scaled entry. Starting with 2% allows room to add on consolidation or pullback. Stop at 2x ATR (~$183) limits risk to 1.5% of portfolio. Target 4% if thesis confirms and valuation digests recent gains."
}
```