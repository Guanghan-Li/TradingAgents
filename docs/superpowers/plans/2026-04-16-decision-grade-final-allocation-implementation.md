# Decision-Grade Final Allocation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the current ranking-style final allocation flow with a decision-grade committee memo that always selects exactly 3 `Buy` names, always allocates exactly `$200`, retries once on scorer failure, and emits a clearly labeled fallback artifact if both decision-grade attempts fail.

**Architecture:** Introduce a richer evidence-packet builder, a decision-grade scorer schema and prompt, a verifier that enforces the business rules, a retry path that preserves the same schema, and a separately labeled fallback memo path. Keep Markdown/PDF rendering in `cli/automation.py`, but change it from a leaderboard renderer to a committee-memo renderer driven by structured output.

**Tech Stack:** Python, pytest, Ruff, existing `cli/automation.py` batch pipeline, local CLI-backed LLM clients.

---

## File Map

### Existing files to modify

- `cli/automation.py`
  - Add rich evidence packet collection for eligible `Buy` runs.
  - Replace the current ranking prompt/schema with a decision-grade committee memo prompt/schema.
  - Add verifier logic for the committee memo contract.
  - Add retry orchestration for the primary scorer.
  - Replace current Markdown rendering sections with committee-memo sections.
  - Replace fallback content so it remains clearly labeled and internally consistent with the new exactly-3 / `$200` rules.
- `tests/test_batch_summary.py`
  - Add unit tests for rich packet building, decision-grade schema validation, retry behavior, fallback labeling, exactly-3 enforcement, and new Markdown sections.
- `tests/test_batch_cli.py`
  - Add or update tests to confirm the batch driver still calls final allocation generation and preserves returned artifact paths under the new flow.

### New files to create

- None required unless `cli/automation.py` becomes too unwieldy during implementation.

### Optional split if `cli/automation.py` becomes too large during implementation

- `cli/allocation_decision.py`
  - Extract prompt building, schema validation, retry orchestration, and fallback memo generation.
- `tests/test_allocation_decision.py`
  - Move targeted decision-pipeline tests out of `tests/test_batch_summary.py`.

Only split if the implementation becomes hard to reason about inside `cli/automation.py`. Do not do an unrelated refactor.

## Task 1: Lock Down Rich Buy-Only Candidate Input

**Files:**
- Modify: `cli/automation.py`
- Test: `tests/test_batch_summary.py`

- [ ] **Step 1: Write the failing test for eligible decision candidates**

Add a test that creates a same-day batch directory with mixed `Buy`, `Hold`, and `Sell` runs and asserts the decision input builder returns only completed same-day `Buy` names with richer fields than the current compact packets.

```python
def test_build_decision_allocation_packets_keeps_only_completed_buys_and_collects_rich_fields(tmp_path):
    ...
    packets = build_decision_allocation_packets(results_dir=tmp_path, analysis_date="2026-04-16")
    assert [packet["ticker"] for packet in packets] == ["AMZN", "MU", "NVDA"]
    assert packets[0]["chief_summary"]
    assert packets[0]["chief_thesis"]
    assert packets[0]["risk_summary"]
    assert packets[0]["decision"] == "Buy"
```

- [ ] **Step 2: Run the targeted test and verify it fails**

Run: `python -m pytest tests/test_batch_summary.py -k decision_allocation_packets -v`

Expected: FAIL because the richer builder does not exist yet.

- [ ] **Step 3: Implement the minimal rich packet builder**

In `cli/automation.py`, add a new helper that:

- scans same-day run summaries
- filters to completed same-day `Buy` names only
- preserves top-line decision and relative stance
- carries rich narrative fields needed by the committee memo
- captures sizing, scenario, catalyst, and invalidation details when present

Prefer a new helper rather than overloading the current compact packet builder.

- [ ] **Step 4: Run the targeted test and verify it passes**

Run: `python -m pytest tests/test_batch_summary.py -k decision_allocation_packets -v`

Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add cli/automation.py tests/test_batch_summary.py
git commit -m "feat: add rich buy-only allocation input packets"
```

## Task 2: Replace Ranking Schema With Decision-Grade Committee Schema

**Files:**
- Modify: `cli/automation.py`
- Test: `tests/test_batch_summary.py`

- [ ] **Step 1: Write the failing test for the new scorer contract**

Add a test that stubs the LLM response and asserts the primary decision scorer accepts only the new committee-memo structure:

- `executive_decision`
- `selected_positions`
- `rejected_close_alternatives`
- `portfolio_risks`
- `decision_quality`

It should also assert the scorer requires exactly 3 selected positions and `$200` total allocation.

```python
def test_generate_decision_grade_allocation_requires_committee_schema(monkeypatch):
    ...
    payload = generate_decision_grade_allocation(...)
    assert len(payload["selected_positions"]) == 3
    assert payload["executive_decision"]["total_allocated_dollars"] == 200
```

- [ ] **Step 2: Run the targeted test and verify it fails**

Run: `python -m pytest tests/test_batch_summary.py -k committee_schema -v`

Expected: FAIL because the scorer still uses the ranking schema.

- [ ] **Step 3: Implement the new primary prompt and parser**

In `cli/automation.py`:

- add a new prompt builder that defines the model as an investment committee decision writer
- remove ranking-first instructions from the primary path
- require direct comparison versus rejected `Buy` alternatives
- require exact 3-name output and exact `$200` allocation
- parse the new JSON contract

Do not delete the fallback path yet.

- [ ] **Step 4: Run the targeted test and verify it passes**

Run: `python -m pytest tests/test_batch_summary.py -k committee_schema -v`

Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add cli/automation.py tests/test_batch_summary.py
git commit -m "feat: add decision-grade allocation scorer schema"
```

## Task 3: Add Verifier That Rejects Broken Committee Memos

**Files:**
- Modify: `cli/automation.py`
- Test: `tests/test_batch_summary.py`

- [ ] **Step 1: Write failing tests for verifier rules**

Add separate tests that fail when:

- fewer or more than 3 selected positions are returned
- a selected name is not a valid same-day `Buy`
- the dollar total is not exactly `200`
- a selected position has `0` dollars
- selected positions do not name rejected comparisons
- rejected alternatives are not valid rejected `Buy` names

```python
def test_verify_decision_grade_allocation_rejects_non_buy_selection():
    ...
    with pytest.raises(ValueError):
        verify_decision_grade_allocation(...)
```

- [ ] **Step 2: Run the targeted tests and verify they fail**

Run: `python -m pytest tests/test_batch_summary.py -k verify_decision_grade_allocation -v`

Expected: FAIL because verifier logic does not exist yet.

- [ ] **Step 3: Implement the verifier**

Add a verifier helper in `cli/automation.py` that checks:

- exactly 3 selections
- no duplicates
- all selected names are valid eligible `Buy` names
- all rejected alternatives are valid rejected `Buy` names
- total dollars equals `200`
- each selected name has positive dollars
- each selected name contains named rejected comparisons
- required fields are present and non-empty

- [ ] **Step 4: Run the targeted tests and verify they pass**

Run: `python -m pytest tests/test_batch_summary.py -k verify_decision_grade_allocation -v`

Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add cli/automation.py tests/test_batch_summary.py
git commit -m "feat: verify decision-grade allocation outputs"
```

## Task 4: Add Retry Orchestration Before Fallback

**Files:**
- Modify: `cli/automation.py`
- Test: `tests/test_batch_summary.py`

- [ ] **Step 1: Write failing tests for retry behavior**

Add tests that prove:

- timeout on first attempt triggers a retry
- invalid schema on first attempt triggers a retry
- second successful attempt is accepted
- fallback is not used when retry succeeds

```python
def test_generate_decision_grade_allocation_retries_after_timeout(monkeypatch):
    ...
    assert calls == ["primary", "retry"]
```

- [ ] **Step 2: Run the targeted tests and verify they fail**

Run: `python -m pytest tests/test_batch_summary.py -k retries_after_timeout -v`

Expected: FAIL because the primary decision-grade path does not exist with retry orchestration yet.

- [ ] **Step 3: Implement retry orchestration**

In `cli/automation.py`:

- add a primary-attempt configuration
- add a retry-attempt configuration with same schema and tighter cost envelope
- rerun verification after retry
- only proceed to fallback if both attempts fail

Keep retry orchestration isolated so it is easy to test.

- [ ] **Step 4: Run the targeted tests and verify they pass**

Run: `python -m pytest tests/test_batch_summary.py -k retries_after_timeout -v`

Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add cli/automation.py tests/test_batch_summary.py
git commit -m "feat: retry decision-grade allocation before fallback"
```

## Task 5: Redesign The Fallback Artifact To Be Honest And Rule-Compliant

**Files:**
- Modify: `cli/automation.py`
- Test: `tests/test_batch_summary.py`

- [ ] **Step 1: Write failing tests for fallback artifact rules**

Add tests that require the fallback artifact to:

- be explicitly labeled as fallback
- still select exactly 3 names
- select only valid same-day `Buy` names
- allocate exactly `$200`
- render a visible fallback banner in Markdown

```python
def test_generate_final_allocation_markdown_labels_fallback_and_selects_exactly_three(tmp_path, monkeypatch):
    ...
    assert "Fallback Allocation Memo" in markdown
    assert len(selected_rows) == 3
```

- [ ] **Step 2: Run the targeted tests and verify they fail**

Run: `python -m pytest tests/test_batch_summary.py -k fallback_allocation_memo -v`

Expected: FAIL because the existing fallback is ranking-oriented and not exact-3 constrained.

- [ ] **Step 3: Implement the new fallback contract**

Change fallback generation so it:

- picks exactly 3 eligible `Buy` names
- allocates exactly `$200`
- uses deterministic but honest tie-breaking
- emits a labeled fallback executive section
- never uses fake committee-grade language

Do not let fallback relabel non-buy names as buys.

- [ ] **Step 4: Run the targeted tests and verify they pass**

Run: `python -m pytest tests/test_batch_summary.py -k fallback_allocation_memo -v`

Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add cli/automation.py tests/test_batch_summary.py
git commit -m "feat: add labeled exact-three fallback allocation memo"
```

## Task 6: Replace Markdown Rendering With Committee-Memo Sections

**Files:**
- Modify: `cli/automation.py`
- Test: `tests/test_batch_summary.py`

- [ ] **Step 1: Write failing tests for the new Markdown structure**

Add tests that assert the rendered allocation Markdown contains:

- `Executive Decision`
- `Selected Positions and Allocations`
- `Why This Portfolio, Not The Next-Best Portfolio`
- `Position Memos`
- `Closest Rejected Buy Alternatives`
- `Portfolio Risks`
- `Decision Quality and Key Assumptions`

Also add a fallback-markdown test that asserts the fallback banner appears only for fallback output.

```python
def test_render_decision_grade_allocation_markdown_uses_committee_sections():
    ...
    assert "## Executive Decision" in markdown
    assert "## Position Memos" in markdown
```

- [ ] **Step 2: Run the targeted tests and verify they fail**

Run: `python -m pytest tests/test_batch_summary.py -k committee_sections -v`

Expected: FAIL because the current renderer still uses the ranking-table structure.

- [ ] **Step 3: Implement the renderer changes**

Update `render_final_allocation_markdown()` or replace it with a new renderer that:

- consumes the decision-grade schema
- renders the committee memo sections in the approved order
- handles fallback banner rendering cleanly
- preserves enough table structure for the existing PDF renderer to remain workable

- [ ] **Step 4: Run the targeted tests and verify they pass**

Run: `python -m pytest tests/test_batch_summary.py -k committee_sections -v`

Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add cli/automation.py tests/test_batch_summary.py
git commit -m "feat: render final allocation as committee memo"
```

## Task 7: Wire The New Pipeline Into Batch Final Allocation Generation

**Files:**
- Modify: `cli/automation.py`
- Test: `tests/test_batch_cli.py`
- Test: `tests/test_batch_summary.py`

- [ ] **Step 1: Write failing integration tests for final artifact generation**

Add or update tests that prove:

- `generate_final_allocation_artifacts()` uses the decision-grade pipeline
- the artifact paths are still written
- batch command still returns `final_allocation`
- fallback still writes both Markdown and PDF

```python
def test_run_batch_command_generates_decision_grade_final_allocation_artifacts(...):
    ...
    assert result["final_allocation"]["markdown_path"].endswith("final_allocation.md")
```

- [ ] **Step 2: Run the targeted integration tests and verify they fail if needed**

Run: `python -m pytest tests/test_batch_cli.py -k final_allocation -v`

Expected: adjust tests until they fail for the right reason before implementation.

- [ ] **Step 3: Wire the new pipeline into artifact generation**

Update the final allocation generation path to:

- build rich decision packets
- execute primary scorer
- verify
- retry on failure
- fall back if both attempts fail
- render Markdown and PDF

Keep the public return shape unchanged where possible:

- `markdown_path`
- `pdf_path`

- [ ] **Step 4: Run the targeted integration tests and verify they pass**

Run: `python -m pytest tests/test_batch_cli.py -k final_allocation -v`

Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add cli/automation.py tests/test_batch_cli.py tests/test_batch_summary.py
git commit -m "feat: wire decision-grade final allocation pipeline into batch artifacts"
```

## Task 8: Full Verification And Cleanup

**Files:**
- Modify: any files required by previous tasks only
- Test: `tests/test_batch_summary.py`
- Test: `tests/test_batch_cli.py`

- [ ] **Step 1: Run the focused allocation test suite**

Run: `python -m pytest tests/test_batch_summary.py tests/test_batch_cli.py -v`

Expected: PASS

- [ ] **Step 2: Run lint on touched files**

Run: `ruff check cli/automation.py tests/test_batch_summary.py tests/test_batch_cli.py`

Expected: `All checks passed!`

- [ ] **Step 3: Run any additional project checks that are available in the environment**

Run: `python -m pytest tests/test_batch_summary.py -k "allocation or committee or fallback" -v`

Expected: PASS

If `mypy` is installed:

Run: `mypy cli/automation.py tests/test_batch_summary.py tests/test_batch_cli.py`

Expected: no type errors

- [ ] **Step 4: Manual artifact smoke test**

Run a local generation pass against an existing results date and inspect:

- selected names are exactly 3
- all selected names are `Buy`
- total equals `$200`
- fallback banner appears only on fallback
- rejected alternatives are named specifically

- [ ] **Step 5: Commit**

```bash
git add cli/automation.py tests/test_batch_summary.py tests/test_batch_cli.py
git commit -m "test: verify decision-grade final allocation pipeline"
```
