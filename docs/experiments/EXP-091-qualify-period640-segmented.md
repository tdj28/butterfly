# EXP-091 — Independently qualify period 640

Status: executed; passed

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

The clean run at `afbd1e0d3281935171b6a37089c8ce10650bb95a` passed. Both
64-segment signs correct at common `b=0.17971235` with matching residuals
`1.21e-12` and `1.35e-12`; their periods agree to machine precision. Their
dominant nontrivial moduli are `0.07076441` and `0.07076453`, differing by
only `1.22e-7`. Multiresolution alignment finds phase shift
`0.5000000023574` and whole-orbit RMS `1.39e-8`, with maximum segment endpoint
error `6.03e-11`. Full receipt SHA-256:
`3a26c981a4462051e2d5666b28538520141a94d6459f52ca16d3db9b81b35445`.

The 320→640 flip therefore produces one geometrically identified, strongly
stable period-640 child. The seventh local supercritical rung is numerically
closed.
