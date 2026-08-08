# EXP-137 — Phase-robust lag-12 flow continuation and identity

Status: executed; substantive gates passed, strict Float64 equality gate failed

## Question

Do both primitive lag-12 flow orbits continue across the complete local
two/three-branch bracket, does a phase-shifted full-period window retain 12
oriented Barrio crossings, and are the endpoint seeds one family or two?

## Why this replaces the failed EXP-136 gate

EXP-136 began each crossing count at the arbitrary shooting phase. That phase
lay within roughly `1.1e-6` time units of the section, while the terminal
allowance after one period was only about `7.5e-7`. A post-hoc window shift
restored the missing crossing and ruled out the initially suspected grazing.

EXP-137 therefore treats the periodic flow orbit as primary. Flow closure,
neutral multiplier, primitivity, and transverse instability remain stopping
gates. Section count is recorded separately over `(0.1 T, 1.1 T]` and is
qualified only after both complete paths have run.

## Frozen design

At fixed `(b,c)=(0.2,20)`, both EXP-133 primitive lag-12 seeds are continued in
opposite directions over all 21 points of `a in [0.148,0.14825]`, using the
same `1.25e-5` natural-continuation step and DOP853 reference tolerances as
EXP-136. No adaptive step rescue is allowed.

At `a=0.148125`, continuous phase-invariant whole-orbit comparison classifies
the paths prospectively:

- same family if relative period difference is at most `1e-6` and scaled RMS
  is at most `1e-5`;
- distinct families if relative period difference is at least `1e-4` or scaled
  RMS is at least `1e-3`; or
- inconclusive otherwise, which fails the classification gate.

The experiment passes only if both flow continuations reach the opposite
endpoint, all 42 phase-shifted counts equal 12, and the midpoint comparison is
decisive. Either `same` or `distinct` is an admissible prospective outcome.

Immutable manifest:
`experiments/manifests/EXP-137-phase-robust-lag12-flow-continuation.json`.

## Reproduction command

```bash
PYTHONPATH=python:scripts .venv/bin/python scripts/continue_pim_upos_in_a.py \
  --manifest experiments/manifests/EXP-137-phase-robust-lag12-flow-continuation.json \
  --source-receipt artifacts/EXP-133/receipt.json \
  --identity-receipt artifacts/EXP-135/receipt.json \
  --output artifacts/EXP-137/receipt.json
```

## Interpretation boundary

A pass establishes finite continuation and local orbit-family identity only.
It does not establish the manifold event that opens the third chaotic-saddle
return-map branch or explain the global hub superstructure.

## Result

The clean `5cd1544` run completes both 21-point flow continuations in
`126.39 s`. Every correction, closure, neutral-multiplier, primitivity, and
instability gate passes. All 42 shifted windows contain exactly 12 oriented
Barrio crossings, confirming that the EXP-136 count failure was a boundary
artifact.

The midpoint classifier reports `distinct`: relative period difference
`1.7970e-3` and scaled whole-orbit RMS `6092.16`. Nevertheless, the overall
receipt remains failed because the lower grid value is represented as
`0.14812499999999998`, and the implementation required bitwise equality with
`0.148125`. EXP-138 freezes a `1e-14` parameter tolerance and reruns the full
calculation. Raw receipt SHA-256:
`1269da1be112b45ab23e7d1eb23c538999f0ad1839e7a8932ef3b6c37a68077f`.
