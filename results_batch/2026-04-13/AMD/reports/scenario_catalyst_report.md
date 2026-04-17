# AMD Scenario & Catalyst Analysis
**As of April 13, 2026**

## Executive Summary

AMD trades at a **forward PE of 22.6x** (vs. 93.6x TTM), implying the market expects significant earnings acceleration driven by AI datacenter share gains and client CPU/GPU momentum. The **bull case (35% probability)** hinges on MI300-series AI accelerator adoption exceeding consensus, sustained server CPU share gains vs. Intel, and margin expansion from mix shift. The **base case (45%)** assumes steady but unspectacular execution with modest AI TAM capture. The **bear case (20%)** centers on Nvidia maintaining AI moat, inventory correction in PC/gaming, and margin pressure from competitive pricing.

---

## Scenario Map

### 🐂 Bull Case (35% probability)
**Thesis:** AMD captures 15–20% of AI accelerator TAM by 2027, driven by hyperscaler diversification away from Nvidia. EPYC server CPUs reach 30%+ x86 share. Gross margins expand to 54–56% on favorable mix.

**Valuation Implication:** Fair value $280–320 (26–30x forward EPS of ~$11–12). Upside driven by multiple expansion as AI revenue visibility improves.

**Key Signposts:**
- Q2/Q3 2026 earnings show MI300 revenue run-rate >$6B annualized
- Major cloud customer (AWS, Azure, Google) announces MI300-based instance family
- EPYC Genoa/Bergamo design wins at 3+ hyperscalers
- Gross margin exceeds 53% for two consecutive quarters

---

### ⚖️ Base Case (45% probability)
**Thesis:** AMD grows revenue 12–15% annually through 2027, with AI contributing but not transformational. Server CPU share stabilizes at 25–27%. PC/gaming remains cyclical. Margins hold 51–53%.

**Valuation Implication:** Fair value $220–250 (20–23x forward EPS of ~$10.50). Stock trades in line with semis peer group.

**Key Signposts:**
- MI300 revenue $3–4B in 2026, growing but below bull expectations
- EPYC share gains slow as Intel Granite Rapids launches
- Client CPU (Ryzen) ASPs stable; no major share loss to Qualcomm ARM
- Free cash flow conversion remains 12–14% of revenue

---

### 🐻 Bear Case (20% probability)
**Thesis:** Nvidia's CUDA moat proves insurmountable; AMD's AI revenue disappoints. Intel regains server share with aggressive pricing. PC market enters prolonged downturn. Margins compress to 48–50%.

**Valuation Implication:** Fair value $140–180 (13–17x forward EPS of ~$9). Multiple de-rates to mature semis valuation.

**Key Signposts:**
- MI300 revenue <$2B in 2026; hyperscaler orders pushed out
- EPYC server share declines sequentially for 2+ quarters
- Gross margin falls below 50%
- Cathie Wood-style institutional selling accelerates (recent $10M sale a leading indicator)

---

## Dated Catalyst Map

| Catalyst | Date/Window | Related Scenarios | Expected Impact | Confidence |
|----------|-------------|-------------------|-----------------|------------|
| **Q1 2026 Earnings** | Late April 2026 | All | MI300 revenue disclosure critical; guidance for H2 2026 AI ramp | High |
| **Computex Taipei** | Early June 2026 | Bull, Base | Potential Zen 5 Ryzen 9000X3D launch, RDNA 4 GPU refresh | Medium |
| **Fed Rate Decision** | June 18, 2026 | All | If Fed signals cuts, risk-on benefits high-beta AMD (β=1.96) | Medium |
| **Intel Granite Rapids Launch** | Q3 2026 | Base, Bear | Competitive threat to EPYC; watch hyperscaler commentary | High |
| **Nvidia Blackwell Ramp** | Q3–Q4 2026 | Bear | If Blackwell supply unconstrained, AMD MI300 positioning weakens | High |
| **CPI/PPI Prints** | Monthly (next: May 14) | All | Inflation resurgence → Fed hawkish → growth multiple compression | Medium |
| **Ryzen 9950X3D2 Sales Data** | Q2 2026 | Base | $1,200+ pricing tests premium PC demand; watch Steam Hardware Survey share | Low |

---

## Invalidation Triggers

| Trigger | Affected Scenarios | Severity | Evidence to Watch |
|---------|-------------------|----------|-------------------|
| **MI300 revenue guide cut >20%** | Bull invalidated | Critical | Q1 or Q2 earnings call; hyperscaler CapEx commentary |
| **Gross margin <50% for 2 quarters** | Bull/Base invalidated | High | Quarterly financials; implies pricing pressure or unfavorable mix |
| **EPYC server share <23%** | Bull invalidated | High | Mercury Research quarterly x86 server data |
| **Nvidia announces MI300-killer at <20% price premium** | Bull severely weakened | High | Nvidia investor day or product launch; TCO analysis by hyperscalers |
| **Fed hikes rates (unexpected)** | All scenarios compress | Medium | FOMC meeting; would pressure high-PE growth stocks |
| **Major hyperscaler (AWS/Azure/Google) cancels MI300 deployment** | Bull/Base invalidated | Critical | Supply chain checks, earnings call Q&A, or public cloud announcements |

---

## Macro & Technical Context

- **Fed Policy:** Stable at 3.64%; curve upward-sloping (2Y-10Y +51bps) suggests no imminent recession. Neutral for semis.
- **Volatility:** VIX at 19.23 (moderate); AMD's β=1.96 means 2x sensitivity to market swings.
- **Valuation:** Forward PE 22.6x vs. sector median ~18x. Premium justified only if AI thesis plays out (bull case).
- **Sentiment:** Cathie Wood's $10M sale (April 2026 news) signals caution among growth investors; watch for further institutional rotation.

---

## Investment Committee Recommendation Framework

- **Bull case probability 35%** × $300 target = $105  
- **Base case probability 45%** × $235 target = $106  
- **Bear case probability 20%** × $160 target = $32  
- **Probability-weighted fair value: ~$243**

Current price context needed to finalize BUY/HOLD/SELL, but framework suggests:
- **BUY** if <$220 (>10% upside to base, asymmetric bull optionality)
- **HOLD** if $220–260 (fair value range)
- **SELL** if >$280 (priced for bull case with limited margin of safety)

**Next decision point:** Q1 2026 earnings (late April) for MI300 revenue trajectory.

---

```json
{
  "scenario_map": [
    {
      "name": "Bull Case",
      "probability_pct": 35,
      "thesis": "AMD captures 15-20% of AI accelerator TAM by 2027 via MI300 hyperscaler adoption; EPYC server share reaches 30%+; gross margins expand to 54-56% on favorable mix.",
      "valuation_implication": "Fair value $280-320 (26-30x forward EPS). Multiple expansion as AI revenue visibility improves.",
      "signposts": [
        "MI300 revenue run-rate >$6B annualized by Q2/Q3 2026",
        "Major cloud customer announces MI300-based instance family",
        "EPYC design wins at 3+ hyperscalers",
        "Gross margin >53% for 2 consecutive quarters"
      ]
    },
    {
      "name": "Base Case",
      "probability_pct": 45,
      "thesis": "AMD grows 12-15% annually through 2027; AI contributes but not transformational; server CPU share stabilizes 25-27%; margins 51-53%.",
      "valuation_implication": "Fair value $220-250 (20-23x forward EPS ~$10.50). Trades in line with semis peer group.",
      "signposts": [
        "MI300 revenue $3-4B in 2026",
        "EPYC share gains slow as Intel Granite Rapids launches",
        "Ryzen ASPs stable; no major ARM share loss",
        "FCF conversion 12-14% of revenue"
      ]
    },
    {
      "name": "Bear Case",
      "probability_pct": 20,
      "thesis": "Nvidia CUDA moat insurmountable; AMD AI revenue disappoints; Intel regains server share with aggressive pricing; PC downturn; margins compress to 48-50%.",
      "valuation_implication": "Fair value $140-180 (13-17x forward EPS ~$9). Multiple de-rates to mature semis valuation.",
      "signposts": [
        "MI300 revenue <$2B in 2026",
        "EPYC share declines sequentially 2+ quarters",
        "Gross margin <50%",
        "Accelerating institutional selling (Cathie Wood $10M sale as leading indicator)"
      ]
    }
  ],
  "dated_catalyst_map": [
    {
      "catalyst": "Q1 2026 Earnings",
      "date_or_window": "Late April 2026",
      "related_scenarios": ["Bull", "Base", "Bear"],
      "expected_impact": "MI300 revenue disclosure critical; H2 2026 AI ramp guidance determines scenario probabilities",
      "confidence": "High"
    },
    {
      "catalyst": "Computex Taipei",
      "date_or_window": "Early June 2026",
      "related_scenarios": ["Bull", "Base"],
      "expected_impact": "Potential Zen 5 Ryzen 9000X3D launch, RDNA 4 GPU refresh; client momentum indicator",
      "confidence": "Medium"
    },
    {
      "catalyst": "Fed Rate Decision",
      "date_or_window": "June 18, 2026",
      "related_scenarios": ["Bull", "Base", "Bear"],
      "expected_impact": "Rate cuts signal → risk-on benefits high-beta AMD (β=1.96); hawkish surprise compresses multiples",
      "confidence": "Medium"
    },
    {
      "catalyst": "Intel Granite Rapids Launch",
      "date_or_window": "Q3 2026",
      "related_scenarios": ["Base", "Bear"],
      "expected_impact": "Competitive threat to EPYC; hyperscaler commentary on performance/TCO critical",
      "confidence": "High"
    },
    {
      "catalyst": "Nvidia Blackwell Ramp",
      "date_or_window": "Q3-Q4 2026",
      "related_scenarios": ["Bear"],
      "expected_impact": "Unconstrained Blackwell supply weakens AMD MI300 positioning; watch hyperscaler allocation",
      "confidence": "High"
    },
    {
      "catalyst": "CPI/PPI Monthly Prints",
      "date_or_window": "Monthly (next: May 14, 2026)",
      "related_scenarios": ["Bull", "Base", "Bear"],
      "expected_impact": "Inflation resurgence → Fed hawkish → growth multiple compression; deflationary surprise supports risk assets",
      "confidence": "Medium"
    },
    {
      "catalyst": "Ryzen 9950X3D2 Sales Data",
      "date_or_window": "Q2 2026",
      "related_scenarios": ["Base"],
      "expected_impact": "$1,200+ pricing tests premium PC demand; Steam Hardware Survey share indicates client strength",
      "confidence": "Low"
    }
  ],
  "invalidation_triggers": [
    {
      "trigger": "MI300 revenue guide cut >20%",
      "affected_scenarios": ["Bull"],
      "severity": "Critical",
      "evidence_to_watch": "Q1 or Q2 earnings call guidance; hyperscaler CapEx commentary on AI accelerator allocation"
    },
    {
      "trigger": "Gross margin <50% for 2 consecutive quarters",
      "affected_scenarios": ["Bull", "Base"],
      "severity": "High",
      "evidence_to_watch": "Quarterly financials; implies pricing pressure or unfavorable product mix shift"
    },
    {
      "trigger": "EPYC server share falls below 23%",
      "affected_scenarios": ["Bull"],
      "severity": "High",
      "evidence_to_watch": "Mercury Research quarterly x86 server CPU market share data"
    },
    {
      "trigger": "Nvidia announces MI300-killer at <20% price premium",
      "affected_scenarios": ["Bull"],
      "severity": "High",
      "evidence_to_watch": "Nvidia product launches, investor day; hyperscaler TCO analysis and deployment decisions"
    },
    {
      "trigger": "Fed unexpectedly hikes rates",
      "affected_scenarios": ["Bull", "Base", "Bear"],
      "severity": "Medium",
      "evidence_to_watch": "FOMC meeting outcomes; high-PE growth stocks compress on rising discount rates"
    },
    {
      "trigger": "Major hyperscaler cancels MI300 deployment",
      "affected_scenarios": ["Bull", "Base"],
      "severity": "Critical",
      "evidence_to_watch": "Supply chain checks, earnings call Q&A, public cloud service announcements"
    }
  ]
}
```