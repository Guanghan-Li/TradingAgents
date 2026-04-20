## META Scenario Summary

META screens as a quality compounder with unusually high margins for its scale, but the near-term setup is a timing question around AI monetization versus AI spend. The fundamental backdrop is strong: ~30% net margin, ~41% operating margin, forward EPS materially above trailing EPS, and a forward P/E (~18.9x) below the trailing multiple (~28.6x), which implies earnings growth is expected. The main company-specific swing factors in the supplied context are the Broadcom AI-chip deal on the positive side and EU pressure around third-party AI assistant access on WhatsApp on the negative side.

**Base case (50%)**: core ads stay resilient, AI improves engagement/targeting incrementally, and the stock digests heavy infrastructure spend without a major rerating. **Bull case (30%)**: AI capex begins to show clearer payoff through earnings beats, stronger guidance, and lower infrastructure bottleneck risk from the Broadcom partnership. **Bear case (20%)**: regulation broadens, capex remains elevated ahead of monetization, and a still-firm rate backdrop compresses the multiple if ad demand softens.

Key signposts for `META`: earnings commentary on capex discipline, evidence that AI features lift ad efficiency or time spent, any expansion of the EU interoperability issue beyond WhatsApp, and whether management can sustain forward EPS delivery without another step-up in spending.

| Catalyst | Date / Window | Related Scenarios | Expected Impact | Confidence |
| --- | --- | --- | --- | --- |
| `META` Q1 2026 earnings and guidance | Late April 2026 window (inferred from normal reporting cadence) | Bull / Base / Bear | Highest-probability near-term stock mover; will frame AI payoff vs. spend | Medium |
| Broadcom AI infrastructure execution updates | Next 1-2 quarters | Bull / Base | Positive if it reduces supply risk and supports AI feature rollout across apps | Medium |
| EU action on WhatsApp third-party AI assistant access | Ongoing over coming weeks/months | Bear / Base | Negative if remedies broaden to product constraints or monetization limits | Medium |
| Fed/rate and long-yield backdrop | April-June 2026 | Base / Bear | Higher long yields can cap multiple expansion even if fundamentals hold | Medium |

Invalidation logic: the bull case breaks if AI monetization remains anecdotal while capex keeps rising; the bear case breaks if `META` posts another clean beat-and-raise with limited regulatory spillover; the base case breaks if either monetization inflects faster than expected or regulation/capex pressure worsens sharply.

```json
{
  "scenario_map": [
    {
      "name": "Bull",
      "probability_pct": 30,
      "thesis": "`META` converts heavy AI investment into visible product and ad-performance gains, the Broadcom partnership lowers infrastructure bottleneck risk, and earnings/guidance support confidence in the forward EPS ramp.",
      "valuation_implication": "Upside rerating through earnings confidence, with scope for the multiple to hold or expand despite elevated capex.",
      "signposts": [
        "Q1 results beat with stronger-than-expected guidance",
        "Management points to measurable AI-driven engagement or ad conversion gains",
        "Capex messaging stays controlled relative to revenue growth",
        "No material expansion of EU regulatory remedies"
      ]
    },
    {
      "name": "Base",
      "probability_pct": 50,
      "thesis": "Core advertising remains healthy and AI improves the platform gradually, but investors wait for clearer monetization proof while elevated spending and regulation keep valuation expansion contained.",
      "valuation_implication": "Range-bound to modest upside; earnings growth does most of the work while the multiple stays disciplined.",
      "signposts": [
        "Solid but not explosive ad revenue growth",
        "Forward EPS tracking remains intact",
        "AI commentary is positive but still early-stage",
        "EU issue remains manageable and localized"
      ]
    },
    {
      "name": "Bear",
      "probability_pct": 20,
      "thesis": "AI spending stays ahead of monetization, regulatory pressure around WhatsApp/AI interoperability broadens, and a higher-rate backdrop weakens sentiment toward large-cap growth multiples.",
      "valuation_implication": "Multiple compression and downside if investors question return on AI capex or see higher legal/product friction risk.",
      "signposts": [
        "Guide implies another capex step-up without matching revenue benefit",
        "EU actions expand beyond a narrow interoperability remedy",
        "Ad demand commentary softens",
        "Long-end yields remain elevated or move higher"
      ]
    }
  ],
  "dated_catalyst_map": [
    {
      "catalyst": "`META` Q1 2026 earnings and guidance",
      "date_or_window": "Late April 2026 window",
      "related_scenarios": ["Bull", "Base", "Bear"],
      "expected_impact": "High; likely the key near-term decision point on AI payoff, capex, and ad resilience.",
      "confidence": "Medium"
    },
    {
      "catalyst": "Broadcom AI-chip deal execution and infrastructure updates",
      "date_or_window": "Next 1-2 quarters",
      "related_scenarios": ["Bull", "Base"],
      "expected_impact": "Medium-high positive if execution improves AI rollout speed and reduces supply uncertainty.",
      "confidence": "Medium"
    },
    {
      "catalyst": "EU WhatsApp third-party AI assistant access order / follow-on remedies",
      "date_or_window": "Ongoing over coming weeks/months",
      "related_scenarios": ["Bear", "Base"],
      "expected_impact": "Medium-high negative if the issue broadens into product restrictions or monetization limits.",
      "confidence": "Medium"
    },
    {
      "catalyst": "Fed/rates and long-yield backdrop",
      "date_or_window": "April-June 2026",
      "related_scenarios": ["Base", "Bear"],
      "expected_impact": "Medium; affects multiple tolerance for a high-capex megacap even with good fundamentals.",
      "confidence": "Medium"
    }
  ],
  "invalidation_triggers": [
    {
      "trigger": "AI monetization remains vague while capex and infrastructure spending rise materially again",
      "affected_scenarios": ["Bull"],
      "severity": "High",
      "evidence_to_watch": "Earnings guidance, capex commentary, disclosures on AI-driven ad performance or engagement"
    },
    {
      "trigger": "`META` posts a clean beat-and-raise with clear AI revenue/ad-efficiency benefits and limited regulatory fallout",
      "affected_scenarios": ["Bear"],
      "severity": "High",
      "evidence_to_watch": "Quarterly results, management commentary, analyst estimate revisions"
    },
    {
      "trigger": "Either a sharp AI monetization inflection or a materially worse regulatory/capex shock than expected",
      "affected_scenarios": ["Base"],
      "severity": "Medium",
      "evidence_to_watch": "Earnings call tone, EU enforcement updates, capex trajectory, revenue acceleration/deceleration"
    }
  ]
}
```