# EXP-152 — Prospective transverse UPO manifold-seed validation

Status: passed all seven transverse-slice manifold-seed instances

## Question

Can every distinct primitive UPO family recovered at the two endpoints of the
qualified `c=19.9` bracket supply a section-tangent unstable direction whose
finite-perturbation amplification reproduces its Floquet multiplier?

## Frozen adapter and gates

The new adapter joins the eventual hashed EXP-150 discovery receipt to the
eventual hashed EXP-151 continuous-phase identity receipt. For every family it
selects only the representative named by the identity audit and passes its
fundamental state, period, and lag into the already qualified EXP-142 seed
validator. Unit tests reject missing cases, mismatched parameters, invalid
indices, and unaccepted representatives.

Every numerical gate is copied unchanged from EXP-142: both signs at
perturbation sizes `1e-9`, `3e-9`, and `1e-8`; at least two passing sizes per
sign; 1% relative multiplier error and transverse residual; `1e-6` base
lag-return closure; real unstable direction; instability margin `0.001`;
positive section speed `0.001`; and DOP853 tolerances `1e-11/1e-13` with
maximum step `0.025`. All distinct families at both required endpoints must
pass.

The remaining frozen fields are source-parameter tolerance `1e-14`, coordinate
scales `(1,30,0.0006)`, maximum multiplier/direction imaginary parts `1e-8`,
section tangent and scaled-normalization residuals `1e-12`, crossing search
fractions `0.05` transient and `0.75` observation, maximum flight time 50, and
required case IDs `c19p9-two-branch-saddle` and
`c19p9-three-branch-saddle`.

## Execution boundary

After EXP-150 and EXP-151, only their receipt paths/hashes and identifiers may
be inserted into the manifest. Family selection and scientific tolerances may
not change. Passing validates local unstable-manifold seeds on a second
transverse slice; it does not establish lobe inclusion, a manifold connection,
or a continuous topology surface.

## Result

All seven distinct primitive families pass. The two-branch endpoint contributes
lags 3, 10, and 13; the three-branch endpoint contributes lags 13, 14, and two
distinct lag-15 families. Every perturbation size and sign reproduces the
signed unstable Floquet amplification within the frozen 1% gates. Maximum
relative multiplier error is `0.003477`, maximum transverse residual ratio is
`0.001258`, and maximum base lag-return scaled closure is `2.652e-9`.

Tracked receipt: `docs/experiments/receipts/EXP-152.json`.
