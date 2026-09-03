# EXP-278 — Canonical period-768 Floquet audit

Status: completed — passed

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

## Result

All twelve gates pass. On the identical phase-fixed orbit, DOP853/Radau give
stable moduli `0.0879289933/0.0879290911`, absolute spread `9.78e-8` against
the unchanged `0.002` ceiling. Both corrections retain exact `896/1024`
section identity and half-period closures above `6.13e-6`; matching residuals
are at most `2.46e-11`.

Together with EXP-277's passed whole-orbit sign identities, this resolves the
four-representation failure as phase-conditioned product evaluation and
qualifies one unified stable primitive period-768 branch. EXP-279 freezes its
exact continuation toward a separately gated seventh-flip scan.

Raw receipt: `artifacts/EXP-278/receipt.json`, 132,805 bytes, SHA-256
`6f7ca773bcc0d8346b9a7293fd6143a39468d58681b7f576efbba1a65a15c114`.
Compact receipt:
[`receipts/EXP-278.json`](receipts/EXP-278.json).
