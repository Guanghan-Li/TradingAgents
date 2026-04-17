**ASML Segment View (Ticker: ASML)**

ASML is best understood as a concentrated lithography franchise with one dominant value engine: `EUV`. The prefetched news flow points to EUV demand running ahead of supply into 2027, which supports durable backlog quality, pricing power, and a favorable mix. Company-level profitability remains strong, with TTM operating margin around 36.0% and Q1 2026 revenue of about EUR 8.77B versus EUR 9.72B in Q4 2025, suggesting some quarter-to-quarter lumpiness but no clear impairment in underlying demand.

`EUV` is the strategic core. It likely carries the highest gross margin and the strongest competitive insulation because it is tied to leading-edge logic and AI infrastructure spending. Recent commentary about AI spending resilience and EUV demand outpacing supply implies the segment remains the main upside driver for both growth and margin.

`DUV` remains a large and important cash generator, but it is more cyclical and more exposed to regional policy risk, especially China-related restrictions. It benefits from mature-node demand, foundry utilization recovery, and memory normalization, but its moat and pricing power are below EUV. The segment is still strategically important because it broadens ASML's revenue base and absorbs fab capacity investment outside the most advanced nodes.

`Installed Base Management` (service, support, upgrades) is the stabilizer. This business is typically more recurring, less cyclical than new system sales, and supportive of consolidated margin durability. As the EUV and DUV fleets grow, this segment should compound even if system shipments fluctuate.

The main concentration risk is that ASML's economics are heavily tied to a small number of large customers and to advanced-node capex timing. A second risk is mix: if DUV or service grows faster than EUV in a given period, revenue can still be solid while margin expansion slows. A third risk is supply chain execution, which recent coverage still flags as a constraint.

| Segment | Growth Outlook | Margin Trend | Trading Implication |
|---|---|---|---|
| EUV Systems | Strong | Improving to stable-high | Primary bullish driver; strongest backlog/pricing signal |
| DUV Systems | Moderate | Stable to slightly down vs EUV mix | Supports baseline revenue but adds cyclicality/policy risk |
| Installed Base Management | Steady | Stable to improving | Improves durability and downside support |

```json
{
  "business_unit_decomposition": [
    {
      "segment": "EUV Systems",
      "revenue_share_pct": null,
      "growth_trend": "Strong; demand appears to exceed supply based on recent news and earnings commentary",
      "strategic_role": "Primary growth and moat-defining business tied to leading-edge logic and AI-driven semiconductor capex"
    },
    {
      "segment": "DUV Systems",
      "revenue_share_pct": null,
      "growth_trend": "Moderate; supported by mature-node, foundry, and memory demand but more cyclical and policy-sensitive",
      "strategic_role": "Broadens customer exposure across less advanced nodes and remains an important cash-generating equipment franchise"
    },
    {
      "segment": "Installed Base Management / Services & Upgrades",
      "revenue_share_pct": null,
      "growth_trend": "Steady; benefits from the expanding installed base of EUV and DUV tools",
      "strategic_role": "Recurring revenue layer that improves resilience, customer lock-in, and margin stability"
    }
  ],
  "segment_economics": {
    "margin_profile": "Company-level margins are strong; EUV likely carries the highest margin and pricing power, DUV is solid but lower quality, and services/upgrades are supportive of stable profitability.",
    "capital_intensity": "High for system manufacturing and supplier coordination; comparatively lower incremental capital intensity for service and upgrade revenue.",
    "cyclicality": "Moderate overall; EUV demand is strategically durable but shipment timing is lumpy, DUV is more cyclical, and installed base revenue is the least cyclical."
  },
  "value_driver_map": [
    {
      "driver": "AI-related advanced logic demand",
      "impacted_segments": ["EUV Systems"],
      "direction": "Positive",
      "horizon": "12-24 months",
      "evidence": "Prefetched news cites ASML and TSMC indicating AI spending is not slowing down."
    },
    {
      "driver": "EUV demand exceeding current supply",
      "impacted_segments": ["EUV Systems", "Installed Base Management / Services & Upgrades"],
      "direction": "Positive",
      "horizon": "12-24 months",
      "evidence": "RBC commentary in prefetched news says EUV demand is outpacing supply and points to strong growth in 2027."
    },
    {
      "driver": "Supply chain constraints",
      "impacted_segments": ["EUV Systems", "DUV Systems"],
      "direction": "Negative",
      "horizon": "0-12 months",
      "evidence": "Prefetched earnings-call summary highlights strong sales alongside supply chain challenges."
    },
    {
      "driver": "China export controls / regional restrictions",
      "impacted_segments": ["DUV Systems", "EUV Systems"],
      "direction": "Negative",
      "horizon": "6-24 months",
      "evidence": "Prefetched news explicitly references China curbs as part of the ASML narrative."
    },
    {
      "driver": "Growing installed fleet requiring service and upgrades",
      "impacted_segments": ["Installed Base Management / Services & Upgrades"],
      "direction": "Positive",
      "horizon": "12-36 months",
      "evidence": "Inferred from ASML's expanding shipment base and the typical annuity characteristics of semiconductor equipment service revenue."
    }
  ]
}
```