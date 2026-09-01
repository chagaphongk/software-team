# Synthesizing decisions into a spec

Read this for multi-session work before drafting the next PLAN: a `references/wayfinder.md`
map that just closed, or a `references/plan-sizing.md` Phase Map spanning more than the
current session. A fresh session — or a fresh set of `references/to-tickets.md` tickets —
should pick the work up from one document instead of re-deriving decisions from the
conversation that produced them.

**Synthesize, never generate.** Everything in the spec is already decided. If a question is
still open it is a fork (put it to the human) or fog (back to the map) — it is not spec
content, and writing it in as a plausible-sounding sentence launders an undecided question
into a settled one.

## Seam-first

Before writing any spec prose, sketch the **seams** — the public boundaries the eventual
implementation will be tested against: an API endpoint, a module interface, a CLI command,
a public function signature. Put the sketch to the human and get explicit confirmation on
the **fewest workable entry points** before drafting the rest; a seam list nobody agreed to
is a design decision smuggled in as documentation.

These seams carry forward verbatim into the **Seams** item of `## PLAN output shape (T1/T2)`
(`references/t1.md`) for every plan that comes out of this spec. This is where they are
first proposed for multi-session work; a single-session plan drafts its own.

## Spec shape

Write to `.claude/state/tracker/<slug>-spec.md`:

```
---
title: <one line>
status: ready-for-agent
created: YYYY-MM-DD
---

Destination: <one line — what success looks like>

Decisions:
- <settled architectural/implementation choice> — <why> (.claude/state/tracker/<id>-<slug>.md)

Seams:
- <public boundary the implementation is tested against>

Out of scope:
- <what this spec does not cover>
```

`status: ready-for-agent` marks the spec as picked-up-able — the local equivalent of a
tracker issue with a ready label, with no external tracker to depend on.

The spec file, `MAP.md`, and ticket files are all under `.claude/state/tracker/`, inside the
carve-out `SKILL.md` already grants — the orchestrator writes them directly, same as
`docs/decisions.md` (`references/tracker.md`). `CONTEXT.md` and `docs/adr/` records are not:
they are real project documentation and go through a builder spawn like any other project
file (`references/unsettled-requirements.md`).

## After the spec

A spec small enough for one BUILD goes straight into `## PLAN output shape (T1/T2)`. A spec
too large for one BUILD goes to `references/to-tickets.md` to be sliced first.
