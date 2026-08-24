# EXP-353 — Node-bounded fixed-a warm restart

Status: frozen; not yet run

EXP-352 aborts when the trust-region optimizer proposes an unbounded internal
shooting node from which Radau cannot take a representable step. EXP-353 binds
the same exact EXP-351 failure and adds a prospective `+/-0.5` component box
around each of its 127 internal nodes. The receipt reports the maximum
normalized displacement, and passing requires at least `0.01` normalized
margin from every node boundary.

No physical parameter, manifold construction, segment count, Radau tolerance,
global-variable box, evaluation budget, or `1e-8` scientific gate changes.
The node box is a numerical guardrail against invalid trial states, not a
relaxation of the root criterion.

Manifest:
[`../../experiments/manifests/EXP-353-jones-homoclinic-fixed-a-node-bounded-restart.json`](../../experiments/manifests/EXP-353-jones-homoclinic-fixed-a-node-bounded-restart.json).
