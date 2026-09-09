# EXP-495 pre-outcome validation

2026-09-09. The target is a new cross-artifact analysis of already-published
states, not new integration. Relevant parent outcomes were already known;
the new fold-to-cycle distance matrix was not measured during this preflight.

The first 16 synthetic controls passed. The first authentic public-input
preflight then rejected an incorrectly assumed upstream terminal label:
EXP-494 uses `complete-ledger`, not `completed`. The exception occurred in
`validate_inputs` before the distance function or attempt-marker creation.
The source and synthetic fixture were corrected to the actual producer label;
the upstream artifact and its hash were not altered. A regression now invokes
the real public-input preflight with the distance function forbidden.

All **19 focused controls pass**, including the complete arithmetic matrix,
separate scalar replay, wrong successor, x-only false proximity, exact threshold,
cyclic wrap, failed parent family, one bad solver/window, missing and nonfinite
inputs, primitive-period failure, semantic tampering, an exclusive consumed
attempt and the explicit public replay path without a private attempt file.

The authentic public-input check passes for all 26 candidates and both base
cycles. It reports `new_distances_measured=false`; this is not a target result.
The plan hash at preflight is
`57295e6228a5ac4a621e5bd0d7bf7264aef25d82b9c9cd13784c9cb4216b1e1e`.

Local design audit: paired consecutive endpoints prevent a minimum-at-unrelated-
phases artifact; fixed full-state scaling prevents an x-only match from hiding
z separation; all variants and qualified finite-history representatives enter
the same-index envelope; failed parents are retained rather than counted as
zero distances. The radius is operational, not an error probability. The test
does not license C/D, exact superstable membership, an invariant quotient or
a Jones arrow. Source qualification and proximity are separate requirements.

The full regression suite passed **2138 tests**, with one existing Linux-only
process-identity skip, in 136.69 seconds. Its receipt is retained under
`artifacts/EXP-495/preflight-tests-01.xml`. The execution freeze follows
its successful completion and the staged public-repository scan. No paid
review was requested or run, under the human-directed review policy.
