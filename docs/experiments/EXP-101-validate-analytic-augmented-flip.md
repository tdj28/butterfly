# EXP-101 — Validate the exact-Jacobian augmented flip solve

Status: preregistered; not executed

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
