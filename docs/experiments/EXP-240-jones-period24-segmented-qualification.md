# EXP-240 — Independent period-24 endpoint qualification

Status: frozen — not yet executed

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
