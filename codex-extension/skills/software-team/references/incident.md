# INCIDENT playbook

Something is down or broken in production right now. No new role — existing roles in a
fixed order:

1. **Triage** — the `researcher` role, read-only diagnosis: what broke, since when,
   blast radius, and which reversible mitigation is available. A diagnosis, not a fix.
2. **Mitigate** — human approval first (same bar as any deploy), then the `deployer`
   role runs a **reversible mitigation only**: rollback, restart, feature-disable.
   Never a new forward code/config fix — that becomes a normal T2 BUILD once the
   service has recovered. The diagnosis substitutes for the usual prior gates on the
   deployer's spawn.
3. **Confirm** — the `verifier` role confirms recovery with evidence.
4. **Postmortem** — the `builder` role writes a one-page postmortem after recovery
   is verified; its operational claims trace to the researcher's diagnosis and the
   deployer's/verifier's recorded evidence (there may be no code diff to cite).

The mitigate-then-verify order is the one exception to the Done gate's usual
verify-before-deploy order — the mitigation is what the recovery verification confirms.
