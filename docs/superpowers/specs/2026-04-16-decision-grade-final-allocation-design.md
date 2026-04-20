# Decision-Grade Final Allocation Design

## Goal

Replace the current final-allocation ranking flow with a decision-grade portfolio committee memo that can be rendered to Markdown and PDF. The future system must produce a materially stronger artifact than the current ranked-list output while remaining reliable in unattended batch runs.

This design covers the allocation-decision stage only. It does not redesign the underlying single-name research agents.

## Hard Requirements

- The final allocation must always select exactly 3 names.
- Every selected name must have a final top-line decision of `Buy`.
- No selected name may have a top-line `Hold`, `Neutral`, `Sell`, `Underweight`, or equivalent non-buy stance.
- The final allocation must always allocate exactly `$200`.
- Each of the 3 selected names must receive a positive dollar allocation.
- The primary artifact must be decision-grade, not merely ranked or descriptive.
- The normal path must use the full underlying report stack for each eligible name, not just compact packets.
- The system must retry if the primary decision-grade scorer fails.
- If retries still fail, the system must emit a clearly labeled fallback artifact instead of silently masquerading as a decision-grade memo.

## Non-Goals

- Do not allow 1-name or 2-name allocations in the final system.
- Do not allow cash allocations in the primary or fallback artifact.
- Do not allow selected names whose top-line decision is not `Buy`.
- Do not rely on generic justification phrases such as "stronger support" without naming evidence.
- Do not present the output as a leaderboard-first document.

## Problems With The Current Design

The current final allocation flow is not decision-grade for four reasons:

1. It is optimized for ranking output instead of portfolio committee reasoning.
2. It relies on compact stock packets that strip out too much of the underlying analysis.
3. It allows shallow comparative language that does not prove why a selected name beat a close alternative.
4. Its fallback path is deterministic and useful for continuity, but not decision-grade.

## User-Facing Outcome

The final artifact should read like an investment committee memorandum, not a screening table. A strong reader should be able to answer the following from the PDF alone:

- Why these exact 3 names were chosen
- Why the chosen 3 beat the closest rejected `Buy` names
- Why the weights differ
- What evidence matters most
- What evidence weakens the case
- What would invalidate the allocation
- How much confidence the committee has in the decision

## Eligible Universe

The decision engine must build its candidate set from completed same-day runs whose final top-line decision is `Buy`.

Eligibility rules:

- Include only completed same-day runs.
- Include only names with final top-line `Buy`.
- Exclude any name whose final top-line decision is not `Buy`, even if some lower-level narrative appears favorable.
- Preserve the original top-line decision and stance from the source report; never relabel a non-buy name as a buy during allocation.

## Evidence Inputs

The primary decision-grade scorer must consume a richer per-name packet assembled from the existing artifact stack.

Minimum per-name evidence to provide:

- top-line decision
- relative stance
- chief summary
- chief thesis
- risk summary
- scenario probabilities when available
- initial weight, target weight, and max loss when available
- key catalysts
- timing and technical-entry notes
- valuation notes
- any explicit invalidation or stop logic

The daily summary may still be included as context, but it should not substitute for per-name evidence.

## Decision Standard

The primary scorer is a portfolio committee decision writer, not a ranking assistant.

It must:

- choose exactly 3 names from the eligible `Buy` universe
- allocate exactly `$200` across the 3 names
- defend the selection at the portfolio level and at the single-name level
- directly compare selected names against the strongest rejected `Buy` alternatives
- explain not only thesis quality, but also entry quality and downside control
- state when a selected name wins on defensiveness, timing, asymmetry, or cross-name diversification
- state when a rejected name lost due to entry quality, concentration, valuation stretch, timing, catalyst asymmetry, weaker downside control, or weaker role in the 3-name portfolio

It must not:

- rely on generic comparative filler
- hide rejected alternatives behind "the rest"
- rank names only by stance label
- allocate weights by normalized scores without explicit portfolio reasoning

## Primary Output Contract

The scorer should return structured JSON that can drive both Markdown and PDF rendering.

Required top-level sections:

- `executive_decision`
- `selected_positions`
- `rejected_close_alternatives`
- `portfolio_risks`
- `decision_quality`

### `executive_decision`

Purpose:

- summarize the final 3-name allocation in committee language

Required fields:

- `summary`
- `why_this_portfolio`
- `weighting_principle`
- `total_allocated_dollars`

Constraints:

- `total_allocated_dollars` must equal `200`

### `selected_positions`

Exactly 3 objects, no duplicates.

Required fields per object:

- `ticker`
- `allocated_dollars`
- `weight_pct`
- `selection_role`
- `core_thesis`
- `key_supporting_evidence`
- `key_disconfirming_evidence`
- `entry_quality_assessment`
- `why_it_beats_closest_rejected_buy`
- `risk_controls_and_invalidation`
- `confidence`

Constraints:

- every `allocated_dollars` must be a positive integer
- the sum of `allocated_dollars` across the 3 objects must equal `200`
- `ticker` must refer to a same-day eligible `Buy`
- `why_it_beats_closest_rejected_buy` must name at least one rejected `Buy` ticker
- `entry_quality_assessment` must explicitly address timing or valuation, not just business quality

### `rejected_close_alternatives`

At least 3 objects, unless fewer than 3 rejected `Buy` names exist.

Required fields per object:

- `ticker`
- `why_it_was_close`
- `why_it_lost`
- `what_would_have_changed_the_decision`

Constraints:

- each object must reference a rejected eligible `Buy`
- at least one rejected name must be directly compared against each selected position across the overall memo

### `portfolio_risks`

Required fields:

- `top_risks`
- `concentration_notes`
- `macro_notes`
- `timing_notes`

### `decision_quality`

Required fields:

- `evidence_quality`
- `main_assumptions`
- `known_weak_points`
- `internal_consistency_check`

Purpose:

- force the memo to admit where the decision is strong and where it is carrying assumptions

## Primary Prompt Design

The prompt should explicitly define the model as an investment committee memo writer.

It should instruct the model to:

- work only from supplied evidence
- select exactly 3 `Buy` names
- allocate exactly `$200`
- justify why the 3 selected names beat the closest rejected `Buy` names
- explain the weighting differences
- discuss both upside case and entry quality
- admit weak evidence where it exists
- avoid generic phrases such as:
  - stronger support
  - better overall profile
  - higher conviction without saying why
  - the rest of the names

It should also require:

- explicit mention of named rejected alternatives
- portfolio-level reasoning, not just single-name praise
- internal consistency with the supplied top-line decisions

## Verification Pass

Add a verifier stage after the primary scorer returns JSON and before Markdown/PDF rendering.

The verifier checks:

- exactly 3 selected positions
- all selected positions are valid same-day `Buy` names
- no selected name is non-buy
- total dollars equals `200`
- every selected position has positive dollars
- each selected position includes a named rejected comparison
- rejected alternatives are valid rejected `Buy` names
- the memo does not contradict top-line source decisions
- all required fields are present and non-empty

If verification fails, the run should retry rather than render a broken committee memo.

## Retry Strategy

The system should retry once before falling back.

Recommended sequence:

1. Primary attempt:
   - deep reasoning
   - full evidence packet
   - strict decision-grade schema
2. Retry attempt:
   - same schema
   - tighter prompt
   - reduced reasoning cost or shorter context framing if needed

The retry must aim for the same artifact quality and structure. It is not a fallback.

## Fallback Artifact

If both primary and retry attempts fail, emit a clearly labeled fallback artifact.

Fallback requirements:

- it must still select exactly 3 eligible `Buy` names
- it must still allocate exactly `$200`
- it must clearly declare at the top that it is a fallback allocation memo
- it must clearly state why fallback was used
- it must not present itself as a full committee-grade memo
- it must remain internally consistent with source decisions

Fallback tone:

- factual
- explicit about limitations
- no fake comparative precision

Fallback content should be reduced and honest:

- selected names and weights
- short rationale based on deterministic ranking rules
- named closest rejected `Buy` alternatives
- risk note that this is continuity output, not the preferred decision-grade memo

## Markdown and PDF Structure

The primary artifact should be rendered in this order:

1. Executive Decision
2. Selected Positions and Allocations
3. Why This Portfolio, Not The Next-Best Portfolio
4. Position Memos
5. Closest Rejected Buy Alternatives
6. Portfolio Risks
7. Decision Quality and Key Assumptions

If fallback is used, prepend a visible fallback banner section:

- title line indicating fallback status
- reason fallback was triggered
- note that the artifact is continuity output, not the preferred committee memo

## Data Flow Changes

New or changed flow:

1. collect eligible same-day `Buy` runs
2. assemble rich per-name evidence packets
3. run primary decision-grade scorer
4. verify result
5. if failed, retry once
6. verify retry result
7. if failed again, build clearly labeled fallback allocation
8. render Markdown
9. render PDF

## Testing Strategy

Add tests for:

- exactly 3 selected positions in primary path
- selected names must all be `Buy`
- total allocation equals `200`
- verifier rejects non-buy selections
- verifier rejects wrong dollar totals
- verifier rejects missing rejected-name comparisons
- retry path triggers on timeout or invalid schema
- fallback artifact is clearly labeled
- fallback still selects exactly 3 `Buy` names and allocates `200`
- Markdown rendering includes the new committee-memo sections
- PDF generation still succeeds for both primary and fallback artifacts

## Migration Notes

The current `generate_final_allocation_scores()` contract is ranking-oriented and too narrow. It should be replaced or split so the decision-grade flow has its own schema and prompt contract.

The current fallback logic can remain conceptually, but it must be repositioned as an explicitly limited continuity artifact rather than a substitute for the committee memo.

## Recommendation

Implement this as a distinct decision-grade allocation pipeline rather than incrementally patching the current ranking prompt. The current prompt shape and schema encode the wrong task. A clean committee-memo contract will be easier to verify, easier to render, and much more likely to produce stable decision-grade PDFs.
