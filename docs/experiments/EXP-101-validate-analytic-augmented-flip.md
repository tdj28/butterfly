# EXP-101 — Validate the exact-Jacobian augmented flip solve

Status: executed; failed at the frozen evaluation cap

Repeat EXP-100's mandatory known-event validation with the same full EXP-089
source receipt, `b` perturbation `+5e-9`, bounds
`[0.17971245,0.17971255]`, 32 segments, and baseline integrator. Bind the
failed full EXP-100 receipt so the comparison cannot silently change the
starting problem.

Replace only the derivative engine. For each segment, integrate the Rössler
flow, transition matrix, `b` sensitivity, transported tangent, tangent
initial-state sensitivity, and tangent `b` sensitivity. The last two satisfy
the exact second-variational equations. The Rössler Hessian contributes only
the symmetric third-component action
`p_z q_x + p_x q_z`. Unit tests compare the segment actions and complete
augmented Jacobian with centered finite differences before execution.

Permit at most 20 exact residual/Jacobian evaluations with tolerance `1e-11`.
Pass only if the solver reports success, recovers the EXP-089 event within
`5e-10`, and has orbit, phase, tangent-transport, and normalization residuals
each `<=1e-8`. Four direct monodromy products must select the eigenvalue
closest to `-1`, have real residual `<=1e-6`, imaginary part `<=1e-8`, and
cyclic spread `<=1e-8`. The block-cyclic cluster closest to `-1` must agree
within `1e-8`; generic neutral/nontrivial labels are deliberately not used.

Passing validates DEC-003's analytic formulation at period 320 and permits a
separately preregistered period-640 application. It does not itself correct the
eighth event or establish a period-1280 child. Failure keeps the target locked
and requires diagnosis before any further event claim.

The clean run at `3bcb0a2c91c6baefbe18c84e4948671234f98c5e` exhausted the
20-evaluation cap after `207.38 s`. It reduced the total residual from
`3.09e-4` to `1.79e-9`. Orbit matching `1.78e-9`, tangent transport
`1.77e-10`, phase `7.94e-19`, and normalization `1.45e-12` all pass their
frozen gates. Four direct products give `-0.99999997628334` with spread
`1.55e-15`, and the explicitly selected block flip cluster agrees within
`3.20e-14`. This confirms both the exact derivatives and the corrected
spectral selection. Full receipt SHA-256:
`be34f74bde50df60763f26b25179e1309c953aa08e0413131e77bad98c9ff95a`.

The experiment still fails: the solver does not report success at the cap and
the recovered `b=0.17971249507978945` is `1.086e-9` from the EXP-089
reference, above the required `5e-10`. Relative to EXP-100, wall time falls
from `2367.32 s` to `207.38 s` (`11.4x`) while the orbit residual improves by
`97x`. A separately frozen exact-Jacobian resume may bind this full receipt and
continue from its stored nodes and tangent field; no target-period application
is permitted yet.
