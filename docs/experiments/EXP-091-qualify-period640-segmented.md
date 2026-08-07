# EXP-091 — Independently qualify period 640

Status: preregistered after EXP-090; pending clean execution

Take both EXP-090 switch signs at frozen step `0.002` and independently
correct their 64-segment states at common `b=0.17971235`. Compute signed
block-Floquet spectra without composing a duration-4184 monodromy. Reconstruct
dense output separately inside every segment and align the two whole orbits
using the already validated five-stage multiresolution phase search.

Pass only if both matching residuals are `<=1e-8`, half-node RMS values are
`>=1e-5`, dominant nontrivial moduli are `<=0.999` and agree within `1e-4`,
periods agree within `1e-8`, segment endpoints within `1e-8`, and continuous
phase-aligned whole-orbit RMS is `<=1e-5`. Passing establishes one
geometrically identified stable period-640 child and closes the seventh local
supercritical rung numerically.
