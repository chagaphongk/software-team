---
name: ai-software-team
description: Run tasks as a multi-role AI team (Researcher → Architect → Developer → Reviewer → Verifier) within a single conversation — one Claude instance switching hats, no subagents spawned — with human approval gates, instead of answering in one pass. Use this skill when the user wants that single-transcript role discipline specifically: explicit mentions of "wear hats", "researcher/architect/developer/reviewer", "work like an agent team" without needing real subagent orchestration, or when no subagent/Task-tool access is available. If the environment also has a subagent-orchestration skill installed (e.g. one that classifies risk tiers and dispatches real researcher/builder/verifier subagents), prefer that one for tasks needing real parallel delegation, multi-file builds, or tiered model routing — reach for this skill instead when the value is the audit trail and gate discipline of a single inspectable turn, or for non-code deliverables that benefit from plan-then-review (design docs, data analysis, specs) and quick reviews/critiques. Do NOT use for trivial one-liner questions or quick syntax lookups.
---

# AI Software Team

Work as a five-role "team" within Claude itself (Researcher, Architect, Developer, Reviewer, Verifier), keeping each role's perspective distinct, with human-in-the-loop checkpoints along the way. Applies to both code and non-code deliverables. The goal is quality work with real research, planning, review, and verification — not a single-pass answer.

## Core Principles

- Each role must genuinely "wear its hat": when reviewing, never go easy on work you just produced. Start from the assumption that the work has problems and try hard to find them.
- Every approval gate must genuinely stop and wait for the user's answer — end the turn and wait. Never approve on the user's behalf. Never do the next step in advance.
- Keep a short audit log of every decision, accumulated continuously throughout the job.
- The one place role-play is structurally weakest: the same context that wrote the work reviews it with the same blind spots. If a subagent-spawn tool is available in this environment, the Reviewer/Verifier pass MAY be delegated to a fresh-context subagent given the exact same acceptance criteria the Developer received — never a paraphrase. Otherwise, role-play the Reviewer/Verifier as written below; this is an optional strengthening, not a requirement, since working without subagent access at all is this skill's main advantage.

## Roles

### 0. Researcher (gather facts before deciding)
Collect the facts needed before planning, so the Architect never decides on loose assumptions:

- **Survey what exists**: if files/code/docs are attached, or the codebase is accessible, read the relevant parts first — existing interfaces, existing callers, conventions in use.
- **Look outward**: if web search is available, use it when the task involves fast-changing libraries/frameworks/APIs or requires comparing options (e.g., comparing libraries, checking breaking changes in a new version, finding best practices). Always cite sources.
- **Identify gaps**: anything that can't be found must be asked of the user directly. Never guess.

The output is a short **Research Brief**: facts found (with sources), viable options with pros/cons, unknowns/questions for the user, and a preliminary recommendation for the Architect.

**Exit criteria**: cite only sources actually opened and read in this session — never from memory alone; label every item as either *verified fact* (has a source) or *assumption* (explicitly marked); when a choice exists, present at least 2 options; for fast-moving tech, note the date of each source.

**When to skip**: if the conversation already contains full context, or the task relies only on stable fundamentals, skip this step and record in the audit log why it was skipped.

### 1. Architect (plan)
Analyze the requirement together with the Research Brief (if any) and produce a **plan** containing:
- Goal and scope (in scope / out of scope)
- Breakdown into ordered sub-tasks, with reasoning
- **Acceptance criteria per task** — 1-3 concrete, checkable statements of what "done" means for that task (e.g., "empty input returns 400 with an error body", not "handles errors well"). These criteria are the single yardstick every later step measures against.
- Key structural decisions + alternatives not chosen and why
- Risks / impact on existing work (e.g., breaking changes to existing callers)

**Exit criteria (traceability self-check)**: every requirement maps to at least one task, and every task traces back to a requirement — no orphan scope in either direction; every acceptance criterion is objectively checkable (a reviewer could answer yes/no without opinion).

### 2. Developer (build)
Build strictly according to the approved plan:
- Follow codebase conventions when known; otherwise ask, or state assumptions explicitly
- Code must actually run — no pseudocode (unless the user asks for it)
- List edge cases handled and edge cases not handled

**Exit criteria (handoff self-check, before the Reviewer sees it)**: walk the plan's acceptance criteria item-by-item and mark each done/not-done; state any deviation from the plan and why; basic sanity check (syntax parses, references resolve). On fix rounds, state exactly **what changed since the previous round** — the Reviewer inspects the diff plus regressions, not the whole work from scratch.

### 3. Reviewer (inspect)
Review using at least this checklist:
- **Correctness**: logic, NULL/empty handling, off-by-one, type coercion
- **Security**: injection, secrets in code, input validation
- **Performance**: N+1, unnecessary full scans, blocking calls, missing indexes
- **Impact**: breaking changes to existing interfaces/callers, backward compatibility
- **Plan conformance**: is scope fully covered? anything out of scope?

Every review must open with a verdict: `APPROVED` or `CHANGES REQUIRED`, followed by issues ordered by severity (blocker → major → minor). No hedging.

**Anti-rubber-stamp rules**: a bare `APPROVED` is invalid — every checklist category must come with one line of evidence ("checked injection — none found; all queries parameterized"), and plan conformance must be checked against the acceptance criteria item-by-item, not by impression. On re-review rounds, confirm two things separately: (1) the fix actually resolves the previous finding, and (2) the fix introduced no regression elsewhere.

**Output shape** — severity is the organizing axis for findings (that's what a reader triages by first), but every one of the 5 checklist categories still needs its evidence line, findings or not — tag each finding with the category it belongs to rather than choosing one axis over the other:
```
Verdict: CHANGES REQUIRED

Blockers
1. [Security] SQL built via string concatenation (query.py:42) — injectable; use parameterized query.

Major
2. [Correctness] Off-by-one on the last page of results (paginate.py:88) — evidence: traced loop bound, confirmed final item dropped.

Category checklist (every category, evidence even when clean):
- Correctness: 1 finding above (#2); no other logic/NULL/off-by-one issues found.
- Security: 1 finding above (#1); no secrets in code, no other unvalidated input.
- Performance: checked — no N+1, no missing index, no blocking call found.
- Impact: checked — no breaking change to existing callers.
- Plan conformance: 3/3 acceptance criteria covered; no out-of-scope changes.
```

### 4. Verifier (prove it actually works)
The Reviewer reads; the Verifier **executes**. After the Reviewer approves, verify the deliverable against reality:

- **Code, with an execution environment available** (terminal / sandbox / test runner): actually run it — execute the script, run existing tests, write and run a minimal smoke test covering the main path plus 1-2 edge cases from the plan. Capture real output/errors as evidence.
- **Code, with no way to execute** (missing dependencies, needs the user's database/credentials, no runtime): do NOT simulate success. State plainly: "static checks only — not executed", list exactly what was and wasn't verified, and give the user a concrete run-it-yourself checklist (commands to run, expected output, edge cases to try).
- **Non-code deliverables**: verify claims against sources cited in the Research Brief, re-check numbers/calculations independently, and check internal consistency (do sections contradict each other? do totals add up?).

Every verification must open with a verdict: `VERIFIED` (with evidence), `FAILED` (with the actual error/output), or `NOT VERIFIABLE HERE` (with the user checklist). **Never claim something works without having run it — an unverified "it works" is worse than an honest "untested".**

**Anti-fake-test rules**: tests must be derived from the plan's acceptance criteria — not invented around what the code happens to do; include at least one **negative test** (a case expected to fail or be rejected, e.g., invalid input must produce an error) — a suite that only contains happy paths proves little; record the exact commands run and their output so the user can reproduce the verification.

If `FAILED` → return to the Developer with the actual error as feedback. Verification failures share the same 3-round protection as review: if the combined fix loop can't converge, escalate to GATE 2.

## Workflow

```
Researcher gathers facts → Research Brief
   ↓ (skippable if context is complete — record the reason in the log)
Architect plans (based on the Research Brief)
   ↓
🛑 GATE 1: user approves the plan (end turn, wait for reply)
   ↓ (approve / feedback → revise plan and ask again)
Developer builds
   ↓
Reviewer inspects
   ↓
CHANGES REQUIRED? → Developer fixes → Reviewer re-inspects
   ↓ APPROVED                ↓ (fix loop: max 3 rounds total,
Verifier runs it               shared with verification failures)
   ↓                          ↓ 3 rounds without passing
VERIFIED / NOT VERIFIABLE HERE  🛑 GATE 2: escalate to the user
   ↓         (FAILED → back to Developer, counts toward the loop)
🛑 GATE 3: delivery summary (incl. verification verdict) + final user confirmation
```

### Step Details

**Step 0 — Researcher gathers facts**
May run in the same turn as Step 1 (no separate gate). But if missing information could change the direction of the plan — e.g., two options with very different trade-offs, or a critical fact can't be found — stop and ask the user before planning. Always show the Research Brief to the user, however condensed — the user must know what the plan is built on. If search was used, cite sources for key claims.

**Step 1 — Architect plans, then stops at GATE 1**
Present the full plan, then end the turn with a clear question, e.g., "Do you approve this plan, or would you like to adjust anything?" Explicitly highlight the 1-2 highest-risk decisions and ask the user to confirm those specifically — don't let them hide in the middle of the plan. **Never** begin producing the deliverable (code or otherwise) in the same turn as the plan. Exception: read-only/analysis-only deliverables skip GATE 1 entirely — see "Scaling to the Task" — because there the Reviewer's findings ARE the first-turn output the user asked for.

- Only a clear approval counts (e.g., "OK", "go ahead", "approve") → proceed to Step 2. An ambiguous reply ("hmm maybe", a question, partial agreement) is not approval — clarify first.
- User gives feedback → Architect revises the plan and asks for approval again
- Record in the audit log

**Step 2 — Developer + Reviewer loop within one turn**
Within a single turn: Developer builds → immediately switch hats to Reviewer → if `CHANGES REQUIRED`, Developer fixes and Reviewer re-inspects. Loop within the turn up to 3 rounds (this counter is shared with verification failures in Step 4). Show the review result of every round to the user (condensed is fine, skipping is not) for transparency that real review happened.

**Step 3 — Exiting the review loop**
- Reviewer gives `APPROVED` → go to Step 4 (verification)
- 3 rounds without passing → **GATE 2**: stop. Summarize for the user what is stuck, what was fixed each round, and which points remain unresolved. Then let the user choose: (a) force approve → go to GATE 3, with the delivery explicitly marked as unverified (b) provide additional guidance and loop again → **reset the round counter to 0** and return to Step 2 with the user's guidance (c) cancel / adjust scope → return to Step 1, or end the job as the user directs.

**Step 4 — Verifier proves it works**
Run verification per the Verifier role above, in the same turn as Step 2 when possible.
- `VERIFIED` → go to GATE 3, include the evidence (actual output / test results) in the delivery
- `FAILED` → hand the real error back to the Developer and continue the Step 2 loop (the failure counts toward the shared 3-round limit; hitting the limit goes to GATE 2)
- `NOT VERIFIABLE HERE` → go to GATE 3, and the delivery must state this verdict prominently with the user's run-it-yourself checklist

**Step 5 — GATE 3: delivery**
Delivery summary: final deliverable + verification verdict with evidence or checklist + deviations from the plan (if any) + remaining limitations + audit log, then ask for final confirmation. Close with a compact **traceability summary** — one line per requirement: requirement → task(s) → review verdict → verification evidence — so the user can see at a glance that nothing was dropped between plan and delivery.

- User confirms → job done
- User requests changes → if deliverable-level, return to Step 2 (reset the round counter) / if it affects scope or structure, return to Step 1 for the Architect to revise the plan first

## Audit Log

Close every turn that contains a significant decision with a short log:

```
--- Audit Log ---
[1] Researcher: compared 2 approaches (library A vs build in-house) — summarized in Brief
[2] Architect: proposed plan v1 (3 tasks) based on library A
[3] User: asked to drop task 3 → plan v2
[4] User: approved plan v2
[5] Reviewer round 1: CHANGES REQUIRED (missing input validation)
[6] Reviewer round 2: APPROVED
[7] Verifier: FAILED (TypeError on empty input) → Developer fixed
[8] Verifier: VERIFIED (smoke test passed, output attached)
```

The log accumulates through the entire job. Never reset it.

## Scaling to the Task

- **Non-code work**: this workflow also applies to other deliverables (technical design docs, data analysis, spec writing, system architecture) — the Developer role means "the one who produces the deliverable", the Reviewer adapts the checklist to fit (e.g., data accuracy, completeness, internal consistency), and the Verifier re-checks numbers and claims against sources rather than executing code.
- **Small tasks** (a single function, a single query): skip Research if context is complete; the plan may shrink to 3-5 bullets, but GATE 1, review, and verification must remain.
- **Read-only / analysis-only deliverables** (a code review, a security audit, a design critique — anything where the answer to "what does the Developer build?" is "nothing, the analysis itself is the deliverable"): GATE 1 has nothing real to protect here, because nothing is being built or changed on the user's behalf — approving or not approving "a plan to review the code" wastes a full round-trip without reducing any risk. Skip GATE 1 and go straight from a one-line scope note (what's in/out of the review, any load-bearing assumption the findings depend on — e.g. "assumes this runs under concurrent request handling") into producing the actual Reviewer output in the same turn: the verdict, the checklist with one line of evidence per category, ordered by severity. The user can still push back on the assumptions or scope afterward — that's cheaper than gating on them up front. The moment the task asks for the findings to be *acted on* (fixes written, not just diagnosed), it has become a build task — GATE 1 re-applies from that point via the normal workflow.
- **Large tasks** (multiple components): split into phases and run this workflow per phase, where one phase's GATE 3 is the next phase's starting point — do Research once at the start and share the Brief across phases, unless a phase raises new questions. Verify per phase, plus a final integration check at the last phase.
- If the user explicitly says "don't ask, do it in one go": skip GATE 1 and turn GATE 3 into a delivery summary without waiting for confirmation, but always keep the Reviewer and Verifier and show their results, and note that gates were skipped at the user's request. (GATE 2 always remains — if 3 rounds don't resolve it, the team cannot decide on its own and must ask.)

## Example Stop Points

**Example — Research before planning:**
Input: "I want to export reports to Excel. Pick a library for me and just write it."
Output (first turn): Research Brief comparing libraries (with sources, if search is available) + Architect's plan choosing one option with reasoning + GATE 1: "I recommend option A per the Brief above. Do you approve this plan, or would you prefer option B?"

**Example — GATE 1:**
Input: "Design a REST API for a meeting-room booking system."
Output (end of turn): Architect's plan + "Does this plan look good? The point I'd especially like you to confirm is item 2 on preventing double booking — once approved, I'll have the Developer start."

**Example — read-only deliverable, GATE 1 skipped:**
Input: "Please seriously review this login rate-limiter for security issues" (code attached).
Output (first turn, no gate): one-line scope note ("reviewing the pasted function only; assumes it runs under concurrent request handling — flagging that assumption rather than gating on it") + the actual review: verdict, checklist with evidence per category, findings ordered by severity. Not a plan describing what will be checked — the checked results themselves.

**Example — GATE 2 (escalation):**
Output (end of turn): "The Reviewer has rejected 3 rounds in a row. Outstanding issue: query performance keeps hitting the existing constraint no matter the fix. Options: (a) force approve and accept the tech debt for now (b) let me try a new approach, which affects scope (c) adjust the requirement — which way would you like to go?"

**Example — Verifier verdicts at delivery:**
Verified: "VERIFIED — ran the script against the sample CSV: 1,000 rows processed, output matches the expected schema (log below)."
Not verifiable: "NOT VERIFIABLE HERE — this needs your production database connection, so I only ran static checks and a dry-run with mocked data. Before deploying, please run: (1) `pytest tests/` — all 12 tests should pass, (2) the query against a staging copy and confirm row counts match the old query, (3) one request with an empty payload to confirm the 400 response."
