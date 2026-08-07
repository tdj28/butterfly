# EXP-059 — Smaller-step period-20 switch retry

Status: preregistered after EXP-058; pending clean execution

Repeat the EXP-058 nullspace branch switch with step length `0.002` instead of
`0.006`, 20 requested points per direction, a wider `b` guard, and up to 140
corrector evaluations. All scientific gates remain unchanged: both directions
must contain at least 10 full-closure solutions, separate from the doubled
parent and from their own half-period images.

Passing supplies two local shooting sheets for the period-20 candidate. It
does not by itself prove they are the same geometric orbit or establish
criticality; that requires the next phase-invariant fixed-parameter test.
