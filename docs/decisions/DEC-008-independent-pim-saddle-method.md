# DEC-008 — Use strict PIM straddles as the independent saddle method

Date: 2026-08-07
Status: adopted for EXP-114

## Context

EXP-112 and EXP-113 qualify the same survival-ensemble sprinkler observable on
CPU and GPU. That is strong numerical convergence and backend parity, but not
structural method independence: both select a saddle from long-lived ensemble
survivors.

Nusse and Yorke define a proper interior maximum (PIM) triple as three ordered
points on a segment whose interior point has strictly longer escape time than
both neighbors. Recursively refining the segment and re-refining its mapped
image when the bracket expands produces a saddle-straddle trajectory. This
solves a different numerical problem from the sprinkler: restraining one
trajectory near the stable set rather than selecting a middle-time ensemble.

## Decision

EXP-114 uses the PIM construction on the Barrio first-return section with:

- adaptive DOP853 return integration and event localization;
- strict, not plateau or non-strict, interior escape-time maxima;
- five frozen full-width section segments at fixed `z` levels;
- deterministic longest-lifetime/lowest-index tie breaking;
- normalized bracket tolerance `1e-7`;
- repeated stable-period-4 capture as the declared escape event; and
- repeated refinement only after the mapped bracket exceeds tolerance.

Independent escape-time evaluations within one refinement level may run in an
ordered eight-process pool. This changes wall time only: result order, strict
maximum selection, integration, and all gates are identical to serial
execution. The parallel amendment was frozen after interrupting the first
serial launch before it emitted a line result.

The target controls are not executed until the implementation, manifest, and
acceptance gates are committed. Failed segments, censored lifetime evaluations,
and unresolved topology are retained rather than replaced after inspection.

## Independence boundary

The stable-cycle capture neighborhood and branch oracle intentionally remain
common measurement layers so the methods answer the same question. The saddle
construction and state integrator are independent: PIM straddling plus adaptive
DOP853 versus scrambled survival sprinklers plus fixed-step RK4/Hermite events.
Agreement therefore corroborates the invariant-set reconstruction without
pretending the observable definitions are unrelated.
