# EXP-157 period-2 branch switch frozen

Date: 2026-08-07

EXP-157 freezes the local branch switch from the exact first period-1 flip in
EXP-156 to the prospective period-2 child at fixed `a=0.1798`, `b=0.2`.
The input hashes bind the run to the EXP-156 event and the EXP-155
Hopf-to-hub parent family.

The numerical roles are deliberately separated:

- adaptive DOP853 integrates the state, variational equations, and exact
  parameter sensitivity `f_c=(0,0,-z)`;
- a Newton-style least-squares corrector enforces periodic closure, phase, and
  pseudo-arclength equations after each predictor;
- the doubled parent at the flip supplies a two-dimensional shooting
  nullspace;
- the observed doubled-parent tangent is projected out, leaving the
  transverse candidate child tangent;
- closure and failure of half-period closure are frozen acceptance tests.

The exact `c` sensitivity and the complete shooting Jacobian match centered
finite differences in `tests/test_periodic_c.py`. The full local suite passes
147 tests before execution. The manifest is
`experiments/manifests/EXP-157-switch-period1-c-flip.json` and the runner is
`scripts/switch_period1_c_flip.py`.

Passing EXP-157 will establish a local switched branch, not yet independent
period-2 identity, stability exchange, or attraction. Those are reserved for
the hash-bound successor qualification.
