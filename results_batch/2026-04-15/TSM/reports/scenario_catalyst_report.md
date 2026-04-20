## TSM Scenario Framing
TSM remains fundamentally strong: very high profitability (45.1% net margin, 53.9% operating margin), strong FCF, and a large gap between trailing and forward EPS/PE that implies the market is underwriting another step-up in earnings. The near-term setup is constructive but no longer cheap: TSM trades near its 52-week high, at 36.0x trailing and 20.3x forward earnings, so execution and AI demand durability matter more than multiple expansion.

- **Bull case (35%)**: AI infrastructure demand stays tight, leading-edge utilization remains high, and upcoming results/guidance confirm the forward EPS ramp implied by valuation. Positive ASML readthrough supports the capex and node-demand backdrop.
- **Base case (45%)**: TSM executes well enough to justify premium valuation, but upside is moderated by already-elevated expectations, sticky inflation, and higher long-end yields. Shares consolidate while earnings catch up.
- **Bear case (20%)**: Export-control tightening, China weakness, or softer-than-expected AI/order momentum compress the multiple from current levels. With TSM near highs, even solid results could disappoint if guidance is not strong enough.

### Key Signposts
- TSM gross/operating margin stability versus current elite levels.
- Management commentary on AI, advanced packaging, and leading-edge utilization.
- Any evidence that China-related restrictions are spilling into broader semiconductor equipment or foundry demand.
- Whether inflation and long yields stay firm enough to cap semiconductor multiples.

### Thesis Invalidation Logic
The constructive thesis weakens materially if TSM fails to convert the implied forward earnings ramp into guidance, or if policy/export restrictions broaden from equipment into end-demand and customer mix.

### Dated Catalyst Map
| Catalyst | Date or Window | Related Scenarios | Expected Impact | Confidence |
| --- | --- | --- | --- | --- |
| TSM next quarterly results and guidance (inferred; exact date not in context) | Late Apr 2026 | Bull, Base, Bear | Highest-impact company-specific catalyst for validating AI demand, margins, and forward EPS expectations | Medium |
| Fed/inflation readthrough after March 2026 CPI/PPI firmness | Apr-May 2026 | Base, Bear | Sticky inflation and elevated long yields can limit multiple expansion even if fundamentals hold | Medium |
| ASML/export-control readthrough for China demand | Ongoing over Q2 2026 | Bull, Bear | Positive capex commentary helps bull case; tighter export controls or China weakness help bear case | Medium |
| Sector earnings from AI semiconductor peers | Apr-May 2026 | Bull, Base, Bear | Confirms or challenges durability of AI hardware demand supporting TSM utilization | Medium |

```json
{
  "scenario_map": [
    {
      "name": "Bull",
      "probability_pct": 35,
      "thesis": "TSM sustains strong leading-edge and AI-related demand, upcoming results validate the large forward EPS step-up implied by the current valuation, and peer capex/news flow stays supportive.",
      "valuation_implication": "Premium multiple holds or expands modestly; upside comes from earnings delivery plus limited rerating.",
      "signposts": [
        "Revenue and EPS guidance supports forward EPS near current implied trajectory",
        "Gross and operating margins remain near best-in-class levels",
        "Management cites strong AI, advanced packaging, and leading-edge utilization",
        "Peer equipment commentary remains constructive"
      ]
    },
    {
      "name": "Base",
      "probability_pct": 45,
      "thesis": "TSM continues executing well, but the stock digests a rich starting valuation near 52-week highs as macro rates and already-high expectations cap upside.",
      "valuation_implication": "Multiple stays roughly stable to slightly lower while earnings growth does the work.",
      "signposts": [
        "Results are good rather than exceptional",
        "Guidance is supportive but not meaningfully above consensus-style expectations",
        "Margins stay healthy but do not inflect higher",
        "Rates and inflation remain firm enough to restrain semiconductor multiple expansion"
      ]
    },
    {
      "name": "Bear",
      "probability_pct": 20,
      "thesis": "China/export-control pressures, softer AI order momentum, or a guidance miss undermine confidence in the forward earnings ramp embedded in TSM's valuation.",
      "valuation_implication": "Multiple compresses from elevated levels; downside exceeds near-term earnings benefit.",
      "signposts": [
        "Management tempers demand or utilization commentary",
        "China-related weakness broadens beyond equipment into foundry demand",
        "Margins fall below recent elite levels",
        "Long-end yields remain elevated while earnings revisions flatten or turn negative"
      ]
    }
  ],
  "dated_catalyst_map": [
    {
      "catalyst": "TSM next quarterly results and guidance",
      "date_or_window": "Late Apr 2026 (inferred; exact date not provided)",
      "related_scenarios": ["Bull", "Base", "Bear"],
      "expected_impact": "Primary company-specific validation of AI demand durability, margins, and the forward EPS ramp.",
      "confidence": "Medium"
    },
    {
      "catalyst": "Fed and inflation readthrough after March 2026 CPI/PPI data",
      "date_or_window": "Apr-May 2026",
      "related_scenarios": ["Base", "Bear"],
      "expected_impact": "Persistent inflation or firmer yields can restrain valuation multiples for long-duration semiconductor leaders.",
      "confidence": "Medium"
    },
    {
      "catalyst": "ASML and export-control news flow tied to China demand",
      "date_or_window": "Q2 2026 ongoing",
      "related_scenarios": ["Bull", "Bear"],
      "expected_impact": "Constructive equipment demand supports the bull case; broader China restrictions or weakness support the bear case.",
      "confidence": "Medium"
    },
    {
      "catalyst": "AI semiconductor peer earnings and capex commentary",
      "date_or_window": "Apr-May 2026",
      "related_scenarios": ["Bull", "Base", "Bear"],
      "expected_impact": "Sector readthrough can reinforce or weaken confidence in utilization and pricing power for TSM.",
      "confidence": "Medium"
    }
  ],
  "invalidation_triggers": [
    {
      "trigger": "TSM guidance fails to support the forward EPS acceleration implied by the current forward PE",
      "affected_scenarios": ["Bull", "Base"],
      "severity": "High",
      "evidence_to_watch": "Quarterly revenue/EPS guidance, management commentary on utilization and customer demand"
    },
    {
      "trigger": "China and export-control headwinds broaden materially into TSM end-demand or customer mix",
      "affected_scenarios": ["Bull", "Base"],
      "severity": "High",
      "evidence_to_watch": "Company commentary, peer equipment updates, and news on additional restrictions"
    },
    {
      "trigger": "Margins compress meaningfully from current levels without offsetting volume growth",
      "affected_scenarios": ["Bull", "Base"],
      "severity": "Medium",
      "evidence_to_watch": "Gross margin, operating margin, advanced-node mix, and pricing commentary"
    },
    {
      "trigger": "Inflation and long-end yields stay elevated long enough to force semiconductor multiple compression",
      "affected_scenarios": ["Bull", "Base"],
      "severity": "Medium",
      "evidence_to_watch": "CPI/PPI trend, Treasury yields, and sector valuation reactions"
    }
  ]
}
```