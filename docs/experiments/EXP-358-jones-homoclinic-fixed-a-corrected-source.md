# EXP-358 — Renewed exact fixed-a intersection solve

Status: frozen; not yet run

EXP-357's corrected curve nodes are only `1.74900e-5` from exact
`a=0.1798`, roughly 51 times closer than the source of the first direct solve.
EXP-358 fixes `(a,b)=(0.1798,0.2)`, solves `c`, and starts from those exact
nodes at the prospectively updated `c=10.317189121880126`.

The 128 arcs, Radau tolerances, manifold settings, node guardrail, 40-evaluation
budget, and `1e-8` root gate remain unchanged. Passing directly qualifies the
historical fixed-`a` intersection, subject to the stated numerical—not
computer-assisted—scope.

Manifest:
[`../../experiments/manifests/EXP-358-jones-homoclinic-fixed-a-corrected-source.json`](../../experiments/manifests/EXP-358-jones-homoclinic-fixed-a-corrected-source.json).
