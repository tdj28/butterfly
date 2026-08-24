# EXP-358 — Renewed exact fixed-a intersection solve

Status: failed; repeated fixed-a residual floor

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

The renewed solve is preserved as failed at maximum defect
`0.000210831193`, with `c=10.317127208993021`. Despite starting from nodes 51
times closer in `a` than EXP-351, it returns to essentially the same
stable-end residual floor and `c` value. All boundary and source-agreement
checks pass; node margin is `0.99805`.

This repeat blocks a numerical intersection claim. It does not show that the
qualified revised-coordinate homoclinic roots are false. The remaining
alternatives are a fold/termination before the historical path or singular
conditioning of the fixed-`a` endpoint formulation. Pseudo-arclength or
collocation continuation with an explicit gauge must distinguish them.

Raw receipt: `artifacts/EXP-358/receipt.json`, 31,784 bytes, SHA-256
`73d555bcc205f4df2d602de6bacd4fe5498167be95cbe76c84b6cdeb568b303e`.
