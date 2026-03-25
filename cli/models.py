from enum import Enum


class AnalysisMode(str, Enum):
    STOCK = "stock"
    POLYMARKET = "polymarket"


class AnalystType(str, Enum):
    MARKET = "market"
    SOCIAL = "social"
    NEWS = "news"
    FUNDAMENTALS = "fundamentals"
