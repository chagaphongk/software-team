# Unsettled requirements before PLAN

Read this before drafting anything when a new feature's requirements themselves are
unsettled. "Add a thing" without a clear shape isn't yet a task the office can plan
against — PLAN's acceptance criteria need a settled destination to test against.

**Brand-new, large work first routes to a dedicated brainstorming skill when one is
installed**: a greenfield feature or product whose requirement space is itself wide
deserves a full intent/design exploration, and that skill's output becomes this file's
settled input. **Routing out is not handing off the task**: when the brainstorm
concludes, come back to `SKILL.md` and carry its settled requirements straight into
`## PLAN output shape (T1/T2)` (`references/t1.md`) and the normal office loop — the office still builds, reviews, and
verifies what the brainstorm decided. The steps below are the self-contained path — use
them when no such skill is installed, or when the work is small enough that a few direct
questions settle it. Before drafting anything:

1. **State your current understanding** in one or two lines — what you think is being
   asked — so the human can correct a wrong assumption cheaply, before it costs a full
   BUILD/REVIEW/VERIFY round trip instead of one turn. If the current directory doesn't
   look like the codebase the request is actually about (no matching app/service found,
   or the request names a system this repo isn't), say that plainly as the first thing —
   don't draft product-shaped forks against the wrong target.
2. **Surface every genuinely open question as an explicit fork**, per
   the fork shape in `references/t1.md`: concrete options (2–4), one marked recommended,
   the cost of each. Never a bare "what do you want?" — that pushes the thinking the
   office is supposed to do back onto the human.
3. **Stop and wait.** Don't draft PLAN speculatively "in case" the human picks the option
   you'd have guessed — a guessed destination that turns out wrong is the exact round
   trip step 1 exists to avoid.

Once every fork here resolves, the request has a destination — proceed to
`## PLAN output shape (T1/T2)` in `references/t1.md` (or `references/plan-sizing.md` if resolving these
questions reveals the work is actually oversized).
