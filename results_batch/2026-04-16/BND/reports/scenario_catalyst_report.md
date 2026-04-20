## BND Scenario Summary

BND is trading near its medium-term averages (`74.08` 50-day, `74.06` 200-day) and closer to the top of its `71.76-75.23` 52-week range, which suggests the market is already discounting a fairly benign rate path. The key driver for BND over the next 1-3 months is rate direction: with the Fed funds rate at `3.64%`, CPI and PPI re-accelerating in March, and a positively sloped 2Y-10Y curve (`+0.53%`), BND has carry support from its `3.91%` yield but remains exposed to any renewed move higher in intermediate and long Treasury yields.

### Scenario Framing

| Scenario | Prob. | What Has To Happen | Implication For BND |
| --- | ---: | --- | --- |
| Bull | 30% | Inflation data cools after March, labor softens modestly, and the market pulls forward easing expectations or at least prices lower term yields | Price upside toward/through the 52-week high as duration tailwinds add to carry |
| Base | 50% | Growth stays okay, inflation remains mixed, and the Fed stays near neutral with yields range-bound | BND behaves mostly as an income vehicle, with modest total return driven by yield rather than price |
| Bear | 20% | Inflation stays sticky or re-accelerates, term premium rises, and the 10Y/long end backs up further | Price retracement toward the lower half of the 52-week range offsets carry |

### Key Signposts

- `10Y` Treasury yield relative to the current `4.29%` level. Sustained downside is constructive for BND; another leg higher is the main risk.
- Next inflation prints after March CPI/PPI. March was firm on both series, so BND needs evidence that this was not a new inflation upswing.
- Labor-market cooling versus continued resilience. A softer unemployment/payroll trend would help duration.
- Whether BND can hold above its `50-day`/`200-day` averages. Losing both would imply rate pressure is dominating carry.

### Thesis Invalidation Logic

- Bull case is invalidated if inflation remains sticky for multiple prints and long-end yields continue rising despite stable Fed policy.
- Base case is invalidated if macro data break decisively in either direction, producing either a strong bond rally or a sharper term-premium selloff.
- Bear case is invalidated if disinflation resumes quickly and the market starts pricing a clearer easing path.

### Dated Catalyst Map

| Catalyst | Date or Window | Related Scenarios | Expected Impact | Confidence |
| --- | --- | --- | --- | --- |
| Next U.S. CPI release | Late Apr to mid-May 2026 | Bull, Base, Bear | Most important near-term signal for whether March inflation strength was noise or trend | Medium |
| Next U.S. PPI release | Late Apr to mid-May 2026 | Bull, Base, Bear | Confirms or challenges inflation pipeline pressure; can move Treasury yields and BND quickly | Medium |
| Next U.S. jobs report | Early May 2026 | Bull, Base, Bear | Softer labor data would favor BND; firm payrolls/unemployment can keep yields elevated | Medium |
| Fed communication / next policy window | Next FOMC window, spring 2026 | Bull, Base, Bear | Even without a rate change, tone on inflation persistence versus neutrality matters for duration | Low |
| Treasury supply / auction windows | Ongoing over the next 2-6 weeks | Base, Bear | Weak demand or higher term premium would pressure BND even if the Fed stays unchanged | Low |

```json
{
  "scenario_map": [
    {
      "name": "bull",
      "probability_pct": 30,
      "thesis": "BND benefits if post-March inflation data cool, labor conditions soften modestly, and intermediate-to-long Treasury yields fall from current levels, allowing duration gains to add to the fund's 3.91% yield.",
      "valuation_implication": "BND can retest and potentially exceed its 52-week high of 75.23, producing above-carry total returns.",
      "signposts": [
        "10Y Treasury yield falls below the current 4.29% area",
        "Next CPI and PPI prints come in softer than March",
        "Unemployment rate drifts higher or payroll growth cools",
        "BND holds above its 50-day and 200-day averages"
      ]
    },
    {
      "name": "base",
      "probability_pct": 50,
      "thesis": "BND remains range-bound as growth stays intact, inflation is mixed rather than clearly improving, and the Fed remains near neutral with no decisive change in rate expectations.",
      "valuation_implication": "Total return is driven mainly by income carry, with price action oscillating around current levels near the 50-day and 200-day averages.",
      "signposts": [
        "10Y Treasury yield remains near current levels",
        "Inflation data are inconsistent but not materially worse",
        "Fed policy stays unchanged around 3.64% effective funds rate",
        "BND trades inside the current 52-week range without breakout"
      ]
    },
    {
      "name": "bear",
      "probability_pct": 20,
      "thesis": "BND weakens if inflation stays sticky or re-accelerates, term premium rises, and the long end of the Treasury curve reprices higher despite unchanged Fed policy.",
      "valuation_implication": "Price pressure offsets coupon income and pushes BND back toward the lower half of its 71.76-75.23 52-week range.",
      "signposts": [
        "10Y and 30Y Treasury yields make sustained moves higher",
        "CPI and PPI remain firm for multiple releases",
        "Labor data stay resilient enough to delay easing expectations",
        "BND breaks below its 50-day and 200-day averages"
      ]
    }
  ],
  "dated_catalyst_map": [
    {
      "catalyst": "Next U.S. CPI release",
      "date_or_window": "Late Apr to mid-May 2026",
      "related_scenarios": ["bull", "base", "bear"],
      "expected_impact": "A softer print would support BND through lower Treasury yields; a firm print would reinforce duration pressure.",
      "confidence": "medium"
    },
    {
      "catalyst": "Next U.S. PPI release",
      "date_or_window": "Late Apr to mid-May 2026",
      "related_scenarios": ["bull", "base", "bear"],
      "expected_impact": "Confirms whether pipeline inflation is cooling or worsening, affecting intermediate-rate expectations and BND pricing.",
      "confidence": "medium"
    },
    {
      "catalyst": "Next U.S. jobs report",
      "date_or_window": "Early May 2026",
      "related_scenarios": ["bull", "base", "bear"],
      "expected_impact": "A softer labor print would help the bull case; continued resilience would support the base-to-bear path.",
      "confidence": "medium"
    },
    {
      "catalyst": "Fed communication / next policy window",
      "date_or_window": "Spring 2026",
      "related_scenarios": ["bull", "base", "bear"],
      "expected_impact": "Tone on inflation persistence and neutrality can move duration expectations even without a policy-rate change.",
      "confidence": "low"
    },
    {
      "catalyst": "Treasury supply and auction windows",
      "date_or_window": "Next 2-6 weeks",
      "related_scenarios": ["base", "bear"],
      "expected_impact": "Weak auction demand or rising term premium would pressure broad bond ETFs including BND.",
      "confidence": "low"
    }
  ],
  "invalidation_triggers": [
    {
      "trigger": "Inflation remains firm for multiple consecutive releases and long-end Treasury yields continue rising",
      "affected_scenarios": ["bull"],
      "severity": "high",
      "evidence_to_watch": "CPI, PPI, 10Y Treasury yield, 30Y Treasury yield"
    },
    {
      "trigger": "Macro data break decisively softer or hotter instead of staying mixed and range-bound",
      "affected_scenarios": ["base"],
      "severity": "medium",
      "evidence_to_watch": "Payrolls, unemployment rate, CPI, Treasury yield volatility"
    },
    {
      "trigger": "Disinflation resumes quickly and the market prices a clearer easing path",
      "affected_scenarios": ["bear"],
      "severity": "high",
      "evidence_to_watch": "CPI trend, Fed communications, 2Y and 10Y Treasury yields"
    }
  ]
}
```