# TradingAgents/graph/setup.py

from typing import Dict, Any
from langchain_openai import ChatOpenAI
from langgraph.graph import END, StateGraph, START
from langgraph.prebuilt import ToolNode

from tradingagents.agents import (
    create_aggressive_debator,
    create_bear_researcher,
    create_bull_researcher,
    create_conservative_debator,
    create_factor_rule_analyst,
    create_fundamentals_analyst,
    create_macro_analyst,
    create_market_analyst,
    create_msg_delete,
    create_neutral_debator,
    create_news_analyst,
    create_portfolio_manager,
    create_position_sizing_analyst,
    create_research_manager,
    create_scenario_catalyst_analyst,
    create_segment_analyst,
    create_social_media_analyst,
    create_trader,
    create_valuation_analyst,
)
from tradingagents.agents.managers.chief_analyst import create_chief_analyst
from tradingagents.agents.utils.agent_states import (
    AgentState,
    make_default_position_sizing_data,
    make_default_scenario_catalyst_data,
    make_default_segment_data,
    make_default_valuation_data,
)
from tradingagents.agents.utils.analyst_resilience import wrap_quick_analyst_node

from .conditional_logic import ConditionalLogic


class GraphSetup:
    """Handles the setup and configuration of the agent graph."""

    QUICK_ANALYST_RESILIENCE = {
        "market": {"analyst_name": "Market Analyst", "report_key": "market_report"},
        "social": {"analyst_name": "Social Analyst", "report_key": "sentiment_report"},
        "news": {"analyst_name": "News Analyst", "report_key": "news_report"},
        "fundamentals": {
            "analyst_name": "Fundamentals Analyst",
            "report_key": "fundamentals_report",
        },
        "macro": {"analyst_name": "Macro Analyst", "report_key": "macro_report"},
        "factor_rules": {
            "analyst_name": "Factor Rules Analyst",
            "report_key": "factor_rules_report",
        },
        "valuation": {
            "analyst_name": "Valuation Analyst",
            "extra_state_factory": lambda state, report: {
                "valuation_data": {
                    **make_default_valuation_data(),
                    "primary_method": "degraded_backend_error",
                    "thesis": report,
                }
            },
        },
        "segment": {
            "analyst_name": "Segment Analyst",
            "report_key": "segment_report",
            "extra_state_factory": lambda state, report: {
                "segment_data": {
                    **make_default_segment_data(),
                    "ticker": state.get("company_of_interest", ""),
                    "analysis_date": state.get("trade_date", ""),
                }
            },
        },
        "scenario": {
            "analyst_name": "Scenario Analyst",
            "report_key": "scenario_catalyst_report",
            "extra_state_factory": lambda state, report: {
                "scenario_catalyst_data": {
                    **make_default_scenario_catalyst_data(),
                    "ticker": state.get("company_of_interest", ""),
                    "analysis_date": state.get("trade_date", ""),
                }
            },
        },
        "position_sizing": {
            "analyst_name": "Position Sizing Analyst",
            "report_key": "position_sizing_report",
            "extra_state_factory": lambda state, report: {
                "position_sizing_data": {
                    **make_default_position_sizing_data(),
                    "ticker": state.get("company_of_interest", ""),
                    "analysis_date": state.get("trade_date", ""),
                    "sizing_rationale": report,
                }
            },
        },
        "bull_researcher": {
            "analyst_name": "Bull Researcher",
            "extra_state_factory": lambda state, report: {
                "investment_debate_state": {
                    **state["investment_debate_state"],
                    "history": state["investment_debate_state"].get("history", "") + "\nBull Analyst: " + report,
                    "bull_history": state["investment_debate_state"].get("bull_history", "") + "\nBull Analyst: " + report,
                    "current_response": "Bull Analyst: " + report,
                    "count": state["investment_debate_state"]["count"] + 1,
                }
            },
        },
        "bear_researcher": {
            "analyst_name": "Bear Researcher",
            "extra_state_factory": lambda state, report: {
                "investment_debate_state": {
                    **state["investment_debate_state"],
                    "history": state["investment_debate_state"].get("history", "") + "\nBear Analyst: " + report,
                    "bear_history": state["investment_debate_state"].get("bear_history", "") + "\nBear Analyst: " + report,
                    "current_response": "Bear Analyst: " + report,
                    "count": state["investment_debate_state"]["count"] + 1,
                }
            },
        },
        "research_manager": {
            "analyst_name": "Research Manager",
            "report_key": "investment_plan",
            "extra_state_factory": lambda state, report: {
                "investment_debate_state": {
                    **state["investment_debate_state"],
                    "judge_decision": report,
                    "current_response": report,
                }
            },
        },
        "trader": {
            "analyst_name": "Trader",
            "report_key": "trader_investment_plan",
            "extra_state_factory": lambda state, report: {"sender": "Trader"},
        },
        "aggressive_analyst": {
            "analyst_name": "Aggressive Analyst",
            "extra_state_factory": lambda state, report: {
                "risk_debate_state": {
                    **state["risk_debate_state"],
                    "history": state["risk_debate_state"].get("history", "") + "\nAggressive Analyst: " + report,
                    "aggressive_history": state["risk_debate_state"].get("aggressive_history", "") + "\nAggressive Analyst: " + report,
                    "latest_speaker": "Aggressive",
                    "current_aggressive_response": "Aggressive Analyst: " + report,
                    "count": state["risk_debate_state"]["count"] + 1,
                }
            },
        },
        "neutral_analyst": {
            "analyst_name": "Neutral Analyst",
            "extra_state_factory": lambda state, report: {
                "risk_debate_state": {
                    **state["risk_debate_state"],
                    "history": state["risk_debate_state"].get("history", "") + "\nNeutral Analyst: " + report,
                    "neutral_history": state["risk_debate_state"].get("neutral_history", "") + "\nNeutral Analyst: " + report,
                    "latest_speaker": "Neutral",
                    "current_neutral_response": "Neutral Analyst: " + report,
                    "count": state["risk_debate_state"]["count"] + 1,
                }
            },
        },
        "conservative_analyst": {
            "analyst_name": "Conservative Analyst",
            "extra_state_factory": lambda state, report: {
                "risk_debate_state": {
                    **state["risk_debate_state"],
                    "history": state["risk_debate_state"].get("history", "") + "\nConservative Analyst: " + report,
                    "conservative_history": state["risk_debate_state"].get("conservative_history", "") + "\nConservative Analyst: " + report,
                    "latest_speaker": "Conservative",
                    "current_conservative_response": "Conservative Analyst: " + report,
                    "count": state["risk_debate_state"]["count"] + 1,
                }
            },
        },
        "portfolio_manager": {
            "analyst_name": "Portfolio Manager",
            "report_key": "final_trade_decision",
            "extra_state_factory": lambda state, report: {
                "risk_debate_state": {
                    **state["risk_debate_state"],
                    "judge_decision": report,
                    "latest_speaker": "Judge",
                }
            },
        },
    }

    @staticmethod
    def _order_selected_analysts(selected_analysts):
        if "macro" not in selected_analysts:
            return selected_analysts
        remaining = [analyst for analyst in selected_analysts if analyst != "macro"]
        return ["macro", *remaining]

    def __init__(
        self,
        quick_thinking_llm: ChatOpenAI,
        deep_thinking_llm: ChatOpenAI,
        tool_nodes: Dict[str, ToolNode],
        bull_memory,
        bear_memory,
        trader_memory,
        invest_judge_memory,
        portfolio_manager_memory,
        conditional_logic: ConditionalLogic,
        role_llms: Dict[str, Any] | None = None,
        social_sentiment_available: bool = False,
        single_pass_pipeline: bool = False,
        enable_resilience_wrappers: bool = True,
    ):
        """Initialize with required components."""
        self.quick_thinking_llm = quick_thinking_llm
        self.deep_thinking_llm = deep_thinking_llm
        self.role_llms = role_llms or {}
        self.tool_nodes = tool_nodes
        self.bull_memory = bull_memory
        self.bear_memory = bear_memory
        self.trader_memory = trader_memory
        self.invest_judge_memory = invest_judge_memory
        self.portfolio_manager_memory = portfolio_manager_memory
        self.conditional_logic = conditional_logic
        self.social_sentiment_available = social_sentiment_available
        self.single_pass_pipeline = single_pass_pipeline
        self.enable_resilience_wrappers = enable_resilience_wrappers
        self.market_analyst_llm = self._get_role_llm("market", self.quick_thinking_llm)
        self.social_analyst_llm = self._get_role_llm("social", self.quick_thinking_llm)
        self.news_analyst_llm = self._get_role_llm("news", self.quick_thinking_llm)
        self.fundamentals_analyst_llm = self._get_role_llm(
            "fundamentals", self.quick_thinking_llm
        )
        self.factor_rules_analyst_llm = self._get_role_llm(
            "factor_rules", self.quick_thinking_llm
        )
        self.valuation_analyst_llm = self._get_role_llm(
            "valuation", self.quick_thinking_llm
        )
        self.segment_analyst_llm = self._get_role_llm("segment", self.quick_thinking_llm)
        self.scenario_analyst_llm = self._get_role_llm("scenario", self.quick_thinking_llm)
        self.position_sizing_analyst_llm = self._get_role_llm(
            "position_sizing", self.quick_thinking_llm
        )
        self.macro_analyst_llm = self._get_role_llm("macro", self.quick_thinking_llm)
        self.bull_researcher_llm = self._get_role_llm(
            "bull_researcher", self.quick_thinking_llm
        )
        self.bear_researcher_llm = self._get_role_llm(
            "bear_researcher", self.quick_thinking_llm
        )
        self.research_manager_llm = self._get_role_llm(
            "research_manager", self.deep_thinking_llm
        )
        self.trader_llm = self._get_role_llm("trader", self.quick_thinking_llm)
        self.aggressive_analyst_llm = self._get_role_llm(
            "aggressive_analyst", self.quick_thinking_llm
        )
        self.neutral_analyst_llm = self._get_role_llm(
            "neutral_analyst", self.quick_thinking_llm
        )
        self.conservative_analyst_llm = self._get_role_llm(
            "conservative_analyst", self.quick_thinking_llm
        )
        self.portfolio_manager_llm = self._get_role_llm(
            "portfolio_manager", self.deep_thinking_llm
        )
        self.chief_analyst_llm = self._get_role_llm(
            "chief_analyst", self.deep_thinking_llm
        )

    def _get_role_llm(self, role: str, fallback_llm: ChatOpenAI):
        return self.role_llms.get(role, fallback_llm)

    def _get_continue_handler(self, analyst_type: str):
        specific_handler = getattr(
            self.conditional_logic,
            f"should_continue_{analyst_type}",
            None,
        )
        if specific_handler is not None:
            return specific_handler

        def default_handler(state: AgentState):
            messages = state["messages"]
            last_message = messages[-1]
            if getattr(last_message, "tool_calls", None):
                return f"tools_{analyst_type}"
            return f"Msg Clear {analyst_type.capitalize()}"

        return default_handler

    def setup_graph(
        self, selected_analysts=["market", "social", "news", "fundamentals", "macro"]
    ):
        """Set up and compile the agent workflow graph.

        Args:
            selected_analysts (list): List of analyst types to include. Options are:
                - "market": Market analyst
                - "social": Social media analyst
                - "news": News analyst
                - "fundamentals": Fundamentals analyst
                - "factor_rules": Factor rule analyst
                - "valuation": Valuation analyst
                - "segment": Segment analyst
                - "scenario": Scenario and catalyst analyst
                - "position_sizing": Position sizing analyst
                - "macro": Macro analyst
        """
        if len(selected_analysts) == 0:
            raise ValueError("Trading Agents Graph Setup Error: no analysts selected!")
        selected_analysts = self._order_selected_analysts(list(selected_analysts))

        # Create analyst nodes
        analyst_nodes = {}
        delete_nodes = {}
        tool_nodes = {}

        if "market" in selected_analysts:
            analyst_nodes["market"] = create_market_analyst(
                self.market_analyst_llm
            )
            delete_nodes["market"] = create_msg_delete()
            tool_nodes["market"] = self.tool_nodes["market"]

        if "social" in selected_analysts:
            analyst_nodes["social"] = create_social_media_analyst(
                self.social_analyst_llm,
                social_sentiment_available=self.social_sentiment_available,
            )
            delete_nodes["social"] = create_msg_delete()
            tool_nodes["social"] = self.tool_nodes["social"]

        if "news" in selected_analysts:
            analyst_nodes["news"] = create_news_analyst(
                self.news_analyst_llm
            )
            delete_nodes["news"] = create_msg_delete()
            tool_nodes["news"] = self.tool_nodes["news"]

        if "fundamentals" in selected_analysts:
            analyst_nodes["fundamentals"] = create_fundamentals_analyst(
                self.fundamentals_analyst_llm
            )
            delete_nodes["fundamentals"] = create_msg_delete()
            tool_nodes["fundamentals"] = self.tool_nodes["fundamentals"]

        if "factor_rules" in selected_analysts:
            analyst_nodes["factor_rules"] = create_factor_rule_analyst(
                self.factor_rules_analyst_llm
            )
            delete_nodes["factor_rules"] = create_msg_delete()

        if "valuation" in selected_analysts:
            analyst_nodes["valuation"] = create_valuation_analyst(
                self.valuation_analyst_llm
            )
            delete_nodes["valuation"] = create_msg_delete()
            tool_nodes["valuation"] = self.tool_nodes["valuation"]

        if "segment" in selected_analysts:
            analyst_nodes["segment"] = create_segment_analyst(self.segment_analyst_llm)
            delete_nodes["segment"] = create_msg_delete()
            tool_nodes["segment"] = self.tool_nodes["segment"]

        if "scenario" in selected_analysts:
            analyst_nodes["scenario"] = create_scenario_catalyst_analyst(
                self.scenario_analyst_llm
            )
            delete_nodes["scenario"] = create_msg_delete()
            tool_nodes["scenario"] = self.tool_nodes["scenario"]

        if "position_sizing" in selected_analysts:
            analyst_nodes["position_sizing"] = create_position_sizing_analyst(
                self.position_sizing_analyst_llm
            )
            delete_nodes["position_sizing"] = create_msg_delete()
            tool_nodes["position_sizing"] = self.tool_nodes["position_sizing"]

        if "macro" in selected_analysts:
            analyst_nodes["macro"] = create_macro_analyst(self.macro_analyst_llm)
            delete_nodes["macro"] = create_msg_delete()
            tool_nodes["macro"] = self.tool_nodes["macro"]

        if self.enable_resilience_wrappers:
            for analyst_type, node in list(analyst_nodes.items()):
                resilience = self.QUICK_ANALYST_RESILIENCE.get(analyst_type)
                if resilience:
                    analyst_nodes[analyst_type] = wrap_quick_analyst_node(
                        node,
                        analyst_name=resilience["analyst_name"],
                        report_key=resilience.get("report_key"),
                        extra_state_factory=resilience.get("extra_state_factory"),
                    )

        # Create researcher and manager nodes
        bull_researcher_node = create_bull_researcher(
            self.bull_researcher_llm, self.bull_memory
        )
        bear_researcher_node = create_bear_researcher(
            self.bear_researcher_llm, self.bear_memory
        )
        research_manager_node = create_research_manager(
            self.research_manager_llm, self.invest_judge_memory
        )
        trader_node = create_trader(self.trader_llm, self.trader_memory)

        # Create risk analysis nodes
        aggressive_analyst = create_aggressive_debator(self.aggressive_analyst_llm)
        neutral_analyst = create_neutral_debator(self.neutral_analyst_llm)
        conservative_analyst = create_conservative_debator(
            self.conservative_analyst_llm
        )
        portfolio_manager_node = create_portfolio_manager(
            self.portfolio_manager_llm, self.portfolio_manager_memory
        )
        chief_analyst_node = create_chief_analyst(self.chief_analyst_llm)

        if self.enable_resilience_wrappers:
            bull_researcher_node = wrap_quick_analyst_node(
                bull_researcher_node,
                analyst_name=self.QUICK_ANALYST_RESILIENCE["bull_researcher"]["analyst_name"],
                extra_state_factory=self.QUICK_ANALYST_RESILIENCE["bull_researcher"]["extra_state_factory"],
            )
            bear_researcher_node = wrap_quick_analyst_node(
                bear_researcher_node,
                analyst_name=self.QUICK_ANALYST_RESILIENCE["bear_researcher"]["analyst_name"],
                extra_state_factory=self.QUICK_ANALYST_RESILIENCE["bear_researcher"]["extra_state_factory"],
            )
            research_manager_node = wrap_quick_analyst_node(
                research_manager_node,
                analyst_name=self.QUICK_ANALYST_RESILIENCE["research_manager"]["analyst_name"],
                report_key=self.QUICK_ANALYST_RESILIENCE["research_manager"]["report_key"],
                extra_state_factory=self.QUICK_ANALYST_RESILIENCE["research_manager"]["extra_state_factory"],
            )
            trader_node = wrap_quick_analyst_node(
                trader_node,
                analyst_name=self.QUICK_ANALYST_RESILIENCE["trader"]["analyst_name"],
                report_key=self.QUICK_ANALYST_RESILIENCE["trader"]["report_key"],
                extra_state_factory=self.QUICK_ANALYST_RESILIENCE["trader"]["extra_state_factory"],
            )
            aggressive_analyst = wrap_quick_analyst_node(
                aggressive_analyst,
                analyst_name=self.QUICK_ANALYST_RESILIENCE["aggressive_analyst"]["analyst_name"],
                extra_state_factory=self.QUICK_ANALYST_RESILIENCE["aggressive_analyst"]["extra_state_factory"],
            )
            neutral_analyst = wrap_quick_analyst_node(
                neutral_analyst,
                analyst_name=self.QUICK_ANALYST_RESILIENCE["neutral_analyst"]["analyst_name"],
                extra_state_factory=self.QUICK_ANALYST_RESILIENCE["neutral_analyst"]["extra_state_factory"],
            )
            conservative_analyst = wrap_quick_analyst_node(
                conservative_analyst,
                analyst_name=self.QUICK_ANALYST_RESILIENCE["conservative_analyst"]["analyst_name"],
                extra_state_factory=self.QUICK_ANALYST_RESILIENCE["conservative_analyst"]["extra_state_factory"],
            )
            portfolio_manager_node = wrap_quick_analyst_node(
                portfolio_manager_node,
                analyst_name=self.QUICK_ANALYST_RESILIENCE["portfolio_manager"]["analyst_name"],
                report_key=self.QUICK_ANALYST_RESILIENCE["portfolio_manager"]["report_key"],
                extra_state_factory=self.QUICK_ANALYST_RESILIENCE["portfolio_manager"]["extra_state_factory"],
            )

        # Create workflow
        workflow = StateGraph(AgentState)

        # Add analyst nodes to the graph
        for analyst_type, node in analyst_nodes.items():
            workflow.add_node(f"{analyst_type.capitalize()} Analyst", node)
            workflow.add_node(
                f"Msg Clear {analyst_type.capitalize()}", delete_nodes[analyst_type]
            )
            if analyst_type in tool_nodes:
                workflow.add_node(f"tools_{analyst_type}", tool_nodes[analyst_type])

        # Add other nodes
        workflow.add_node("Bull Researcher", bull_researcher_node)
        workflow.add_node("Bear Researcher", bear_researcher_node)
        workflow.add_node("Research Manager", research_manager_node)
        workflow.add_node("Trader", trader_node)
        workflow.add_node("Aggressive Analyst", aggressive_analyst)
        workflow.add_node("Neutral Analyst", neutral_analyst)
        workflow.add_node("Conservative Analyst", conservative_analyst)
        workflow.add_node("Portfolio Manager", portfolio_manager_node)
        workflow.add_node("Chief Analyst", chief_analyst_node)

        # Define edges
        # Start with the first analyst
        first_analyst = selected_analysts[0]
        workflow.add_edge(START, f"{first_analyst.capitalize()} Analyst")

        # Connect analysts in sequence
        for i, analyst_type in enumerate(selected_analysts):
            current_analyst = f"{analyst_type.capitalize()} Analyst"
            current_tools = f"tools_{analyst_type}"
            current_clear = f"Msg Clear {analyst_type.capitalize()}"

            # Add conditional edges for current analyst
            workflow.add_conditional_edges(
                current_analyst,
                self._get_continue_handler(analyst_type),
                [current_tools, current_clear]
                if analyst_type in tool_nodes
                else [current_clear],
            )
            if analyst_type in tool_nodes:
                workflow.add_edge(current_tools, current_analyst)

            # Connect to next analyst or to Bull Researcher if this is the last analyst
            if i < len(selected_analysts) - 1:
                next_analyst = f"{selected_analysts[i+1].capitalize()} Analyst"
                workflow.add_edge(current_clear, next_analyst)
            else:
                workflow.add_edge(current_clear, "Bull Researcher")

        # Add remaining edges
        if self.single_pass_pipeline:
            workflow.add_edge("Bull Researcher", "Bear Researcher")
            workflow.add_edge("Bear Researcher", "Research Manager")
            workflow.add_edge("Research Manager", "Trader")
            workflow.add_edge("Trader", "Aggressive Analyst")
            workflow.add_edge("Aggressive Analyst", "Conservative Analyst")
            workflow.add_edge("Conservative Analyst", "Neutral Analyst")
            workflow.add_edge("Neutral Analyst", "Portfolio Manager")
        else:
            workflow.add_conditional_edges(
                "Bull Researcher",
                self.conditional_logic.should_continue_debate,
                {
                    "Bear Researcher": "Bear Researcher",
                    "Research Manager": "Research Manager",
                },
            )
            workflow.add_conditional_edges(
                "Bear Researcher",
                self.conditional_logic.should_continue_debate,
                {
                    "Bull Researcher": "Bull Researcher",
                    "Research Manager": "Research Manager",
                },
            )
            workflow.add_edge("Research Manager", "Trader")
            workflow.add_edge("Trader", "Aggressive Analyst")
            workflow.add_conditional_edges(
                "Aggressive Analyst",
                self.conditional_logic.should_continue_risk_analysis,
                {
                    "Conservative Analyst": "Conservative Analyst",
                    "Portfolio Manager": "Portfolio Manager",
                },
            )
            workflow.add_conditional_edges(
                "Conservative Analyst",
                self.conditional_logic.should_continue_risk_analysis,
                {
                    "Neutral Analyst": "Neutral Analyst",
                    "Portfolio Manager": "Portfolio Manager",
                },
            )
            workflow.add_conditional_edges(
                "Neutral Analyst",
                self.conditional_logic.should_continue_risk_analysis,
                {
                    "Aggressive Analyst": "Aggressive Analyst",
                    "Portfolio Manager": "Portfolio Manager",
                },
            )

        workflow.add_edge("Portfolio Manager", "Chief Analyst")
        workflow.add_edge("Chief Analyst", END)

        # Compile and return
        return workflow.compile()
