# Model routing

The spawn tool's `model` and `reasoning_effort` fields are available (confirmed by live
introspection — but the tool name and field set have already drifted once; introspect
your own tool set rather than trusting a dated string). No model string is hardcoded
here on purpose: resolve which string is currently the cheap/mid/top tier, and which
`reasoning_effort` value is currently low/medium/high-or-above, yourself before
spawning.

Never spawn on a fixed default. Pick `model` + `reasoning_effort` per spawn from
**difficulty**; the tier sets a **floor**; the stronger of the two wins. Pass both
explicitly on the spawn call and note the reason (mechanical / simple / complex, plus
which signal) in the spawn's `Context:` line.

| Difficulty | Model / effort | Signal |
|---|---|---|
| Mechanical | cheapest model, lowest effort | rename, typo, reformat, an identical substitution repeated across files — no logic decision anywhere |
| Simple | mid-tier model, medium effort | small change following an existing codebase pattern; crisp, mechanically checkable criteria; no interacting logic across files |
| Complex/hard | top-tier model, high-or-above effort | any signal below |

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

**Floors:** T0 cheapest · T0.5 mid · T1 mid · T2 top (one exception — the
fully-specified builder in `references/t2.md`).

Escalation is one-way within a task, on both axes: a tier moved up stays up; a model
moved up stays up. Never downgrade mid-task to save cost.

**Other roles:** `security-reviewer` matches the builder's model/effort (under the T2
fully-specified exception it stays at the top tier); `deployer` always runs at the
cheapest tier (precise execution of an approved command — nothing left to decide);
`designer` follows the difficulty scale.

**A T1 top-tier build gets a top-tier verifier, not a fresh-context second
review** — the mandatory second review exists only as T2's gated review
(`references/t2.md`). Independence plus model quality is the property that matters; a
second top-tier review pass on a T1 diff buys nothing.

## Planning consult — optional, gated

For a genuine architecture/design trade-off, cross-cutting or hard-to-reverse work, or
a BUILD/REVIEW/VERIFY loop stuck after 2 failed rounds. Skip it for routine
implementation or an obvious fix — state the one-line reason either way — and skip the
gate entirely (consult immediately) when the human explicitly asked for one.

Spawn once at the top model/effort with fresh context (read-only by instruction) with a
self-contained brief: the goal, the human's constraints quoted verbatim, what's already
known, the specific question, and "state your assumptions instead of asking questions
back" (a spawn starts cold and cannot interrupt you). Treat the answer as advice, not
authority: the human's explicit instructions win on conflict, and any open question the
plan flags goes to the human before BUILD. Budget about two planning calls per task
before checking with the human whether to keep spending — separate from T2's mandatory
gated review.
