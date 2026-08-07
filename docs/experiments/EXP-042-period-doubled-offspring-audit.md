# EXP-042 — Off-event period-doubled offspring audit

Status: executed; passed
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

## Result

The clean execution at commit `a2dd8e1385b2f0fd02f7ca0e326db20ca3f60e88`
passed every frozen gate at all three points.

| Event | Parent half closure | Parent fundamental modulus | Child half closure | Child full closure | Child modulus | Period ratio |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| source | `1.81e-12` | `1.01713` | `0.23338` | `1.01e-13` | `0.93178` | `1.999642` |
| separated `c=4.9` | `7.79e-13` | `1.01085` | `0.22906` | `2.16e-13` | `0.95700` | `1.999784` |
| minimum-`b` fold | `4.86e-12` | `1.00505` | `0.15867` | `2.34e-13` | `0.97979` | `2.000004` |

The complete receipt SHA-256 is
`51b4d48b2f6711d7e18655339c3c6639d373120341f81b757aab6917aaae0eff`.

## Decision

Accept direct off-event confirmation of a supercritical period-doubling at all
three qualified points. Beyond each event, the fundamental parent is unstable,
whereas a stable child closes only after approximately twice the parent's
fundamental period. The result independently confirms and strengthens the
event-point multiplier identity from EXP-041.

The local mechanism—including at the event curve's projection fold—is now
closed numerically. The research frontier moves from local classification to
global continuation: determine how many flip-surface components exist, where
they fold or connect, and how their intersections organize atlas window edges.
