from typing import Any, Dict, List, Optional

from tradingagents.llm_clients import create_llm_client

from .graph import pm_trading_graph
from .graph.pm_trading_graph import PMTradingAgentsGraph
from .pm_config import PM_DEFAULT_CONFIG


class PredictionMarketGraph(PMTradingAgentsGraph):
    """Compatibility wrapper exposing the PR #432 Polymarket graph via a stable path."""

    def __init__(
        self,
        selected_analysts: Optional[List[str]] = None,
        debug: bool = False,
        config: Optional[Dict[str, Any]] = None,
        callbacks: Optional[List] = None,
    ):
        normalized_config = PM_DEFAULT_CONFIG.copy()
        if config:
            normalized_config.update(config)
        normalized_config["market_type"] = "polymarket"

        pm_trading_graph.create_llm_client = create_llm_client
        resolved_analysts = selected_analysts or [
            "event",
            "odds",
            "information",
            "sentiment",
        ]
        super().__init__(
            selected_analysts=resolved_analysts,
            debug=debug,
            config=normalized_config,
            callbacks=callbacks,
        )
        self.product = "polymarket"
        self.selected_analysts = resolved_analysts
