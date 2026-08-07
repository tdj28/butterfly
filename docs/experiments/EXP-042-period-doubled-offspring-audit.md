# EXP-042 — Off-event period-doubled offspring audit

Status: preregistered; pending clean execution
Manifest: `experiments/manifests/EXP-042-period-doubled-offspring-audit.json`
Claim target: direct parent/offspring confirmation of the EXP-041 flip classification

## Hypothesis and method

At the source, separated-`c`, and minimum-`b` fold events qualified by EXP-041,
move prospectively to the fixed offset `b=b*+0.0004`. Independently correct the
parent from its event orbit and the child from the negative switched branch.

The corrected parent, still stored over two traversals, must close at half its
stored period and be unstable under that fundamental traversal. The child must
close over its full period but not at half-period, must be stable, and must have
period approximately twice the parent's fundamental period.

This test uses only previously frozen event and switched-branch receipts. The
offset, branch direction, solver, and all gates were fixed before execution.

## Acceptance and limits

At all three points, full parent and child closures must be at most `1e-8`, and
parent half-period closure must also be at most `1e-8`. Child half-period
closure must be at least `0.01`. The parent fundamental transverse multiplier
modulus must be at least `1.0001`, the child full-period transverse modulus at
most `0.9999`, and the child/parent-fundamental period ratio must lie within
`0.02` of two.

Passing will independently confirm a supercritical period-doubling: beyond the
surface the fundamental parent is unstable and a stable orbit with twice its
period exists. It will not prove global surface uniformity, rule out additional
attractors, or replace interval validation.
