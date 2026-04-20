from tradingagents.graph.setup import GraphSetup
from tradingagents.graph.trading_graph import TradingAgentsGraph


class RecordingStateGraph:
    def __init__(self, _state_type):
        self.nodes = {}
        self.edges = []
        self.conditional_edges = {}

    def add_node(self, name, node):
        self.nodes[name] = node

    def add_edge(self, source, destination):
        self.edges.append((source, destination))

    def add_conditional_edges(self, source, condition, destinations):
        self.conditional_edges[source] = {
            "condition": condition,
            "destinations": destinations,
        }

    def compile(self):
        return {
            "nodes": self.nodes,
            "edges": self.edges,
            "conditional_edges": self.conditional_edges,
        }


class DummyToolNode:
    def __init__(self, tools):
        self.tools = tools


class DummyConditionalLogic:
    def should_continue_market(self, _state):
        return "Msg Clear Market"

    def should_continue_news(self, _state):
        return "Msg Clear News"

    def should_continue_debate(self, _state):
        return "Research Manager"

    def should_continue_risk_analysis(self, _state):
        return "Portfolio Manager"


def _patch_setup_factories(monkeypatch):
    monkeypatch.setattr("tradingagents.graph.setup.StateGraph", RecordingStateGraph)
    monkeypatch.setattr("tradingagents.graph.setup.ToolNode", DummyToolNode)
    monkeypatch.setattr("tradingagents.graph.setup.create_msg_delete", lambda: "delete")

    def make_factory(node_name):
        def factory(*_args, **_kwargs):
            return node_name

        return factory

    monkeypatch.setattr("tradingagents.graph.setup.create_market_analyst", make_factory("Market Analyst"))
    monkeypatch.setattr("tradingagents.graph.setup.create_news_analyst", make_factory("News Analyst"))
    monkeypatch.setattr("tradingagents.graph.setup.create_social_media_analyst", make_factory("Social Analyst"))
    monkeypatch.setattr("tradingagents.graph.setup.create_fundamentals_analyst", make_factory("Fundamentals Analyst"))
    monkeypatch.setattr("tradingagents.graph.setup.create_factor_rule_analyst", make_factory("Factor Rules Analyst"))
    monkeypatch.setattr("tradingagents.graph.setup.create_valuation_analyst", make_factory("Valuation Analyst"))
    monkeypatch.setattr("tradingagents.graph.setup.create_segment_analyst", make_factory("Segment Analyst"))
    monkeypatch.setattr("tradingagents.graph.setup.create_scenario_catalyst_analyst", make_factory("Scenario Analyst"))
    monkeypatch.setattr("tradingagents.graph.setup.create_position_sizing_analyst", make_factory("Position Sizing Analyst"))
    monkeypatch.setattr("tradingagents.graph.setup.create_macro_analyst", make_factory("Macro Analyst"))
    monkeypatch.setattr("tradingagents.graph.setup.create_bull_researcher", make_factory("Bull Researcher"))
    monkeypatch.setattr("tradingagents.graph.setup.create_bear_researcher", make_factory("Bear Researcher"))
    monkeypatch.setattr("tradingagents.graph.setup.create_research_manager", make_factory("Research Manager"))
    monkeypatch.setattr("tradingagents.graph.setup.create_trader", make_factory("Trader"))
    monkeypatch.setattr("tradingagents.graph.setup.create_aggressive_debator", make_factory("Aggressive Analyst"))
    monkeypatch.setattr("tradingagents.graph.setup.create_neutral_debator", make_factory("Neutral Analyst"))
    monkeypatch.setattr("tradingagents.graph.setup.create_conservative_debator", make_factory("Conservative Analyst"))
    monkeypatch.setattr("tradingagents.graph.setup.create_portfolio_manager", make_factory("Portfolio Manager"))
    monkeypatch.setattr("tradingagents.graph.setup.create_chief_analyst", make_factory("Chief Analyst"))


def test_graph_setup_uses_single_pass_edges_for_claude_pipeline(monkeypatch):
    _patch_setup_factories(monkeypatch)
    monkeypatch.setattr(
        "tradingagents.graph.setup.wrap_quick_analyst_node",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(AssertionError("resilience wrapper should be disabled")),
    )

    setup = GraphSetup(
        quick_thinking_llm="quick-llm",
        deep_thinking_llm="deep-llm",
        tool_nodes={"market": "market-tools", "news": "news-tools"},
        bull_memory=object(),
        bear_memory=object(),
        trader_memory=object(),
        invest_judge_memory=object(),
        portfolio_manager_memory=object(),
        conditional_logic=DummyConditionalLogic(),
        single_pass_pipeline=True,
        enable_resilience_wrappers=False,
    )

    graph = setup.setup_graph(["market", "news"])

    assert "Bull Researcher" not in graph["conditional_edges"]
    assert "Aggressive Analyst" not in graph["conditional_edges"]
    assert ("Msg Clear News", "Bull Researcher") in graph["edges"]
    assert ("Bull Researcher", "Bear Researcher") in graph["edges"]
    assert ("Bear Researcher", "Research Manager") in graph["edges"]
    assert ("Research Manager", "Trader") in graph["edges"]
    assert ("Trader", "Aggressive Analyst") in graph["edges"]
    assert ("Aggressive Analyst", "Conservative Analyst") in graph["edges"]
    assert ("Conservative Analyst", "Neutral Analyst") in graph["edges"]
    assert ("Neutral Analyst", "Portfolio Manager") in graph["edges"]
    assert ("Portfolio Manager", "Chief Analyst") in graph["edges"]


def test_trading_graph_enables_single_pass_pipeline_for_claude_code(monkeypatch):
    captured = {}

    class FakeClient:
        def __init__(self, provider, model, base_url=None, **kwargs):
            self.provider = provider
            self.model = model
            self.base_url = base_url
            self.kwargs = kwargs

        def get_llm(self):
            return {"provider": self.provider, "model": self.model, "kwargs": self.kwargs}

    class FakeGraphSetup:
        def __init__(self, *args, **kwargs):
            captured["kwargs"] = kwargs

        def setup_graph(self, selected_analysts):
            captured["selected_analysts"] = selected_analysts
            return {"selected_analysts": selected_analysts}

    monkeypatch.setattr(
        "tradingagents.graph.trading_graph.create_llm_client",
        lambda provider, model, base_url=None, **kwargs: FakeClient(provider, model, base_url, **kwargs),
    )
    monkeypatch.setattr(
        "tradingagents.graph.trading_graph.FinancialSituationMemory",
        lambda *args, **kwargs: object(),
    )
    monkeypatch.setattr("tradingagents.graph.trading_graph.GraphSetup", FakeGraphSetup)

    TradingAgentsGraph(
        selected_analysts=["market"],
        config={
            "llm_provider": "claude_code",
            "backend_url": "claude://local",
            "quick_think_llm": "claude-sonnet-4-6",
            "deep_think_llm": "claude-sonnet-4-6",
        },
    )

    assert captured["kwargs"]["single_pass_pipeline"] is True
    assert captured["kwargs"]["enable_resilience_wrappers"] is False
