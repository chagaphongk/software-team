# Model routing

Never spawn on a fixed default model. Pick per spawn from **difficulty**; the tier sets
a **floor**; the stronger of the two wins. Pass the model explicitly — the `Model:`
line and the Agent call's `model` parameter — and note the reason (mechanical / simple
/ complex, plus which signal) in the spawn's `Context:` line.

| Difficulty | Model | Signal |
|---|---|---|
| Mechanical | haiku | rename, typo, reformat, an identical substitution repeated across files — no logic decision anywhere |
| Simple | sonnet | small change following an existing codebase pattern; crisp, mechanically checkable criteria; no interacting logic across files |
| Complex/hard | opus | any signal below |

Complex/hard signals:

- Logic genuinely interacting across more than ~3 files/modules (not the same
  mechanical edit ×3 — that's still simple).
- Concurrency, algorithmic subtlety, a race/ordering condition.
- The criteria leave a real judgment call to the spawn — an uncrispable acceptance
  criterion is itself the signal.
- Round ≥ 2 after a REVIEW `CHANGES REQUIRED` or VERIFY `FAIL` **against the build
  itself** — escalate the retry; the same model repeats the same blind spot. (A
  `BLOCKED`, or a round lost to a wrong prompt/criteria, is not this signal — fix the
  prompt and re-spawn at the same model; it still counts toward the 3-round cap.)
- Architecture/planning with real trade-offs, or a cross-cutting/hard-to-reverse
  design.

**Floors:** T0 haiku · T0.5 sonnet · T1 sonnet · T2 opus (one exception — the
fully-specified builder in `references/t2.md`).

Escalation is one-way within a task, on both axes: a tier moved up stays up; a model
moved up stays up. Never downgrade mid-task to save cost.

**Other roles:** `security-reviewer` matches the builder's model (under the T2
fully-specified exception it stays at opus); `documenter` is always haiku; `deployer`
is always haiku (precise execution of an approved command — nothing left to decide);
`designer` DESIGN mode follows the difficulty scale, REVIEW mode matches the paired
review pass.

**A T1 opus build gets an opus reviewer, not a Fable pass** — the mandatory Fable
review exists only as T2's gated review (`references/t2.md`). Independence plus model
quality is the property that matters; a second top-tier review persona on a T1 diff
buys nothing.

## Fable planning consult — optional, gated

For a genuine architecture/design trade-off, cross-cutting or hard-to-reverse work, or
a BUILD/REVIEW/VERIFY loop stuck after 2 failed rounds. Skip it for routine
implementation or an obvious fix — state the one-line reason either way — and skip the
gate entirely (consult immediately) when the human explicitly asked for Fable.

Spawn once via the Agent tool (`model: "fable"`, `subagent_type: general-purpose`,
read-only by instruction) with a self-contained brief: the goal, the human's
constraints quoted verbatim, what's already known, the specific question, and "state
your assumptions instead of asking questions back" (a subagent starts cold and cannot
interrupt you). Treat the answer as advice, not authority: the human's explicit
instructions win on conflict, and any open question the plan flags goes to the human
before BUILD. Budget about two planning calls per task before checking with the human
whether to keep spending — this budget is separate from T2's mandatory gated review.
