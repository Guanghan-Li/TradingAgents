## NOW Scenario Framing

ServiceNow (`NOW`) screens as a high-quality software compounder with strong cash generation, but the setup is still rate- and execution-sensitive. The core bull argument is that `NOW` can defend premium software multiples because fundamentals remain solid: ~$13.3B TTM revenue, ~16.5% operating margin, ~$5.0B free cash flow, and a large gap between trailing and forward EPS/PE that implies material earnings expansion if execution holds. The base case is that `NOW` continues to grow into valuation, but multiple expansion stays limited while long-duration software remains tied to macro and yields. The bear case is that premium valuation support weakens if enterprise demand moderates, AI monetization takes longer than expected, or 10Y yields remain elevated near 4.3%.

Probability-weighted view: **Base 50% / Bull 30% / Bear 20%**.

Key signposts for `NOW` are subscription/revenue growth durability, margin expansion versus reinvestment, commentary on AI/pro workflow monetization, and whether macro stays benign enough for software multiples to hold. Invalidation is straightforward: the bull case breaks if growth decelerates materially or management signals elongating deal cycles; the bear case weakens if `NOW` posts another clean beat/raise with stable enterprise spending and expanding margins.

| Catalyst | Date or Window | Related Scenarios | Expected Impact | Confidence |
| --- | --- | --- | --- | --- |
| `NOW` next earnings / guidance update | Late April to early May 2026 (inferred, not confirmed in provided context) | Bull, Base, Bear | Highest-impact company catalyst for growth durability, cRPO/backlog tone, margins, and AI monetization commentary | Medium |
| CPI / inflation trend | Next monthly print after March 2026 data | Base, Bear, Bull | Cooler inflation supports duration-sensitive software multiples; hotter inflation pressures valuation | High |
| Fed policy path / rate expectations | Into next FOMC window after 2026-04-16 | Base, Bear, Bull | Stable-to-easing policy helps premium software; hawkish repricing is a multiple headwind | Medium |
| Treasury yield direction | Ongoing, daily | Base, Bear, Bull | 10Y near 4.29% is manageable but still relevant for high-multiple software discount rates | High |
| Enterprise software spending checks | Q2 2026 field commentary / peer earnings window | Bull, Base, Bear | Confirms whether large-enterprise budgets remain resilient or deal scrutiny is rising | Medium |

```json
{
  "scenario_map": [
    {
      "name": "Bull",
      "probability_pct": 30,
      "thesis": "NOW sustains strong enterprise workflow demand, shows credible AI-led upsell or productivity monetization, and converts its large revenue base into faster EPS growth, allowing investors to underwrite the forward valuation despite elevated rates.",
      "valuation_implication": "Multiple holds or expands modestly as earnings revisions move higher.",
      "signposts": [
        "Beat-and-raise quarter",
        "Stable or improving large-deal commentary",
        "Margin expansion alongside growth",
        "Positive AI monetization signals",
        "Falling or stable long-end yields"
      ]
    },
    {
      "name": "Base",
      "probability_pct": 50,
      "thesis": "NOW continues executing as a high-quality software leader, but upside is mostly earned through fundamentals rather than multiple expansion because macro and rates keep valuation discipline in place.",
      "valuation_implication": "Shares trade in a relatively contained range while earnings growth gradually supports the stock.",
      "signposts": [
        "Solid but not accelerating revenue growth",
        "Guidance roughly in line with expectations",
        "Healthy free cash flow conversion",
        "No major deterioration in enterprise demand",
        "Rates remain near current levels"
      ]
    },
    {
      "name": "Bear",
      "probability_pct": 20,
      "thesis": "Enterprise spending slows, deal cycles lengthen, or AI enthusiasm fails to translate into near-term monetization, while higher-for-longer yields compress the valuation investors are willing to pay for premium software names like NOW.",
      "valuation_implication": "De-rating risk with downside led by multiple compression and lower estimate revisions.",
      "signposts": [
        "Guide-down or softer billings/subscription outlook",
        "Longer procurement cycles",
        "Margin pressure from reinvestment",
        "Hot inflation prints or rising 10Y yields",
        "Weak peer software commentary"
      ]
    }
  ],
  "dated_catalyst_map": [
    {
      "catalyst": "NOW next earnings / guidance update",
      "date_or_window": "Late April to early May 2026 (inferred, not confirmed in provided context)",
      "related_scenarios": ["Bull", "Base", "Bear"],
      "expected_impact": "Defines near-term direction through growth, margin, and AI monetization commentary.",
      "confidence": "Medium"
    },
    {
      "catalyst": "Monthly CPI / inflation data",
      "date_or_window": "Next release after March 2026 data",
      "related_scenarios": ["Base", "Bear", "Bull"],
      "expected_impact": "Affects rate expectations and valuation support for premium software.",
      "confidence": "High"
    },
    {
      "catalyst": "Fed policy / FOMC expectations",
      "date_or_window": "Next policy window after 2026-04-16",
      "related_scenarios": ["Base", "Bear", "Bull"],
      "expected_impact": "Stable-to-easing path supports multiples; hawkish repricing pressures them.",
      "confidence": "Medium"
    },
    {
      "catalyst": "Treasury yield moves",
      "date_or_window": "Ongoing",
      "related_scenarios": ["Base", "Bear", "Bull"],
      "expected_impact": "Discount-rate sensitivity remains important given NOW's premium valuation.",
      "confidence": "High"
    },
    {
      "catalyst": "Enterprise software peer earnings / budget checks",
      "date_or_window": "Q2 2026 earnings season",
      "related_scenarios": ["Bull", "Base", "Bear"],
      "expected_impact": "Confirms whether demand conditions are improving, stable, or deteriorating.",
      "confidence": "Medium"
    }
  ],
  "invalidation_triggers": [
    {
      "trigger": "NOW reports a clean beat-and-raise with resilient enterprise demand and margin upside",
      "affected_scenarios": ["Bear"],
      "severity": "High",
      "evidence_to_watch": "Revenue/subscription growth, guidance, large-deal commentary, operating margin"
    },
    {
      "trigger": "Management signals materially slower demand, weaker pipeline conversion, or elongated deal cycles",
      "affected_scenarios": ["Bull", "Base"],
      "severity": "High",
      "evidence_to_watch": "Guidance cuts, weaker remaining performance obligations or billings tone, customer budget commentary"
    },
    {
      "trigger": "Inflation and long-end yields move meaningfully higher from current levels",
      "affected_scenarios": ["Bull", "Base"],
      "severity": "Medium",
      "evidence_to_watch": "CPI/PPI trend, 10Y Treasury yield, Fed repricing"
    },
    {
      "trigger": "AI product commentary remains positive but monetization is deferred without estimate support",
      "affected_scenarios": ["Bull"],
      "severity": "Medium",
      "evidence_to_watch": "Management commentary on attach rates, pricing, upsell contribution, sales cycle impact"
    }
  ]
}
```