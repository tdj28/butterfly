# EXP-142 — UPO unstable-manifold seed validation

Status: preregistered; unexecuted

## Question

Can every member of the eleven-family persistent UPO census supply a
section-tangent unstable direction whose exact lag-return amplification agrees
with its Floquet multiplier at both topology endpoints?

## Frozen design

At `a=0.148` and `a=0.14825`, each source orbit is phase-shifted to an exact
positive Barrio crossing. Its largest-modulus real monodromy eigenvector is
projected along the flow into the section and normalized using scales
`(x,y,z)=(1,30,0.0006)`.

Both signs of perturbations `1e-9`, `3e-9`, and `1e-8` are advanced for the
family's exact fundamental lag. The signed tangent amplification must reproduce
the unstable Floquet multiplier to 1% relative error, with transverse residual
at most 1%. At least two sizes per sign must pass. Base lag-return closure must
be at most `1e-6` in scaled section coordinates, the section speed must be
positive by at least `1e-3`, and tangent/normalization residuals must be at most
`1e-12`. All integrations use DOP853 at `1e-11/1e-13` tolerances.

All 22 family-endpoint instances must pass. A failed family is excluded from
manifold tracing until its direction or numerical representation is repaired;
no thresholds are retuned within this experiment.

Immutable manifest:
`experiments/manifests/EXP-142-upo-manifold-seed-validation.json`.

## Reproduction command

```bash
PYTHONPATH=python:scripts .venv/bin/python scripts/validate_upo_manifold_seeds.py \
  --manifest experiments/manifests/EXP-142-upo-manifold-seed-validation.json \
  --output artifacts/EXP-142/receipt.json
```

## Interpretation boundary

A pass validates local unstable-manifold seeds only. It neither demonstrates a
homoclinic/heteroclinic connection nor explains the return-map branch opening.
