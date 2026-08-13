# EXP-232 — Residual-safe exact period-12 flip localization

Status: frozen — not yet executed

EXP-231 stops administratively when Radau reports `xtol` termination at the
right endpoint despite raw closure `6.76e-9` and phase residual `2.09e-19`.
EXP-232 retains the bracket, solvers, exact source-event correction, bilateral
points, and every scientific threshold.

The sole change is receipt-visible correction handling: `success=false` is
accepted only for the exact `xtol` message and only when raw correction closure
is at most `2e-8` and phase residual at most `1e-8`. Root primitivity, `7/8`
versus `14/16` section identity, multiplier/neutral residuals, bilateral
stable/unstable exchange, and DOP853/Radau root agreement remain mandatory.

A pass establishes an exact sampled period-12 flip on this path. It does not
establish a stable period-24 child or supercriticality.

Manifest:
[`../../experiments/manifests/EXP-232-returning-period12-flip-residual-safe.json`](../../experiments/manifests/EXP-232-returning-period12-flip-residual-safe.json).
