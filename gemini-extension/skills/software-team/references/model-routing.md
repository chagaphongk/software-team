# Model routing

Gemini's model catalog churns fast — no model string is hardcoded here on purpose.
Resolve which exact model string is currently the Flash-Lite/Flash/Pro/Deep-Think class
yourself before spawning.

Never spawn on a fixed default model. Pick per spawn from **difficulty**; the tier sets
a **floor**; the stronger of the two wins. Pass the model explicitly on the `Model:`
line (applied via the per-delegation override if your Gemini CLI's spawn mechanism
supports one; otherwise the line is a flag for the human/log — the shipped `agents/*.md`
files carry no `model:` frontmatter field) and note the reason (mechanical / simple /
complex, plus which signal) in the spawn's `Context:` line.

| Difficulty | Model | Signal |
|---|---|---|
| Mechanical | cheapest/fastest tier (Flash-Lite class) | rename, typo, reformat, an identical substitution repeated across files — no logic decision anywhere |
| Simple | balanced tier (Flash class) | small change following an existing codebase pattern; crisp, mechanically checkable criteria; no interacting logic across files |
| Complex/hard | most capable tier (Pro class) | any signal below |

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

**Floors:** T0 cheapest/fastest · T0.5 balanced · T1 balanced · T2 most capable (one
exception — the fully-specified builder in `references/t2.md`).

Escalation is one-way within a task, on both axes: a tier moved up stays up; a model
moved up stays up. Never downgrade mid-task to save cost.

**Other roles:** `security-reviewer` matches the builder's model (under the T2
fully-specified exception it stays at the most capable tier); `documenter` is always
the cheapest tier; `deployer` is always the cheapest tier (precise execution of an
approved command — nothing left to decide); `designer` DESIGN mode follows the
difficulty scale, REVIEW mode matches the paired review pass.

**A T1 most-capable-tier build gets a most-capable-tier reviewer, not a Deep Think
pass** — the mandatory Deep Think review exists only as T2's gated review
(`references/t2.md`). Independence plus model quality is the property that matters; a
second top-tier review persona on a T1 diff buys nothing.

## Deep Think planning consult — optional, gated

For a genuine architecture/design trade-off, cross-cutting or hard-to-reverse work, or
a BUILD/REVIEW/VERIFY loop stuck after 2 failed rounds. Skip it for routine
implementation or an obvious fix — state the one-line reason either way — and skip the
gate entirely (consult immediately) when the human explicitly asked for it.

Spawn once with fresh context at the Deep-Think/extended-reasoning class (read-only by
instruction) with a self-contained brief: the goal, the human's constraints quoted
verbatim, what's already known, the specific question, and "state your assumptions
instead of asking questions back" (a subagent starts cold and cannot interrupt you).
Treat the answer as advice, not authority: the human's explicit instructions win on
conflict, and any open question the plan flags goes to the human before BUILD. Budget
about two planning calls per task before checking with the human whether to keep
spending — this budget is separate from T2's mandatory gated review.
