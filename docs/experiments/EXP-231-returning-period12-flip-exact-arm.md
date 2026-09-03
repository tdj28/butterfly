# EXP-231 — Exact returning-arm period-12 flip localization

Status: complete — administrative failure before receipt

EXP-230 removes the source-arm interpolation error and reveals a different
obstruction: the primitive period-12 child's real multiplier approaches and
crosses `-1` while the period-6 parent remains unstable. EXP-231 freezes
independent DOP853/Radau scalar localization inside
`c=[7.6256448847,7.6258741167]`.

Every evaluation freshly corrects the period-6 event at identical `c`, applies
the unchanged exact-arm offset, and corrects the period-12 orbit. The root must
retain primitive `14/16` child identity and agree across solvers within
`2e-7` in `c`. Bilateral points at `c_root±1.5e-4` must show stable versus
unstable primitive period-12 multipliers.

A pass establishes an exact sampled period-12 flip on this path. It does not
yet establish a stable period-24 child, supercriticality, a complete cascade,
a global child sheet, paired shrimp boundaries, TBA membership,
double-criticality, or a full-plane explanation.

Manifest:
[`../../experiments/manifests/EXP-231-returning-period12-flip-exact-arm.json`](../../experiments/manifests/EXP-231-returning-period12-flip-exact-arm.json).

## Result

The run stops before atomic receipt during Radau's right-bracket child
correction. The optimizer reports `xtol` termination with `success=false`, so
the inherited helper raises before evaluating the scientific residuals. A
deterministic replay recovers raw correction closure `6.76e-9`, phase residual
`2.09e-19`, reintegrated closure `6.03e-10`, neutral error `1.90e-8`, and
child multiplier `-1.00049880`: every numerical quantity is inside the
existing science thresholds.

EXP-232 changes only representation handling. It records optimizer status and
accepts an `xtol` stop only when raw closure and phase residual pass the frozen
gates; all orbit, multiplier, primitivity, section, bilateral, and cross-solver
thresholds are unchanged.
