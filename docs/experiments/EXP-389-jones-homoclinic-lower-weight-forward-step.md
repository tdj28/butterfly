# EXP-389 — Lower-weight homoclinic forward step

Status: executed; failed prospectively

EXP-388 passes the prerequisite zero-step control under nuisance weight
`0.003`, reproducing the EXP-368 root while retaining a minimum Jacobian
singular value of `1.76697e-9`.  EXP-389 now executes the licensed forward
test.

The desired increment remains the smaller EXP-387 value `Delta c=2e-5`, and
the predictor must lie inside `c >= current c + 1e-7`.  The exact EXP-367/368
sources, 512 arcs, analytic sensitivities, CSR/LSMR solver, Radau/manifold
settings, source-centered bounds, and 40-evaluation budget remain unchanged.
The `1e-8` matching/arclength gates are joined by the prospectively established
`5e-10` minimum-Jacobian-singular-value gate.

A pass adds a twelfth qualified curve point above `a=0.1798` and licenses a
shorter-secanted section attempt.  It does not itself qualify the exact
historical fixed-`a` intersection, uniqueness, proof, or global topology.

## Result

EXP-389 does not pass.  It terminates normally after 19 evaluations at

```text
(a, c) = (0.1798178525799760, 10.317081588741923)
maximum block defect = 5.8182759803643756e-8
arclength residual = 1.4498028645670846e-11
minimum Jacobian singular value = 1.2457345669926514e-9
```

The conditioning gate passes, and the defect is slightly lower than
EXP-387's `6.13398e-8`.  The corrector nevertheless returns to exactly the
same prospective lower wall `c=current c+1e-7`; its normalized `c` margin is
`3.91e-14`.  The root and global-interiority gates fail, so this is not a
twelfth curve point.

Because both `0.01` and `0.003` planes hit the same wall at the same step,
insufficient nuisance down-weighting is no longer the primary diagnosis.  The
next test changes the predictor basin: it holds nodes, time, and angle at the
qualified current root while extrapolating only physical `(a,c)`, retaining
the passed `0.003` closing plane and every scientific gate.

Raw receipt: `artifacts/EXP-389/receipt.json`, 81,895 bytes,
SHA-256 `541047bf46259f523d5aa08ba4d5586200310cbfdc76feae9f226b069074ce8c`.
Compact receipt: [`receipts/EXP-389.json`](receipts/EXP-389.json).

Manifest:
[`../../experiments/manifests/EXP-389-jones-homoclinic-lower-weight-forward-step.json`](../../experiments/manifests/EXP-389-jones-homoclinic-lower-weight-forward-step.json).
