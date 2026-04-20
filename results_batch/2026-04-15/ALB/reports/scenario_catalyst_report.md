## ALB Scenario Framing
ALB has a high-beta recovery setup with fundamentals still in transition. The core tension is that trailing profitability remains weak (`EPS TTM -5.75`, net loss, low operating margin), while forward expectations and recent price strength imply a meaningful lithium-cycle recovery is being priced in. With ALB trading well above its 200-day average and recent news flow skewing positive, the stock is vulnerable to timing risk around confirmation of volume, pricing, and margin recovery.

### Scenario Summary
- **Bull case: 30%**. Lithium pricing and contract realizations improve faster than expected, ALB converts positive free cash flow into visible earnings recovery, and forward EPS expectations hold or rise. In that setup, the recent rerating can extend toward a premium chemicals/materials recovery multiple.
- **Base case: 45%**. Recovery continues but unevenly: earnings normalize versus the loss-making trailing period, yet upside is moderated by still-fragile margins, cyclical commodity sensitivity, and a stock that has already rallied sharply. That argues for range-bound appreciation with higher volatility around each update.
- **Bear case: 25%**. The recent rally runs ahead of fundamentals, lithium pricing or customer demand disappoints, and forward estimates get cut. Given ALB's beta and still-thin operating margin, downside can be sharp if the market stops underwriting a 2026 earnings rebound.

### Key Signposts
- Forward EPS revisions versus the current `8.81` forward EPS anchor.
- Evidence that free cash flow stays positive even if lithium pricing remains choppy.
- Margin trajectory: gross profit and operating margin need to inflect materially from depressed trailing levels.
- Whether management commentary confirms destocking is over and EV/battery demand is translating into realized pricing.
- Macro backdrop: easing policy expectations and a normal upward-sloping curve help cyclicals, but sticky CPI/PPI could delay multiple expansion.

### Invalidation Logic
- **Bull invalidates** if ALB posts another weak guide, margins fail to recover, or forward EPS is revised materially lower.
- **Base invalidates** if results sharply outperform and pricing recovery becomes clearly durable, or if losses re-accelerate and liquidity/balance-sheet concerns rise.
- **Bear invalidates** if earnings recovery is confirmed by multiple quarters of improving margins and estimate upgrades.

### Dated Catalyst Map
| Catalyst | Date or Window | Related Scenarios | Expected Impact | Confidence |
| --- | --- | --- | --- | --- |
| ALB earnings / guidance update | Late Apr to early May 2026 (inferred seasonal window; exact date not provided) | Bull, Base, Bear | Highest-impact company-specific catalyst for pricing, volumes, margins, and 2026 outlook | Medium |
| Monthly CPI / PPI releases | Mid-April to mid-May 2026 windows | Base, Bear | Sticky inflation could pressure rate-cut expectations and cyclicals valuation; softer prints would help multiple support | Medium |
| U.S. labor-market update | Early May 2026 window | Base, Bear | Strong labor with controlled inflation supports soft-landing base case; macro deterioration would hurt cyclical demand expectations | Medium |
| Next Fed decision / communication window | Q2 2026 (exact meeting date not provided in context) | Base, Bear, Bull | Dovish tone helps risk appetite and long-duration cyclicals; hawkish hold due to inflation would cap rerating | Low-Medium |
| Lithium market pricing / peer commentary | Ongoing through Q2 2026 | Bull, Bear | Peer updates and spot/contract signals can quickly shift sentiment on ALB earnings power | Medium |

```json
{
  "scenario_map": [
    {
      "name": "Bull",
      "probability_pct": 30,
      "thesis": "ALB converts recent momentum into a fundamental recovery as lithium pricing and realized contract economics improve, forward EPS expectations are maintained or revised higher, and free cash flow remains positive.",
      "valuation_implication": "Further rerating toward a premium cyclical recovery multiple with upside beyond the recent rally.",
      "signposts": [
        "Forward EPS revisions move higher from the current 8.81 consensus anchor",
        "Gross profit and operating margin improve materially from depressed trailing levels",
        "Management commentary confirms stronger battery-demand pull-through and reduced destocking",
        "Positive free cash flow persists through the recovery"
      ]
    },
    {
      "name": "Base",
      "probability_pct": 45,
      "thesis": "ALB recovers from trough conditions, but the improvement is uneven. Earnings normalize relative to the trailing loss, though commodity volatility and already-strong share-price performance limit near-term multiple expansion.",
      "valuation_implication": "Mostly range-bound trading with episodic upside around results, but elevated volatility and less room for error.",
      "signposts": [
        "Forward EPS holds roughly stable",
        "Margins improve gradually but remain below prior-cycle highs",
        "Recent analyst support continues without broad estimate upgrades",
        "Macro backdrop stays supportive enough for cyclicals but not clearly reflationary"
      ]
    },
    {
      "name": "Bear",
      "probability_pct": 25,
      "thesis": "The stock's rally has moved ahead of fundamentals. Lithium pricing, EV demand, or customer ordering disappoint, causing renewed estimate cuts and exposing weak trailing profitability.",
      "valuation_implication": "De-rating toward lower-cycle commodity/chemicals multiples with sharp downside given ALB's beta and earnings sensitivity.",
      "signposts": [
        "Forward EPS revisions trend lower",
        "Gross profit and operating margin fail to recover",
        "Management guides cautiously on pricing or customer demand",
        "Peer lithium names signal weaker realizations or slower recovery"
      ]
    }
  ],
  "dated_catalyst_map": [
    {
      "catalyst": "ALB earnings / guidance update",
      "date_or_window": "Late Apr to early May 2026 (inferred seasonal window; exact date not provided)",
      "related_scenarios": ["Bull", "Base", "Bear"],
      "expected_impact": "Primary catalyst for validating or rejecting the forward earnings recovery narrative.",
      "confidence": "Medium"
    },
    {
      "catalyst": "Monthly CPI / PPI releases",
      "date_or_window": "Mid-April to mid-May 2026 windows",
      "related_scenarios": ["Base", "Bear"],
      "expected_impact": "Sticky inflation would reduce odds of easier policy and pressure valuation support for cyclicals.",
      "confidence": "Medium"
    },
    {
      "catalyst": "U.S. labor-market update",
      "date_or_window": "Early May 2026 window",
      "related_scenarios": ["Base", "Bear"],
      "expected_impact": "A stable labor backdrop supports soft-landing demand assumptions; deterioration would hurt cyclical sentiment.",
      "confidence": "Medium"
    },
    {
      "catalyst": "Next Fed decision / communication window",
      "date_or_window": "Q2 2026 (exact meeting date not provided in context)",
      "related_scenarios": ["Bull", "Base", "Bear"],
      "expected_impact": "Dovish communication would support multiple expansion; hawkish tone would cap the rerating.",
      "confidence": "Low-Medium"
    },
    {
      "catalyst": "Lithium market pricing / peer commentary",
      "date_or_window": "Ongoing through Q2 2026",
      "related_scenarios": ["Bull", "Bear"],
      "expected_impact": "Incremental signals on lithium realizations can quickly change expectations for ALB's earnings power.",
      "confidence": "Medium"
    }
  ],
  "invalidation_triggers": [
    {
      "trigger": "Forward EPS estimates are cut materially below the current recovery profile",
      "affected_scenarios": ["Bull", "Base"],
      "severity": "High",
      "evidence_to_watch": "Consensus estimate revisions, management guidance, analyst target changes"
    },
    {
      "trigger": "Margins fail to recover despite the recent share-price rally",
      "affected_scenarios": ["Bull", "Base"],
      "severity": "High",
      "evidence_to_watch": "Gross profit, operating margin, EBITDA trend in the next earnings update"
    },
    {
      "trigger": "Lithium pricing and peer commentary improve sustainably",
      "affected_scenarios": ["Bear"],
      "severity": "High",
      "evidence_to_watch": "Peer results, sector commentary, realized pricing and contract updates"
    },
    {
      "trigger": "Macro inflation remains sticky and delays policy easing",
      "affected_scenarios": ["Bull", "Base"],
      "severity": "Medium",
      "evidence_to_watch": "CPI, PPI, Fed communications, Treasury yield repricing"
    }
  ]
}
```