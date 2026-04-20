## JPM Scenario Framing
JPM enters this window with strong absolute profitability, a premium-but-not-extreme bank valuation, and supportive macro carry. The prefetched context shows solid earnings power (`14.8x` TTM P/E, `13.1x` forward P/E, `2.41x` P/B, `16.5%` ROE), while the macro backdrop remains broadly constructive for large diversified banks: the Fed funds rate is `3.64%`, unemployment is still low at `4.3%`, and the 2Y/10Y curve is positively sloped by `53 bps`. Near-term news flow also leans favorable on capital markets performance, though private credit risk and regulatory uncertainty remain the main swing factors.

My base case is that JPM stays in a high-quality compounding lane rather than re-rating sharply. The bull case depends on sustained markets/IB strength, resilient credit, and no material regulatory capital surprise. The bear case is a mix of fee/trading normalization, reserve builds tied to private credit or consumer stress, and a less favorable rate/curve setup.

| Scenario | Prob. | What Has To Be True | Market Read-Through |
| --- | ---: | --- | --- |
| Bull | 30% | Capital markets and asset/wealth trends remain strong, credit losses stay contained, and regulation does not materially impair capital returns | JPM can sustain a premium multiple and push toward/highly retest the 52-week high zone |
| Base | 50% | Core banking stays healthy, fee income normalizes but remains solid, and macro stays stable with modest growth | Shares likely trade around current valuation bands with earnings growth doing most of the work |
| Bear | 20% | Credit costs rise faster than expected, private credit concerns spread, or regulation/rates pressure profitability | Multiple compresses toward large-bank averages and the stock de-rates toward book-driven support |

### Key Signposts
- Net interest income resilience versus a now-more-neutral Fed backdrop.
- Whether strong Q1 capital markets performance is durable or just a favorable quarter.
- Any reserve build or charge-off commentary tied to commercial credit, consumer credit, or private credit exposures.
- Management commentary on regulation, capital requirements, and capital return flexibility.
- Yield-curve behavior: a still-positive curve helps, but renewed flattening would pressure the thesis.

### Invalidation Logic
- Bull case is invalidated if JPM posts clear credit deterioration, materially weaker fee/trading momentum, or guides to a more constrained capital/regulatory outlook.
- Base case is invalidated if either upside becomes obviously stronger than “steady compounder” or downside shifts into a genuine credit-cost cycle.
- Bear case is invalidated if reserve trends stay benign and management shows that earnings breadth across consumer, corporate, markets, and asset management can offset rate normalization.

### Catalyst Table
| Catalyst | Date Or Window | Related Scenarios | Expected Impact | Confidence |
| --- | --- | --- | --- | --- |
| JPM Q1 2026 earnings read-through and management commentary | Mid-April 2026 / immediate | Bull, Base, Bear | High: sets tone on markets revenue, credit, guidance, and regulation | High |
| Peer big-bank earnings and sector read-through | April 2026 earnings season | Bull, Base, Bear | Medium-High: confirms whether JPM strength is firm-specific or industry-wide | High |
| Next CPI/PPI/NFP cycle | Late April to early May 2026 | Base, Bear | Medium: shapes rate path, curve, and recession/credit expectations | Medium |
| Next Fed communication/policy window | Next 4-8 weeks | Base, Bear, Bull | Medium: impacts NII outlook and bank multiple support | Medium |
| Private credit / regulatory headlines | Ongoing through Q2 2026 | Bull, Bear | Medium-High: swing factor for sentiment, reserve assumptions, and capital treatment | Medium |

```json
{
  "scenario_map": [
    {
      "name": "Bull",
      "probability_pct": 30,
      "thesis": "JPM sustains above-consensus earnings power as capital markets and asset/wealth businesses remain strong, credit quality stays controlled, and the still-positive yield curve supports core banking profitability without a major regulatory capital hit.",
      "valuation_implication": "Premium large-bank valuation is sustained or expands modestly, supporting a retest of the upper end of the recent trading range and potentially the 52-week high area.",
      "signposts": [
        "Strong markets and investment banking revenue beyond a single quarter",
        "Stable reserve build and benign net charge-off commentary",
        "Resilient net interest income despite a more neutral Fed backdrop",
        "No materially adverse regulatory capital surprise"
      ]
    },
    {
      "name": "Base",
      "probability_pct": 50,
      "thesis": "JPM remains a high-quality diversified bank compounder with stable core banking, decent fee income, and manageable credit costs, but upside is moderated by normalization in trading/investment banking and an already solid valuation.",
      "valuation_implication": "Shares trade near current valuation bands, with forward earnings growth carrying returns more than multiple expansion.",
      "signposts": [
        "Management reiterates a steady but not accelerating outlook",
        "Capital markets remain good but normalize from Q1 strength",
        "Credit metrics stay healthy with only modest reserve adjustments",
        "Macro data remains consistent with slowing-but-positive growth"
      ]
    },
    {
      "name": "Bear",
      "probability_pct": 20,
      "thesis": "JPM faces multiple compression if credit costs rise, private credit or commercial exposures become a broader concern, fee/trading momentum fades, or policy/rate dynamics turn less supportive for bank earnings.",
      "valuation_implication": "Stock de-rates toward lower large-bank multiples, with downside more anchored by book value than by current earnings power.",
      "signposts": [
        "Reserve builds accelerate or management flags deteriorating credit",
        "Capital markets revenue falls back sharply after a strong quarter",
        "Yield curve flattens materially or recession fears rise",
        "Regulatory or capital-return constraints worsen"
      ]
    }
  ],
  "dated_catalyst_map": [
    {
      "catalyst": "JPM Q1 2026 earnings read-through and management commentary",
      "date_or_window": "Mid-April 2026 / immediate",
      "related_scenarios": ["Bull", "Base", "Bear"],
      "expected_impact": "High",
      "confidence": "High"
    },
    {
      "catalyst": "Peer big-bank earnings and sector read-through",
      "date_or_window": "April 2026 earnings season",
      "related_scenarios": ["Bull", "Base", "Bear"],
      "expected_impact": "Medium-High",
      "confidence": "High"
    },
    {
      "catalyst": "Next CPI/PPI/NFP macro cycle",
      "date_or_window": "Late April to early May 2026",
      "related_scenarios": ["Base", "Bear"],
      "expected_impact": "Medium",
      "confidence": "Medium"
    },
    {
      "catalyst": "Next Fed communication or policy window",
      "date_or_window": "Next 4-8 weeks",
      "related_scenarios": ["Base", "Bear", "Bull"],
      "expected_impact": "Medium",
      "confidence": "Medium"
    },
    {
      "catalyst": "Private credit and regulatory headlines",
      "date_or_window": "Ongoing through Q2 2026",
      "related_scenarios": ["Bull", "Bear"],
      "expected_impact": "Medium-High",
      "confidence": "Medium"
    }
  ],
  "invalidation_triggers": [
    {
      "trigger": "Material reserve build or clearly worsening charge-off trends",
      "affected_scenarios": ["Bull", "Base"],
      "severity": "High",
      "evidence_to_watch": "Quarterly provision expense, management comments on commercial/consumer/private credit stress"
    },
    {
      "trigger": "Sharp normalization in trading and investment banking revenue after Q1 strength",
      "affected_scenarios": ["Bull"],
      "severity": "Medium-High",
      "evidence_to_watch": "Capital markets revenue guidance and peer-bank read-through"
    },
    {
      "trigger": "Yield-curve flattening or renewed recession scare that weakens NII expectations",
      "affected_scenarios": ["Bull", "Base"],
      "severity": "Medium",
      "evidence_to_watch": "2Y-10Y spread, Fed repricing, management NII outlook"
    },
    {
      "trigger": "More punitive regulatory capital or capital-return constraints",
      "affected_scenarios": ["Bull", "Base"],
      "severity": "Medium-High",
      "evidence_to_watch": "Management commentary, regulatory proposals, stress-capital and buyback language"
    },
    {
      "trigger": "Credit stays benign and earnings breadth remains strong across banking, markets, and asset management",
      "affected_scenarios": ["Bear"],
      "severity": "High",
      "evidence_to_watch": "Stable provisions, healthy fee mix, unchanged or improved forward guidance"
    }
  ]
}
```