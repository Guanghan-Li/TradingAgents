## TSM Scenario Summary

TSM enters this window with strong operating momentum: recent Q1 beat and higher guidance, very high profitability (about 45.1% net margin, 53.9% operating margin), strong free cash flow, and a large gap between trailing and forward earnings multiples (`34.7x` TTM vs `19.2x` forward), which implies the market is underwriting a sizable earnings step-up. Macro is supportive but not clean: the yield curve is positively sloped, Fed policy is broadly neutral, and inflation remains firm enough to keep duration sensitivity relevant for a high-multiple AI beneficiary like TSM.

**Bull case (30%)**: AI accelerator demand stays supply-constrained, TSM sustains upward revisions, advanced-node mix keeps expanding, and investors tolerate premium valuation because earnings are outrunning it. This supports further multiple durability and upward EPS revisions.

**Base case (50%)**: TSM remains fundamentally strong, but post-beat upside gets more selective. Revenue growth continues, though expectations are already elevated after the guide-up. Shares can still work, but mostly through execution and estimates rising rather than large multiple expansion.

**Bear case (20%)**: Expectations prove too rich versus delivery. Any sign of AI order normalization, margin pressure from overseas fabs/capex intensity, or renewed geopolitical/policy risk around Taiwan would likely compress the premium quickly.

| Catalyst | Date / Window | Related Scenarios | Expected Impact | Confidence |
| --- | --- | --- | --- | --- |
| TSM post-Q1 follow-through in monthly sales / customer demand commentary | Late Apr to May 2026 | Bull, Base, Bear | Confirms whether guide-up is broadening or was only a strong quarter | Medium |
| US inflation prints and rates repricing | Apr to Jun 2026 | Base, Bear | Higher-for-longer yields pressure premium semiconductor multiples | Medium |
| Fed communication / FOMC window | Jun 2026 | Base, Bear | Neutral-to-dovish tone helps duration-sensitive leaders like TSM; hawkish tone weighs on valuation | Medium |
| Customer AI demand and GPU/ASIC ramp evidence | Q2 2026 | Bull, Base | Reinforces advanced packaging and leading-edge utilization strength | Medium |
| TSM next earnings / guidance reset | July 2026 window | Bull, Base, Bear | Most important near-term test of whether forward EPS expectations remain too low or too high | Medium |
| Geopolitical or trade-policy headlines affecting Taiwan / semis | Any time | Bear | Fast multiple compression regardless of near-term fundamentals | Low-Medium |

**Key signposts for TSM**

- Upward estimate revisions need to continue; the forward multiple only looks reasonable if earnings keep catching up.
- Evidence that advanced-node and AI-related capacity remains tight is the clearest bull signal.
- Watch whether margins stay resilient despite expansion spending and offshore manufacturing buildout.
- If macro rates rise while growth expectations flatten, TSM becomes more vulnerable to de-rating even with good operating results.

**Invalidation logic**

- Bull case is weakened if demand commentary stops improving, monthly sales momentum cools materially, or margin progression stalls.
- Base case is weakened if TSM delivers another major upside revision cycle, because that would argue expectations are still too low.
- Bear case is weakened if TSM keeps posting beats with rising guidance and no visible geopolitical or policy escalation.

```json
{
  "scenario_map": [
    {
      "name": "Bull",
      "probability_pct": 30,
      "thesis": "TSM extends its AI-led foundry leadership, recent guide-up is followed by additional estimate revisions, and leading-edge plus advanced-packaging demand remains supply-constrained.",
      "valuation_implication": "Premium valuation holds or expands modestly as forward earnings rise fast enough to justify the multiple.",
      "signposts": [
        "Continued monthly sales strength after the Q1 beat",
        "Further customer AI ramp commentary",
        "Sustained leading-edge utilization and resilient margins",
        "Positive earnings estimate revisions"
      ]
    },
    {
      "name": "Base",
      "probability_pct": 50,
      "thesis": "TSM remains fundamentally strong, but the stock shifts into an execution-driven phase where good results are needed to defend already-elevated expectations.",
      "valuation_implication": "Multiple stays roughly stable; returns depend more on earnings growth than on further rerating.",
      "signposts": [
        "Growth remains solid but less surprising after the guide-up",
        "Margins remain healthy despite capex and footprint expansion",
        "Macro rates stay range-bound",
        "No major geopolitical escalation"
      ]
    },
    {
      "name": "Bear",
      "probability_pct": 20,
      "thesis": "TSM faces expectation compression from softer AI demand trajectory, margin drag from expansion costs, or renewed geopolitical or trade-policy stress.",
      "valuation_implication": "Forward multiple compresses and the stock underperforms even if absolute earnings remain strong.",
      "signposts": [
        "Cooling monthly sales momentum",
        "Less constructive customer capex commentary",
        "Margin pressure tied to overseas fabs or mix",
        "Taiwan or semiconductor trade-policy shocks"
      ]
    }
  ],
  "dated_catalyst_map": [
    {
      "catalyst": "Post-Q1 sales and demand follow-through for TSM",
      "date_or_window": "Late April to May 2026",
      "related_scenarios": ["Bull", "Base", "Bear"],
      "expected_impact": "Tests whether the recent beat and higher guidance represent a durable acceleration.",
      "confidence": "Medium"
    },
    {
      "catalyst": "US CPI/PPI and rates repricing",
      "date_or_window": "April to June 2026",
      "related_scenarios": ["Base", "Bear"],
      "expected_impact": "Sticky inflation and higher yields would pressure valuation for TSM and other premium semiconductor names.",
      "confidence": "Medium"
    },
    {
      "catalyst": "Fed communication and FOMC window",
      "date_or_window": "June 2026",
      "related_scenarios": ["Base", "Bear"],
      "expected_impact": "A neutral or dovish read supports risk appetite; a hawkish read raises discount-rate pressure.",
      "confidence": "Medium"
    },
    {
      "catalyst": "Customer AI ramp and packaging demand evidence for TSM",
      "date_or_window": "Q2 2026",
      "related_scenarios": ["Bull", "Base"],
      "expected_impact": "Strength would reinforce the thesis that AI demand is still outrunning supply at the leading edge.",
      "confidence": "Medium"
    },
    {
      "catalyst": "Next TSM earnings and guidance reset",
      "date_or_window": "July 2026 window",
      "related_scenarios": ["Bull", "Base", "Bear"],
      "expected_impact": "Primary test of whether forward EPS assumptions need to move materially up or down.",
      "confidence": "Medium"
    },
    {
      "catalyst": "Taiwan or semiconductor trade-policy/geopolitical headlines affecting TSM",
      "date_or_window": "Any time",
      "related_scenarios": ["Bear"],
      "expected_impact": "Could cause abrupt multiple compression regardless of operating execution.",
      "confidence": "Low-Medium"
    }
  ],
  "invalidation_triggers": [
    {
      "trigger": "Monthly sales or customer commentary for TSM decelerates materially after the recent guide-up",
      "affected_scenarios": ["Bull"],
      "severity": "High",
      "evidence_to_watch": "Monthly revenue releases, customer capex commentary, analyst estimate revisions"
    },
    {
      "trigger": "TSM delivers another significant beat-and-raise cycle that exceeds already improved expectations",
      "affected_scenarios": ["Base", "Bear"],
      "severity": "High",
      "evidence_to_watch": "Quarterly results, guidance changes, consensus forward EPS revisions"
    },
    {
      "trigger": "Gross or operating margin compression becomes persistent rather than transitory",
      "affected_scenarios": ["Bull", "Base"],
      "severity": "Medium-High",
      "evidence_to_watch": "Quarterly margin trends, fab ramp commentary, capex intensity"
    },
    {
      "trigger": "Material escalation in Taiwan geopolitical risk or semiconductor trade restrictions",
      "affected_scenarios": ["Bull", "Base"],
      "severity": "High",
      "evidence_to_watch": "Government policy statements, export-control developments, regional security headlines"
    },
    {
      "trigger": "Rates move higher while inflation stays sticky, reducing appetite for premium-duration equities like TSM",
      "affected_scenarios": ["Bull", "Base"],
      "severity": "Medium",
      "evidence_to_watch": "CPI, PPI, Treasury yields, Fed communication"
    }
  ]
}
```