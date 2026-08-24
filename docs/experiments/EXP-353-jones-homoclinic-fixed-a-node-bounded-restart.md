# EXP-353 — Node-bounded fixed-a warm restart

Status: failed; bounded warm restart reaches a residual floor

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

The run completes without an integration exception and every prospective
guardrail check passes, but the scientific root gate does not. The maximum
defect changes only from `0.000209830047` to `0.000209824665` in 40
evaluations. Maximum normalized node displacement is only `0.00178451`,
leaving `0.99821549` node-boundary margin, so the new box is not causing the
floor.

The fixed-`a` result remains unresolved. The next successor returns to the
qualified fixed-`c` curve, corrects its 128 nodes directly at the prospective
crossing `c`, and only then reimposes exact `a=0.1798`. This supplies a local
predictor-corrector state instead of asking the fixed-`a` solver to repair a
two-parameter node displacement at once.

Raw receipt: `artifacts/EXP-353/receipt.json`, 31,956 bytes, SHA-256
`2071945f1b4379999db059c90fcb326771ca2e52d7872c65853b9c760b73f6f7`.
