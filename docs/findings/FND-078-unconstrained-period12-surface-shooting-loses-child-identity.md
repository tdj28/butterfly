# FND-078 — Unconstrained period-12 surface shooting intermittently loses child identity

Status: qualified negative method result over the complete EXP-210 grid

EXP-210 completes all 124 fixed-parameter cells, but 16 nominal child
corrections converge to the double-covered parent. The failure is unambiguous:
opening RMS and every proper-subperiod closure collapse to numerical zero, and
the resulting doubled-parent orbit is unstable. The corrupted cells make the
strict surface gate fail despite 108 pointwise passes.

Several collapses are isolated between valid primitive stable children on the
same fixed-offset line. Valid anchors also exist independently at
`c=7.18,7.24,7.30`. The result therefore diagnoses competing shooting roots
and loss of orbit identity, not absence or physical termination of a period-12
sheet. Surface continuation must explicitly select a nonclosing child root.

Evidence:
[`../experiments/EXP-210-period12-surface.md`](../experiments/EXP-210-period12-surface.md).
