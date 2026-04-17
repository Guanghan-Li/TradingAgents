## NEE Scenario Framing

NEE screens as a high-quality but rate-sensitive utility/growth hybrid. The setup is mixed: fundamentals show strong margins and forward EPS support, while valuation is elevated for a regulated utility, leverage is high (`debt/equity 146.2`), and free cash flow is materially negative. News flow in the last 10 days is mostly supportive but soft in quality: analyst target hikes and thematic commentary around data center demand and solar exposure, rather than hard operating updates.

### Scenario Summary
- **Bull case: 30%**. NEE sustains premium valuation as data center power demand translates into incremental contracted renewables/generation opportunities, forward EPS de-risks, and long-duration yields remain contained. In this case, NEE continues to trade as a defensive growth utility rather than a plain regulated utility.
- **Base case: 50%**. NEE executes steadily, but upside is capped because much of the good news is already reflected near the top of the 52-week range. EPS grows, dividend remains intact, and sentiment stays constructive, but higher long-end yields and valuation discipline keep shares range-bound.
- **Bear case: 20%**. Higher-for-longer rates, financing pressure, or weaker-than-expected project monetization compress the premium multiple. With negative free cash flow and heavy capital intensity, NEE is vulnerable if investors rotate away from bond proxies/growth utilities.

### Key Signposts
- Confirmation of **data center-related power/renewables contracts** or major customer wins.
- **Forward EPS cadence** versus the current `Forward PE ~20.9x` premium.
- **10Y Treasury direction** from the current `4.26%`; a renewed backup in yields is a direct valuation headwind.
- Any update on **capital plan, financing mix, or balance-sheet pressure** given negative free cash flow.
- Whether NEE can hold a premium multiple while already trading well above its `200-day average` and near its `52-week high`.

### Thesis Invalidation Logic
- The bullish thesis weakens materially if data center/power-demand enthusiasm does not convert into signed projects, if EPS guidance stalls, or if rates move higher enough to compress utility multiples.
- The bearish thesis is invalidated if NEE delivers clear backlog/contract wins, maintains strong earnings visibility, and the rate backdrop becomes more supportive.

## Catalyst Table

| Catalyst | Date or Window | Related Scenarios | Expected Impact | Confidence |
| --- | --- | --- | --- | --- |
| NEE earnings / guidance update | Late Apr to early May 2026 (typical window, unconfirmed) | Bull, Base, Bear | High; guidance and project commentary likely drive the next rerating | Medium |
| U.S. CPI release | Mid-Apr to mid-May 2026 recurring window | Base, Bear | Medium; hotter inflation could pressure long-end yields and utility valuations | Medium |
| Fed / policy communication | Next FOMC window in coming weeks (exact date not provided) | Base, Bear, Bull | High; rate sensitivity is central to NEE multiple support | Medium |
| Data center or renewable contract announcements | Rolling / anytime | Bull, Base | High if confirmed with size, counterparties, and timing | Low-Medium |
| Treasury yield moves / curve repricing | Continuous | Base, Bear | High; 10Y yield direction is a primary cross-asset driver for NEE | High |
| Analyst target/rating revisions | Ongoing | Bull, Base | Low-Medium; sentiment supportive but secondary to hard fundamentals | Medium |

```json
{
  "scenario_map": [
    {
      "name": "Bull",
      "probability_pct": 30,
      "thesis": "NEE preserves its premium utility-growth multiple as data center electricity demand converts into incremental contracted projects, forward EPS is realized, and interest rates remain contained enough to support long-duration defensive equities.",
      "valuation_implication": "Multiple stays elevated or expands modestly versus regulated utility peers; shares can remain near or above recent highs.",
      "signposts": [
        "Confirmed data center-related power or renewables contracts",
        "Upward or reaffirmed EPS guidance",
        "Stable-to-lower 10Y Treasury yields",
        "Constructive capital allocation and financing commentary"
      ]
    },
    {
      "name": "Base",
      "probability_pct": 50,
      "thesis": "NEE continues to execute operationally, but the stock consolidates because premium valuation already discounts much of the favorable outlook. Earnings remain solid and dividend support stays intact, though upside is limited by rates and valuation discipline.",
      "valuation_implication": "Range-bound trading with modest earnings-driven appreciation rather than major multiple expansion.",
      "signposts": [
        "In-line earnings and maintained guidance",
        "No major deterioration in balance-sheet metrics",
        "10Y yield remains around current levels",
        "Project pipeline remains intact but without major upside surprise"
      ]
    },
    {
      "name": "Bear",
      "probability_pct": 20,
      "thesis": "NEE derates if higher-for-longer rates, financing needs, or underwhelming project conversion expose the risk in paying a premium multiple for a capital-intensive utility with negative free cash flow and high leverage.",
      "valuation_implication": "Forward multiple compresses toward lower utility peer levels; downside can be meaningful even without a severe earnings miss.",
      "signposts": [
        "10Y Treasury yield moves materially higher",
        "Weak or cautious earnings guidance",
        "Limited evidence of monetizable data center demand",
        "Funding, capex, or balance-sheet strain becomes a larger investor focus"
      ]
    }
  ],
  "dated_catalyst_map": [
    {
      "catalyst": "NEE earnings / guidance update",
      "date_or_window": "Late Apr to early May 2026 (typical reporting window, unconfirmed)",
      "related_scenarios": ["Bull", "Base", "Bear"],
      "expected_impact": "High",
      "confidence": "Medium"
    },
    {
      "catalyst": "U.S. CPI release",
      "date_or_window": "Mid-Apr to mid-May 2026 recurring window",
      "related_scenarios": ["Base", "Bear"],
      "expected_impact": "Medium",
      "confidence": "Medium"
    },
    {
      "catalyst": "Fed / policy communication",
      "date_or_window": "Next FOMC window in coming weeks (exact date not provided)",
      "related_scenarios": ["Bull", "Base", "Bear"],
      "expected_impact": "High",
      "confidence": "Medium"
    },
    {
      "catalyst": "Data center or renewable contract announcements",
      "date_or_window": "Rolling / ongoing",
      "related_scenarios": ["Bull", "Base"],
      "expected_impact": "High",
      "confidence": "Low-Medium"
    },
    {
      "catalyst": "Treasury yield repricing",
      "date_or_window": "Continuous",
      "related_scenarios": ["Base", "Bear"],
      "expected_impact": "High",
      "confidence": "High"
    }
  ],
  "invalidation_triggers": [
    {
      "trigger": "No meaningful conversion of data center demand narrative into signed projects or backlog growth",
      "affected_scenarios": ["Bull"],
      "severity": "High",
      "evidence_to_watch": "Customer announcements, PPAs, pipeline disclosures, management commentary"
    },
    {
      "trigger": "Material rise in long-term Treasury yields from current levels",
      "affected_scenarios": ["Bull", "Base"],
      "severity": "High",
      "evidence_to_watch": "10Y U.S. Treasury yield, inflation prints, Fed messaging"
    },
    {
      "trigger": "Earnings miss or weaker forward guidance",
      "affected_scenarios": ["Bull", "Base"],
      "severity": "High",
      "evidence_to_watch": "Quarterly EPS, management outlook, analyst estimate revisions"
    },
    {
      "trigger": "Improving guidance plus confirmed contracted growth opportunities",
      "affected_scenarios": ["Bear"],
      "severity": "High",
      "evidence_to_watch": "Earnings call details, project awards, capex returns framework"
    },
    {
      "trigger": "Balance-sheet strain eases despite capex intensity",
      "affected_scenarios": ["Bear"],
      "severity": "Medium",
      "evidence_to_watch": "Financing updates, debt metrics, free cash flow trajectory"
    }
  ]
}
```