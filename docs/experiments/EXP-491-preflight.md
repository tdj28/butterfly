# EXP-491 preflight

2026-09-08 local date; prospective, before the target marker exists.

- All 26 original candidates / 16 families are independently reconstructed
  through the frozen EXP-490 input validator. Three points and two solvers
  give 156 target trajectories; there are no alternative seeds or retries.
- The complete analytic control run at
  `artifacts/EXP-491/preflight-controls-01/controls.json` passed all eight
  triples (48 solver profiles). SHA-256:
  `1a0fb0fec8443a8d2fd26f9a7727fb28348284ab3ffe504d1435edbbb1cb5b8e`.
  `audit_exp491_event_sheet_probe.check_controls` independently checked the
  known event times and sensitivities and replayed every decision. These are
  same-agent numerical audits, not independent peer review.
- The exact-tangency control explicitly permits an uncertain numerical pair
  at the central tangency, but requires rejecting that point. Its two regular
  endpoints have independently known event counts. Requiring a particular
  count at the uncertain center would itself be an incorrect control oracle.
- The stricter uncertain-extremum adjacency guard was designed and tested
  before the target run. The read-only impact audit covers all 52 EXP-490
  profiles and their 72 census reports: **zero uncertain extrema and zero
  newly rejected censuses**. Its public receipt is
  [EXP-491-legacy-uncertainty-impact.json](receipts/EXP-491-legacy-uncertainty-impact.json),
  SHA-256 `b9999e24cfc14b307f4c779b2a3ccdc7c9465609f47055c2c91fcccac33f4546`.
  This does not clear other legacy issues or change EXP-490's verdicts.
- Twenty-one focused tests pass. They include all solver-error channels,
  missing/duplicated arms, altered manifest settings, a coherent nonlinear
  time curve, jumps, input sign changes and uncertainty immediately after a
  selected crossing. Full suite: **1,960 passed, one platform-specific skip**
  in 129.31 seconds (`.venv/bin/python -m pytest -q`). The skip requires Linux
  `/proc`; this execution host is macOS.
- The local filesystem has approximately 27 GiB available, above the 16 GiB
  start requirement. The runner additionally enforces an 8 GiB floor, 8 GiB
  output cap, 156-target cap and 7,200-second whole-run deadline. It checks
  storage before and after each integration. No paid services are used.
- The runtime feasibility heuristic uses EXP-490's observed 1,572.141615 s:
  `2 * 1572.141615 * 156 / 72 = 6812.613665 s`. This deliberately charges the
  entire old run (including Newton and controls) to its 72 censuses before
  doubling. It is an operational estimate, not a performance guarantee.

The target run repeats all analytic controls before consuming its exclusive
marker. A completed control run does not authorize resetting a consumed
target attempt. Raw meshes remain local and ignored by Git; public compact
receipts and checked-in scripts do not constitute a released raw archive.
