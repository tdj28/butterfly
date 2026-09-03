# EXP-001 saddle-focus evidence correction

Date: 2026-08-07

## What changed

The claim ledger had continued to label the proposed hub equilibrium
classification as analytically checkable but unimplemented. That status was
stale: the reference core already implements analytic equilibria and the
Jacobian, verifies the Jacobian by central differences, checks vector-field
residuals and equilibrium invariance under adaptive DOP853, and emits a
machine-readable verification receipt.

The current clean-code verification receipt is now summarized at
`docs/experiments/receipts/EXP-001.json`. Its raw SHA-256 is
`1bab55975b7c80e46c660b9408810b0a334027a09a55ef2b8b57b75ffe9d91f0`.

## Result

At the reported hub coordinate `(a,b,c)=(0.1798,0.2,10.3084)`, the small
equilibrium is

`(0.003489598512,-0.019408223091,0.019408223091)`

and its eigenvalues are

`0.0889667722 +/- 0.9959555077 i` and `-10.3030439458`.

This qualifies the local saddle-focus classification: the equilibrium has a
two-dimensional unstable spiral eigenspace and one strongly stable real
direction.

## Interpretation boundary

This is good evidence for the local equilibrium statement in Jones. It does
not demonstrate that an unstable manifold returns to the stable manifold, and
therefore does not establish a homoclinic orbit or uniqueness along the
reported transition segment. Those remain separate continuation and
boundary-value problems under CLM-003.

## Next gate

Continue the equilibrium and eigenspectrum over a declared neighborhood,
locate the Hopf curve, and independently pursue a stable/unstable manifold
intersection test. The ongoing blind midpoint saddle control and transverse
slice pipeline remain the immediate compute queue.
