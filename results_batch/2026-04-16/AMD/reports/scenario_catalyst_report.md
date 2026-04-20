## AMD Scenario Summary

AMD is in a momentum-driven re-rating phase as of April 16, 2026: the stock is at/near all-time highs, news flow is centered on AI accelerator traction, and the valuation already discounts a large earnings step-up. The core setup is asymmetric around the next earnings print and AI product execution. TTM P/E of 106.6 versus forward P/E of 25.5 implies the market expects a sharp profit ramp; that supports upside if AMD converts AI demand into visible revenue and margin expansion, but it also raises the penalty for even a modest miss.

**Bull case (30%)**: AMD shows clear AI accelerator share gains, May 2026 earnings confirm data-center acceleration, and MI450 launch commentary improves confidence that AMD can narrow the gap with NVIDIA. TSMC's upbeat quarter/guidance is a secondary positive signpost because foundry strength reduces the risk that AMD demand is supply-constrained rather than genuinely weak.

**Base case (50%)**: AI/data-center growth stays strong enough to support consensus, but AMD remains a credible number-two AI compute supplier rather than a near-term NVIDIA equal. In this path, execution is good, not breakout-great: revenue and forward EPS grow into the valuation, but further multiple expansion is limited after the recent rally.

**Bear case (20%)**: Expectations have moved too far ahead of fundamentals. If May 2026 earnings show slower AI conversion, weaker margin progression, or softer forward commentary, the stock is vulnerable to de-rating because the rally and headline narrative already reflect substantial optimism.

**Key signposts**
- May 2026 earnings: data-center revenue mix, AI accelerator bookings, and gross-margin progression.
- Management commentary on MI450 timing, customer adoption, and production readiness.
- Whether forward EPS expectations near 10.9 remain credible after guidance.
- Macro rate/inflation path: a normal upward-sloping curve and Fed near neutral are supportive, but long-duration growth stocks like AMD remain sensitive to any renewed inflation pressure.

**Thesis invalidation logic**
- Bull case weakens materially if AMD cannot show AI revenue scaling fast enough to justify its current valuation premium.
- Base case breaks if management either meaningfully outperforms into a sustained share-gain cycle (turning bull) or misses/guides down on AI/margins (turning bear).
- Bear case is invalidated if earnings and launch commentary prove that AMD's AI business is compounding faster than the market is currently modeling.

| Catalyst | Date or Window | Related Scenarios | Expected Impact | Confidence |
| --- | --- | --- | --- | --- |
| AMD Q1/Q2-season earnings update and guidance | May 2026 | Bull, Base, Bear | Highest-impact read on AI demand conversion, margins, and FY26 EPS credibility | High |
| MI450 launch/timing updates | 2026 launch window; near-term commentary likely with earnings/product events | Bull, Bear | Positive if timing and customer ramp are concrete; negative if pushed out or vague | Medium |
| Follow-through from TSMC strong quarter/guidance | April to May 2026 | Bull, Base | Supports semiconductor demand backdrop and supply-chain confidence | Medium |
| Next inflation/rates data cycle | Late April to June 2026 | Base, Bear | Hotter inflation or higher long yields can compress AMD's multiple despite solid fundamentals | Medium |

```json
{
  "scenario_map": [
    {
      "name": "Bull",
      "probability_pct": 30,
      "thesis": "AMD converts AI accelerator demand into visibly faster data-center revenue growth, reinforces MI450 competitiveness, and delivers May 2026 results/guidance strong enough to justify the current re-rating and support further upside.",
      "valuation_implication": "Multiple holds or expands from already elevated levels as forward EPS and AI optionality gain credibility.",
      "signposts": [
        "May 2026 earnings beat with strong data-center/AI commentary",
        "Gross margin expansion alongside AI mix improvement",
        "Clear MI450 timing and customer adoption milestones",
        "Sustained positive semiconductor read-through from TSMC and peers"
      ]
    },
    {
      "name": "Base",
      "probability_pct": 50,
      "thesis": "AMD continues executing well in data center and AI, but remains a strong second source rather than a near-term NVIDIA peer. Growth is good enough to support consensus, but not enough for a major additional multiple re-rating after the recent all-time-high move.",
      "valuation_implication": "Forward earnings grow into the stock, with returns driven more by EPS delivery than by further valuation expansion.",
      "signposts": [
        "Results roughly in line with consensus",
        "Forward EPS trajectory near 10.9 stays intact",
        "AI traction improves incrementally rather than step-functionally",
        "Macro backdrop remains neutral to mildly supportive"
      ]
    },
    {
      "name": "Bear",
      "probability_pct": 20,
      "thesis": "Expectations embedded in AMD's rally and valuation outrun near-term fundamentals. Earnings, guidance, or MI450 execution fail to show enough AI monetization, leading investors to compress the multiple.",
      "valuation_implication": "De-rating risk is meaningful because TTM valuation is still rich and the stock is trading near all-time highs.",
      "signposts": [
        "May 2026 earnings miss or cautious guidance",
        "Weak margin progression despite AI narrative",
        "Delayed or less-convincing MI450 roadmap commentary",
        "Rising long yields or hotter inflation pressuring growth-stock multiples"
      ]
    }
  ],
  "dated_catalyst_map": [
    {
      "catalyst": "AMD earnings report and guidance",
      "date_or_window": "May 2026",
      "related_scenarios": ["Bull", "Base", "Bear"],
      "expected_impact": "Primary near-term catalyst for validating AI revenue ramp, margin progression, and forward EPS assumptions.",
      "confidence": "High"
    },
    {
      "catalyst": "MI450 product launch/timing updates",
      "date_or_window": "2026 launch window; likely discussed in upcoming earnings/product events",
      "related_scenarios": ["Bull", "Bear"],
      "expected_impact": "Concrete launch/adoption updates would support the bull case; delays or vague messaging would favor the bear case.",
      "confidence": "Medium"
    },
    {
      "catalyst": "TSMC demand and supply-chain follow-through",
      "date_or_window": "April to May 2026",
      "related_scenarios": ["Bull", "Base"],
      "expected_impact": "Positive semiconductor foundry data helps confirm industry demand health and reduces supply-chain skepticism.",
      "confidence": "Medium"
    },
    {
      "catalyst": "US inflation and rates data cycle",
      "date_or_window": "Late April to June 2026",
      "related_scenarios": ["Base", "Bear"],
      "expected_impact": "Higher inflation or long yields could cap valuation even if company execution remains solid.",
      "confidence": "Medium"
    }
  ],
  "invalidation_triggers": [
    {
      "trigger": "AI/data-center growth fails to accelerate enough to support current valuation",
      "affected_scenarios": ["Bull"],
      "severity": "High",
      "evidence_to_watch": "Earnings revenue mix, AI accelerator commentary, and bookings/customer ramp disclosures"
    },
    {
      "trigger": "Management materially beats and raises with strong AI margin conversion",
      "affected_scenarios": ["Base", "Bear"],
      "severity": "High",
      "evidence_to_watch": "May 2026 guidance, gross margin trend, forward EPS revisions"
    },
    {
      "trigger": "Meaningful earnings miss, weak guidance, or MI450 roadmap slippage",
      "affected_scenarios": ["Base"],
      "severity": "High",
      "evidence_to_watch": "Revenue/gross-margin miss, delayed product timing, weaker customer adoption language"
    },
    {
      "trigger": "Rates/inflation stay benign while AMD execution remains strong",
      "affected_scenarios": ["Bear"],
      "severity": "Medium",
      "evidence_to_watch": "CPI/PPI trend, 10-year yield behavior, and sustained positive estimate revisions"
    }
  ]
}
```