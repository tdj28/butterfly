# EXP-033 — Expanded period-5 unit-event curve across a

Status: executed; failed
Manifest: `experiments/manifests/EXP-033-expanded-period5-unit-event-a-curve.json`
Claim target: bounded extension of the EXP-028/032 event curve

## Hypothesis and method

The coupled period-5 pitchfork-like event continues smoothly at fixed `c=5.1`
across the wider `a in [0.225,0.265]` interval. Use nine frozen values at
spacing `0.005`, continuing independently upward and downward from EXP-028.
Each point must solve the complete orbit/unit-eigenvector system; EXP-032's
solved rows are not used as numerical inputs.

## Acceptance and limits

All nine points are required inside the prospectively expanded
`b in [0.15,0.4]` domain. Closure, nontrivial eigen, and flow-orthogonality
residuals must be at most `1e-8`, with no adjacent `b` jump over `0.03`.

Passing establishes a bounded fixed-`c` event curve over four times EXP-032's
`a` span. It does not establish persistence of the pitchfork normal form at
every point, a two-dimensional surface under `c`, or a connection to the
return-map topology-change/TBA locus.

## Result and decision

The clean run at commit `a1de99ba6548ba1aacf95b75f088a30051acc7ab`
failed. The doubled `a` step was too large for natural seeding. Downward from
the source, the `a=0.24` corrector terminated at a spurious high-residual state
(`closure=0.391`, `eigen residual=0.371`, `b=0.38746`). Upward, valid events
were recovered at `a=0.25` and `0.255`, but the initial fixed-`b` periodic
correction then failed before `a=0.26`. The overall receipt contains four rows,
one explicitly invalid, and must not be used as an event curve. Its SHA-256 is
`8953304eb9ffbe613d52de9a4121ed2d8baffe0a08e647416755f747729e4e49`.

This failure identifies a continuation-resolution limit rather than evidence
that the mathematical curve terminates. EXP-032 already qualified step
`0.0025` over its solved domain. EXP-034 prospectively retains the expanded
domain but restores that finer step, starts again from EXP-028, and does not use
any EXP-033 row as a seed. Full pseudo-arclength in the event surface remains
the longer-term fix if the finer natural continuation also fails.
