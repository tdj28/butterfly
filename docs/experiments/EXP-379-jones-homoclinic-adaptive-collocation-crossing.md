# EXP-379 — Schema-complete adaptive-collocation crossing

Status: post-collocation replay-audit abort; no receipt

EXP-378 aborts before numerical work because the stable-manifold constructor
requires a root-level solver block. EXP-379 adds the same Radau policy already
frozen for independent replay and requires both blocks to be exactly equal.
All sources, initial mesh, equations, derivatives, tolerances, node ceiling,
status checks, and scientific acceptance gates are unchanged.

A pass requires converged adaptive collocation, boundary and independent
uniform-512 Radau replay defects below `1e-8`, interior margins, forward `c`,
and `a<0.1798`. It qualifies a bracket endpoint, not the exact historical
section, uniqueness, or computer-assisted existence.

Manifest:
[`../../experiments/manifests/EXP-379-jones-homoclinic-adaptive-collocation-crossing.json`](../../experiments/manifests/EXP-379-jones-homoclinic-adaptive-collocation-crossing.json).

## Administrative outcome

The collocation call returns, but the independent uniform Radau replay hits
step-size collapse and raises before receipt serialization. This may reflect a
failed or nonphysical collocation result, but EXP-379 preserves no parameters
or residuals and therefore supports no scientific classification. EXP-380
retains the identical solve and changes only the audit boundary: a failed
replay arc is serialized with its index and message and fails the replay gate
instead of destroying the collocation diagnostics.
