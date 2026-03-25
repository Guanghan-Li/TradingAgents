# Polymarket Prediction Market Module

This worktree adds a parallel Polymarket product module without changing the stock graph.

## What Exists

- `cli.main analyze --mode polymarket` dispatches to a dedicated Polymarket entrypoint.
- `tradingagents.prediction_market.PredictionMarketGraph` initializes a separate graph bootstrap with Polymarket-specific config.
- `tradingagents.prediction_market.PM_DEFAULT_CONFIG` keeps product defaults isolated from the stock config.

## Current Scope

This Task 13 implementation is intentionally minimal:

- It proves CLI mode selection for Polymarket.
- It proves prediction-market graph initialization and config stamping.
- It does not yet port the full PR `#432` LangGraph workflow, dataflow clients, or agent roster.

## Example

```python
from tradingagents.prediction_market import PM_DEFAULT_CONFIG, PredictionMarketGraph

config = PM_DEFAULT_CONFIG.copy()
graph = PredictionMarketGraph(selected_analysts=["market", "news"], config=config)
```
