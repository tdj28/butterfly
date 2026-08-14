# EXP-310 — Independent period-3072 stability exchange

Status: completed — failed only the parent neutral-margin classification

EXP-309 nominates two primitive period-3072 candidates. EXP-310 selects the
negative sign solely by its larger direct half-period nonclosure and
independently corrects the period-1536 parent and period-3072 child at their
common coordinate under DOP853 and Radau.

Matching, phase, cross-solver node identity, multiplier spread, child
nonclosure, classification margin, and exact `3584/4096` section identities
are mandatory. Either consistent parent-unstable/child-stable or
parent-stable/child-unstable exchange passes; mixed or unresolved fails.

A pass qualifies the sampled eighth-birth direction only. It does not
establish sign equivalence, basin measure, a global stable child branch, or a
ninth event.

Manifest:
[`../../experiments/manifests/EXP-310-jones-period3072-qualified-criticality.json`](../../experiments/manifests/EXP-310-jones-period3072-qualified-criticality.json).

## Result

After 6,276 seconds, DOP853 and Radau independently classify the primitive
period-3072 child as strongly unstable, with moduli
`18.98176427/18.98180420`. Child multiplier spread is only `2.10e-6`;
matching remains below `1.50e-10`; direct half-period nonclosure is
`2.25e-6/2.65e-6`; and both exact `3584/4096` identities pass.

The parent straddles one but remains inside the frozen `1e-4` neutral margin:
DOP853 gives `1.00003875` and Radau `0.99995754`. Parent spread is
`8.12e-5`, within the independent-solver agreement gate. The combined result
is therefore `other-or-unresolved`, and EXP-310 fails exactly the intended
classification gate.

This is strong evidence consistent with a subcritical eighth birth: a
primitive unstable period-3072 daughter exists at the sampled coordinate. It
is not promoted until a farther same-side coordinate independently resolves
the parent as stable without weakening the margin.

Raw receipt: `artifacts/EXP-310/receipt.json`, 765,920 bytes, SHA-256
`503612aa82a1feb0f717063d0f021229cc7e5f6fef93c7a058b0823cd4b53fad`.
Compact receipt:
[`receipts/EXP-310.json`](receipts/EXP-310.json).
