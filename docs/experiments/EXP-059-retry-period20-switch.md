# EXP-059 — Smaller-step period-20 switch retry

Status: executed; passed

Repeat the EXP-058 nullspace branch switch with step length `0.002` instead of
`0.006`, 20 requested points per direction, a wider `b` guard, and up to 140
corrector evaluations. All scientific gates remain unchanged: both directions
must contain at least 10 full-closure solutions, separate from the doubled
parent and from their own half-period images.

Passing supplies two local shooting sheets for the period-20 candidate. It
does not by itself prove they are the same geometric orbit or establish
criticality; that requires the next phase-invariant fixed-parameter test.

The clean run at `d0fcf59` passed. Both directions produce well-closed child
sheets, with 18 and 14 points, endpoint distances `0.0458` and `0.0470` from
the doubled parent, and endpoint half-period closures `0.2260` and `0.2246`.
The smallest shooting singular value is `2.70e-8` and tangent dot is zero.
Receipt SHA-256:
`050f5739c16216bca36c40dfe56bd4f4bc401e02a12c63e1cee4e7e8a32fc156`.

Accept the local period-20 branch candidate. Both arms contain stable points
near the event and become unstable farther below it. EXP-060 independently
corrects parent and children at `b=0.18`, tests whether the arms are the same
geometric orbit, and verifies the expected stability exchange.
