import os
from typing import Any, Dict, List, Optional

from langchain_core.tools import tool
from langgraph.prebuilt import ToolNode

from tradingagents.llm_clients import create_llm_client

from .pm_config import PM_DEFAULT_CONFIG


@tool
def get_market_context(market_id: str) -> str:
    """Return a basic context string for a Polymarket market."""
    return f"Polymarket market context for {market_id}"


@tool
def get_market_news(market_id: str) -> str:
    """Return a basic news lookup string for a Polymarket market."""
    return f"Polymarket market news for {market_id}"


class PredictionMarketGraph:
    """Minimal prediction-market graph bootstrap parallel to the stock graph."""

    def __init__(
        self,
        selected_analysts: Optional[List[str]] = None,
        debug: bool = False,
        config: Optional[Dict[str, Any]] = None,
        callbacks: Optional[List] = None,
    ):
        self.product = "polymarket"
        self.debug = debug
        self.callbacks = callbacks or []
        self.selected_analysts = selected_analysts or ["market", "news"]
        self.config = PM_DEFAULT_CONFIG.copy()
        if config:
            self.config.update(config)
        self.config["market_type"] = "polymarket"

        os.makedirs(self.config["data_cache_dir"], exist_ok=True)

        llm_kwargs = self._get_provider_kwargs()
        if self.callbacks:
            llm_kwargs["callbacks"] = self.callbacks

        deep_client = create_llm_client(
            provider=self.config["llm_provider"],
            model=self.config["deep_think_llm"],
            base_url=self.config.get("backend_url"),
            **llm_kwargs,
        )
        quick_client = create_llm_client(
            provider=self.config["llm_provider"],
            model=self.config["quick_think_llm"],
            base_url=self.config.get("backend_url"),
            **llm_kwargs,
        )

        self.deep_thinking_llm = deep_client.get_llm()
        self.quick_thinking_llm = quick_client.get_llm()
        self.tool_nodes = self._create_tool_nodes()
        self.graph = None

    def _get_provider_kwargs(self) -> Dict[str, Any]:
        kwargs: Dict[str, Any] = {}
        provider = self.config.get("llm_provider", "").lower()

        if provider == "google" and self.config.get("google_thinking_level"):
            kwargs["thinking_level"] = self.config["google_thinking_level"]
        elif provider == "openai" and self.config.get("openai_reasoning_effort"):
            kwargs["reasoning_effort"] = self.config["openai_reasoning_effort"]
        elif provider == "anthropic" and self.config.get("anthropic_effort"):
            kwargs["effort"] = self.config["anthropic_effort"]

        return kwargs

    def _create_tool_nodes(self) -> Dict[str, ToolNode]:
        return {
            "market": ToolNode([get_market_context]),
            "news": ToolNode([get_market_news]),
        }
