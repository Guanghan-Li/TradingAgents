## MU Scenario Framing

MU is in a very strong AI-memory upcycle, but expectations are now extremely high. The key near-term anchor is Micron's March 18, 2026 fiscal Q2 report, which showed record results and guided fiscal Q3 revenue to about $33.5B and non-GAAP EPS to about $19.15, implying the market is underwriting continued HBM/DRAM tightness and exceptional mix. Base case remains constructive because fundamentals are powerful, but after a move toward 52-week highs, MU is more exposed to any sign of pricing normalization, customer digestion, or margin slippage.

Bull case: MU sustains tight industry supply, HBM share gains, and near-80% gross margin, producing another beat/raise cycle. Base case: demand stays strong, but upside narrows as valuation already discounts a large part of the cycle. Bear case: memory pricing or AI capex enthusiasm cools, and MU de-rates quickly given its high beta and cyclical history. Key signposts are DRAM/HBM pricing, data-center demand commentary, inventory discipline, and whether inflation/rates stay contained enough to support long-duration semiconductor multiples.

Bull invalidation: a clean miss versus guided fiscal Q3 revenue/EPS or visible gross-margin compression. Base invalidation: either a fresh step-function beat/raise that reopens the bull case, or a sudden pricing rollover that shifts MU into a downcycle setup. Bear invalidation: continued tight supply plus another quarter of outsized beat/raise and strong free-cash-flow conversion.

| Catalyst | Date or Window | Related Scenarios | Expected Impact |
| --- | --- | --- | --- |
| Fed meeting | April 28-29, 2026 | Bull, Base, Bear | Dovish/steady outcome supports MU multiple; hawkish tone raises discount-rate risk for semis |
| U.S. Employment Situation | May 8, 2026 | Base, Bear | Strong labor with no rate scare is neutral-positive; overheating can reinforce hawkish fears |
| U.S. CPI | May 12, 2026 | Bull, Base, Bear | Cooler inflation supports risk appetite; hot inflation is a fast multiple-compression trigger |
| U.S. PPI | May 13, 2026 | Base, Bear | Higher producer inflation can pressure rate expectations and cyclicals sentiment |
| MU fiscal Q3 2026 earnings | Late June 2026 (timing inferred from prior fiscal cadence; not confirmed in supplied evidence) | Bull, Base, Bear | Most important company-specific test of HBM/DRAM pricing, margin durability, and beat/raise capacity |

```json
{
  "scenario_map": [
    {
      "name": "bull",
      "probability_pct": 35,
      "thesis": "MU extends the AI-memory supercycle as HBM and DRAM supply remain tight, data-center demand stays strong, and fiscal Q3/Q4 results continue the beat-and-raise pattern implied by March 18, 2026 guidance.",
      "valuation_implication": "Upside multiple support with earnings revisions still outrunning valuation concerns; MU can trade materially above current levels if gross margin stays near guided levels.",
      "signposts": [
        "Fiscal Q3 revenue/EPS at or above guided range",
        "Gross margin holds near 80%",
        "HBM and data-center mix keeps improving",
        "Customer inventory commentary stays lean",
        "No material DRAM pricing rollover"
      ]
    },
    {
      "name": "base",
      "probability_pct": 45,
      "thesis": "MU remains fundamentally strong, but the stock consolidates as current pricing already reflects much of the near-term AI and memory upside; earnings stay good, not shocking.",
      "valuation_implication": "Range-bound to modest upside as earnings growth offsets some multiple compression.",
      "signposts": [
        "Results are in line with elevated guidance",
        "Margins remain strong but stop expanding",
        "AI demand remains healthy without another major upward reset",
        "Macro stays stable with policy near neutral",
        "Semiconductor leadership broadens beyond MU"
      ]
    },
    {
      "name": "bear",
      "probability_pct": 20,
      "thesis": "MU de-rates if memory pricing momentum softens, AI infrastructure spending pauses, or inflation/rates re-accelerate and pressure semiconductor multiples after a very large rally.",
      "valuation_implication": "Sharp downside from multiple compression and lower forward earnings assumptions, typical of memory-cycle reversals.",
      "signposts": [
        "Gross margin misses or guides down",
        "Management comments on customer digestion or weaker pricing",
        "Inventories begin building",
        "Hot CPI/PPI pushes yields higher",
        "Industry supply response outpaces demand growth"
      ]
    }
  ],
  "dated_catalyst_map": [
    {
      "catalyst": "Federal Open Market Committee meeting",
      "date_or_window": "April 28-29, 2026",
      "related_scenarios": ["bull", "base", "bear"],
      "expected_impact": "A benign or dovish message supports MU valuation; hawkish surprise would pressure semiconductor multiples.",
      "confidence": "high"
    },
    {
      "catalyst": "U.S. Employment Situation release",
      "date_or_window": "May 8, 2026",
      "related_scenarios": ["base", "bear"],
      "expected_impact": "Can move rate expectations and risk appetite for high-beta semiconductors like MU.",
      "confidence": "high"
    },
    {
      "catalyst": "U.S. CPI release",
      "date_or_window": "May 12, 2026",
      "related_scenarios": ["bull", "base", "bear"],
      "expected_impact": "Cool inflation helps the bull/base cases; hot inflation raises discount-rate risk.",
      "confidence": "high"
    },
    {
      "catalyst": "U.S. PPI release",
      "date_or_window": "May 13, 2026",
      "related_scenarios": ["base", "bear"],
      "expected_impact": "Producer inflation can reinforce or relieve pressure on yields and cyclicals sentiment.",
      "confidence": "high"
    },
    {
      "catalyst": "MU fiscal Q3 2026 earnings and outlook",
      "date_or_window": "Late June 2026 (inferred from historical cadence; exact date not confirmed in supplied evidence)",
      "related_scenarios": ["bull", "base", "bear"],
      "expected_impact": "Primary company-specific catalyst for confirming whether HBM/DRAM tightness and margin expansion remain durable.",
      "confidence": "medium"
    }
  ],
  "invalidation_triggers": [
    {
      "trigger": "MU reports fiscal Q3 revenue or EPS below the March 18, 2026 guided range",
      "affected_scenarios": ["bull"],
      "severity": "high",
      "evidence_to_watch": "Quarterly results, updated company outlook, and analyst estimate revisions"
    },
    {
      "trigger": "Gross margin falls materially below the roughly 81% fiscal Q3 guide or management signals pricing softness",
      "affected_scenarios": ["bull", "base"],
      "severity": "high",
      "evidence_to_watch": "Earnings call commentary, DRAM/HBM pricing checks, and segment margin trends"
    },
    {
      "trigger": "CPI/PPI re-accelerate enough to push yields meaningfully higher and turn Fed tone more hawkish",
      "affected_scenarios": ["base"],
      "severity": "medium",
      "evidence_to_watch": "BLS inflation releases, Treasury yield moves, and Fed communications"
    },
    {
      "trigger": "Industry supply remains tight and MU delivers another clear beat-and-raise with strong free cash flow",
      "affected_scenarios": ["bear"],
      "severity": "high",
      "evidence_to_watch": "Next MU earnings release, management commentary on supply discipline, and customer demand signals"
    }
  ]
}
```