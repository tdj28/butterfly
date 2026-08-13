# EXP-240 — Independent period-24 endpoint qualification

Status: completed — passed reproducibility, criticality unresolved

EXP-239 supplies a separated primitive period-24 endpoint whose preliminary
multiplier is strongly unstable. EXP-240 corrects both that child and its
period-12 parent at the same fixed `(a,b,c)` using independent 16/32-segment
DOP853 and Radau systems. It compares nodes and periods across solvers, uses
block-Floquet products for stability classification, and independently checks
child closure, neutral direction, half-period nonclosure, and `28/32` section
identity.

The acceptance rule does not preselect stable or unstable. It requires both
solvers to agree outside a frozen neutral margin. Stable parent plus unstable
child on the lower-`a` child side is classified as subcritical; unstable parent
plus stable child is supercritical; other pairings remain unresolved.

Manifest:
[`../../experiments/manifests/EXP-240-jones-period24-segmented-qualification.json`](../../experiments/manifests/EXP-240-jones-period24-segmented-qualification.json).

## Result

The numerical audit passes. DOP853 and Radau independently recover the same
period-24 endpoint (zero sampled-node RMS) and multiplier
`-703.4363544`, with relative modulus spread `4.16e-11`. Both retain `28/32`
identity and half-period closure `0.11948`.

Both solvers also correct an unstable period-12 solution at the terminal
coordinate, with multiplier near `-29.3841`. The receipt therefore labels the
pairing `other-or-unresolved`, not subcritical: direct correction from the
event took 26 evaluations and does not prove continuous parent identity over
the full `8.14e-6` jump. More importantly, criticality is a near-birth
property. EXP-241 is frozen at EXP-238's near-event child point, where the
child was preliminarily stable.

Raw receipt: `artifacts/EXP-240/receipt.json`, 17,381 bytes, SHA-256
`bc8f89f829cbf708027764ae581fd9e554904df579054730977a5bfdc2894c6f`.
Compact receipt:
[`receipts/EXP-240.json`](receipts/EXP-240.json).
