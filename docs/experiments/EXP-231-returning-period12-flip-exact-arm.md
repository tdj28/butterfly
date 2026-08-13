# EXP-231 — Exact returning-arm period-12 flip localization

Status: frozen — not yet executed

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
