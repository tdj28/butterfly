# EXP-379 — Schema-complete adaptive-collocation crossing

Status: frozen; not yet run

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
