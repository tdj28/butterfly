# EXP-521: from stationary-point identification to a contact-preserving step

The next scientific task is an executable c-response test, not another symbolic
word copied from Jones. Its target is a measured step along the local
fold/orbit-contact neighborhood toward the first identified periodic maximum's
section grazing. Both inner maxima remain tracked.

The [frozen protocol](../experiments/EXP-521-critical-periodic-response.md)
specifies four c-stencil points and one conditional correction, with complete
new raw audits. The plan SHA-256 is
`29178f095da8a15602e8290d0d2339437f57148efad3fdc9aac0ad1471f9303b`.
There are no EXP-521 target outcomes at this design checkpoint.

## Design audit and qualifications

- All five completed EXP-520 points pass unique full-state/phase/curvature
  matching of all 16 roots to the corrected anchor. The historical a-gap
  coarse/fine response qualifies. These are outcome-informed input checks,
  not new independently sampled observations.
- Reused a derivatives have a different center from the fresh c derivatives.
  The code records both centers, constrains a to the measured old domain,
  and requires new full-vector prediction agreement. It cannot label this an
  exact Jacobian or an exact critical locus.
- The second inner maximum can move away, but must pass identity and prediction
  checks. Neither an attractive first scalar nor a favorable stencil point can
  override failed full-state contact or substitute for the prescribed step.
- All 142 frozen EXP-519 source paths and all 70 EXP-520 paths were rehashed
  against their execution commits: no changes. The new source inventory has
  186 paths. Dependency files are carried byte-identically from the published
  parent branches; pending release CI does not imply new numerical authorization.
- Direct fixed-SHA authentication of completed parent audits replaces recursive
  replay of the growing historical startup chain. Every **new** raw trajectory
  still receives the complete numerical audit. This is an explicit prospective
  runner design, not a rewrite of an already-executed gate.

Preflight failure history is retained locally. The first synthetic pass caught
NumPy boolean values in the new verdict (not JSON serializable); corrected
before any target access. A combined-suite run then exposed that the test was
checking pytest's ambient imports, rather than the authentic isolated consumer.
The test now checks the real sealed consumer's validation result. Neither
repair changed a scientific threshold or any historical executed file.

The integrated final preflight passed **124 tests in 2.85 seconds** and covers controller, runner, exact-polynomial
census, old census runner, root isolation and bounded writer tests. Local XML
receipts remain under `artifacts/EXP-521/preflight-*.xml`; the synthetic execution
test uses mock fold authority and real file/census/audit accounting, and must not
be called an independent flow verification. An ordinary reference-core smoke
is distinct from the new target observations; that reference smoke also passed.

## Continuity and claim boundary

The work branch was cut from freshly fetched main. EXP-519 and EXP-520 release
PRs remain separate concerns; no failed CI check has been bypassed or represented
as passing. No new paid Pro review, Runpod charge or private raw upload was made.

This experiment is complete only after the prescribed measurements and raw
audit (including a negative or unqualified result), a dated result update and
a pushed checkpoint. Its design does not itself verify a Jones arrow.
