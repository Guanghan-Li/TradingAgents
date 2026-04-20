from enum import Enum


class AnalysisMode(str, Enum):
    STOCK = "stock"
    POLYMARKET = "polymarket"


class AnalystType(str, Enum):
    MARKET = "market"
    SOCIAL = "social"
    NEWS = "news"
    FUNDAMENTALS = "fundamentals"
    MACRO = "macro"
    FACTOR_RULES = "factor_rules"
    VALUATION = "valuation"
    SEGMENT = "segment"
    SCENARIO = "scenario"
    POSITION_SIZING = "position_sizing"


class PMAnalystType(str, Enum):
    EVENT = "event"
    ODDS = "odds"
    INFORMATION = "information"
    SENTIMENT = "sentiment"
