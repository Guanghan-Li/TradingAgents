from tradingagents.graph.setup import GraphSetup


class DummyStateGraph:
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


def test_graph_setup_wires_chief_analyst_terminal_node(monkeypatch):
    recorded_llms = {}

    monkeypatch.setattr("tradingagents.graph.setup.StateGraph", DummyStateGraph)
    monkeypatch.setattr("tradingagents.graph.setup.create_msg_delete", lambda: "delete")

    def make_factory(node_name):
        def factory(llm, *_args):
            recorded_llms[node_name] = llm
            return node_name

        return factory

    monkeypatch.setattr(
        "tradingagents.graph.setup.create_market_analyst",
        make_factory("Market Analyst"),
    )
    monkeypatch.setattr(
        "tradingagents.graph.setup.create_social_media_analyst",
        make_factory("Social Analyst"),
    )
    monkeypatch.setattr(
        "tradingagents.graph.setup.create_news_analyst",
        make_factory("News Analyst"),
    )
    monkeypatch.setattr(
        "tradingagents.graph.setup.create_fundamentals_analyst",
        make_factory("Fundamentals Analyst"),
    )
    monkeypatch.setattr(
        "tradingagents.graph.setup.create_bull_researcher",
        make_factory("Bull Researcher"),
    )
    monkeypatch.setattr(
        "tradingagents.graph.setup.create_bear_researcher",
        make_factory("Bear Researcher"),
    )
    monkeypatch.setattr(
        "tradingagents.graph.setup.create_research_manager",
        make_factory("Research Manager"),
    )
    monkeypatch.setattr(
        "tradingagents.graph.setup.create_trader",
        make_factory("Trader"),
    )
    monkeypatch.setattr(
        "tradingagents.graph.setup.create_aggressive_debator",
        make_factory("Aggressive Analyst"),
    )
    monkeypatch.setattr(
        "tradingagents.graph.setup.create_neutral_debator",
        make_factory("Neutral Analyst"),
    )
    monkeypatch.setattr(
        "tradingagents.graph.setup.create_conservative_debator",
        make_factory("Conservative Analyst"),
    )
    monkeypatch.setattr(
        "tradingagents.graph.setup.create_portfolio_manager",
        make_factory("Portfolio Manager"),
    )
    monkeypatch.setattr(
        "tradingagents.graph.setup.create_chief_analyst",
        make_factory("Chief Analyst"),
        raising=False,
    )

    class PartialConditionalLogic:
        def should_continue_market(self, _state):
            return "Msg Clear Market"

        def should_continue_debate(self, _state):
            return "Research Manager"

        def should_continue_risk_analysis(self, _state):
            return "Portfolio Manager"

    setup = GraphSetup(
        quick_thinking_llm="quick-llm",
        deep_thinking_llm="deep-llm",
        tool_nodes={"market": "market-tools"},
        bull_memory=object(),
        bear_memory=object(),
        trader_memory=object(),
        invest_judge_memory=object(),
        portfolio_manager_memory=object(),
        conditional_logic=PartialConditionalLogic(),
        role_llms={"chief_analyst": "chief-llm"},
    )

    graph = setup.setup_graph(selected_analysts=["market"])

    assert recorded_llms["Chief Analyst"] == "chief-llm"
    assert graph["nodes"]["Chief Analyst"] == "Chief Analyst"
    assert ("Portfolio Manager", "Chief Analyst") in graph["edges"]


def test_chief_analyst_returns_structured_final_summary():
    from tradingagents.agents.managers.chief_analyst import create_chief_analyst

    node = create_chief_analyst(llm=object())
    output = node(
        {
            "company_of_interest": "AAPL",
            "trade_date": "2026-03-24",
            "market_report": "Demand and liquidity are supportive.",
            "sentiment_report": "Retail sentiment is constructive.",
            "news_report": "Product launch cadence remains intact.",
            "fundamentals_report": "Margins are stable and services mix is improving.",
            "investment_plan": "Research manager favors accumulation on durable earnings power.",
            "trader_investment_plan": "Build a 5% starter over several sessions and add on confirmation.",
            "final_trade_decision": """**Absolute Action**: Buy

**Relative Stance**: Overweight

**Executive Summary**: Accumulate on weakness over a 6-12 month horizon with measured sizing.

**Investment Thesis**: Services resilience and an AI-led upgrade cycle support upside if execution stays on track.""",
            "segment_data": {
                "business_unit_decomposition": [
                    {"segment": "iPhone"},
                    {"segment": "Services"},
                ],
                "value_driver_map": [
                    {"driver": "AI-enabled upgrade cycle"},
                    {"driver": "Services mix expansion"},
                ],
            },
            "scenario_catalyst_data": {
                "scenario_map": [
                    {
                        "name": "bull",
                        "probability_pct": 30,
                        "valuation_implication": "multiple expansion toward upper historical range",
                    },
                    {
                        "name": "base",
                        "probability_pct": 50,
                        "valuation_implication": "range-bound multiple with EPS carry",
                    },
                    {
                        "name": "bear",
                        "probability_pct": 20,
                        "valuation_implication": "derating to cycle-low valuation band",
                    },
                ],
                "dated_catalyst_map": [
                    {
                        "catalyst": "FOMC rate decision",
                        "date_or_window": "2026-05-06",
                        "expected_impact": "changes discount-rate pressure on valuation",
                    }
                ],
                "invalidation_triggers": [
                    {
                        "trigger": "two consecutive quarters of revenue miss versus guidance midpoint",
                        "severity": "high",
                    }
                ],
            },
            "risk_debate_state": {
                "judge_decision": "Buy with staged entries and clear risk limits.",
            },
        }
    )

    assert output["chief_analyst_data"] == {
        "ticker": "AAPL",
        "analysis_date": "2026-03-24",
        "verdict": {
            "absolute_action": "Buy",
            "relative_stance": "Overweight",
            "summary": "Accumulate on weakness over a 6-12 month horizon with measured sizing.",
            "thesis": "Services resilience and an AI-led upgrade cycle support upside if execution stays on track.",
        },
        "fair_value": {
            "bull_case": "multiple expansion toward upper historical range",
            "base_case": "range-bound multiple with EPS carry",
            "bear_case": "derating to cycle-low valuation band",
        },
        "catalysts": [
            {
                "catalyst": "FOMC rate decision",
                "date_or_window": "2026-05-06",
                "expected_impact": "changes discount-rate pressure on valuation",
            }
        ],
        "execution": {
            "research_plan": "Research manager favors accumulation on durable earnings power.",
            "trader_plan": "Build a 5% starter over several sessions and add on confirmation.",
            "portfolio_manager_guidance": "Accumulate on weakness over a 6-12 month horizon with measured sizing.",
        },
        "tail_risk": {
            "risk_summary": "Buy with staged entries and clear risk limits.",
            "invalidation_triggers": [
                {
                    "trigger": "two consecutive quarters of revenue miss versus guidance midpoint",
                    "severity": "high",
                }
            ],
        },
        "variant_perception": {
            "business_segments": ["iPhone", "Services"],
            "value_drivers": [
                "AI-enabled upgrade cycle",
                "Services mix expansion",
            ],
        },
    }


def test_chief_analyst_parses_numbered_portfolio_manager_output():
    from tradingagents.agents.managers.chief_analyst import create_chief_analyst

    node = create_chief_analyst(llm=object())
    output = node(
        {
            "company_of_interest": "MSFT",
            "trade_date": "2026-03-24",
            "investment_plan": "Research wants to lean long on durable cloud demand.",
            "trader_investment_plan": "Scale in over two tranches and keep sizing disciplined.",
            "final_trade_decision": """1. Absolute Action: Buy
2. Relative Stance: Overweight
3. Executive Summary: Add on modest pullbacks, target a 6-12 month holding period, and keep sizing incremental.
4. Investment Thesis: Azure durability and improving operating leverage support upside while consensus still underestimates monetization breadth.""",
            "risk_debate_state": {},
            "segment_data": {},
            "scenario_catalyst_data": {},
        }
    )

    assert output["chief_analyst_data"]["verdict"] == {
        "absolute_action": "Buy",
        "relative_stance": "Overweight",
        "summary": "Add on modest pullbacks, target a 6-12 month holding period, and keep sizing incremental.",
        "thesis": "Azure durability and improving operating leverage support upside while consensus still underestimates monetization breadth.",
    }


def test_chief_analyst_parses_markdown_portfolio_manager_sections():
    from tradingagents.agents.managers.chief_analyst import create_chief_analyst

    node = create_chief_analyst(llm=object())
    output = node(
        {
            "company_of_interest": "VICI",
            "trade_date": "2026-03-31",
            "investment_plan": "Research plan",
            "trader_investment_plan": "Trader plan",
            "final_trade_decision": """1. **Absolute Action**: **Buy**

2. **Relative Stance**: **Overweight**

3. **Executive Summary**  
**VICI** should be **accumulated gradually, not chased aggressively**.

- Start at **1.0%-2.0%** only if support holds.

4. **Investment Thesis**  
My final decision on **VICI** is **Buy** with an **Overweight** tilt, not **Hold**.

The underwriting supports a meaningful starter, but not a blind full-size entry.""",
            "risk_debate_state": {},
            "segment_data": {},
            "scenario_catalyst_data": {},
        }
    )

    assert output["chief_analyst_data"]["verdict"] == {
        "absolute_action": "Buy",
        "relative_stance": "Overweight",
        "summary": "**VICI** should be **accumulated gradually, not chased aggressively**.\n\n- Start at **1.0%-2.0%** only if support holds.",
        "thesis": "My final decision on **VICI** is **Buy** with an **Overweight** tilt, not **Hold**.\n\nThe underwriting supports a meaningful starter, but not a blind full-size entry.",
    }


def test_chief_analyst_returns_stable_defaults_with_missing_data():
    from tradingagents.agents.managers.chief_analyst import create_chief_analyst

    node = create_chief_analyst(llm=object())
    output = node(
        {
            "company_of_interest": "AAPL",
            "trade_date": "2026-03-24",
            "final_trade_decision": "",
            "risk_debate_state": {},
            "segment_data": {},
            "scenario_catalyst_data": {},
        }
    )

    assert output["chief_analyst_data"] == {
        "ticker": "AAPL",
        "analysis_date": "2026-03-24",
        "verdict": {
            "absolute_action": "",
            "relative_stance": "",
            "summary": "",
            "thesis": "",
        },
        "fair_value": {
            "bull_case": "",
            "base_case": "",
            "bear_case": "",
        },
        "catalysts": [],
        "execution": {
            "research_plan": "",
            "trader_plan": "",
            "portfolio_manager_guidance": "",
        },
        "tail_risk": {
            "risk_summary": "",
            "invalidation_triggers": [],
        },
        "variant_perception": {
            "business_segments": [],
            "value_drivers": [],
        },
    }


def test_propagator_initial_state_seeds_chief_analyst_defaults():
    from tradingagents.graph.propagation import Propagator

    state = Propagator().create_initial_state("AAPL", "2026-03-24")

    assert state["chief_analyst_report"] == ""
    assert state["chief_analyst_data"] == {
        "ticker": "",
        "analysis_date": "",
        "verdict": {
            "absolute_action": "",
            "relative_stance": "",
            "summary": "",
            "thesis": "",
        },
        "fair_value": {
            "bull_case": "",
            "base_case": "",
            "bear_case": "",
        },
        "catalysts": [],
        "execution": {
            "research_plan": "",
            "trader_plan": "",
            "portfolio_manager_guidance": "",
        },
        "tail_risk": {
            "risk_summary": "",
            "invalidation_triggers": [],
        },
        "variant_perception": {
            "business_segments": [],
            "value_drivers": [],
        },
    }


def test_debug_mode_propagate_keeps_terminal_chunk_without_messages(monkeypatch):
    from tradingagents.graph.trading_graph import TradingAgentsGraph

    class DummyMessage:
        def pretty_print(self):
            return None

    class DummyGraph:
        def stream(self, _init_state, **_kwargs):
            yield {
                "messages": [DummyMessage()],
                "final_trade_decision": "Buy",
            }
            yield {
                "messages": [],
                "final_trade_decision": "Buy",
                "chief_analyst_report": "final summary",
                "chief_analyst_data": {"verdict": {"absolute_action": "Buy", "relative_stance": "Neutral"}},
            }

    class DummyPropagator:
        def create_initial_state(self, company_name, trade_date):
            return {"messages": [("human", company_name)], "trade_date": trade_date}

        def get_graph_args(self):
            return {"stream_mode": "values", "config": {"recursion_limit": 100}}

    graph = TradingAgentsGraph.__new__(TradingAgentsGraph)
    graph.debug = True
    graph.graph = DummyGraph()
    graph.propagator = DummyPropagator()
    graph._log_state = lambda *_args, **_kwargs: None
    graph.process_signal = lambda signal: signal
    graph.log_states_dict = {}

    final_state, decision = TradingAgentsGraph.propagate(graph, "AAPL", "2026-03-24")

    assert decision == "Buy"
    assert final_state["chief_analyst_report"] == "final summary"
    assert final_state["chief_analyst_data"] == {"verdict": {"absolute_action": "Buy", "relative_stance": "Neutral"}}
