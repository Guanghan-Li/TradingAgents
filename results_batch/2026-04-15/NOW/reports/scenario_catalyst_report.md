## NOW Scenario Framing
ServiceNow (`NOW`) sets up as a high-expectation software name with a sharp forward earnings step-up implied by valuation data: `56.4x` trailing P/E versus `18.8x` forward P/E. That supports a constructive medium-term case if Q1 execution confirms AI monetization and margin durability, but it also raises near-term event risk because the stock is trading well below its `200-day` average and recent coverage flags an AI disruption narrative ahead of Q1 results.

Base case (`50%`): execution remains solid, AI messaging is good enough to defend the multiple, and macro stays broadly supportive with an upward-sloping yield curve and stable Fed backdrop. Bull case (`30%`): Q1 results and guidance show AI products are expanding deal sizes and international traction, including workflow expansion in Brazil, driving a rerating toward growth-software leadership. Bear case (`20%`): Q1 commentary reinforces concerns that AI competition compresses differentiation or elongates enterprise buying cycles, leading to multiple pressure despite decent fundamentals.

### Catalyst Table
| Catalyst | Date or Window | Related Scenarios | Expected Impact | Confidence |
| --- | --- | --- | --- | --- |
| Q1 2026 earnings and guidance for `NOW` | Late April 2026 window, exact date not provided | Bull, Base, Bear | Highest-impact company event; confirms or breaks AI monetization and margin narrative | Medium |
| Post-earnings sell-side revisions | 1-5 trading days after Q1 results | Bull, Bear | Target/estimate revisions could materially move sentiment given valuation debate | Medium |
| AI Workflow Hub expansion in Brazil / international AI adoption updates | Q2 2026 | Bull, Base | Positive if it translates into pipeline acceleration outside core U.S. enterprise demand | Low-Medium |
| Monthly inflation prints and rate repricing | April-May 2026 | Base, Bear | Sticky CPI/PPI or higher long yields would pressure long-duration software multiples | Medium |
| Enterprise software buying behavior amid AI-led discovery changes | Ongoing through Q2 2026 | Bull, Bear | Helpful if `NOW` captures AI budgets; harmful if AI disruption narrative intensifies | Medium |

### Signposts
- Q1 subscription growth, cRPO/backlog tone, and management commentary on AI attach rates.
- Whether forward EPS progression toward `5.02` remains credible without margin slippage.
- Evidence that international AI expansion is creating real demand, not just branding.
- Whether the stock can reclaim the `50-day` moving average first and stabilize versus the much higher `200-day` average.
- Any change in enterprise spending tone if inflation and long yields stay firm.

### Invalidation Logic
The constructive thesis weakens materially if Q1 results show AI enthusiasm without measurable revenue conversion, if guidance is cut or billings/cRPO soften, or if competitive commentary suggests `NOW` is losing strategic relevance in workflow automation. The bearish thesis is invalidated if management demonstrates durable AI-driven upsell, stable margins, and international expansion that lifts forward estimates rather than merely defending them.

```json
{
  "scenario_map": [
    {
      "name": "Bull",
      "probability_pct": 30,
      "thesis": "Q1 2026 results validate AI monetization, enterprise demand stays resilient, and international expansion such as Brazil adds incremental growth confidence. The large gap between trailing and forward P/E compresses through earnings growth rather than multiple contraction.",
      "valuation_implication": "Multiple stabilizes or rerates higher as investors underwrite stronger forward earnings and renewed premium-software leadership.",
      "signposts": [
        "Q1 revenue and guidance beat with strong subscription commentary",
        "Clear evidence of AI upsell or larger deal sizes",
        "Margins remain durable while forward EPS expectations hold or rise",
        "Positive sell-side estimate revisions after earnings"
      ]
    },
    {
      "name": "Base",
      "probability_pct": 50,
      "thesis": "ServiceNow posts solid but not spectacular results, preserving confidence in core workflow demand while leaving debate open on how much AI contributes near term. Macro remains neutral enough that valuation does not break, but upside is capped until execution proves out.",
      "valuation_implication": "Shares trade range-bound with modest recovery potential if estimates hold and macro rates stay contained.",
      "signposts": [
        "In-line or slightly better Q1 results",
        "Management defends AI positioning but gives limited hard monetization detail",
        "Forward EPS remains broadly intact",
        "Macro and long-end yields stay manageable for software multiples"
      ]
    },
    {
      "name": "Bear",
      "probability_pct": 20,
      "thesis": "Q1 results or guidance amplify the AI disruption narrative flagged by recent coverage, showing weaker differentiation, slower enterprise commitment, or elongating sales cycles. Higher-for-longer yields and premium-software derating then compound the downside.",
      "valuation_implication": "Multiple compresses further as investors question whether the forward earnings step-up is achievable.",
      "signposts": [
        "Miss or softer-than-expected guidance in Q1",
        "Weak commentary on AI demand conversion or competitive positioning",
        "Evidence of slower deal cycles or pressured billings/cRPO",
        "Rising long-term yields that weigh on software valuation"
      ]
    }
  ],
  "dated_catalyst_map": [
    {
      "catalyst": "Q1 2026 earnings release and guidance for NOW",
      "date_or_window": "Late April 2026, exact date not provided in context",
      "related_scenarios": ["Bull", "Base", "Bear"],
      "expected_impact": "Very high; primary catalyst for AI monetization, demand durability, and margin credibility",
      "confidence": "Medium"
    },
    {
      "catalyst": "Post-earnings analyst estimate and target changes",
      "date_or_window": "1-5 trading days after Q1 earnings",
      "related_scenarios": ["Bull", "Bear"],
      "expected_impact": "High; sentiment and valuation could move quickly because current debate is expectation-sensitive",
      "confidence": "Medium"
    },
    {
      "catalyst": "AI Workflow Hub expansion and Brazil-related execution updates",
      "date_or_window": "Q2 2026",
      "related_scenarios": ["Bull", "Base"],
      "expected_impact": "Moderate; supports international growth narrative if tied to measurable pipeline or bookings",
      "confidence": "Low-Medium"
    },
    {
      "catalyst": "Monthly CPI/PPI and rate repricing",
      "date_or_window": "April-May 2026",
      "related_scenarios": ["Base", "Bear"],
      "expected_impact": "Moderate to high; firmer inflation or higher long yields could pressure premium software multiples",
      "confidence": "Medium"
    },
    {
      "catalyst": "Enterprise software buying behavior shifts as AI changes research and procurement patterns",
      "date_or_window": "Ongoing through Q2 2026",
      "related_scenarios": ["Bull", "Bear"],
      "expected_impact": "Moderate; could either expand NOW's strategic relevance or intensify disruption concerns",
      "confidence": "Medium"
    }
  ],
  "invalidation_triggers": [
    {
      "trigger": "Q1 results fail to show credible AI revenue conversion and management reduces growth or margin confidence",
      "affected_scenarios": ["Bull", "Base"],
      "severity": "High",
      "evidence_to_watch": "Revenue/guidance miss, weak cRPO or billings tone, lower forward EPS framework"
    },
    {
      "trigger": "Competitive commentary implies NOW is losing workflow or AI relevance",
      "affected_scenarios": ["Bull", "Base"],
      "severity": "High",
      "evidence_to_watch": "Management language on pricing pressure, displacement, slower win rates, or weaker attach rates"
    },
    {
      "trigger": "Long-duration software rerates lower because inflation stays sticky and 10Y yields remain elevated or rise further",
      "affected_scenarios": ["Base"],
      "severity": "Medium",
      "evidence_to_watch": "Higher CPI/PPI prints, rising Treasury yields, broader software multiple compression"
    },
    {
      "trigger": "Strong Q1 beat with clear AI upsell and stable margins",
      "affected_scenarios": ["Bear"],
      "severity": "High",
      "evidence_to_watch": "Raised guidance, positive estimate revisions, improved sentiment on AI differentiation"
    }
  ]
}
```