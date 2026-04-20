Excellent. I now have fundamentals, news context, and catalyst data. Let me synthesize this into a bull/base/bear scenario framework with dated catalysts and invalidation triggers.

---

# TSM Scenario & Catalyst Analysis (as of 2026-04-11)

## Executive Summary

**TSM at $350.57** (50-day MA) is priced at a **35.5x forward PE**, reflecting elevated expectations for AI-driven semiconductor demand and margin expansion. The bull case anchors on sustained AI capex cycles and process node leadership; the base case assumes moderation in growth as capex normalizes; the bear case hinges on geopolitical friction (Taiwan-China-US tensions, export restrictions) and cyclical demand softening.

Key near-term catalyst: **April 13 begins a critical week for equities** (per IBD), while **China-Taiwan "goodwill" measures** signal potential de-escalation. Valuation is stretched on fundamentals (P/B 56.7x, TTM P/E 35.5x) but justified only if forward earnings ($18.26 EPS) materialize with consistency.

---

## Scenario Map & Probabilities

| Scenario | Probability | Thesis | Valuation | Key Signposts |
|----------|-------------|--------|-----------|---------------|
| **Bull** | 35% | AI capex super-cycle sustains; TSM expands margin; process leadership (3nm/2nm) drives pricing power | $420–$480 (20–37% upside) | NVIDIA, AMD sustained orders; 3nm utilization >90%; gross margin >47%; forward EPS beats |
| **Base** | 50% | AI growth moderates; TSM grows EPS mid-single digits; margin stable 44–46%; competition intensifies | $330–$380 (–6% to +8%) | Capex guidance cuts; seasonal Q2 dips; margin compression 100–200 bps; China demand stabilizes |
| **Bear** | 15% | Geopolitical escalation (export bans, Taiwan conflict); demand cliff; margin compression; valuation resets | $200–$280 (–43% to –20%) | US bans advanced node exports; China retaliatory tariffs; AI inventory buildup; multiple compression to 15–20x |

---

## Dated Catalyst Map

| Catalyst | Date/Window | Related Scenarios | Expected Impact | Confidence |
|----------|-------------|-------------------|-----------------|------------|
| April 13: Critical week for equities (macro/earnings inflection) | Apr 13, 2026 | Base, Bear | ±3–5% intraweek vol; risk-off if macro falters | Medium |
| China-Taiwan "goodwill" measures (geopolitical de-escalation signal) | Apr 2026 | Bull, Base | De-risks geopolitical tail; supports Bull +2–3% | Medium-High |
| Q1 2026 earnings & guidance (TSM investor call) | Late Apr 2026 | All | Forward EPS guidance critical; margin outlook determines base case | High |
| NVIDIA, AMD chiplet orders (indirect signal of AI demand) | Ongoing | Bull, Base | Sustained orders = bull thesis; softening = base/bear risk | Medium |
| US-China trade policy clarity (tariffs, export controls) | Q2–Q3 2026 | Bear, Base | Regulatory clarity reduces geopolitical risk premium | Medium |

---

## Invalidation Triggers & Evidence to Watch

| Trigger | Affected Scenarios | Severity | Evidence to Watch |
|---------|-------------------|----------|-------------------|
| **Gross margin <43%** (compression >400 bps YoY) | Bull, Base | High | Q1 earnings call; capacity utilization; pricing power erosion |
| **US export ban on <5nm nodes to China** | Bull, Base | Critical | CFIUS/EAR announcements; Taiwan geopolitical statements; China retaliation |
| **AI capex guidance cut >20%** (NVIDIA, AMD, hyperscalers) | Bull | Critical | Earnings calls; capex commentary; inventory levels in channel |
| **Cross-strait military escalation or blockade** | All scenarios | Critical | Taiwan strait tensions; military drills; diplomatic breakdowns |
| **TSM loses process leadership to Samsung 3nm** | Bull | High | Process node competitive roadmaps; yield data; customer migration signals |
| **Forward EPS misses <$17/share** (2026E) | Bull, Base | High | Q1 actuals; 2026 guidance revision; organic growth deceleration |

---

## Thesis Invalidation Logic

- **Bull case breaks if:** Margin compression accelerates beyond seasonal patterns AND forward EPS guidance declines below $17/share. Export restrictions to China would immediately shift risk to bear case.
- **Base case breaks if:** Capex cycle extends (no moderation in H2 2026) OR geopolitical escalation triggers material export bans. Upside to bull if margin stays >46% and forward EPS beats >$19.
- **Bear case triggers if:** Cross-strait tensions materialize into export restrictions, OR AI capex cycle breaks sharply with >25% guidance cuts from major customers.

---

```json
{
  "scenario_map": [
    {
      "name": "Bull",
      "probability_pct": 35,
      "thesis": "AI capex super-cycle sustains through 2026-2027; TSM expands gross margin to 47%+ via process node pricing power (3nm/2nm); forward EPS grows 15%+ YoY; geopolitical de-escalation holds",
      "valuation_implication": "$420–$480 (20–37% upside); 22–24x forward P/E justified by 15%+ growth",
      "signposts": [
        "NVIDIA, AMD sustained orders; capex guidance holds or increases",
        "3nm fab utilization >90%; 2nm ramps on schedule",
        "Gross margin expands to >47% Q2–Q4 2026",
        "Forward EPS beats expectations (>$19/share for 2026E)",
        "China-Taiwan 'goodwill' measures hold; no export ban escalation"
      ]
    },
    {
      "name": "Base",
      "probability_pct": 50,
      "thesis": "AI capex moderates in H2 2026; TSM earnings growth decelerates to 5–8% YoY; margin remains stable at 44–46%; geopolitical risks managed but present; valuation compresses toward 20x forward P/E",
      "valuation_implication": "$330–$380 (–6% to +8%); sustainable 20x forward P/E at $18.26 forward EPS",
      "signposts": [
        "Capex guidance moderates H2 2026; seasonal Q2 dip in margins",
        "Gross margin contracts 100–200 bps YoY but stabilizes",
        "Forward EPS growth 5–8% vs. bull case 15%+",
        "China demand stabilizes; no new export restrictions",
        "Competitive pressure from Samsung, Intel remains manageable"
      ]
    },
    {
      "name": "Bear",
      "probability_pct": 15,
      "thesis": "Geopolitical escalation (US export ban on <5nm nodes to China) triggers demand cliff; AI capex guidance cut >25%; margin compression to 40–42%; valuation multiple resets to 15–18x forward P/E",
      "valuation_implication": "$200–$280 (–43% to –20%); multiple compression on EPS stagnation or decline",
      "signposts": [
        "US bans advanced node exports to China; Taiwan strait tensions escalate",
        "NVIDIA, AMD capex cuts >25%; inventory builds in channel",
        "Gross margin falls to 40–42%; operating leverage lost",
        "Forward EPS stagnates or declines; 2026E guidance withdrawn",
        "China retaliatory tariffs; customer order cancellations"
      ]
    }
  ],
  "dated_catalyst_map": [
    {
      "catalyst": "April 13 begins critical week for equity market rally (macro/earnings inflection point)",
      "date_or_window": "2026-04-13",
      "related_scenarios": ["Base", "Bear"],
      "expected_impact": "3–5% intraweek volatility; risk-off sentiment if macro data disappoints; potential rotation out of high-beta tech names; TSM exposed to broad market risk-off",
      "confidence": "Medium"
    },
    {
      "catalyst": "China-Taiwan 'goodwill' measures and de-escalation signals",
      "date_or_window": "April 2026 (ongoing)",
      "related_scenarios": ["Bull", "Base"],
      "expected_impact": "Reduces geopolitical risk premium; supports bull thesis by 2–3%; lowers bear case probability; eases export restriction concerns",
      "confidence": "Medium-High"
    },
    {
      "catalyst": "TSM Q1 2026 earnings and forward guidance (investor call)",
      "date_or_window": "Late April 2026",
      "related_scenarios": ["All"],
      "expected_impact": "Critical signpost for forward EPS validation, margin trajectory, and capex outlook; determines whether bull/base/bear case probabilities hold; potential 5–10% stock move on guidance revisions",
      "confidence": "High"
    },
    {
      "catalyst": "NVIDIA, AMD Q1 2026 earnings (indirect signal of AI demand and TSM orders)",
      "date_or_window": "Mid-April to Late April 2026",
      "related_scenarios": ["Bull", "Base"],
      "expected_impact": "Sustained capex guidance validates bull thesis; cuts trigger base-to-bear shift; customer commentary on orders flows to TSM",
      "confidence": "Medium"
    },
    {
      "catalyst": "US-China trade policy clarity (tariffs, export controls on semiconductors)",
      "date_or_window": "Q2–Q3 2026",
      "related_scenarios": ["Base", "Bear"],
      "expected_impact": "Regulatory clarity reduces geopolitical risk premium; export ban would shift base case to bear; tariff announcements trigger volatility; high impact on valuation multiple",
      "confidence": "Medium"
    }
  ],
  "invalidation_triggers": [
    {
      "trigger": "Gross margin compresses below 43% (>400 bps YoY deterioration)",
      "affected_scenarios": ["Bull", "Base"],
      "severity": "High",
      "evidence_to_watch": "Q1 2026 earnings call; capacity utilization rates; pricing power commentary; cost inflation; competitive pricing pressure"
    },
    {
      "trigger": "US imposes export ban on <5nm nodes or advanced technology to China",
      "affected_scenarios": ["Bull", "Base"],
      "severity": "Critical",
      "evidence_to_watch": "CFIUS/EAR announcements; Taiwan geopolitical statements; US-China trade negotiations; Taiwan strait military activity"
    },
    {
      "trigger": "AI capex guidance cut >20% from major customers (NVIDIA, AMD, hyperscalers)",
      "affected_scenarios": ["Bull"],
      "severity": "Critical",
      "evidence_to_watch": "Earnings calls from NVIDIA, AMD, ASML (capex indicator); channel inventory builds; capacity utilization trends; order book commentary"
    },
    {
      "trigger": "Cross-strait military escalation or Taiwan blockade",
      "affected_scenarios": ["All"],
      "severity": "Critical",
      "evidence_to_watch": "Taiwan strait tensions; military drill announcements; diplomatic breakdowns; insurance/shipping cost spikes for Taiwan exports"
    },
    {
      "trigger": "TSM loses process leadership to Samsung 3nm or Intel 20A",
      "affected_scenarios": ["Bull"],
      "severity": "High",
      "evidence_to_watch": "Process node competitive roadmaps; yield benchmarks; customer migration announcements; ASML EUV tool allocation to competitors"
    },
    {
      "trigger": "Forward EPS guidance misses below $17/share (2026E)",
      "affected_scenarios": ["Bull", "Base"],
      "severity": "High",
      "evidence_to_watch": "Q1 2026 actuals; 2026 full-year guidance revision; organic growth deceleration; gross margin guidance cuts"
    }
  ]
}
```

---

## Next Steps & Investment Thesis

**Current Position:** Base case (50% probability) is most likely; valuation at 20x forward P/E is fair but leaves limited upside unless bull triggers materialize.

**Key Watch:** Q1 earnings (late April) and April 13 macro inflection will determine if base case holds or shifts toward bull/bear. China-Taiwan goodwill measures de-risk the geopolitical tail, but export restrictions remain a critical tail risk.

**Risk/Reward:** At $350.57, upside to bull ($420–$480) is 20–37%; downside to bear ($200–$280) is –43% to –20%. Base case offers limited alpha.