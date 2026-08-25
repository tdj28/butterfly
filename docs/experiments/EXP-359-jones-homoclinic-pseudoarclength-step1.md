# EXP-359 — First homoclinic pseudo-arclength step

Status: execution completed; receipt serialization failed

Repeated fixed-`c` and fixed-`a` corrections cannot distinguish a local
homoclinic-curve fold from singular endpoint conditioning. EXP-359 replaces
the forced coordinate with a two-parameter pseudo-arclength system. Both `a`
and `c` are free, and one explicit tangent-plane equation closes the 128-arc
boundary-value system.

The tangent is bound to the two qualified curve roots EXP-347 and EXP-350.
EXP-347's 32 arcs are deterministically subdivided to 128 using Radau, and its
departure angle is transformed into the common EXP-350 eigenspace gauge before
the secant is formed. The first desired advance is only `Delta c=0.0005`,
one-eighth of the qualified source interval.

All manifold radii, integration tolerances, 128-arc representation,
source-centered node guardrail, 40-evaluation budget, and the `1e-8` maximum
matching-defect gate remain fixed. Passing supplies one local
pseudo-arclength point; it cannot yet establish a fold or an intersection with
`a=0.1798`.

Manifest:
[`../../experiments/manifests/EXP-359-jones-homoclinic-pseudoarclength-step1.json`](../../experiments/manifests/EXP-359-jones-homoclinic-pseudoarclength-step1.json).

The clean solve reaches terminal output construction, but canonical JSON
serialization rejects NumPy boolean values in the final check map. No atomic
receipt is written, so EXP-359 cannot be classified scientifically even
though the optimizer completed. This is an administrative failure at the
receipt boundary.

The successor converts every check to a native JSON boolean, adds a regression
test for that boundary, and repeats the identical mathematical protocol under
a new experiment identifier. No source, predictor, solver, budget, or
acceptance gate changes.
