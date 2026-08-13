# EXP-278 — Canonical period-768 Floquet audit

Status: frozen — not yet executed

EXP-277 strengthens whole-orbit equivalence of the two switch signs but again
fails only the four-representation multiplier-spread gate. The negative sign
was independently selected before either sign audit by EXP-275's passed
stability qualification. EXP-278 uses that sign's DOP853 nodes as one
canonical phase seed and corrects the identical seed under tight-step DOP853
and Radau with one phase reference.

The audit binds EXP-277's successful sign identities and applies the unchanged
`0.002` multiplier-spread ceiling to the two canonical solver representations.
Matching, phase, whole-node solver identity, period, stability, half-period
primitivity, and exact `896/1024` section identity also remain mandatory.

A pass resolves phase-representation conditioning and permits continuation of
the unified period-768 branch. It does not establish a seventh event.

Manifest:
[`../../experiments/manifests/EXP-278-jones-period768-canonical-floquet-audit.json`](../../experiments/manifests/EXP-278-jones-period768-canonical-floquet-audit.json).
