`TSLA` sizing should stay modest: target weight `2.5%`, start with `1.0%`, and cap max portfolio loss at `0.6%`.

Core rationale: conviction is only medium-low because the stock is still extremely expensive on fundamentals (353.5x trailing P/E, 140.3x forward P/E) while profitability remains thin (4.0% net margin, 4.9% ROE), even though free cash flow and liquidity are positive. The trading backdrop is volatile: beta is `1.915`, ATR is about `$15.36` or roughly `4.0%` of price, and the last 60 days showed a sharp slide from the low `410s` into the mid `340s` followed by a fast rebound back to `$388.90`. With price still slightly below both the 50-day and 200-day averages, this looks like a name for controlled exposure rather than full sizing. A practical stop is around `2x ATR` below spot, near `$358`, which also lines up with recent support.

```json
{
  "conviction": "medium-low",
  "target_weight_pct": 2.5,
  "initial_weight_pct": 1.0,
  "max_loss_pct": 0.6,
  "sizing_rationale": "TSLA has positive cash flow and decent liquidity, but valuation is still very rich and profitability is modest, which limits thesis quality. Recent price action has been highly volatile, with ATR near 4% of spot and a sharp drawdown/rebound sequence over the last 60 days. Because the stock is still trading just below its 50-day and 200-day averages, the setup supports a scaled entry and a modest final weight rather than an aggressive allocation."
}
```