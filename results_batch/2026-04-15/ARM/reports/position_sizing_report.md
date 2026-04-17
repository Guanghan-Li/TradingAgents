## ARM Position Sizing

ARM supports only a **medium-conviction** size. The business quality is solid with high gross margins, positive net income, and free cash flow, but the stock carries **very high valuation risk** (`~210x` trailing P/E, `~74x` forward P/E) and **high volatility** (beta `3.34`, ATR `8.58`, or about `5.4%` of price). Recent price action is constructive, with ARM trading at `159.34`, above its `50-day` and `200-day` averages after a sharp March breakout, but the tape remains wide and gap-prone.

**Sizing plan:** target **3.0%** portfolio weight, start with **1.25%**, and cap total portfolio loss on the idea at **0.30%**. A practical stop framework is roughly `1.5x ATR` below entry (about `8%`), which argues for scaling in slowly and only adding if ARM holds the post-breakout trend rather than chasing extended upside.

```json
{
  "conviction": "medium",
  "target_weight_pct": 3.0,
  "initial_weight_pct": 1.25,
  "max_loss_pct": 0.3,
  "sizing_rationale": "ARM has strong profitability and cash generation, and price is trending above key moving averages, but valuation is stretched and volatility is elevated. With ATR near 8.58 and beta above 3, position size should stay moderate. A 3.0% target weight with a 1.25% starter allows participation while respecting gap risk and leaves room to add only if the breakout structure remains intact."
}
```